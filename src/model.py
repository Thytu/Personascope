import asyncio
import constants

from typing import List
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

openrouter_client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=constants.OPENROUTER_API_KEY.get_secret_value(),
)


class Feature(BaseModel):
    name: str
    description: str
    description_min_value: str
    description_max_value: str


class ModelFeatureEvaluation(BaseModel):
    feature: Feature
    explanation: str
    score: float

class FeatureEvaluation(BaseModel):
    evaluations: List[ModelFeatureEvaluation]
    min_score: float
    max_score: float
    average_score: float
    standard_deviation: float
    variance: float
    num_evaluations: int


class RubricResponse(BaseModel):
    features: List[Feature]


class RubricEvaluationResponse(BaseModel):
    evaluated_features: List[ModelFeatureEvaluation]


# NOTE: To improve reliability, we should:
# - Have the first output in freeform text invinting the model to think and write down its thoughts (like a scratchpad)
# - Have the second output in the structured rubric format based on the first output
# (like authors have done in General Social Agent paper)
async def generate_rubric(conversation: str, model: str, n_rubrics: int) -> List[RubricResponse]:
    conversations = await asyncio.gather(*[
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
            text_format=RubricResponse
        )
        for _ in range(n_rubrics)
    ], return_exceptions=True)

    num_errors = len([_conversation for _conversation in conversations if isinstance(_conversation, Exception)])

    if num_errors > 0:
        print(f"{num_errors} error(s) generating rubrics")

    if num_errors == len(conversations):
        raise ValueError(f"All rubrics generation failed: {conversations[0]}")

    return [_conversation.output_parsed for _conversation in conversations if not isinstance(_conversation, Exception)]


async def __evaluate_feature_variance_in_rubric(conversation: str, rubric: RubricResponse, model: str) -> RubricEvaluationResponse:
    conversation = await openrouter_client.responses.parse(
        model=model,
        temperature=1.0,
        input=[
            {
                "role": "system",
                "content": RUBRIC_EVALUATION_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"Conversation:\n```\n{conversation}\n```\nRubric:\n```\n{rubric}\n```"
            }
        ],
        text_format=RubricEvaluationResponse
    )

    return conversation.output_parsed


async def evaluate_features(conversation: str, rubrics: List[RubricResponse], models: List[str], num_evaluations_per_model: int) -> List[FeatureEvaluation]:

    evaluated_rubrics: List[RubricEvaluationResponse] = await asyncio.gather(*[
        __evaluate_feature_variance_in_rubric(conversation, _rubric, model=_model_name)
        for _rubric in rubrics
        for _model_name in models
        for _ in range(num_evaluations_per_model)
    ], return_exceptions=True)

    num_errors = len([_evaluation for _evaluation in evaluated_rubrics if isinstance(_evaluation, Exception)])

    if num_errors > 0:
        print(f"{num_errors} error(s) evaluating rubrics")

    evaluated_rubrics = [_evaluation for _evaluation in evaluated_rubrics if not isinstance(_evaluation, Exception)]

    features: List[ModelFeatureEvaluation] = [
        _feature
        for _evaluation in evaluated_rubrics
        for _feature in _evaluation.evaluated_features
    ]

    output: List[FeatureEvaluation] = []

    if not features:
        return output

    # Group evaluations by feature name (uniqueness based on name )
    feature_grouped_by_name: dict[str, List[ModelFeatureEvaluation]] = {}
    feature_order: List[str] = []
    for evaluation in features:
        feature_name = evaluation.feature.name
        if feature_name not in feature_grouped_by_name:
            feature_grouped_by_name[feature_name] = []
            feature_order.append(feature_name)
        feature_grouped_by_name[feature_name].append(evaluation)

    # Build FeatureEvaluation objects with summary statistics
    for feature_name in feature_order:

        evaluations_for_feature = feature_grouped_by_name[feature_name]
        scores = [e.score for e in evaluations_for_feature]

        if len(scores) < 2:
            print(f"Skipping feature '{feature_name}' because not enough evaluations. (Need at least 2 evaluations)")
            continue # We need at least 2 evaluations to compute statistics

        output.append(FeatureEvaluation(
            evaluations=evaluations_for_feature,
            min_score=min(scores),
            max_score=max(scores),
            average_score=mean(scores),
            standard_deviation=stdev(scores),
            variance=variance(scores),
            num_evaluations=len(scores),
        ))

    return output

# TODO: try out empirical (numerical) correlation approach to merge correlated features
async def merge_correlated_features(features: List[Feature], model: str = "openai/gpt-4.1-mini") -> List[Feature]:
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
        text_format=RubricResponse
    )

    return response.output_parsed.features
