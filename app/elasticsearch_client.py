from elasticsearch import AsyncElasticsearch
from app.config import settings

es_client = AsyncElasticsearch(
    [settings.ELASTICSEARCH_URL],
    request_timeout=30,
)

INDEX_NAME = settings.ELASTICSEARCH_INDEX

INDEX_SETTINGS = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "russian_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "russian_stop", "russian_stemmer"],
                }
            },
            "filter": {
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_",
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian",
                },
            },
        },
    },
    "mappings": {
        "properties": {
            "id": {"type": "integer"},
            "text": {
                "type": "text",
                "analyzer": "russian_analyzer",
            },
        }
    },
}


async def create_index():
    if not await es_client.indices.exists(index=INDEX_NAME):
        await es_client.indices.create(index=INDEX_NAME, **INDEX_SETTINGS)
        print(f"Index '{INDEX_NAME}' created.")
    else:
        print(f"Index '{INDEX_NAME}' already exists.")


async def index_document(doc_id: int, text: str):
    await es_client.index(
        index=INDEX_NAME,
        id=doc_id,
        document={"id": doc_id, "text": text},
    )


async def delete_document_from_index(doc_id: int):
    try:
        await es_client.delete(index=INDEX_NAME, id=doc_id)
    except Exception:
        pass


async def search_in_index(query: str, size: int = 20):
    response = await es_client.search(
        index=INDEX_NAME,
        query={"match": {"text": query}},
        size=size,
    )
    hits = response["hits"]["hits"]
    return [hit["_source"]["id"] for hit in hits]


async def close_es():
    await es_client.close()