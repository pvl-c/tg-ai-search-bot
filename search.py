import openai
import qdrant_client
from config import OPENAI_API_KEY, QDRANT_HOST, QDRANT_PORT

client = qdrant_client.QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
openai.api_key = OPENAI_API_KEY

def embed_text(text: str):
    response = openai.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def search_profiles(query: str):
    vector = embed_text(query)
    hits = client.search(
        collection_name="creators",
        query_vector=vector,
        limit=3
    )
    results = []
    for hit in hits:
        payload = hit.payload
        results.append({
            "name": payload["name"],
            "desc": payload["desc"],
            "link": payload.get("link", "")
        })
    return results
