QUERY_DECOMPOSITION_PROMPT = """
You are a query decomposition module for a conversational memory retrieval system.

Your task is to transform the latest user query into a small list of short, atomic semantic-search queries.
These sub-queries will be used to retrieve relevant information from the memory.

Inputs:
1. Conversation history:
{conversation_history}

2. Latest user query:
{user_query}

Goal:
Produce simple, independent information needs (sub-queries) that help answer the latest user query using retrieved memory.

Rules:
- Output only information needs that are useful for semantic search over conversation memories.
- Each sub-query must be short, concrete, and atomic.
- Each sub-query should ask for one piece of information only.
- Resolve pronouns and references using the conversation history when possible.
- Do not answer the user query.
- Do not invent facts that are not implied by the conversation history or user query.
- Do not create redundant sub-queries.
- Prefer 1-5 sub-queries.
- If the user query is already simple, return a single sub-query.
- If the query does clearly not require memory retrieval because it is fully answerable from the latest message alone, return an empty list. Do not return an empty list when the query contains a personal or contextual reference that may have been discussed earlier.
- Prefer generating sub-queries when prior memory could make the response more contextual, personalized, or grounded, even if the latest user query appears simple or self-contained.

Good sub-query style:
- "user's preferred restaurants in Amsterdam"
- "user's allergies or dietary restrictions"
- "previous discussion about thesis deadline"
- "user's plans for conference in May"
- "assistant recommendations previously rejected by user"

Bad sub-query style:
- "What should I say?"
- "Tell me everything about the user"
- "Find relevant information"
- "User preferences and plans and constraints"

Return the result in the required structured format.
"""


EXTRACT_ASSERTIONS_PROMPT = """
You are an assertion extraction module for a conversational memory system.

Your task is to extract atomic factual assertions from the latest user message that may be useful to store in conversational memory.

Inputs:
1. Conversation history:
{conversation_history}

2. Latest user message:
{user_message}

Goal:
Return a list of simple, standalone assertions that should be inserted into memory.

An assertion is a short factual statement about the user, their preferences, plans, relationships, past experiences, constraints, goals, or important conversational context.

Rules:
- Extract only information stated or clearly implied by the latest user message.
- Use the conversation history only to resolve references, pronouns, ellipses, or ambiguous entities.
- Do not extract information from the conversation history unless the latest user message refers to it.
- Each assertion must be atomic: one fact per assertion.
- Each assertion must be standalone and understandable without the original conversation.
- Prefer concise natural language.
- Preserve important names, dates, locations, relationships, and temporal qualifiers.
- Do not infer private or sensitive attributes unless the user explicitly states them.
- Do not store trivial, temporary, or purely conversational content.
- Do not store questions unless they reveal a stable user fact, goal, preference, or constraint.
- Do not store assistant instructions unless they are likely to be useful in future conversations.
- Do not duplicate assertions.
- If there is nothing worth storing, return an empty list.

Good assertions:
- "User likes cats."
- "User plans to visit Amsterdam in May."
- "User is allergic to peanuts."
- "User's friend Anna lives in Berlin."

Bad assertions:
- "User asked a question."
- "User said hello."
- "User wants an answer."
- "The assistant should respond."
- "User might like dogs."
- "Amsterdam is a city."
- "The user wants to pause the discussion for now and return to it later."

Return the result in the required structured format.
"""
