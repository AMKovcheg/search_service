import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Document Search Service is running"}


@pytest.mark.asyncio
async def test_search_no_results(client: AsyncClient):
    response = await client.get("/api/v1/search", params={"q": "несуществующее_слово_xyz"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["documents"] == []


@pytest.mark.asyncio
async def test_search_returns_documents(client: AsyncClient):
    response = await client.get("/api/v1/search", params={"q": "ВАЗ"})
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "documents" in data
    assert isinstance(data["documents"], list)


@pytest.mark.asyncio
async def test_search_document_structure(client: AsyncClient):
    response = await client.get("/api/v1/search", params={"q": "Жиги"})
    assert response.status_code == 200
    data = response.json()
    if data["total"] > 0:
        doc = data["documents"][0]
        assert "id" in doc
        assert "text" in doc
        assert "created_date" in doc
        assert "rubrics" in doc


@pytest.mark.asyncio
async def test_delete_nonexistent_document(client: AsyncClient):
    response = await client.delete("/api/v1/documents/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"


@pytest.mark.asyncio
async def test_import_csv(client: AsyncClient):
    response = await client.post("/import-csv?file_path=posts.csv")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data or "error" in data


@pytest.mark.asyncio
async def test_search_after_import(client: AsyncClient):
    # Сначала импортируем
    await client.post("/import-csv?file_path=posts.csv")

    # Потом ищем
    response = await client.get("/api/v1/search", params={"q": "ваз"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 0


@pytest.mark.asyncio
async def test_search_limit_parameter(client: AsyncClient):
    response = await client.get("/api/v1/search", params={"q": "таз", "limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert len(data["documents"]) <= 5


@pytest.mark.asyncio
async def test_delete_document_workflow(client: AsyncClient):
    # Импортируем данные
    await client.post("/import-csv?file_path=posts.csv")

    # Находим документ
    search_response = await client.get("/api/v1/search", params={"q": "ваз"})
    search_data = search_response.json()

    if search_data["total"] > 0:
        doc_id = search_data["documents"][0]["id"]

        # Удаляем
        delete_response = await client.delete(f"/api/v1/documents/{doc_id}")
        assert delete_response.status_code == 200

        # Проверяем что удалён
        search_response2 = await client.get("/api/v1/search", params={"q": "ваз"})
        search_data2 = search_response2.json()
        ids = [d["id"] for d in search_data2["documents"]]
        assert doc_id not in ids