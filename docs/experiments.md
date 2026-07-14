# LOCOMO Experiments

This guide reproduces the ParaRAG experiments reported in the thesis. Complete the [local setup](setup.md) first: the Python virtual environment must be active, `.env` must contain a valid OpenAI API key, and Qdrant must be running.

See the [artifact index](artifacts.md) for a concise mapping between the generated outputs and the thesis tables.

The experiments make many paid OpenAI requests and can take a long time. They also write to `results/locomo/` and clear the LOCOMO collection between samples. Preserve any local results you need before starting.

## 1. Install Experiment Dependencies

From the repository root, with `.venv` active:

```bash
python -m pip install -r requirements/experiments.txt
python -m nltk.downloader punkt punkt_tab wordnet
```

The LOCOMO dataset and its ten prepared samples are already included under `data/locomo/`.

## 2. Add the Memobase Evaluator

ParaRAG uses the LOCOMO evaluation scripts from Memobase to calculate BLEU-1, token F1, and LLM-judge scores. Only that experiment directory is needed; a Memobase server or API key is not required.

Clone the evaluator as a sparse checkout at the revision used by ParaRAG:

```bash
mkdir -p external
git clone --filter=blob:none --sparse https://github.com/memodb-io/memobase.git external/memobase
git -C external/memobase sparse-checkout set docs/experiments/locomo-benchmark
git -C external/memobase checkout 9e9a115bd6272e3de792ec5c12e93810b3ed111d
```

The benchmark pipeline expects these files to exist:

```text
external/memobase/docs/experiments/locomo-benchmark/evals.py
external/memobase/docs/experiments/locomo-benchmark/generate_scores.py
```

## 3. Configure Evaluation Mode

Set the following values in `.env`:

```dotenv
FOR_LOCOMO=true
ANSWER_MODEL=gpt-4.1-mini
RETRIEVAL_COUNT=9
```

`ANSWER_MODEL` generates benchmark answers, while `RETRIEVAL_COUNT` controls the number of memories returned for each retrieval query.

Start Qdrant if it is not already running:

```bash
docker compose up -d qdrant
```

## 4. Main ParaRAG Evaluation

The main evaluation uses the full profile-enabled ParaRAG pipeline. Each `VERSION` from `1` to `10` selects the corresponding `data/locomo/locomo_sample_<VERSION>.json` file.

Run one sample first to verify the setup:

```bash
make locomo-final VERSION=1
```

The command ingests the conversation, answers its LOCOMO questions, evaluates the answers with the Memobase evaluator, and prints category and overall scores. Run all ten thesis samples with:

```bash
for version in {1..10}; do
  make locomo-final VERSION="$version"
done
```

Each sample produces answer, evaluation, HTML log, and JSON debug files under `results/locomo/`. Aggregate the ten samples and generate the overall runtime statistics:

```bash
python -m benchmarks.aggregate_results
python -m benchmarks.generate_stats pararag_final
python external/memobase/docs/experiments/locomo-benchmark/generate_scores.py \
  --input_path results/locomo/pararag_final_eval.json
```

The aggregate outputs are:

- `results/locomo/pararag_final_result.json`: generated answers and retrieved context
- `results/locomo/pararag_final_eval.json`: BLEU-1, F1, and LLM-judge results
- `results/locomo/debug/pararag_final_logs.json`: detailed ingestion and retrieval logs
- `results/locomo/stats/pararag_final_stats.json`: latency and token statistics

## 5. Ablation Experiments

Run the main evaluation and aggregation first. The ablations reuse `pararag_final_result.json` and `pararag_final_logs.json` so that each experiment removes one component while retaining the other outputs of the full system.

`ITERATION=reproduction` is only an output label. Change it for later reruns to avoid overwriting or colliding with existing result files.

### Profile Ablation

This experiment removes user profiles from the answer prompt while retaining the memories retrieved by the full ParaRAG run:

```bash
make locomo-profile-ablation \
  ITERATION=reproduction \
  VERSION=profile_ablation \
  PREVIOUS=results/locomo/pararag_final_result.json
```

Results and evaluation metrics are written to `reproduction_result_profile_ablation.json` and `reproduction_eval_profile_ablation.json` under `results/locomo/`.

### Deduplication Ablation

This experiment reconstructs the memory store from all extracted assertions before deduplication, while retaining the profiles from the main run:

```bash
make locomo-deduplication-ablation \
  ITERATION=reproduction \
  VERSION=deduplication_ablation
```

Results and metrics are written to `reproduction_result_deduplication_ablation.json` and `reproduction_eval_deduplication_ablation.json`.

### Query-Decomposition Ablation

This experiment retains the deduplicated memories and profiles but disables decomposition of questions into multiple retrieval queries:

```bash
make locomo-decomposition-ablation \
  ITERATION=reproduction \
  VERSION=decomposition_ablation
```

Results and metrics are written to `reproduction_result_decomposition_ablation.json` and `reproduction_eval_decomposition_ablation.json`.

Each Make target runs the Memobase evaluator and prints its scores automatically. To print a result again, pass its evaluation file to `generate_scores.py` as shown in the main evaluation.

## 6. Parallel Versus Sequential Experiment

The thesis latency comparison uses LOCOMO sample 7. Run the profile-enabled pipeline once with ParaRAG's normal parallel execution and once with sequential execution:

```bash
make locomo-parallel VERSION=7
make locomo-sequential VERSION=7
```

Generate latency and token statistics for both runs:

```bash
python -m benchmarks.generate_stats pararag_parallel --suffix _7
python -m benchmarks.generate_stats pararag_sequential --suffix _7
```

Then calculate the relative latency difference:

```bash
python -m benchmarks.compute_latency_diff \
  --first pararag_parallel_stats_7.json \
  --second pararag_sequential_stats_7.json \
  --output-file parallel_to_sequential_latency_diff.json
```

The comparison is written to `results/locomo/stats/parallel_to_sequential_latency_diff.json`. A negative value means the parallel run had lower latency than the sequential run for that metric.

## Returning to Normal Usage

After the experiments, set `FOR_LOCOMO=false` in `.env` before running the normal chatbot example or another non-LOCOMO integration.
