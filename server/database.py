import asyncpg
from typing import Optional, List, Any
import time
from .config import get_settings

settings = get_settings()

class Database:
    def __init__(self):
        self._pool = None
        self.max_retries = 5
        self.initial_delay = 1

    async def connect(self, retries: Optional[int] = None) -> None:
        if retries is None:
            retries = self.max_retries

        last_error = None
        for attempt in range(retries):
            try:
                self._pool = await asyncpg.create_pool(
                    settings.database_url,
                    min_size=2,
                    max_size=10,
                    command_timeout=60,
                    ssl='require'
                )
                print("Database connection established")
                return
            except Exception as e:
                last_error = e
                if attempt < retries - 1:
                    delay = self.initial_delay * (2 ** attempt)
                    print(f"Connection attempt {attempt + 1} failed: {str(e)}")
                    print(f"Retrying in {delay}s...")
                    time.sleep(delay)

        raise Exception(f"Failed to connect after {retries} attempts: {str(last_error)}")

    async def init_db(self) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("Database schema initialized successfully")

    async def fetch_one(self, query: str, *args) -> Optional[dict]:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None

    async def fetch_all(self, query: str, *args) -> List[dict]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]

    async def execute(self, query: str, *args) -> str:
        async with self._pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
            self._pool = None
            print("Database connection closed")