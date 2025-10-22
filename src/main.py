"""
1. get dataset
2. Find stable features
"""

import model
import asyncio

from dataset import build_host_batches


DATASET_MIN_TURN = 10

MODELS_TO_ANALYZE = [
    # Mini / Flash
    # "google/gemini-2.5-flash-lite-preview-06-17",
    "openai/gpt-4.1-mini",

    # "anthropic/claude-sonnet-4.5",
    # "openai/gpt-4.1",
    # "openai/gpt-5",
    # "google/gemini-2.5-pro",
]

NUM_RUBRICS_PER_MODEL = 2
NUM_EVALUATIONS_PER_MODEL = 5
MAX_STD_DEVIATION = 1


# NOTE: would be good to evaluate variance per model, so we know if some model are more reliable than others
# TODO: do the same but skip the rubric creation and directly use Big 5
async def main():

    train_set, test_set = build_host_batches()
    conversation = "\n".join([segment["text"] for segment in train_set[0]])

    rubrics = await asyncio.gather(*[
        model.generate_rubric(conversation, model=_model_name, n_rubrics=NUM_RUBRICS_PER_MODEL)
        for _model_name in MODELS_TO_ANALYZE
    ])
    rubrics = [_rubric for sublist in rubrics for _rubric in sublist] # flatten

    evaluated_features = await model.evaluate_features(conversation, rubrics, MODELS_TO_ANALYZE, num_evaluations_per_model=NUM_EVALUATIONS_PER_MODEL)
    evaluated_features = sorted(evaluated_features, key=lambda x: x.standard_deviation)
    evaluated_features = list(filter(lambda x: x.standard_deviation <= MAX_STD_DEVIATION, evaluated_features))

    print("--- Evaluated features ---")
    for _feature in evaluated_features:
        print(f"Name: {_feature.evaluations[0].feature.name}")
        print(f"- Description: {_feature.evaluations[0].feature.description}")
        print(f"- Description Min Value: {_feature.evaluations[0].feature.description_min_value}")
        print(f"- Description Max Value: {_feature.evaluations[0].feature.description_max_value}")
        print(f"- Min Score: {_feature.min_score}")
        print(f"- Max Score: {_feature.max_score}")
        print(f"- Average Score: {_feature.average_score}")
        print(f"- Standard Deviation: {_feature.standard_deviation}")
        print(f"- Variance: {_feature.variance}")
        print(f"- Number of Evaluations: {_feature.num_evaluations}")
        print(end="\n\n")

    merged_features = await model.merge_correlated_features([_feature.evaluations[0].feature for _feature in evaluated_features], model=MODELS_TO_ANALYZE[0])

    print("--- Merged features ---")
    for _feature in merged_features:
        print(f"Name: {_feature.name}")
        print(f"- Description: {_feature.description}")
        print(f"- Description Min Value: {_feature.description_min_value}")
        print(f"- Description Max Value: {_feature.description_max_value}")
        print(end="\n\n")


    # TODO: Run evaluation using final features on train set

    # TODO: Run evaluation using final features on test set and compute accuracy


if __name__ == "__main__":
    asyncio.run(main())
