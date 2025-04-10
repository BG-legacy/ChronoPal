from pydantic import BaseModel
from typing import List 
from datetime import datetime

class Pet(BaseModel):
    userId: str
    petName: str
    level: int
    mood: str
    evolutionStage:str
    lastFed: datetime
    memoryLog: List[str]

    class Config:
        orm_mode = True