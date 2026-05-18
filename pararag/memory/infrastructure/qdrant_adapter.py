from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FilterSelector, FieldCondition, MatchValue
import logging
import uuid

from pararag.shared.models import MemoryEntry
from pararag.shared.types import Collection, Vector
from pararag.memory.domain.interfaces import MemoryStore
from .mappers import memory_to_payload, payload_to_memory


REST_PORT = 6333
QDRANT_URL = f"http://localhost:{REST_PORT}"

VECTOR_SIZE = 3072 # Matches openai text-embedding-3-large
DISTANCE_METRIC = Distance.COSINE

NAMESPACE_FIELD = "namespace"

logger = logging.getLogger(__name__)


class QdrantAdapter(MemoryStore):
    def __init__(self):
        self.client = AsyncQdrantClient(url=QDRANT_URL)
    
    async def init_collections(self) -> None:
        # Create collections if not present
        for collection in Collection:
            if not await self.client.collection_exists(collection):

                await self.client.create_collection(
                    collection_name=collection,
                    vectors_config=VectorParams(
                        size=VECTOR_SIZE, 
                        distance=DISTANCE_METRIC,
                    )
                )
    
    async def clear_collection(self, namespace: str, collection: Collection) -> None:
        filter = self._get_namespace_filter(namespace)
        await self.client.delete(
            collection_name=collection,
            points_selector=FilterSelector(filter=filter),
        )
    
    async def insert(self, vector: Vector, memory_entry: MemoryEntry, namespace: str, collection: Collection) -> None:
        point_id = str(uuid.uuid4())
        payload = memory_to_payload(memory_entry, namespace)
        point = PointStruct(id=point_id, vector=vector, payload=payload)

        await self.client.upsert(
            collection_name=collection,
            wait=True,
            points=[point]
        )

    async def search(self, vector: Vector, namespace: str, collection: Collection, k: int) -> list[MemoryEntry]:
        results = await self.client.query_points(
            collection_name=collection,
            query=vector,
            with_payload=True,
            query_filter=self._get_namespace_filter(namespace),
            limit=k,
        )
        return [payload_to_memory(result.payload) for result in results.points]
    
    def _get_namespace_filter(self, namespace: str) -> Filter:
        return Filter(
            must=[
                FieldCondition(
                    key=NAMESPACE_FIELD,
                    match=MatchValue(value=namespace)
                )
            ] 
        )
