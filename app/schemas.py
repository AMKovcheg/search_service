from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DocumentCreate(BaseModel):
    rubrics: Optional[List[str]] = None
    text: str
    created_date: datetime


class DocumentResponse(BaseModel):
    id: int
    rubrics: Optional[List[str]] = None
    text: str
    created_date: datetime

    model_config = {"from_attributes": True}


class SearchResponse(BaseModel):
    total: int
    documents: List[DocumentResponse]


class DeleteResponse(BaseModel):
    message: str