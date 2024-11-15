from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
from typing import List

from .database import db
from .models import Entry, EntryCreate, EntryUpdate
from .config import get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await db.connect()
        await db.init_db()
        yield
    finally:
        # Shutdown
        await db.close()

app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        await db.fetch_one("SELECT 1 as value")
        return JSONResponse({"status": "healthy", "database": "connected"})
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": str(e)}
        )

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/api/entries", response_model=List[Entry])
async def get_entries():
    try:
        return await db.fetch_all("SELECT * FROM entries ORDER BY created_at DESC")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/entries", response_model=Entry)
async def create_entry(entry: EntryCreate):
    try:
        query = """
            INSERT INTO entries (title, content)
            VALUES ($1, $2)
            RETURNING id, title, content, created_at
        """
        return await db.fetch_one(query, entry.title, entry.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/entries/{entry_id}", response_model=Entry)
async def get_entry(entry_id: int):
    try:
        entry = await db.fetch_one("SELECT * FROM entries WHERE id = $1", entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        return entry
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/entries/{entry_id}", response_model=Entry)
async def update_entry(entry_id: int, entry: EntryUpdate):
    try:
        query = """
            UPDATE entries 
            SET title = $1, content = $2 
            WHERE id = $3 
            RETURNING id, title, content, created_at
        """
        updated = await db.fetch_one(query, entry.title, entry.content, entry_id)
        if not updated:
            raise HTTPException(status_code=404, detail="Entry not found")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/entries/{entry_id}")
async def delete_entry(entry_id: int):
    try:
        deleted = await db.fetch_one(
            "DELETE FROM entries WHERE id = $1 RETURNING id", 
            entry_id
        )
        if not deleted:
            raise HTTPException(status_code=404, detail="Entry not found")
        return {"message": "Entry deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve index.html for all other routes to support client-side routing
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    return FileResponse("static/index.html")