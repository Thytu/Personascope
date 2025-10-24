import json
import model
import asyncio

from tqdm import tqdm
from typing import List, Any
from dataset_loader.huberman_lab import load_dataset
from model import Feature, StatsFeatureEvaluation
from constants import MODELS_TO_ANALYZE, NUM_RUBRICS_PER_MODEL, NUM_EVALUATIONS_PER_MODEL, MAX_STD_DEVIATION


# NOTE: would be good to evaluate variance per model, so we know if some model are more reliable than others
# TODO: do the same but skip the rubric creation and directly use Big 5


def _save_to_json(data: Any, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def _print_stats_features_evaluation(stats: List[StatsFeatureEvaluation]) -> None:
    for stats_feature_evaluation in stats:
        print(f"Feature: {stats_feature_evaluation.evaluations[0].feature.name}")
        print(f"- Description: {stats_feature_evaluation.evaluations[0].feature.description}")
        print(f"- Description Min Value: {stats_feature_evaluation.evaluations[0].feature.description_min_value}")
        print(f"- Description Max Value: {stats_feature_evaluation.evaluations[0].feature.description_max_value}")
        print(f"- Average Score: {stats_feature_evaluation.average_score}")
        print(f"- Standard Deviation: {stats_feature_evaluation.standard_deviation}")
        print(f"- Variance: {stats_feature_evaluation.variance}", end="\n\n")

    std_deviations = [stats_feature_evaluation.standard_deviation for stats_feature_evaluation in stats]
    print(f"Average Standard Deviation: {sum(std_deviations) / len(std_deviations)}")
    print("-" * 100, end="\n\n")


async def main():

    train_set, test_set, validation_set = load_dataset("dataset/huberman_lab")

    features_bank: List[Feature] = [] # candidate features

    # ####################################################################################################################################
    # # TODO: remove this (for debugging purposes)
    keep_ratio = 0.25
    train_set = train_set[:int(len(train_set) * keep_ratio)]
    test_set = test_set[:int(len(test_set) * keep_ratio)]
    validation_set = validation_set[:int(len(validation_set) * keep_ratio)]
    # ####################################################################################################################################

    # TODO: use multiprocessing to speed up the process
    pbar = tqdm(train_set, desc="Generating features bank", leave=False)
    for batch in pbar:

        data_sample = "\n".join([segment for segment in batch])

        new_features_candidates = await asyncio.gather(*[
            model.generate_features(data_sample, model=_model_name, n_rubrics=NUM_RUBRICS_PER_MODEL)
            for _model_name in MODELS_TO_ANALYZE
        ])

        new_features_candidates = [feature for model_group in new_features_candidates for rubric_group in model_group for feature in rubric_group] # flatten 2 levels (models x rubrics)

        new_features_candidates = await model.merge_similar_features(new_features_candidates)

        new_features_candidates = await model.filter_features_candidates_against_bank(new_features_candidates, features_bank)

        if len(new_features_candidates) == 0:
            continue

        new_features_candidates = await model.evaluate_features_scores(data_sample, new_features_candidates, MODELS_TO_ANALYZE, num_evaluations_per_model=NUM_EVALUATIONS_PER_MODEL)

        new_features_candidates = list(filter(lambda x: x.standard_deviation <= MAX_STD_DEVIATION, new_features_candidates)) # filter out features with high standard deviation

        features_bank.extend([feature.evaluations[0].feature for feature in new_features_candidates]) # discard statistics, keep only the feature
        pbar.set_postfix({"features": len(features_bank)})

    print(f"Features candidates generated: {len(features_bank)}")
    _save_to_json([feature.model_dump() for feature in features_bank], "output/features_bank_unfiltered.json")

    # NOTE: maybe we should try merging features from the bank who are covering the same aspect of personality (making broader more general features)
    # or maybe this will be done by checking correlation

    # Test on segments present in the train set
    train_stats = await model.evaluate_features_scores_across_conversations(train_set, features_bank, MODELS_TO_ANALYZE, num_evaluations_per_model=NUM_EVALUATIONS_PER_MODEL)
    print("Train stats computed")

    # Filter out unstable features from both train_stats and features_bank
    unstable_feature_names = {s.evaluations[0].feature.name for s in train_stats if s.standard_deviation > MAX_STD_DEVIATION}
    features_bank = [f for f in features_bank if f.name not in unstable_feature_names]
    train_stats = [s for s in train_stats if s.evaluations[0].feature.name not in unstable_feature_names]
    print(f"Filtered bank to keep only stable features: {len(features_bank)}")

    _save_to_json([feature.model_dump() for feature in features_bank], "output/features_bank.json")
    _print_stats_features_evaluation(train_stats)

    # TODO: merge features from the bank who have a high correlation into broader more general features

    # Test on segments not present in the train set
    test_stats = await model.evaluate_features_scores_across_conversations(test_set, features_bank, MODELS_TO_ANALYZE, num_evaluations_per_model=NUM_EVALUATIONS_PER_MODEL)
    _print_stats_features_evaluation(test_stats)

    # Test on podcast episodes not present in the train/test sets
    validation_stats = await model.evaluate_features_scores_across_conversations(validation_set, features_bank, MODELS_TO_ANALYZE, num_evaluations_per_model=NUM_EVALUATIONS_PER_MODEL)
    _print_stats_features_evaluation(validation_stats)


if __name__ == "__main__":
    asyncio.run(main())
