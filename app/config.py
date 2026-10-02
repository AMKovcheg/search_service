import os

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./documents.db")
    ELASTICSEARCH_URL: str = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    ELASTICSEARCH_INDEX: str = os.getenv("ELASTICSEARCH_INDEX", "documents")
    TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///./test_documents.db")

settings = Settings()