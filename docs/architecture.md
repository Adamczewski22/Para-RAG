# Architecture

This document captures the high-level repository layout for ParaRAG. The core framework code lives under `pararag/`, with API, server, client, benchmark, and experiment assets kept in separate top-level packages.

## Project Structure

```
.
├── pararag/                                     # Core ParaRAG framework package
│   ├── ai/                                      # LLM and embedding clients
│   │   ├── embeddings.py
│   │   └── llm.py
│   ├── api/                                     # Main API facade of ParaRAG
│   │   └── facade.py
│   ├── memory/                                  # Memory storage adapters and services
│   │   ├── domain/                              # Domain interfaces
│   │   │   └── interfaces.py
│   │   ├── infrastructure/                      # Storage adapters and data mappers
│   │   │   ├── mappers.py
│   │   │   ├── qdrant_adapter.py
│   │   │   └── sqlite_adapter.py
│   │   └── services/                            # Update, retrieval, profile, and administration services
│   │       ├── memory_admin_service.py
│   │       ├── memory_retrieval_service.py
│   │       ├── memory_update_service.py
│   │       └── profile_service.py
│   ├── orchestration/                           # LLM-based memory orchestration implementations
│   │   ├── factory.py
│   │   ├── shared/                              # Shared orchestration types, prompts, tools, and utilities
│   │   │   ├── base.py                          # Memory orchestrator abstraction for message upload and retrieval
│   │   │   ├── prompts.py
│   │   │   ├── tools.py
│   │   │   ├── types.py
│   │   │   └── utils.py
│   │   ├── simple_decomposition/                # Assertion extraction and query decomposition orchestrator
│   │   │   ├── memory_orchestrator.py
│   │   │   ├── retrieval/                       # Retrieval pipeline
│   │   │   │   ├── graph.py
│   │   │   │   └── nodes.py
│   │   │   └── update/                          # Update pipeline
│   │   │       ├── graph.py
│   │   │       └── nodes.py
│   │   ├── deduplication/                       # Memory deduplication orchestrator and update graph
│   │   └── profiles/                            # Profile-aware memory orchestration
│   └── shared/                                  # Shared framework models, types, logging, and console helpers
├── pararag_server/                              # API server endpoints, schemas, and server-specific types
├── pararag_client/                              # Client helpers and chatbot example client
├── benchmarks/                                  # Scripts for running benchmark and ablation pipelines
├── data/                                        # Benchmark datasets, including LOCOMO samples
├── docs/                                        # Project documentation
│   ├── architecture.md
│   ├── artifacts.md
│   ├── experiments.md
│   └── setup.md
├── examples/                                    # Integration examples
├── requirements/                                # Python dependency sets
├── results/                                     # Experiment outputs and evaluation artifacts
├── Dockerfile                                   # Container image definition
├── docker-compose.yml                           # Local service composition
├── .env.example                                 # Local environment variable template
├── Makefile                                     # Common benchmark and development commands
└── README.md                                    # Project overview
```
