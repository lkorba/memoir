from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class EntryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)

class EntryCreate(EntryBase):
    pass

class EntryUpdate(EntryBase):
    pass

class Entry(EntryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True