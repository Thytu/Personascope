## Personascope

Evaluate and compare persona expression across text using three different approaches:

- Zero-shot feature discovery and scoring (LLM-based)
- 16PF-style trait scoring via PERS-16/IPIP prompts (Delphi self-assessment)
- Stylometry with Burrows' Delta (classical baseline)

### Contents
- Getting started (install, data layout, environment)
- Approach 1: Zero-shot feature discovery and scoring
- Approach 2: 16PF classification (IPIP-style self-assessment)
- Approach 3: Burrows' Delta stylometry baseline
- Outputs and reports
- Extensibility and notes


## Getting started

### Install
Using uv (recommended):

```bash
cd Personascope
uv venv
uv sync
source .venv/bin/activate
```

Using pip:

```bash
cd Personascope
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install .
```

### Dataset via Git LFS
This repository stores datasets with Git LFS. After cloning, install and pull LFS content:

```bash
git lfs install
git lfs pull
```

### Environment variables
Create a `.env` file at the repo root as needed:

```bash
# Required for zero-shot feature generation and scoring (via OpenRouter)
OPENROUTER_API_KEY=...

# Optional cookie for delphi.ai clone sessions
# DELPHI_AUTH_TOKEN=...
```

## Approach 1: Zero-shot feature discovery and scoring

Goal: automatically propose human-readable style/personality features from conversation samples, build a stable "feature bank", then score personas across datasets.

Key files:
- `src/zero_shot_feature_detection/main.py` — builds the feature bank from a dataset, filters unstable features, evaluates across splits
- `src/zero_shot_feature_detection/model.py` — LLM calls via OpenRouter, rubric generation, dedupe/merge, scoring, aggregation
- `src/zero_shot_feature_detection/constants.py` — model list, concurrency, sampling controls

Controls (see `src/zero_shot_feature_detection/constants.py`):
- `MODELS_TO_ANALYZE`: default `openai/gpt-4.1-mini` (adjust as desired)
- `NUM_RUBRICS_PER_MODEL`: how many independent rubric proposals per model
- `NUM_EVALUATIONS_PER_MODEL`: how many scoring passes per model per feature
- `MAX_STD_DEVIATION`: filter threshold for feature stability

Run (example with `dataset/dara`):

```bash
python src/zero_shot_feature_detection/main.py
```

Outputs:
- `output/features_bank_unfiltered.json` — raw discovered features
- `output/features_bank.json` — filtered, stable feature bank
- Console summary — per-feature mean/std/variance and avg std across features

Score features across multiple personas/datasets and export a comparison table:

```bash
# Optionally update the input bank path in src/PERS_16/evaluate.py
python src/PERS_16/evaluate.py
```

This prints per-feature scores per dataset and writes:
- `output/features_stats_by_dataset.csv`

Notes:
- This pipeline makes many LLM calls. Control cost/latency by lowering dataset size, `NUM_RUBRICS_PER_MODEL`, and `NUM_EVALUATIONS_PER_MODEL`.
- Requires `OPENROUTER_API_KEY` in `.env`.


## Approach 2: 16PF classification (IPIP-style self-assessment)

Goal: approximate 16PF through IPIP items, asked as self-reflection to a target persona (e.g., delphi.ai clone). Aggregates mean/std trait scores.

Key files:
- `src/PERS_16/constants.py` — 16 factors, IPIP items, prompt templates and scoring
- `src/PERS_16/ask_delphi.py` — queries a Delphi clone and aggregates per-factor stats
- `src/PERS_16/generate_delphi_dataset.py` — optionally generate free-form PERS-16 long-form answers from a clone

Run the trait scorer:

```bash
python src/PERS_16/ask_delphi.py
```

Expected output (printed):
```
WARMTH: score:  6.12 std:  1.43
...
```

Generate long-form PERS-16 responses (writes to `dataset/<persona>_delphi/`):

```bash
python src/PERS_16/generate_delphi_dataset.py
```

Notes:
- `ask_delphi.py` streams through `https://www.delphi.ai`. You may set `DELPHI_AUTH_TOKEN` in `.env` if your clone requires authentication; otherwise it attempts unauthenticated access.
- The script currently targets `Delphi.SAROSH_KHANNA` in code; change the enum to target other clones.


## Approach 3: Burrows' Delta stylometry baseline

Goal: provide a classical, non-LLM baseline for authorship/persona proximity and visualization.

Key files:
- `src/burrows_delta/plot_naive_embedding.py` — runs faststylometry, computes Burrows' Delta, predicts probabilities, and plots PCA views (both chunk-level and author-centroid)
- `src/burrows_delta/run_pca_whole_dataset.py` — PCA over tokenized bag-of-words for all texts
- `src/burrows_delta/run_pca_z_score.py` — UMAP/PCA of sentence-embeddings (illustrates content vs style clustering)

Run:

```bash
python src/burrows_delta/plot_naive_embedding.py
python src/burrows_delta/run_pca_whole_dataset.py
python src/burrows_delta/run_pca_z_score.py
```

Outputs:
- `output/burrows_delta.csv` — Burrows' Delta scores
- `output/burrows_delta_predictions.csv` — class probabilities for test items
- Interactive plots (matplotlib windows)


## Outputs and reports
- Zero-shot features: `output/features_bank.json` (canonical bank), console stats
- Cross-dataset feature table: `output/features_stats_by_dataset.csv`
- Stylometry: `output/burrows_delta*.csv` and plots


## Extensibility
- Add datasets: drop `.txt` files under `dataset/<new_persona>/`. If format differs, add a loader in `src/dataset_loader/` mirroring `jess_lee.py` or `huberman_lab.py`.
- Tune zero-shot: edit `src/zero_shot_feature_detection/constants.py` to change models and sampling. Increase `NUM_RUBRICS_PER_MODEL`/`NUM_EVALUATIONS_PER_MODEL` for stability; raise/lower `MAX_STD_DEVIATION` to filter.
- Alternate scoring: `evaluate_handcrafted.py` and `evaluate_on_other_persona.py` show how to score custom, interpretable feature sets across datasets.


## Caveats and guidance
- Cost/latency: Zero-shot discovery can be expensive. Start with a small dataset and low sampling settings, then scale.
- Determinism: Scores are aggregated across many runs to estimate stability; use the provided std/variance to select reliable features.
