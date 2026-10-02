import asyncio
import json
from datetime import datetime

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Document

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_documents.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def sample_documents(db_session):
    docs = [
        Document(
            rubrics=json.dumps(["rubric1", "rubric2"]),
            text="ВАЗ 2101 классический автомобиль",
            created_date=datetime(2019, 7, 25, 12, 42, 13),
        ),
        Document(
            rubrics=json.dumps(["rubric3"]),
            text="Новый боевой таз. Был в наличии только смоляной кузов пикап",
            created_date=datetime(2019, 12, 24, 15, 5, 57),
        ),
        Document(
            rubrics=None,
            text="Привет всем! Хочу показать свои Жиги из бумаги в масштабе 1:25",
            created_date=datetime(2019, 10, 13, 18, 11, 36),
        ),
    ]
    for doc in docs:
        db_session.add(doc)
    await db_session.commit()
    for doc in docs:
        await db_session.refresh(doc)
    return docs