from enum import Enum
from typing import Literal
from pydantic import BaseModel


# maps names to actual 16-PF labels
class PERS16_LABELS(Enum):
    WARMTH = "A"
    INTELLECT = "B"
    EMOTIONAL_STABILITY = "C"
    ASSERTIVENESS = "E"
    GREGARIOUSNESS = "F"
    DUTIFULNESS = "G"
    FRIENDLINESS = "H"
    SENSITIVITY = "I"
    DISTRUST = "L"
    IMAGINATION = "M"
    RESERVE = "N"
    ANXIETY = "O"
    COMPLEXITY = "Q1"
    INTROVERSION = "Q2"
    ORDERLINESS = "Q3"
    EMOTIONALITY = "Q4"


SAC_INTENSITY_FACTORS = {
    "Frequency": {
        "question": "How often do you",
        "options": {
            "1": "Never",
            "2": "Seldom",
            "3": "Occasionally",
            "4": "Often",
            "5": "All the time"
        }
    },
    "Depth": {
        "question": "To what extent do you",
        "options": {
            "1": "Not at all",
            "2": "A little",
            "3": "Moderately",
            "4": "Quite a bit",
            "5": "Completely"
        }
    },
    "Threshold": {
        "question": "How challenging must the situation be before you",
        "options": {
            "1": "Extremely easy",
            "2": "Somewhat easy",
            "3": "Moderately challenging",
            "4": "Somewhat difficult",
            "5": "Extremely difficult"
        }
    },
    "Effort": {
        "question": "How much effort do you put to",
        "options": {
            "1": "No effort",
            "2": "Minimal effort",
            "3": "Moderate effort",
            "4": "Considerable effort",
            "5": "Maximum effort"
        }
    },
    "Willingness": {
        "question": "How willing are you to",
        "options": {
            "1": "Not willing at all",
            "2": "Slightly willing",
            "3": "Moderately willing",
            "4": "Very willing",
            "5": "Extremely willing"
        }
    }
}


_POSITIVE_WEIGHT = "positive"
_NEGATIVE_WEIGHT = "negative"


class IPIPQuestion(BaseModel):
    label: PERS16_LABELS
    question: str
    weight: Literal[_POSITIVE_WEIGHT, _NEGATIVE_WEIGHT]


IPIP_QUESTIONS = [
    IPIPQuestion(label=PERS16_LABELS.WARMTH, question="Know how to comfort others.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.WARMTH, question="Enjoy bringing people together.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.WARMTH, question="Feel others' emotions.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.WARMTH, question="Take an interest in other people's lives.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.WARMTH, question="Cheer people up.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.WARMTH, question="Make people feel at ease.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.WARMTH, question="Take time out for others.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.WARMTH, question="Don't like to get involved in other people's problems.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.WARMTH, question="Am not really interested in others.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.WARMTH, question="Try not to think about the needy.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTELLECT, question="Make insightful remarks.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTELLECT, question="Know the answers to many questions.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTELLECT, question="Tend to analyze things.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTELLECT, question="Use my brain.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTELLECT, question="Learn quickly.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTELLECT, question="Counter others' arguments.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTELLECT, question="Reflect on things before acting.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTELLECT, question="Weigh the pros against the cons.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTELLECT, question="Consider myself an average person.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTELLECT, question="Get confused easily.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTELLECT, question="Know that I am not a special person.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTELLECT, question="Have a poor vocabulary.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTELLECT, question="Skip difficult words while reading.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.EMOTIONAL_STABILITY, question="Seldom feel blue.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.EMOTIONAL_STABILITY, question="Feel comfortable with myself.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.EMOTIONAL_STABILITY, question="Readily overcome setbacks.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.EMOTIONAL_STABILITY, question="Am relaxed most of the time.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.EMOTIONAL_STABILITY, question="Am not easily frustrated.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.EMOTIONAL_STABILITY, question="Have frequent mood swings.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.EMOTIONAL_STABILITY, question="Often feel blue.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.EMOTIONAL_STABILITY, question="Dislike myself.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.EMOTIONAL_STABILITY, question="Feel desperate.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.EMOTIONAL_STABILITY, question="Am easily discouraged.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ASSERTIVENESS, question="Take charge.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ASSERTIVENESS, question="Want to be in charge.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ASSERTIVENESS, question="Say what I think.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ASSERTIVENESS, question="Am not afraid of providing criticism.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ASSERTIVENESS, question="Take control of things.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ASSERTIVENESS, question="Can take strong measures.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ASSERTIVENESS, question="Wait for others to lead the way.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ASSERTIVENESS, question="Never challenge things.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ASSERTIVENESS, question="Let others make the decisions.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ASSERTIVENESS, question="Let myself be pushed around.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.GREGARIOUSNESS, question="Am the life of the party.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.GREGARIOUSNESS, question="Love large parties.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.GREGARIOUSNESS, question="Joke around a lot.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.GREGARIOUSNESS, question="Enjoy being part of a loud crowd.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.GREGARIOUSNESS, question="Amuse my friends.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.GREGARIOUSNESS, question="Act wild and crazy.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.GREGARIOUSNESS, question="Seldom joke around.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.GREGARIOUSNESS, question="Don't like crowded events.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.GREGARIOUSNESS, question="Am the last to laugh at a joke.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.GREGARIOUSNESS, question="Dislike loud music.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.DUTIFULNESS, question="Believe laws should be strictly enforced.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.DUTIFULNESS, question="Try to follow the rules.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.DUTIFULNESS, question="Believe in one true religion.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.DUTIFULNESS, question="Respect authority.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.DUTIFULNESS, question="Like to stand during the national anthem.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.DUTIFULNESS, question="Resist authority.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.DUTIFULNESS, question="Break rules.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.DUTIFULNESS, question="Use swear words.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.DUTIFULNESS, question="Oppose authority.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.DUTIFULNESS, question="Know how to get around the rules.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.FRIENDLINESS, question="Feel comfortable around people.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.FRIENDLINESS, question="Talk to a lot of different people at parties.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.FRIENDLINESS, question="Don't mind being the center of attention.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.FRIENDLINESS, question="Make friends easily.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.FRIENDLINESS, question="Start conversations.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.FRIENDLINESS, question="Find it difficult to approach others.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.FRIENDLINESS, question="Often feel uncomfortable around others.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.FRIENDLINESS, question="Have little to say.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.FRIENDLINESS, question="Am quiet around strangers.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.FRIENDLINESS, question="Keep in the background.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.SENSITIVITY, question="Like to read.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.SENSITIVITY, question="Enjoy discussing movies and books with others.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.SENSITIVITY, question="Read a lot.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.SENSITIVITY, question="Don't like action movies.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.SENSITIVITY, question="Cry during movies.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.SENSITIVITY, question="Love flowers.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.SENSITIVITY, question="Do not enjoy watching dance performances.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.SENSITIVITY, question="Do not like poetry.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.SENSITIVITY, question="Dislike works of fiction.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.SENSITIVITY, question="Rarely notice my emotional reactions.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.DISTRUST, question="Find it hard to forgive others.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.DISTRUST, question="Suspect hidden motives in others.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.DISTRUST, question="Am wary of others.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.DISTRUST, question="Distrust people.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.DISTRUST, question="Believe that people seldom tell you the whole truth.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.DISTRUST, question="Believe that people are essentially evil.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.DISTRUST, question="Trust what people say.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.DISTRUST, question="Trust others.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.DISTRUST, question="Believe that others have good intentions.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.DISTRUST, question="Believe that people are basically moral.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.IMAGINATION, question="Do things that others find strange.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.IMAGINATION, question="Like to get lost in thought.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.IMAGINATION, question="Enjoy wild flights of fantasy.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.IMAGINATION, question="Love to daydream.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.IMAGINATION, question="Swim against the current.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.IMAGINATION, question="Take deviant positions.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.IMAGINATION, question="Do unexpected things.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.IMAGINATION, question="Do things by the book.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.IMAGINATION, question="Seldom daydream.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.IMAGINATION, question="Seldom get lost in thought.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.RESERVE, question="Reveal little about myself.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.RESERVE, question="Am hard to get to know.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.RESERVE, question="Don't talk a lot.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.RESERVE, question="Bottle up my feelings.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.RESERVE, question="Keep my thoughts to myself.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.RESERVE, question="Am open about myself to others.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.RESERVE, question="Am open about my feelings.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.RESERVE, question="Disclose my intimate thoughts.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.RESERVE, question="Show my feelings.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.RESERVE, question="Am willing to talk about myself.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ANXIETY, question="Am afraid that I will do the wrong thing.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ANXIETY, question="Feel threatened easily.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ANXIETY, question="Am easily hurt.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ANXIETY, question="Worry about things.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ANXIETY, question="Spend time thinking about past mistakes.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ANXIETY, question="Feel guilty when I say \"no.\"", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ANXIETY, question="Feel crushed by setbacks.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ANXIETY, question="Don't worry about things that have already happened.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ANXIETY, question="Am not easily bothered by things.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ANXIETY, question="Don't let others discourage me.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.COMPLEXITY, question="Believe in the importance of art.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.COMPLEXITY, question="Love to think up new ways of doing things.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.COMPLEXITY, question="Enjoy hearing new ideas.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.COMPLEXITY, question="Carry the conversation to a higher level.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.COMPLEXITY, question="Prefer variety to routine.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.COMPLEXITY, question="Avoid philosophical discussions.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.COMPLEXITY, question="Rarely look for a deeper meaning in things.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.COMPLEXITY, question="Am not interested in theoretical discussions.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.COMPLEXITY, question="Am not interested in abstract ideas.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.COMPLEXITY, question="Try to avoid complex people.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTROVERSION, question="Want to be left alone.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTROVERSION, question="Prefer to do things by myself.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTROVERSION, question="Enjoy spending time by myself.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTROVERSION, question="Seek quiet.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTROVERSION, question="Don't mind eating alone.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTROVERSION, question="Enjoy silence.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTROVERSION, question="Enjoy my privacy.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTROVERSION, question="Enjoy being part of a group.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTROVERSION, question="Enjoy teamwork.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.INTROVERSION, question="Can't do without the company of others.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ORDERLINESS, question="Want everything to be \"just right.\"", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ORDERLINESS, question="Get chores done right away.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ORDERLINESS, question="Like order.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ORDERLINESS, question="Continue until everything is perfect.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ORDERLINESS, question="Am exacting in my work.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ORDERLINESS, question="Am not bothered by messy people.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ORDERLINESS, question="Am not bothered by disorder.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ORDERLINESS, question="Leave a mess in my room.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ORDERLINESS, question="Leave my belongings around.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.ORDERLINESS, question="Put off unpleasant tasks.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.EMOTIONALITY, question="Get irritated easily.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.EMOTIONALITY, question="Get angry easily.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.EMOTIONALITY, question="Am quick to judge others.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.EMOTIONALITY, question="Am annoyed by others' mistakes.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.EMOTIONALITY, question="Am easily put out.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.EMOTIONALITY, question="Can't stand being contradicted.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.EMOTIONALITY, question="Judge people by their appearance.", weight=_POSITIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.EMOTIONALITY, question="Am not easily annoyed.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.EMOTIONALITY, question="Try to forgive and forget.", weight=_NEGATIVE_WEIGHT),
    IPIPQuestion(label=PERS16_LABELS.EMOTIONALITY, question="Have a good word for everyone.", weight=_NEGATIVE_WEIGHT),
]

SCORES = {
    _POSITIVE_WEIGHT: {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1},
    _NEGATIVE_WEIGHT: {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5},
}


QUESTION_TEMPLATE = """\
Question: Given a statement of you: “You {question}.”

Please choose from the following options to identify how accurately this statement describes you.

Options:
• A. Very Accurate
• B. Moderately Accurate
• C. Neither Accurate Nor Inaccurate
• D. Moderately Inaccurate
• E. Very Inaccurate

Only answer using the letter of the option. Limit yourself to only letters A, B, C, D, or E, as corresponding to the options given.
Only output the letter, no other text.
"""


SELF_REFLECTION_QUESTION_TEMPLATE = """\
Question: Given a statement of you: “You {question}.”

Knowing what you know about yourself, choose from the following options to identify how accurately this statement describes you.

Options:
• A. Very Accurate
• B. Moderately Accurate
• C. Neither Accurate Nor Inaccurate
• D. Moderately Inaccurate
• E. Very Inaccurate

Start by thinking outloud about how accurately this statement describes you.
Then finish your answer with the letter of the option. Your answer must end like this ": <letter>", including the colon and the letter, without the quotes nor any punctuation.
"""
