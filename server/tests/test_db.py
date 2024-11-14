import pytest
from ..database import Database
from ..config import get_settings

@pytest.fixture
def db():
    database = Database()
    database.init_db()
    yield database
    # Cleanup
    with database.conn.cursor() as cur:
        cur.execute("DELETE FROM entries WHERE title LIKE 'Test Entry%'")
        database.conn.commit()
    database.close()

def test_database_connection(db):
    with db.conn.cursor() as cur:
        cur.execute("SELECT 1")
        result = cur.fetchone()
        assert result is not None

def test_create_entry(db):
    title = "Test Entry 1"
    content = "Test Content 1"
    
    result = db.query(
        "INSERT INTO entries (title, content) VALUES (%s, %s) RETURNING *",
        (title, content)
    )
    
    assert result[0]["title"] == title
    assert result[0]["content"] == content

def test_retrieve_entry(db):
    # Create test entry
    title = "Test Entry 2"
    content = "Test Content 2"
    
    created = db.query(
        "INSERT INTO entries (title, content) VALUES (%s, %s) RETURNING *",
        (title, content)
    )[0]
    
    # Retrieve the entry
    result = db.query(
        "SELECT * FROM entries WHERE id = %s",
        (created["id"],)
    )
    
    assert result[0]["id"] == created["id"]
    assert result[0]["title"] == title
    assert result[0]["content"] == content

def test_error_handling(db):
    with pytest.raises(Exception):
        db.query("INSERT INTO entries (title) VALUES (%s)", ["Test Entry"])
    
    with pytest.raises(Exception):
        db.query("SELECT invalid_column FROM entries")