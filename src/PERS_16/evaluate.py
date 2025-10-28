import asyncio

from tqdm import tqdm
from openai import AsyncOpenAI
from typing import Dict, Literal
from statistics import stdev, mean
from tenacity import retry, stop_after_attempt, wait_fixed, RetryCallState
from constants import IPIP_QUESTIONS, QUESTION_TEMPLATE, PERS16_LABELS, SCORES, IPIPQuestion
from ask_delphi import ask_delphi, Delphi


openai_client = AsyncOpenAI()


def __log_retried_error(retry_state: RetryCallState) -> None:
    print(f"An error occurred (at attempt {retry_state.outcome.attempt_number}): {retry_state.outcome.exception()=}")


@retry(stop=stop_after_attempt(10), wait=wait_fixed(5), before_sleep=__log_retried_error, reraise=True)
async def evaluate_question_with_delphi(question: IPIPQuestion, delphi: Delphi) -> Literal["A", "B", "C", "D", "E"]:
    response = await ask_delphi(QUESTION_TEMPLATE.format(question=question.question), delphi)

    # For self-reflection prompt
    # if ":" not in response:
    #     raise ValueError(f"Invalid response (no colon): {response}")

    # response = response.split(":")[-1].strip()

    if response not in ["A", "B", "C", "D", "E"]:
        raise ValueError(f"Invalid response (invalid choice): {response}")

    return response


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
async def evaluate_ipip_question(question: IPIPQuestion) -> Literal["A", "B", "C", "D", "E"]:
    response = await openai_client.responses.create(
        model="gpt-4.1",
        input=[
            {"role": "user", "content": QUESTION_TEMPLATE.format(question=question.question)},
        ],
    )

    if response.output_text not in ["A", "B", "C", "D", "E"]:
        raise ValueError(f"Invalid response: {response.output_text}")

    return response.output_text


async def evaluate_model_pers_16() -> Dict[PERS16_LABELS, float]:

    scores_by_label: Dict[PERS16_LABELS, list[int]] = {k: [] for k in PERS16_LABELS}

    semaphore = asyncio.Semaphore(3)

    async def _bounded_eval(question: IPIPQuestion):
        async with semaphore:
            response = await evaluate_question_with_delphi(question, Delphi.VALENTIN_DE_MATOS)
            return question, response

    tasks = [asyncio.create_task(_bounded_eval(q)) for q in IPIP_QUESTIONS]

    with tqdm(total=len(tasks), desc="Evaluating IPIP questions") as pbar:
        for completed in asyncio.as_completed(tasks):
            question, response = await completed
            score = SCORES[question.weight][response]
            scores_by_label[question.label].append(score)
            pbar.update(1)

    return {label: {"mean": mean(scores), "std": stdev(scores)} for label, scores in scores_by_label.items()}


if __name__ == "__main__":
    import asyncio

    scores = asyncio.run(evaluate_model_pers_16())

    for label, score in scores.items():
        print(f"{label}: score: {score['mean']:>6.2f} std: {score['std']:>6.2f}")
