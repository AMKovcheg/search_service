import json
from sqlalchemy.orm import Session
from app.models import Document
from app.schemas import DocumentCreate


def create_document(db: Session, doc: DocumentCreate) -> Document:
    document = Document(
        rubrics=json.dumps(doc.rubrics) if doc.rubrics else None,
        text=doc.text,
        created_date=doc.created_date
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def get_document(db: Session, doc_id: int) -> Document:
    return db.query(Document).filter(Document.id == doc_id).first()


def get_documents_by_ids(db: Session, ids: list) -> list:
    if not ids:
        return []
    return db.query(Document).filter(Document.id.in_(ids)).order_by(Document.created_date.desc()).all()


def delete_document(db: Session, doc_id: int) -> bool:
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if doc:
        db.delete(doc)
        db.commit()
        return True
    return False


def parse_rubrics(rubrics_str):
    if not rubrics_str:
        return None
    try:
        return json.loads(rubrics_str)
    except (json.JSONDecodeError, TypeError):
        return None