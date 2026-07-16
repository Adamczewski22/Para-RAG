# Third-party notices

ParaRAG's original work is licensed under the Apache License 2.0. That license does not replace the licenses of the third-party material identified below.

## Mem0 and Memobase evaluation materials

The LoCoMo evaluation workflow used by ParaRAG has the following lineage:

- `benchmarks/prompts.py` contains an answer-generation prompt adapted from the Memobase LoCoMo RAG baseline and modified for ParaRAG.
- The reproducibility workflow described in `docs/experiments.md` fetches evaluation scripts from Memobase rather than vendoring them in this repository.
- Memobase states that its LoCoMo benchmark project was originally forked from the Mem0 evaluation framework at commit `393a4fd5a6cfeb754857a2229726f567a9fadf36`.

Upstream projects:

- Mem0: <https://github.com/mem0ai/mem0>
- Memobase: <https://github.com/memodb-io/memobase>

Copyright notices supplied by the upstream projects include:

- Copyright [2023] [Taranjeet Singh]
- Copyright 2024 Memobase

These materials are licensed under the Apache License, Version 2.0. A copy is provided at `third_party/licenses/Apache-2.0.txt`.

ParaRAG's changes include prompt wording and formatting changes, integration with ParaRAG's memory output, orchestration of the evaluator, and generation and aggregation of experiment results.

## LoCoMo dataset

ParaRAG redistributes and transforms material from the LoCoMo dataset. This includes:

- the dataset and prepared conversation samples under `data/locomo/`; and
- LoCoMo-originating questions, ground-truth answers, dialogue content, and other dataset material reproduced within `results/locomo/`.

Source: <https://github.com/snap-research/locomo>

Creators: Adyasha Maharana, Dong-Ho Lee, Sergey Tulyakov, Mohit Bansal, Francesco Barbieri, and Yuwei Fang.

The LoCoMo material is licensed under the Creative Commons Attribution-NonCommercial 4.0 International license (CC BY-NC 4.0). A copy is provided at `third_party/licenses/CC-BY-NC-4.0.txt`.

ParaRAG's changes include selecting and splitting conversations into per-sample files, flattening or merging data for evaluation, and combining dataset material with generated answers, retrieved context, profiles, logs, and evaluation metrics. These files are therefore marked as modified where applicable through this notice.

The upstream authors request citation of:

> Adyasha Maharana et al. “Evaluating Very Long-Term Conversational Memory of LLM Agents.” Proceedings of ACL 2024, pp. 13851–13870. <https://doi.org/10.18653/v1/2024.acl-long.747>.

CC BY-NC 4.0 permits sharing and adaptation only for noncommercial purposes and requires attribution, a license reference, a source link where reasonably practicable, and an indication of modifications. The repository's Apache-2.0 license does not grant commercial rights to LoCoMo material. Commercial users of ParaRAG should omit or replace the LoCoMo dataset and LoCoMo-derived artifacts unless they obtain separate permission or another legal basis applies.

## Package dependencies

The Python packages and container images referenced by this project are not vendored here. They remain subject to their own licenses, which should be reviewed when building or redistributing an application or container image.
