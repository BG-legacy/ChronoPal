from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MemoryLog(BaseModel):
    user_id: Optional[str]
    prompt: str
    response: str
    timestamp: datetime = datetime.utcnow()
