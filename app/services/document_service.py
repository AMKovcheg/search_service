import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Document
from app.schemas import DocumentCreate


async def create_document(db: AsyncSession, doc: DocumentCreate) -> Document:
    document = Document(
        rubrics=json.dumps(doc.rubrics) if doc.rubrics else None,
        text=doc.text,
        created_date=doc.created_date,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


async def get_document(db: AsyncSession, doc_id: int) -> Document | None:
    result = await db.execute(select(Document).where(Document.id == doc_id))
    return result.scalar_one_or_none()


async def get_documents_by_ids(db: AsyncSession, ids: list) -> list:
    if not ids:
        return []
    result = await db.execute(
        select(Document)
        .where(Document.id.in_(ids))
        .order_by(Document.created_date.desc())
    )
    return result.scalars().all()


async def delete_document(db: AsyncSession, doc_id: int) -> bool:
    doc = await get_document(db, doc_id)
    if doc:
        await db.delete(doc)
        await db.commit()
        return True
    return False


def parse_rubrics(rubrics_str):
    if not rubrics_str:
        return None
    try:
        return json.loads(rubrics_str)
    except (json.JSONDecodeError, TypeError):
        return None