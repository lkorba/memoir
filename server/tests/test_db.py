import pytest
import asyncio
from ..database import db

@pytest.fixture(autouse=True)
async def setup_database():
    await db.connect()
    await db.init_db()
    yield db
    # Cleanup
    async with db._pool.acquire() as conn:
        await conn.execute("DELETE FROM entries WHERE title LIKE 'Test Entry%'")
    await db.close()

@pytest.mark.asyncio
async def test_database_connection():
    result = await db.fetch_one("SELECT 1 as value")
    assert result["value"] == 1

@pytest.mark.asyncio
async def test_create_entry():
    title = "Test Entry 1"
    content = "Test Content 1"
    
    result = await db.fetch_one(
        "INSERT INTO entries (title, content) VALUES ($1, $2) RETURNING *",
        title, content
    )
    
    assert result["title"] == title
    assert result["content"] == content

@pytest.mark.asyncio
async def test_retrieve_entry():
    # Create test entry
    title = "Test Entry 2"
    content = "Test Content 2"
    
    created = await db.fetch_one(
        "INSERT INTO entries (title, content) VALUES ($1, $2) RETURNING *",
        title, content
    )
    
    # Retrieve the entry
    result = await db.fetch_one(
        "SELECT * FROM entries WHERE id = $1",
        created["id"]
    )
    
    assert result["id"] == created["id"]
    assert result["title"] == title
    assert result["content"] == content

@pytest.mark.asyncio
async def test_error_handling():
    with pytest.raises(Exception):
        await db.execute("INSERT INTO entries (title) VALUES ($1)", "Test Entry")
    
    with pytest.raises(Exception):
        await db.fetch_all("SELECT invalid_column FROM entries")