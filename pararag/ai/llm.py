from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from dotenv import load_dotenv, find_dotenv
from functools import lru_cache

LLM_MODEL = "gpt-5.2"

load_dotenv(find_dotenv())

@lru_cache(maxsize=1)
def get_llm() -> BaseChatModel:
    return ChatOpenAI(
        model=LLM_MODEL,
        temperature=0.0,
    )
