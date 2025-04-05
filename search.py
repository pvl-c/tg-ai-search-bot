import weaviate
from config import WEAVIATE_URL, OPENAI_API_KEY

client = weaviate.connect_to_local(
    port=8080,
    grpc_port=50051,
    headers={"X-OpenAI-Api-Key": OPENAI_API_KEY},
)

collection = client.collections.get("Profile")

def search_profiles(query: str, score_threshold: float = 0.33):
    try:
        result = collection.query.hybrid(
            query=query,
            limit=10,
            alpha=0.5,
            return_metadata=["score"]
        )
        filtered = [
            obj for obj in result.objects
            if obj.metadata and obj.metadata.score >= score_threshold
        ]
        return filtered

    except Exception as e:
        print(f"[search_profiles] ❌ Ошибка: {e}")
        return []
