from elasticsearch import Elasticsearch
from app.config import settings

es_client = Elasticsearch(
    [settings.ELASTICSEARCH_URL],
    request_timeout=30
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
                    "filter": ["lowercase", "russian_stop", "russian_stemmer"]
                }
            },
            "filter": {
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_"
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "id": {"type": "integer"},
            "text": {
                "type": "text",
                "analyzer": "russian_analyzer"
            }
        }
    }
}


def create_index():
    if not es_client.indices.exists(index=INDEX_NAME):
        es_client.indices.create(index=INDEX_NAME, **INDEX_SETTINGS)
        print(f"Index '{INDEX_NAME}' created.")
    else:
        print(f"Index '{INDEX_NAME}' already exists.")


def index_document(doc_id: int, text: str):
    es_client.index(
        index=INDEX_NAME,
        id=doc_id,
        document={"id": doc_id, "text": text}
    )


def delete_document_from_index(doc_id: int):
    try:
        es_client.delete(index=INDEX_NAME, id=doc_id)
    except Exception:
        pass


def search_in_index(query: str, size: int = 20):
    response = es_client.search(
        index=INDEX_NAME,
        query={
            "match": {
                "text": query
            }
        },
        size=size
    )
    hits = response["hits"]["hits"]
    return [hit["_source"]["id"] for hit in hits]