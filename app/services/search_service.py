from sqlalchemy.ext.asyncio import AsyncSession
from app.elasticsearch_client import search_in_index, index_document, delete_document_from_index
from app.services.document_service import get_documents_by_ids, parse_rubrics
from app.schemas import DocumentResponse


async def search_documents(db: AsyncSession, query: str, limit: int = 20):
    doc_ids = await search_in_index(query, size=limit)
    documents = await get_documents_by_ids(db, doc_ids)

    results = []
    for doc in documents:
        results.append(
            DocumentResponse(
                id=doc.id,
                rubrics=parse_rubrics(doc.rubrics),
                text=doc.text,
                created_date=doc.created_date,
            )
        )

    return {"total": len(results), "documents": results}


async def delete_document_full(db: AsyncSession, doc_id: int):
    from app.services.document_service import delete_document

    await delete_document_from_index(doc_id)
    return await delete_document(db, doc_id)


async def index_all_documents(db: AsyncSession):
    from sqlalchemy import select
    from app.models import Document

    result = await db.execute(select(Document))
    docs = result.scalars().all()
    for doc in docs:
        await index_document(doc.id, doc.text)
    print(f"Indexed {len(docs)} documents.")