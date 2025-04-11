from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId

# Constants for mood levels
MOOD_LEVELS = {
    "HAPPY": "happy",
    "CONTENT": "content",
    "NEUTRAL": "neutral",
    "GRUMPY": "grumpy",
    "ANGRY": "angry"
}

# Constants for sass levels
SASS_LEVELS = {
    "SWEET": 1,
    "PLAYFUL": 2,
    "SNARKY": 3,
    "SASSY": 4,
    "SAVAGE": 5
}

# Neglect threshold in hours
NEGLECT_THRESHOLD_HOURS = 24

class Pet(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    name: str
    species: str
    mood: str = Field(default=MOOD_LEVELS["HAPPY"])
    level: int = Field(default=1)
    sassLevel: int = Field(default=SASS_LEVELS["SWEET"])
    userId: str
    lastFed: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    lastInteraction: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    interactionCount: int = 0
    memoryLog: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(
        json_encoders={
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        },
        json_schema_extra={
            "example": {
                "name": "Fluffy",
                "species": "cat",
                "mood": MOOD_LEVELS["HAPPY"],
                "level": 1,
                "sassLevel": SASS_LEVELS["SWEET"],
                "userId": "user_id_here"
            }
        }
    )