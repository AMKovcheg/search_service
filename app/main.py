import json
from datetime import datetime

import pandas as pd
from fastapi import FastAPI, Query
from sqlalchemy import select

from app.database import init_db, async_session
from app.elasticsearch_client import create_index, index_document, close_es
from app.models import Document
from app.routes import search

app = FastAPI(
    title="Document Search Service",
    description="Простой поисковик по текстам документов с использованием Elasticsearch",
    version="1.0.0",
)

app.include_router(search.router, prefix="/api/v1", tags=["search"])


@app.on_event("startup")
async def startup_event():
    await init_db()
    await create_index()
    print("Database and Elasticsearch index initialized.")


@app.on_event("shutdown")
async def shutdown_event():
    await close_es()


@app.get("/")
async def root():
    return {"message": "Document Search Service is running"}


@app.post("/import-csv")
async def import_csv(file_path: str = Query("posts.csv")):
    """Импорт данных из CSV файла в БД и Elasticsearch."""
    try:
        df = pd.read_csv(file_path)
        count = 0

        async with async_session() as db:
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
                    created_date=created_date,
                )
                db.add(doc)
                count += 1

            await db.commit()

            # Индексируем все документы
            result = await db.execute(select(Document))
            docs = result.scalars().all()
            for doc in docs:
                await index_document(doc.id, doc.text)

        return {"message": f"Imported {count} documents"}

    except Exception as e:
        return {"error": str(e)}