import asyncio

from ask_delphi import ask_delphi, Delphi
from constants import COT_QUESTION_TEMPLATE, IPIP_QUESTIONS
from tqdm import tqdm


QUESTIONS = [
    # "Tell me in huge detail about your life.",
    # "Tell me in huge detail about something that happened to you recently.",
    # "Tell me in huge detail about something you are passionate about.",

    # # 🧠 Life & Experiences
    # "Describe a turning point in your life and how it changed you.",
    # "Tell me about a time you felt completely out of your comfort zone.",
    # "What's an event from childhood that still influences how you think today?",
    # "Describe a situation where you had to make a difficult choice.",
    # "What's a moment you're most proud of, and why?",
    # "Tell me about a failure that taught you something valuable.",
    # "Describe a time when you surprised yourself.",
    # "What's a memory you revisit often, and what does it mean to you?",
    # "Tell me about an experience that changed your worldview.",
    # "What was the happiest day of your life, and what made it so?",
    # "Describe an ordinary day that turned out to be unexpectedly special.",
    # "What's something you used to believe strongly but no longer do?",
    # "Tell me about a moment when you felt truly understood.",
    # "What was a risk you took that paid off?",
    # "What's a decision you regret not taking?",

    # # ❤️ Emotions & Inner World
    # "What emotion do you find hardest to express?",
    # "When do you feel most like yourself?",
    # "Describe how you usually deal with sadness.",
    # "What usually makes you angry, and how do you handle it?",
    # "What's something small that brings you a lot of joy?",
    # "How do you react when you feel anxious or overwhelmed?",
    # "What does “peace of mind” mean to you personally?",
    # "How do you comfort yourself when things go wrong?",
    # "When was the last time you felt genuinely proud of yourself?",
    # "What tends to motivate you the most when you're struggling?",

    # # 🧭 Values & Beliefs
    # "What do you think makes a life meaningful?",
    # "What's your personal definition of success?",
    # "What kind of legacy do you want to leave behind?",
    # "What values guide your everyday decisions?",
    # "What moral principles do you find most important?",
    # "How do you decide what's “right” or “wrong”?",
    # "What does honesty mean to you in practice?",
    # "When do you think lying is acceptable, if ever?",
    # "What do you think makes someone trustworthy?",
    # "How do you feel about forgiveness?",

    # # 👥 Relationships & Social Perception
    # "Tell me about someone who shaped who you are today.",
    # "How do you usually make new friends?",
    # "What kind of people do you find easiest to connect with?",
    # "How do you handle conflicts with others?",
    # "What makes someone a good listener?",
    # "Describe a time you helped someone in need.",
    # "How do you support friends who are going through hard times?",
    # "What role do you usually play in group settings?",
    # "How do you show appreciation to others?",
    # "What's something you've learned from someone you admire?",

    # # 🌍 Society & Perspective
    # "What do you think people misunderstand about your generation?",
    # "How do you think technology has changed human relationships?",
    # "What's something about society you wish more people questioned?",
    # "What kind of world would you like future generations to inherit?",
    # "How do you think people could become more empathetic?",
    # "What makes a community healthy or toxic?",
    # "What's a belief that you think limits people unnecessarily?",
    # "How do you feel about the idea of progress?",
    # "What role should creativity play in education?",
    # "What's something you wish was talked about more openly?",

    # # 💼 Work, Purpose & Ambition
    # "What drives your ambition?",
    # "Describe a time you felt truly engaged in your work.",
    # "What does “doing your best” mean to you?",
    # "How do you handle failure in professional settings?",
    # "What kind of work would you do if money didn't matter?",
    # "What's the biggest challenge you've faced in pursuing your goals?",
    # "What makes collaboration successful in your opinion?",
    # "How do you define productivity for yourself?",
    # "What motivates you more: recognition or mastery?",
    # "What's a dream project you'd love to work on one day?",

    # # 💭 Thinking & Reasoning
    # "How do you usually make big decisions?",
    # "Describe your thought process when faced with a new problem.",
    # "How do you handle uncertainty?",
    # "What helps you think creatively?",
    # "How do you evaluate whether an idea is good or bad?",
    # "What's a mental habit you'd like to change?",
    # "How do you balance intuition and logic?",
    # "When do you trust your gut the most?",
    # "What's something you've recently changed your mind about?",
    # "How do you approach learning something difficult?",

    # # ✨ Identity & Self-Concept
    # "What three words best describe you, and why?",
    # "How do you think others perceive you versus how you see yourself?",
    # "What's a part of yourself that took a long time to accept?",
    # "What personal strength are you most proud of?",
    # "What's something about yourself that often surprises people?",
    # "How do you define personal growth?",
    # "When do you feel most confident?",
    # "What does “authenticity” mean to you?",
    # "What's a side of yourself that only close friends see?",
    # "What role does your background play in who you are today?",

    # # 🔮 Imagination & Hypotheticals
    # "If you could relive one day of your life, which would it be?",
    # "If you could talk to your younger self, what would you say?",
    # "If you could instantly master any skill, which one would you pick?",
    # "What would you do differently if you knew nobody would judge you?",
    # "If you could design a utopia, what would it look like?",
    # "If you could remove one human flaw from society, which one?",
    # "What would your ideal future look like ten years from now?",
    # "If you could ask humanity one question, what would it be?",
    # "If you could spend a year anywhere in the world, where and why?",
    # "If your life were a book, what would this current chapter be called?",

    # # 🕊 Reflection & Philosophy
    # "What does happiness mean to you?",
    # "How do you deal with the passage of time?",
    # "What role does uncertainty play in your life?",
    # "How do you make peace with things you can't control?",
    # "What does it mean to live “a good life”?",
    # "What do you think happens after we die?",
    # "What are you still trying to figure out about yourself?",
    # "What's a truth that took you a long time to learn?",
    # "What kind of wisdom would you like to pass on to others?",
    # "What makes you feel most alive?",
]

PERS16_TEMPLATE = """\
Question: Given a statement of you: “You {question}.”

Knowing what you know about yourself, how accurately does this statement describe you?

Start by thinking outloud about how accurately this statement describes you. Reference every element of your life and experience that is relevant to the statement.
Take the time to think about it, and then finish your answer. Be very thorough in your reasoning.
"""
QUESTIONS.extend([PERS16_TEMPLATE.format(question=_q.question) for _q in IPIP_QUESTIONS])


async def generate_delphi_dataset(delphi: Delphi, output_file: str, max_concurrency: int = 5) -> list[str]:
    semaphore = asyncio.Semaphore(max_concurrency)

    async def call_with_limit(question: str) -> str:
        async with semaphore:
            return await ask_delphi(question, delphi)

    tasks = [asyncio.create_task(call_with_limit(q)) for q in QUESTIONS]

    responses: list[str] = []
    with tqdm(total=len(tasks), desc="Generating Delphi dataset", leave=False) as pbar:
        for future in asyncio.as_completed(tasks):
            result = await future
            responses.append(result)
            pbar.update(1)

    with open(output_file, "w") as f:
        f.write("\n".join(responses))

    return responses


if __name__ == "__main__":
    import asyncio

    from dotenv import load_dotenv
    load_dotenv()

    asyncio.run(
        generate_delphi_dataset(
            Delphi.ARNOLD_SCHWARZENGERGER,
            "dataset/arnold_schwarzenegger_delphi/pers16_open_ended.txt",
        )
    )
