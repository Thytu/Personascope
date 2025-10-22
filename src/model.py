import asyncio
import constants

from typing import List, Dict
from pydantic import BaseModel
from openai import AsyncOpenAI
from statistics import mean, stdev, variance


RUBRIC_GENERATION_SYSTEM_PROMPT = """
You are an expert Social Science researcher designing feature detectors for subjective traits in conversational data.

Your goal is to propose a structured evaluation schema (“rubric”) that captures the perceived personality and tone of a given conversational dataset sample.

Follow these principles:
* The rubric should consist of continuous dimensions (rated 0-10) that describe how the speaker "feels" to an observer.
* Do not focus on correctness or content; instead, focus on style, tone, and interpersonal perception.
* Include the interpretable traits you perceive in the conversation, each with a short description and clear semantic contrast (e.g., “0 = cold/detached, 10 = warm/affectionate”).
* The dimensions should collectively cover aspects like: emotional tone, personality expression, conversational style, and relationship dynamics.
* The goal is not to define the ground truth, but to capture what the you perceive, subjective impressions are acceptable.
""".strip()


RUBRIC_EVALUATION_SYSTEM_PROMPT = """
You are an expert rater applying a subjective style/persona rubric to conversational text.

Your job: score each trait 0-10, cite evidence spans, and return a clean machine-readable object.

You are evaluating style/tone only (not factual correctness or task quality).
""".strip()


MERGE_CORRELATED_FEATURES_SYSTEM_PROMPT = """
You are an expert Social Science researcher.

Given a list of features, merge the features that are highly correlated (either positively or negatively) into a single feature.
You must output the list of deduplicated features. The 10-score should represent the maximum presence of the feature in the conversation, the 0-score should represent the antonym of the feature, and the 5-score should represent the neutrality/absence of the feature.
""".strip()


DEDUPE_AGAINST_BANK_SYSTEM_PROMPT = """
You are an expert Social Science researcher.

You will be given two lists of features:
- Bank: features that have already been accepted
- Candidates: newly proposed features

Task: Return ONLY the subset of Candidate features that are NOT already represented in the Bank. Use semantic equivalence, not exact string match. Consider synonyms, near-synonyms, inversions along the same axis, and overlapping constructs.

Guidelines:
- If a Candidate meaning substantially overlaps with any Bank feature (even if phrased differently), exclude the Candidate.
- If a Candidate is narrower but does not introduce a clearly distinct evaluative axis, exclude it.
- If a Candidate introduces a genuinely new axis of evaluation, keep it as-is.
- Preserve the original Candidate text (name and descriptions) for any kept feature.

Output: A list of Feature objects. If no Candidates remain after deduplication, return an empty list.
""".strip()

openrouter_client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=constants.SECRET_OPENROUTER_API_KEY.get_secret_value(),
)


class Feature(BaseModel):
    name: str
    description: str
    description_min_value: str
    description_max_value: str


class FeatureListModelResponse(BaseModel):
    features: List[Feature]


class FeatureEvaluation(BaseModel):
    feature: Feature
    explanation: str
    score: float


class StatsFeatureEvaluation(BaseModel):
    evaluations: List[FeatureEvaluation]
    min_score: float
    max_score: float
    average_score: float
    standard_deviation: float
    variance: float
    num_evaluations: int


class FeaturesEvaluationResponse(BaseModel):
    evaluated_features: List[FeatureEvaluation]


# NOTE: To improve reliability, we should:
# - Have the first output in freeform text invinting the model to think and write down its thoughts (like a scratchpad)
# - Have the second output in the structured rubric format based on the first output
# (like authors have done in General Social Agent paper)
async def generate_features(conversation: str, model: str, n_rubrics: int) -> List[Feature]:
    rubrics = await asyncio.gather(*[
        openrouter_client.responses.parse(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": RUBRIC_GENERATION_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": f"Conversation:\n```\n{conversation}\n```"
                }
            ],
            text_format=FeatureListModelResponse
        )
        for _ in range(n_rubrics)
    ], return_exceptions=True)

    num_errors = len([_rubric for _rubric in rubrics if isinstance(_rubric, Exception)])

    if num_errors > 0:
        print(f"{num_errors} error(s) generating rubrics")

    if num_errors == len(rubrics):
        raise ValueError(f"All rubrics generation failed: {rubrics[0]}")

    return [_rubric.output_parsed.features for _rubric in rubrics if not isinstance(_rubric, Exception)]


async def __evaluate_features_scores(conversation: str, features: List[Feature], model: str) -> List[FeatureEvaluation]:
    model_output = await openrouter_client.responses.parse(
        model=model,
        temperature=1.0,
        input=[
            {
                "role": "system",
                "content": RUBRIC_EVALUATION_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"Conversation:\n```\n{conversation}\n```\nFeatures:\n```\n{features}\n```"
            }
        ],
        text_format=FeaturesEvaluationResponse
    )

    return model_output.output_parsed.evaluated_features


async def evaluate_features_scores(conversation: str, features: List[Feature], models: List[str], num_evaluations_per_model: int) -> List[StatsFeatureEvaluation]:

    evaluated_features: List[List[FeatureEvaluation]] = await asyncio.gather(*[
        __evaluate_features_scores(conversation, features, model=_model_name)
        for _model_name in models
        for _ in range(num_evaluations_per_model)
    ], return_exceptions=True)

    num_errors = len([_evaluation for _evaluation in evaluated_features if isinstance(_evaluation, Exception)])

    if num_errors > 0:
        print(f"{num_errors} error(s) evaluating features scores")

    evaluated_features = [_evaluation for _evaluation in evaluated_features if not isinstance(_evaluation, Exception)] # filter out errors

    evaluated_features: List[FeatureEvaluation] = [_evaluation for sublist in evaluated_features for _evaluation in sublist] # flatten


    # Group evaluations by feature name (uniqueness based on name)
    feature_grouped_by_name: dict[str, List[FeatureEvaluation]] = {}
    feature_order: List[str] = []
    for evaluation in evaluated_features:
        feature_name = evaluation.feature.name
        if feature_name not in feature_grouped_by_name:
            feature_grouped_by_name[feature_name] = []
            feature_order.append(feature_name)
        feature_grouped_by_name[feature_name].append(evaluation)

    # Build FeatureEvaluation objects with summary statistics
    output: List[StatsFeatureEvaluation] = []
    for feature_name in feature_order:

        evaluations_for_feature = feature_grouped_by_name[feature_name]
        scores = [e.score for e in evaluations_for_feature]

        if len(scores) < 2:
            print(f"Skipping feature '{feature_name}' because not enough evaluations. (Need at least 2 evaluations)")
            continue # We need at least 2 evaluations to compute statistics

        output.append(StatsFeatureEvaluation(
            evaluations=evaluations_for_feature,
            min_score=min(scores),
            max_score=max(scores),
            average_score=mean(scores),
            standard_deviation=stdev(scores),
            variance=variance(scores),
            num_evaluations=len(scores),
        ))

    return sorted(output, key=lambda x: x.standard_deviation)


async def evaluate_features_scores_across_conversations(conversations: List[str], features: List[Feature], models: List[str], num_evaluations_per_model: int) -> List[StatsFeatureEvaluation]:

    evaluations: Dict[str, List[FeatureEvaluation]] = {feature.name: [] for feature in features}

    batched_evaluations = await asyncio.gather(*[
        evaluate_features_scores(
            "\n".join([segment["text"] for segment in batch]),
            features,
            models,
            num_evaluations_per_model=num_evaluations_per_model
        )
        for batch in conversations
    ])

    for batch_evaluations in batched_evaluations:
        for _evaluation in batch_evaluations:
            evaluations[_evaluation.evaluations[0].feature.name].extend(_evaluation.evaluations)

    stats = []
    for feature_evaluations in evaluations.values():

        stats.append(StatsFeatureEvaluation(
            evaluations=feature_evaluations,
            min_score=min(_evaluation.score for _evaluation in feature_evaluations),
            max_score=max(_evaluation.score for _evaluation in feature_evaluations),
            average_score=mean(_evaluation.score for _evaluation in feature_evaluations),
            standard_deviation=stdev(_evaluation.score for _evaluation in feature_evaluations),
            variance=variance(_evaluation.score for _evaluation in feature_evaluations),
            num_evaluations=len(feature_evaluations),
        ))

    return sorted(stats, key=lambda x: x.standard_deviation)


# TODO: try out empirical (numerical) correlation approach to merge correlated features
async def merge_similar_features(features: List[Feature], model: str = "openai/gpt-4.1") -> List[Feature]:
    response = await openrouter_client.responses.parse(
        model=model,
        input=[
            {
                "role": "system",
                "content": MERGE_CORRELATED_FEATURES_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"Features:\n```\n{features}\n```"
            }
        ],
        text_format=FeatureListModelResponse
    )

    return response.output_parsed.features


async def filter_features_candidates_against_bank(candidates: List[Feature], bank: List[Feature], model: str = "openai/gpt-4.1") -> List[Feature]:

    if len(candidates) == 0:
        return []

    if len(bank) == 0:
        return candidates

    response = await openrouter_client.responses.parse(
        model=model,
        input=[
            {
                "role": "system",
                "content": DEDUPE_AGAINST_BANK_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": (
                    "Bank features:\n```\n"
                    f"{bank}\n"
                    "```\n\n"
                    "Candidate features:\n```\n"
                    f"{candidates}\n"
                    "```"
                )
            }
        ],
        text_format=FeatureListModelResponse
    )

    return response.output_parsed.features
