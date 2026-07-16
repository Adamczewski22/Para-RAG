# The initial answer prompt below was adapted from the Memobase LoCoMo RAG
# baseline, whose evaluation project was forked from Mem0. It was modified for
# ParaRAG, including replacing "conversation" with "memory" and adding later
# prompt variants. The upstream material is licensed under Apache-2.0.
# See THIRD_PARTY_NOTICES.md and third_party/licenses/Apache-2.0.txt.
# Used in simple decomposition (1, 2)
ANSWER_PROMPT_1 = """
You are a helpful assistant that can answer questions based on the provided context.
If the question involves timing, use the memory date for reference.
Provide the shortest possible answer.
Use words directly from the memory when possible.
Avoid using subjects in your answer.
"""

# Used in simple decomposition (3_1)
ANSWER_PROMPT_2 = """
You are a helpful assistant that can answer questions based on the provided context.
If the question involves timing, use the memory date for reference and resolve relative dates whenever possible.
Preserve the original time granularity: answer with a day, month, or year only when that level is supported.
Provide the shortest possible answer.
Use words directly from the memory when possible, except unresolved relative time expressions.
Avoid using subjects in your answer.

# Question:
{question}

# Context:
{context}

# Short answer:
"""

# Used in dedupliacation (1_3)
ANSWER_PROMPT_3 = """
You are a helpful assistant that can answer questions based on the provided context.
If the question involves timing, use the memory date for reference and resolve relative dates whenever possible.
Preserve the original time granularity: answer with a day, month, or year only when that level is supported.
Provide concise answers, but ensure that all relevant information is included.
Use words directly from the memory when possible, except unresolved relative time expressions.
Avoid using subjects in your answer.

# Question:
{question}

# Context:
{context}

# Short answer:
"""

ANSWER_PROMPT_4 = """
You are a helpful assistant that can answer questions based on the provided context.
- If the question involves timing, use the memory date for reference and resolve relative dates whenever possible.
- Preserve the original time granularity: answer with a day, month, or year only when that level is supported.
- Provide concise answers, but ensure that all relevant information is included.
- Use words directly from the memory when possible, except unresolved relative time expressions.
- Avoid using subjects in your answer.
- Before answering, identify all memories that directly satisfy the question, not just the most salient one. If several memories give compatible answers, combine them into one concise answer instead of choosing only one. Do not include merely related background memories unless they answer the exact question.

# Question:
{question}

# Context:
{context}

# Short answer:
"""

ANSWER_PROMPT_4_2 = """
You are a helpful assistant that can answer questions based on the provided context.
- The context consists of memories and user profiles
- If the question involves timing, use the memory date for reference and resolve relative dates whenever possible.
- Preserve the original time granularity: answer with a day, month, or year only when that level is supported.
- Provide concise answers, but ensure that all relevant information is included.
- Use words directly from the context when possible, except unresolved relative time expressions.
- Avoid using subjects in your answer.
- Before answering, identify all context that directly satisfies the question, not just the most salient one. If several memories and profile fragments give compatible answers, combine them into one concise answer instead of choosing only one. Do not include merely related background context unless they answer the exact question.

# Question:
{question}

# Context:

## User profiles
{profiles}

## Memories
{memories}

# Short answer:
"""
