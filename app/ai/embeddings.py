from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.embeddings import Embeddings
from dotenv import find_dotenv, load_dotenv
from functools import lru_cache

load_dotenv(find_dotenv())

EMBEDDINGS_MODEL = "text-embedding-3-large"

@lru_cache(maxsize=1)
def get_embedder() -> Embeddings:
    return OpenAIEmbeddings(model=EMBEDDINGS_MODEL)
