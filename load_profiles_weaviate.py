import json
import weaviate
from weaviate.classes.config import Configure
from weaviate.classes.config import Property, DataType
from config import OPENAI_API_KEY

client = weaviate.connect_to_local(
    port=8080,
    grpc_port=50051,
    headers={"X-OpenAI-Api-Key": OPENAI_API_KEY},
)

# создаем класс, если его нет
if "Profile" not in client.collections.list_all():
    client.collections.create(
        name="Profile",
        vectorizer_config=Configure.Vectorizer.text2vec_openai(),
        properties=[
            Property(name="name", data_type=DataType.TEXT),
            Property(name="desc", data_type=DataType.TEXT),
            Property(name="link", data_type=DataType.TEXT),
        ],
    )

collection = client.collections.get("Profile")

with open("profiles.json", "r") as f:
    profiles = json.load(f)

for p in profiles:
    collection.data.insert({
        "name": p["name"],
        "desc": p["desc"],
        "link": p["link"]
    })

print("✅ Загружено", len(profiles), "профилей")

client.close()