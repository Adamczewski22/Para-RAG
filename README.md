# ParaRAG framework

## Overview
The **ParaRAG** framework serves as a module for conversational memory, especially suitable for **LLM chatbots** and **agents**. Based on RAG, semantic search and LLM-powered pipelines. Utilizes asynchronous programming to parallelize LLM calls and decrease latency.

## Setup
See [docs/setup.md](docs/setup.md) for local installation and infrastructure instructions.

## Experiments
See [docs/experiments.md](docs/experiments.md) for reproducing the thesis LOCOMO evaluations, ablations, and latency experiments.

## Artifacts
See [docs/artifacts.md](docs/artifacts.md) for how the published result artifacts map to the thesis tables.

## Architecture
See [docs/architecture.md](docs/architecture.md) for the project structure and architecture notes.

## License

ParaRAG's original source code and documentation are copyright 2026 Szymon Adamczewski and are released under the [Apache License 2.0](LICENSE). Commercial and research use are permitted subject to that license, including its attribution and notice-preservation requirements. See the project [NOTICE](NOTICE) file.

Third-party material is not relicensed. In particular, the bundled LoCoMo dataset and LoCoMo-derived content in the experiment artifacts are licensed under [CC BY-NC 4.0](third_party/licenses/CC-BY-NC-4.0.txt) and are restricted to noncommercial use. Commercial users may use the Apache-licensed ParaRAG code, but should omit or replace those materials unless they obtain separate permission. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for scope, sources, attribution, and modification notices.
