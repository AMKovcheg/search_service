from sqlalchemy.orm import Session
from app.elasticsearch_client import search_in_index, index_document, delete_document_from_index
from app.services.document_service import get_documents_by_ids, parse_rubrics
from app.schemas import DocumentResponse


def search_documents(db: Session, query: str, limit: int = 20):
    doc_ids = search_in_index(query, size=limit)
    documents = get_documents_by_ids(db, doc_ids)

    results = []
    for doc in documents:
        results.append(DocumentResponse(
            id=doc.id,
            rubrics=parse_rubrics(doc.rubrics),
            text=doc.text,
            created_date=doc.created_date
        ))

    return {
        "total": len(results),
        "documents": results
    }


def delete_document_full(db: Session, doc_id: int):
    from app.services.document_service import delete_document
    delete_document_from_index(doc_id)
    return delete_document(db, doc_id)


def index_all_documents(db: Session):
    from app.models import Document
    docs = db.query(Document).all()
    for doc in docs:
        index_document(doc.id, doc.text)
    print(f"Indexed {len(docs)} documents.")