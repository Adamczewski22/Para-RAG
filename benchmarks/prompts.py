# The same prompt as in the original baseline memobase RAG is used for fair evaluation.
# The only change is replacement of word "conversation" by "memory" as the context is supplied in different form.
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