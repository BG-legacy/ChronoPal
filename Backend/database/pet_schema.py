from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
from bson import ObjectId

class Pet(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    userId: str
    petName: str
    level: int = 1
    mood: str = "happy"
    evolutionStage: str = "baby"
    lastFed: datetime = Field(default_factory=datetime.utcnow)
    memoryLog: List[str] = Field(default_factory=list)

    class Config:
        json_encoders = {
            ObjectId: str
        }
        json_schema_extra = {
            "example": {
                "userId": "user123",
                "petName": "Fluffy",
                "level": 1,
                "mood": "happy",
                "evolutionStage": "baby",
                "lastFed": datetime.utcnow(),
                "memoryLog": ["First memory"]
            }
        } 