from fastapi import FastAPI
from app.database import engine, Base, SessionLocal
from app.models import Document
from app.elasticsearch_client import create_index, index_document
from app.routes import search
from app.services.document_service import parse_rubrics
import pandas as pd
import json
from datetime import datetime

app = FastAPI(
    title="Document Search Service",
    description="Простой поисковик по текстам документов с использованием Elasticsearch",
    version="1.0.0"
)

app.include_router(search.router, prefix="/api/v1", tags=["search"])


@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    create_index()


@app.get("/")
def root():
    return {"message": "Document Search Service is running"}


@app.post("/import-csv")
def import_csv(file_path: str = "posts.csv"):
    """Импорт данных из CSV файла в БД и Elasticsearch."""
    try:
        df = pd.read_csv(file_path)
        db = SessionLocal()

        count = 0
        for _, row in df.iterrows():
            text = row.get("text", "")
            created_date_str = row.get("created_date", "")
            rubrics_str = row.get("rubrics", "")

            if pd.isna(text) or not text:
                continue

            try:
                created_date = datetime.strptime(created_date_str, "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                try:
                    created_date = datetime.strptime(created_date_str, "%Y-%m-%d")
                except (ValueError, TypeError):
                    created_date = datetime.now()

            rubrics = None
            if rubrics_str and not pd.isna(rubrics_str):
                try:
                    rubrics = json.loads(rubrics_str)
                except (json.JSONDecodeError, TypeError):
                    rubrics = [rubrics_str]

            doc = Document(
                rubrics=json.dumps(rubrics) if rubrics else None,
                text=str(text),
                created_date=created_date
            )
            db.add(doc)
            count += 1

        db.commit()

        docs = db.query(Document).all()
        for doc in docs:
            index_document(doc.id, doc.text)

        db.close()
        return {"message": f"Imported {count} documents"}

    except Exception as e:
        return {"error": str(e)}