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


# Makes assertions less atomic, richer, and capturing more context
LOCOMO_EXTRACT_ASSERTIONS_PROMPT_2 = """
You are a memory extraction module for a conversational memory system.

Your task is to extract compact, standalone memory entries from the latest message.

Inputs:
1. Conversation history:
{conversation_history}

2. Latest message:
{user_message}

Goal:
Return a list of useful memory entries that should be inserted into conversational memory.

A memory entry should capture one meaningful fact, preference, plan, event, relationship, experience, or attitude.
It should be specific enough to be useful when retrieved later.

Rules:
- Extract information only from the latest message.
- Use the conversation history only to resolve references, pronouns, ellipses, or ambiguous entities.
- When the latest message depends on earlier context, resolve what it refers to and include enough of that context so the memory entry remains clear and useful when retrieved alone.
- Do not extract new information from the conversation history itself.
- Each memory entry must be standalone and understandable without the original conversation.
- Preserve the identity of the speaker and other people involved.
- Preserve important names, dates, locations, relationships, events, and temporal qualifiers.
- Keep tightly connected details together when separating them would make the memory vague or incomplete.
- Do not split emotions, opinions, or intentions away from the thing they are about.
- Prefer concise natural language.
- Do not store trivial greetings, filler, or purely conversational reactions.
- Do not duplicate memory entries.
- If there is nothing worth storing, return an empty list.

Good memory entries:
- "Maya prefers quiet cafés because they help her focus while studying."
- "Ethan plans to visit his sister in Lisbon next spring."
- "Priya is allergic to cats and avoids homes with cat hair."
- "Luca enjoyed his hiking trip in the Dolomites because the views were peaceful."
- "Ava wants Omar to review her presentation before Friday's meeting."
- "Noah finds jazz piano relaxing after work."
- "Sofia and Daniel agreed to try a cooking class together next month."

Bad memory entries:
- "Maya likes quiet places." (bad: loses the reason and context)
- "Ethan is excited for next spring." (bad: unclear what he is excited about)
- "Priya avoids homes." (bad: loses the allergy-related reason)
- "The trip was peaceful." (bad: loses who experienced it and what trip it was)
- "Ava wants a review." (bad: loses who should review what and by when)
- "Omar replied to Ava." (bad: conversational metadata)
- "The speaker had fun." (bad: loses speaker identity and context)
- "User asked a question." (bad: not useful memory)

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

# This prompt strives to make deduplication less agressive which has proven to be an issue in locomo benchmark.
MEMORY_DEDUPLICATION_PROMPT_2 = """
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
Return "no" if the new memory is a duplicate, near-duplicate, or only adds a very small amount of information.
Provide a reason for your judgement briefly in one sentence.

Rules:

- Return "no" if the same fact is already present in the past memories.
- Return "no" if the new memory only rephrases an existing memory without adding any useful detail.
- Return "yes" if the new memory contains a new fact, new entity, new date, new location, new preference, new relationship, or new event.
- Return "yes" if the new memory adds a specific detail that is not explicitly preserved in the past memories, such as a description, feeling, reason, intention, quote-like phrase, object, or action.
- Return "yes" if the new memory updates, corrects, or contradicts an existing memory.
- Return "yes" if the new memory is more specific than the existing memories in a useful way.
- Return "yes" if there are no similar past memories.
- When unsure whether a detail may be useful later, prefer "yes".
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

# This deduplication prompt aims to make deduplication even less aggressive as some failures in locomo were still caused by deduplication.
MEMORY_DEDUPLICATION_PROMPT_3 = """
You are a memory deduplication module for a conversational memory system.

Your task is to compare a new memory with the most similar memories that are already stored.

Inputs:
1. New memory:
{new_memory}

2. Most similar past memories:
{past_memories}

Goal:
Decide whether the new memory should be inserted into memory.

Return "yes" if the new memory should be inserted.
Return "no" only if the new memory is already fully covered by the past memories.
Provide a brief one-sentence reason.

Rules:
- Prefer "yes" unless the new memory is clearly redundant.
- Return "no" only if a past memory expresses the same fact with the same important meaning.
- Return "no" if the new memory is only a rephrasing of an existing memory and adds no useful detail.
- Return "yes" if the new memory contains any new useful detail, including a new reason, cause, description, feeling, intention, date, event, object, action, quote-like phrase, or relationship.
- Return "yes" if the new memory could help answer a future question differently or more precisely.
- Return "yes" if the new memory is more specific than the past memories.
- Return "yes" if the new memory updates, corrects, narrows, or contradicts a past memory.
- Return "yes" if there are no similar past memories.
- Do not reject a memory just because it is related to an existing memory.
- Do not reject a memory just because it supports the same general topic as an existing memory.
- Do not judge whether the memory is true in the real world.
- Do not rewrite the memory.

Examples:

New memory:
"Emma enjoyed hiking with Leo."

Past memories:
- "Emma had a good time hiking with Leo."

Decision:
"no"

New memory:
"Emma enjoyed hiking with Leo because the mountain views were peaceful."

Past memories:
- "Emma enjoyed hiking with Leo."

Decision:
"yes"

New memory:
"Amir believes Nora's patience and creativity make her a good teacher."

Past memories:
- "Amir believes Nora will be a good teacher."

Decision:
"yes"

New memory:
"Sofia has two rabbits."

Past memories:
- "Sofia owns two rabbits."

Decision:
"no"

New memory:
"Daniel moved to Prague."

Past memories:
- "Daniel lives in Vienna."

Decision:
"yes"

Return the result in the required structured format.
"""


UPDATE_PROFILE_PROMPT = """
You are a profile update module for a conversational memory system.

Your task is to update concise person profiles using newly extracted memory assertions.

Inputs:
1. New information:
{assertions}

2. Current profiles:
{profiles}

Goal:
Return only the profiles that should be created or updated.

A profile should capture key, relatively stable information about a person, such as:
- important personal facts
- stable preferences
- goals
- occupations or studies
- important relationships
- recurring activities or interests
- major life events
- long-term plans or constraints

Rules:
- Use the new information to decide whether any profile should change.
- You may update no profiles, single, or multiple profiles.
- If the new information is irrelevant to stable profiles, return an empty list.
- Do not update a profile for trivial, temporary, or one-off conversational details.
- Do not create a profile just because a person is mentioned.
- Preserve useful existing profile information unless it is corrected or outdated.
- Add new stable information when it meaningfully improves the profile.
- Update a profile if the new information corrects, contradicts, or refines it.
- Keep each profile concise, they should not exceed 10 sentences.
- Each returned profile must be the full new version of that person's profile, not just the added part.
- People's names must be perfectly preserved in the updated profiles.
- Do not invent information.
- Return an empty list if no profile should be created or updated.

Examples:

New information:
- "Maya is studying architecture."
- "Maya recently bought a blue notebook."

Current profiles:
[]

Profile update:
name: "Maya"
profile: "Maya studies architecture."

New information:
- "Leo said the movie was fun."
- "Leo ordered pasta for dinner."

Current profiles:
- name: "Leo"
  profile: "Leo enjoys science fiction."

Profile update:
[]

New information:
- "Nora lost her job last week."
- "Nora is looking for a new role in marketing."

Current profiles:
- name: "Nora"
  profile: "Nora works in marketing."

Profile update:
name: "Nora"
profile: "Nora lost her job in marketing, and is looking for a new positon in the field."

New information:
- "Omar is training for his first marathon."
- "Omar felt tired after today's run."

Current profiles:
[]

Profile update:
name: "Omar"
profile: "Omar is training for his first marathon."

New information:
- "Sofia moved to Berlin for graduate school."
- "Sofia misses her old apartment."

Current profiles:
- name: "Sofia"
  profile: "Sofia is interested in psychology."

Profile update:
name: "Sofia"
profile: "Sofia is interested in psychology. She has moved to Berlin for graduate school."

New information:
- "Daniel joked that he could eat pizza every day."

Current profiles:
[]

Profile update:
[]

Return the result in the required structured format.
"""


UPDATE_PROFILE_PROMPT_2 = """
You are a profile update module for a conversational memory system.

Your task is to update concise person profiles using newly extracted memory assertions.

Inputs:
1. New information:
{assertions}

2. Current profiles:
{profiles}

Goal:
Return only the profiles that should be created or updated.

A profile is a compact high-level summary of a person. It should contain only core, stable, or life-significant information, such as:
- important personal facts
- occupation, studies, or major career status
- major life events, such as losing a job, moving, starting a business, or getting a new role
- stable passions, long-term goals, or central interests
- important relationships or long-term constraints

Rules:
- Update a profile only when the new information changes the person's core profile.
- Return an empty list if the new information is only ordinary memory, conversation detail, encouragement, advice, a temporary emotion, a minor plan, or a one-off event.
- Do not update a profile just because the new information is true or potentially useful.
- Do not update a profile just to add small refinements, compliments, reactions, motivational statements, or details about a specific conversation.
- Preserve useful existing profile information unless it is corrected, outdated, or should be compressed.
- If updating, return a concise full replacement profile, not just the added part.
- Keep each profile concise, they should not exceed 7 sentences.
- People's names must be perfectly preserved in the updated profiles.
- Do not invent information.
- Return an empty list if no profile should be created or updated.

Examples:

New information:
- "Maya lost her job at a design agency."
- "Maya is looking for a new role in architecture."

Current profiles:
- name: "Maya"
  profile: "Maya works in architecture."

Profile update:
name: "Maya"
profile: "Maya has experience in architecture and is looking for a new role after losing her job at a design agency."

New information:
- "Leo thanked Maya for believing in him."
- "Leo said Maya's support gives him confidence."

Current profiles:
- name: "Leo"
  profile: "Leo is starting a small bakery and is passionate about baking."

Profile update:
[]

New information:
- "Nora started a small online clothing business."
- "Nora wants to become financially independent."

Current profiles:
[]

Profile update:
name: "Nora"
profile: "Nora started a small online clothing business and wants to become financially independent."

New information:
- "Omar asked for advice about tomorrow's presentation."
- "Omar felt nervous but encouraged after the conversation."

Current profiles:
- name: "Omar"
  profile: "Omar studies computer science."

Profile update:
[]

New information:
- "Sofia is 20 years old."
- "Sofia has loved dancing since childhood."

Current profiles:
[]

Profile update:
name: "Sofia"
profile: "Sofia is 20 years old and has loved dancing since childhood."

New information:
- "Daniel moved to Berlin for graduate school."

Current profiles:
- name: "Daniel"
  profile: "Daniel studies psychology."

Profile update:
name: "Daniel"
profile: "Daniel studies psychology and moved to Berlin for graduate school."

Return the result in the required structured format.
"""
