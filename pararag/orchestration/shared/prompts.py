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
- If the user query clearly does not require memory retrieval because it is fully answerable from the latest message alone, return an empty list (e.g., in the case of simple smalltalk). Do not return an empty list when the query contains a personal or contextual reference that may have been discussed earlier.
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


LOCOMO_QUERY_DECOMPOSITION_PROMPT = """
You are a query decomposition module for a memory-based question answering system.

Your task is to transform a single benchmark question into one or more short, atomic search queries.
The queries will be used to retrieve evidence from long-term conversation memory.

Input question:
{question}

Goal:
Produce simple retrieval queries that help find the evidence needed to answer the question.

Rules:
- Always return at least one sub-query.
- Each sub-query must be short, concrete, and useful for semantic search.
- Each sub-query should target one atomic piece of evidence.
- Preserve important names, entities, dates, time periods, relationships, and constraints from the question.
- For single-hop questions, usually return one sub-query.
- For multi-hop questions, return multiple sub-queries, one for each needed fact.
- Do not answer the question.
- Do not invent facts.
- Do not create redundant sub-queries.
- Prefer 1-4 sub-queries.

Good examples:

Question:
"What pets wouldn't cause any discomfort to Joanna?"

Sub-queries:
- "Joanna's allergies or causes of discomfort from pets"
- "pets that do not trigger Joanna's allergies"

Question:
"What are Joanna's hobbies?"

Sub-queries:
- "Joanna's hobbies"

Question:
"How long has Nate had his first two turtles?"

Sub-queries:
- "when Nate got his first two turtles"

Question:
"Was the first half of September 2022 a good month career-wise for Nate and Joanna? Answer yes or no."

Sub-queries:
- "Nate's career events in the first half of September 2022"
- "Joanna's career events in the first half of September 2022"

Bad sub-query style:
- "Answer the question"
- "Find relevant information"
- "Everything about Joanna"
- "Nate and Joanna career and pets and hobbies"
- "Was it good?"

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
- "The user wants to pause the discussion for now and return to it later." (bad: temporary and unstable information)
- "The user wants a reminder about the prior discussion regarding their injury." (bad: temporary and not valuable long-term)

Return the result in the required structured format.
"""


LOCOMO_EXTRACT_ASSERTIONS_PROMPT = """
You are an assertion extraction module for a dialogue memory system.

Your task is to extract atomic factual assertions from the latest dialogue message.
These assertions will be inserted into memory and later used for question answering.

Inputs:
1. Conversation history:
{conversation_history}

2. Latest message:
{user_message}

Goal:
Return a list of simple, standalone assertions stated or clearly implied by the latest message.

Important:
- The dialogue has named speakers, such as Maria, John, Nate, or Joanna.
- Always preserve the identity of the speaker or person the assertion is about.
- There is no generic "user" or "assistant"; use the actual speaker names.

Rules:
- Extract assertions only from the latest message.
- Use the conversation history only to resolve pronouns, names, ellipses, or references.
- Do not extract new assertions from the conversation history itself.
- Each assertion must be atomic: one fact per assertion.
- Each assertion must be standalone and understandable without the original dialogue.
- Preserve speaker names, other person names, dates, locations, events, relationships, preferences, emotions, and temporal qualifiers when relevant.
- If the latest message refers to something from earlier, include the resolved reference in the assertion.
- Do not invent facts.
- Do not extract vague reactions, greetings, or filler unless they reveal useful factual information.
- Do not duplicate assertions.
- If there is nothing useful to store, return an empty list.

Good assertions:
- "John went camping with Max."
- "John enjoyed being out in nature."
- "John felt that camping was a nice break from everyday hustle and bustle."
- "Maria thinks camping with pets can be soul-nourishing."
- "Joanna is allergic to pets with fur."
- "Nate has had his first two turtles for three years."

Bad assertions:
- "Maria said wow."
- "John replied to Maria."
- "The speaker had a good time."
- "Someone went somewhere."
- "The conversation is about camping."
- "Maria asked a question."
- "John definitely agreed."

Return the result in the required structured format.
"""

MEMORY_DEDUPLICATION_PROMPT = """
You are a memory deduplication module for a conversational memory system.

Your task is to compare a new memory assertion with the most similar memories that are already stored.

Inputs:
1. New memory assertion:
{new_memory}

2. Most similar past memories:
{past_memories}

Goal:
Decide whether the new memory should be inserted into memory.

Return "yes" if the new memory adds meaningful new information.
Return "no" if the new memory is a duplicate, near-duplicate, or only adds a marginal amount of information.
Provide a reason for your judgement birefly in one sentence.

Rules:
- Return "no" if the same fact is already present in the past memories.
- Return "no" if the new memory only rephrases an existing memory.
- Return "yes" if the new memory contains a new fact, new entity, new date, new location, new preference, new relationship, or new event.
- Return "yes" if the new memory updates, corrects, or contradicts an existing memory.
- Return "yes" if the new memory is more specific than the existing memories in a useful way.
- Return "yes" if there are no similar past memories.
- Do not judge whether the memory is true in the real world.
- Do not rewrite the memory.

Examples:

New memory:
"John enjoyed camping with Max."

Past memories:
- "John had a good time camping with Max."

Decision:
"no"

New memory:
"John went camping with Max in September 2022."

Past memories:
- "John went camping with Max."

Decision:
"yes"

New memory:
"Joanna is allergic to pets with fur."

Past memories:
- "Joanna is allergic to cats."

Decision:
"yes"

New memory:
"Nate has two turtles."

Past memories:
- "Nate owns two turtles."

Decision:
"no"

New memory:
"Maria moved to Boston."

Past memories:
- "Maria lives in Chicago."

Decision:
"yes"

Return the result in the required structured format.
"""
