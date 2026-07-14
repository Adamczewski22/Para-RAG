# Thesis Artifacts

The repository includes aggregate outputs from the thesis experiments under `results/locomo/`. The [experiment guide](experiments.md) explains how to reproduce them.

| Thesis result | Repository artifacts | Contents |
| --- | --- | --- |
| Table 3 and the ParaRAG row in Table 4 | `pararag_final_result.json`, `pararag_final_eval.json` | Generated answers and retrieved context, followed by per-question BLEU-1, F1, and LLM-judge scores for all 1,540 evaluated questions. |
| Table 5: ablation study | `pararag_result_*_ablation.json`, `pararag_eval_*_ablation.json` | Raw answers and evaluated scores for the profile, deduplication, and query-decomposition ablations. |
| Table 6: parallel versus sequential latency | `stats/pararag_parallel_stats_7.json`, `stats/pararag_sequential_stats_7.json`, `stats/parallel_to_sequential_latency_diff.json` | Measurements from LOCOMO sample 7 and the percentage differences reported in the thesis. |
| Tables 7-9: ParaRAG latency and token usage | `stats/pararag_final_stats.json` | Aggregate update and retrieval latency, LLM-token usage, and embedding-token usage. |

`debug/pararag_final_logs.json` contains the detailed pipeline measurements from which the final statistics were generated. Files ending in `_result.json` preserve model responses and context, `_eval.json` files preserve question-level accuracy measurements, and files under `stats/` contain aggregated values.

`stats/pararag_to_sequential_latency_diff.json` contains the same comparison as `parallel_to_sequential_latency_diff.json` with additional decimal precision. Table 10 in the thesis is a summary derived from the final evaluation, ablations, latency, and token artifacts rather than a separate output file.
