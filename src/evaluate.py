import json
import model
import asyncio

from dataset_loader.crucible_moments import load_dataset
from model import Feature, StatsFeatureEvaluation
from constants import MODELS_TO_ANALYZE, NUM_EVALUATIONS_PER_MODEL


def _print_stats_features_evaluation(stats: list[StatsFeatureEvaluation]) -> None:
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

    train_set, test_set, validation_set = load_dataset("dataset/crucible_moments", max_words_per_batch=2000)

    validation_set.extend(train_set)
    validation_set.extend(test_set)

    features_bank = json.load(open("output/features_bank.json"))
    features_bank = [Feature.model_validate(_feature) for _feature in features_bank]

    # ####################################################################################################################################
    # # TODO: remove this (for debugging purposes)
    # keep_ratio = 0.25
    # validation_set = validation_set[:int(len(validation_set) * keep_ratio)]
    # ####################################################################################################################################

    validation_stats = await model.evaluate_features_scores_across_conversations(validation_set, features_bank, MODELS_TO_ANALYZE, num_evaluations_per_model=NUM_EVALUATIONS_PER_MODEL)
    _print_stats_features_evaluation(validation_stats)

if __name__ == "__main__":
    asyncio.run(main())
