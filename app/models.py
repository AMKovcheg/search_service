from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rubrics = Column(Text, nullable=True)
    text = Column(Text, nullable=False)
    created_date = Column(DateTime, nullable=False)