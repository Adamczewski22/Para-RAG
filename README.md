# ParaRAG framework

## Overview
The **ParaRAG** framework serves as a module for conversational memory, especialy suitable for **LLM chatbots** and **agents**. It features parallel memory retrieval from underlying vector stores to minimize latency while providing rich context.

## Project Structure
```
.
├── pararag/                                     # Core ParaRAG framework package
│   ├── ai/                                      # LLM and embedding clients
│   │   ├── embeddings.py
│   │   └── llm.py
│   ├── api/                                     # Main API facade of ParaRAG
│   │   └── facade.py
│   ├── memory/                                  # Vector store adapters and memory services
│   │   ├── domain/                              # Domain interfaces
│   │   │   └── interfaces.py
│   │   ├── infrastructure/                      # Adapters and mappers for underlying infrustructure
│   │   │   ├── mappers.py
│   │   │   └── qdrant_adapter.py
│   │   └── services/                            # Update, retrieval and administrative memory services
│   │       ├── memory_admin_service.py
│   │       ├── memory_retrieval_service.py
│   │       └── memory_update_service.py
│   ├── orchestration/                           # LLM-based memory orchestration package. Holds multiple implementations of memory orchestrator abstraction.
│   │   ├── factory.py
│   │   ├── shared/                              # Shared resources like types, prompts and utilities etc.
│   │   │   ├── base.py                          # Memory orchestrator abstraction for uploading messages and retrieval
│   │   │   ├── prompts.py
│   │   │   ├── tools.py
│   │   │   ├── types.py
│   │   │   └── utils.py
│   │   └── simple_decomposition/                # First implementation of memory orchestrator based on assertions extraction and query decompostion.
│   │       ├── memory_orchestrator.py
│   │       ├── retrieval/                       # Retrieval pipeline
│   │       │   ├── graph.py
│   │       │   └── nodes.py
│   │       └── update/                          # Update pipeline
│   │           ├── graph.py
│   │           └── nodes.py
│   └── shared/                                  # Shared resources
│       ├── console.py
│       ├── models.py
│       └── types.py
├── benchmarks/                                  # Scripts for running benchmark pipelines
├── data/                                        # Data e.g., locomo benchmark
│   └── locomo/
├── examples/                                    # Examples such as integrating a chatbot with ParaRAG
│   └── chatbot_integration.py
├── external/                                    # External repos used such as memobase for baselines and locomo automations
│   └── memobase/
├── infra/                                       # Underlying infrustructure.
│   └── qdrant/
├── results/                                     # Results of experiments and benchmark evaluations
│   └── locomo/
├── Makefile                                     # Common benchmark commands
├── README.md                                    # Project documentation
└── requirements.txt                             # Python dependencies
```
