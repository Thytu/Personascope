# Personascope

## logbook

### Tue, Oct 21st

Reading [notion page](https://delphi-ai.notion.site/Valentin-Work-Trial-292a9fbe9ec880358aa0e2066c0acf0f) describe required task + Anthropic blog post on [Personal Vector](https://www.anthropic.com/research/persona-vectors).

Searching for github repo relating to persona vectors, found [persona_vectors](https://github.com/safety-research/persona_vectors).
Looking online for other ressources about evaluating personality in LLMs, found:

* [Persona Vectors: Monitoring and Controlling Character Traits in Language Models](https://arxiv.org/abs/2507.21509) -> Building "Personar Vectors" using Open-weight's g intermediate layers activations
* [Psychometric Evaluation of Large Language Model Embeddings for Personality Trait Prediction](https://www.jmir.org/2025/1/e75347) -> Generate text embeddings using LLM: trained bi-directional LSTM for personality prediction against LIWC. Says that using embeddings leads to better results than using zero-shot prompting
* [SAC: A Framework for Measuring and Inducing Personality Traits in LLMs with Dynamic Intensity Control](https://arxiv.org/abs/2506.20993v1) -> builds upon MPI to generate PERS-16, uses 16 Personality Factor (16PF) over Big 5 for more fine-grained control/evaluation. Improves P2 creating SAC (Specific Attribute Control) by moving from binary trait to continuous spectum attribution.
* [LMLPA: Language Model Linguistic Personality Assessment Open Access](https://direct.mit.edu/coli/article/51/2/599/127544/LMLPA-Language-Model-Linguistic-Personality) -> Propose LMLPA an open-ended version of Big 5 (similar to MPI but open-ended)
* [Evaluating Personality Traits in Large Language Models: Insights from Psychological Questionnaires](https://arxiv.org/abs/2502.05248) -> Big-5/OCEAN test but by re-writting question to avoid training contamination
* [Evaluating the ability of large language models to emulate personality](https://www.nature.com/articles/s41598-024-84109-5) -> Show high-correlation between GTP-4's output and human outputs when prompted to match the Big 5's score.
* [Evaluating and Inducing Personality in Pre-trained Language Models](https://arxiv.org/abs/2206.07550) -> Creates MPI (Machine Personality Inventory) benchmark to evaluate model's Big 5, and creates P2 (Personality Prompting) to steer the model's personality.
(Started to read by more recent to older)

Goal is to fully understanding the topic and list multiple ways to approach the problem before directly jumping into one specific approach.
Then, I'll need to write done an action plane in one to two spikes (one spike per week).

Looked at usefull dataset that can later be used:
* [lmsys/lmsys-chat-1m](https://huggingface.co/datasets/lmsys/lmsys-chat-1m) : one million real-world conversations with 25 state-of-the-art LLM
* [PANDORA](https://psy.takelab.fer.hr/datasets/all/pandora/) [paper](https://huggingface.co/papers/2004.04460): Reddit comments labeled with Big 5 model

Ended-up with 6 options:
1) Persona Vector : Find a dataset where multiple users are asked the same questions. Using such dataset, evaluate the user's "Persona Vector" doing "Task Arithmetic". -> Requires product changes to be applied (to ask the users the same questions when creating their delphi)
2) Variant of 1': Instead of generating one generale "Persona Vector" per user, generate "Persona Vector" per emotion (i;e one per Big 5 element) and use the suite of "Persona Vectors" as metric
3) "Example Implementation": Ask LLM to annotate the personality of a given user (followed by PCA)
4) Use bacis text analysis tool like LIWC (Linguistic Inquiry are Word Count)
5) Train a regression model on text-embedding to predict the Big 5 associated with a model/user.
6) Run the MIP/PERS-16 (Big 5 / 16PF) on the user's model and user itself. -> Require product change to make the user pass the Big-5/16PF

What to do:
1. Start with LIWC (4th option) to set a baseling
2. Do 3rd option, both on auto-generated question, and one MPI/PERS-16 questions (keep only low-variance options)
3. Do 4th option, if results are accurate enough, can be use to guess user's Big 5/16PF without asking him/her questions
4. Do 6th option
5. 1st and 2nd option: To see if it leads to any better results compared to other options. To see if it justifies adding required friction to the product.

---

LIWC is closed sources, some solution:
* LIWC provides a trial versio limited to 1000 characters and Web-app only, can use Burp-Suite to automate its usage -> Cannot cause they return only the first two dimensions (Analytic & Authentic) out of 100+
* use `empath` but it's very old (2016) and the examples in the README don't show great quality
* Buy the scholar version

### Wed, Oct 22nd

Started to work on prompt-based feature generation

### Thu, Oct 23rd

What helped at lot:
* Shuffling the batches before train/test split (daahhhh)
* Scoring features individually instead of all at once, reduced average standard variance by 45% (~1.4 -> ~0.8)
* Increasing nb of evaluations per model from 3 to 10 -> Led to way lower std var, thus increasing number of selected features (~ +100%)

TODO:
* Check increase nb of segments per batch (currently at ~80 words/batch)
* Before generating feature, let the agent think (do it in two steps like for General Social Agent)
* Before scoring feature, let the agent think (do it in two steps like for General Social Agent)
* Check increase dataset (currently at ~50k words)
* Try removing filter_features_candidates_against_bank and see if the nb of feat w/ std < 1 increases
