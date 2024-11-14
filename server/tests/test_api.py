import pytest
from httpx import AsyncClient
from ..main import app
from ..database import Database
import asyncio

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(autouse=True)
async def setup_database():
    db = Database()
    await db.connect()
    await db.init_db()
    yield db
    # Cleanup
    async with db._pool.acquire() as conn:
        await conn.execute("DELETE FROM entries WHERE title LIKE 'Test Entry%'")
    await db.close()

@pytest.mark.asyncio
async def test_create_entry(client):
    response = await client.post("/api/entries", json={
        "title": "Test Entry 1",
        "content": "Test Content 1"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Entry 1"
    assert data["content"] == "Test Content 1"

@pytest.mark.asyncio
async def test_get_entries(client):
    # Create test entry
    await client.post("/api/entries", json={
        "title": "Test Entry 2",
        "content": "Test Content 2"
    })
    
    response = await client.get("/api/entries")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(entry["title"] == "Test Entry 2" for entry in data)

@pytest.mark.asyncio
async def test_update_entry(client):
    # Create entry
    create_response = await client.post("/api/entries", json={
        "title": "Test Entry 3",
        "content": "Original Content"
    })
    entry_id = create_response.json()["id"]
    
    # Update entry
    update_response = await client.put(f"/api/entries/{entry_id}", json={
        "title": "Updated Title",
        "content": "Updated Content"
    })
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated Content"

@pytest.mark.asyncio
async def test_delete_entry(client):
    # Create entry
    create_response = await client.post("/api/entries", json={
        "title": "Test Entry 4",
        "content": "To Be Deleted"
    })
    entry_id = create_response.json()["id"]
    
    # Delete entry
    delete_response = await client.delete(f"/api/entries/{entry_id}")
    assert delete_response.status_code == 200
    
    # Verify deletion
    get_response = await client.get(f"/api/entries/{entry_id}")
    assert get_response.status_code == 404