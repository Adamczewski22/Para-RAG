from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.embeddings import Embeddings
from dotenv import find_dotenv, load_dotenv
from functools import lru_cache
import tiktoken

load_dotenv(find_dotenv())

EMBEDDINGS_MODEL = "text-embedding-3-large"


@lru_cache(maxsize=None)
def _get_token_encoding(model: str):
    try:
        return tiktoken.encoding_for_model(model)
    except Exception:
        return None


def count_embedding_tokens(text: str, model: str = EMBEDDINGS_MODEL) -> dict:
    encoding = _get_token_encoding(model)
    if encoding is not None:
        input_tokens = len(encoding.encode(text))
        estimated = False
    else:
        # Avoid making benchmark runs depend on tiktoken's lazy network fetch
        input_tokens = 0 if not text else max(1, len(text.encode("utf-8")) // 4)
        estimated = True

    return {
        "input_tokens": input_tokens,
        "output_tokens": 0,
        "total_tokens": input_tokens,
        "estimated": estimated,
    }

@lru_cache(maxsize=1)
def get_embedder() -> Embeddings:
    return OpenAIEmbeddings(model=EMBEDDINGS_MODEL)
