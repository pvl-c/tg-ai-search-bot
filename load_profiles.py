import json
import openai
from config import OPENAI_API_KEY, QDRANT_HOST, QDRANT_PORT
import qdrant_client
from qdrant_client.models import PointStruct, VectorParams, Distance

openai.api_key = OPENAI_API_KEY
client = qdrant_client.QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

COLLECTION_NAME = "creators"

def embed_text(text):
    response = openai.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def main():
    with open("profiles.json", "r") as f:
        profiles = json.load(f)

    if COLLECTION_NAME not in [c.name for c in client.get_collections().collections]:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )

    points = []
    for profile in profiles:
        vector = embed_text(profile["desc"])
        points.append(PointStruct(
            id=profile["id"],
            vector=vector,
            payload=profile
        ))

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print("✅ Профили загружены")

if __name__ == "__main__":
    main()
