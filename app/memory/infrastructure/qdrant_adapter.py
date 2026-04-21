from qdrant_client import AsyncQdrantClient, QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from enum import Enum
import logging
import uuid


REST_PORT = 6333
QDRANT_URL = f"http://localhost:{REST_PORT}"

VECTOR_SIZE = 3072 # Matches openai text-embedding-3-large
DISTANCE_METRIC = Distance.COSINE

logger = logging.getLogger(__name__)


class Collection(str, Enum):
    ASSERTIONS = "assertions"


class QdrantAdapter:
    def __init__(self):
        self.client = AsyncQdrantClient(url=QDRANT_URL)
    
    async def init_collections(self) -> None:
        # Create collections if not present
        for collection in Collection:
            if not await self.client.collection_exists(collection.value):

                await self.client.create_collection(
                    collection_name=collection,
                    vectors_config=VectorParams(
                        size=VECTOR_SIZE, 
                        distance=DISTANCE_METRIC,
                    )
                )
    
    async def insert(self, vector: list[float], payload: dict, collection: Collection) -> None:
        point_id = str(uuid.uuid4())
        point = PointStruct(id=point_id, vector=vector, payload=payload)

        await self.client.upsert(
            collection_name=collection,
            wait=True,
            points=[point]
        )

    async def search(self, vector: list[float], collection: Collection, k: int) -> list[dict]:
        results = await self.client.query_points(
            collection_name=collection,
            query=vector,
            with_payload=True,
            limit=k,
        )
        return [result.payload for result in results.points]
