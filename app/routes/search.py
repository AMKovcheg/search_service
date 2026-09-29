from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.search_service import search_documents, delete_document_full
from app.schemas import SearchResponse, DeleteResponse

router = APIRouter()


@router.get("/search", response_model=SearchResponse, summary="Поиск документов по тексту")
def search(
    q: str = Query(..., description="Текстовый запрос для поиска"),
    limit: int = Query(20, description="Максимальное количество результатов"),
    db: Session = Depends(get_db)
):
    """
    Поиск по тексту документа в индексе Elasticsearch.
    Возвращает первые N документов со всеми полями БД,
    упорядоченные по дате создания.
    """
    results = search_documents(db, q, limit)
    return results


@router.delete("/documents/{doc_id}", response_model=DeleteResponse, summary="Удаление документа")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db)
):
    """
    Удаляет документ из БД и индекса Elasticsearch по полю id.
    """
    success = delete_document_full(db, doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": f"Document {doc_id} deleted successfully"}