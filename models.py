from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Location(BaseModel):
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    hasGPS: Optional[bool] = True


class EmotionData(BaseModel):
    id: Optional[int] = None
    emotion: int = Field(..., ge=1, le=5)  # 1=Very Sad, 2=Sad, 3=Neutral, 4=Happy, 5=Very Happy
    emotionLabel: str  # "Very Sad", "Sad", "Neutral", "Happy", "Very Happy"
    timestamp: str  # ISO format timestamp from frontend
    hasVlog: Optional[bool] = False
    location: Optional[Location] = None
    user_id: Optional[str] = None


class VlogData(BaseModel):
    id: Optional[int] = None
    mood: int = Field(..., ge=1, le=5)  # Same as emotion scale
    moodLabel: str  # Chinese labels like "非常開心", "心情不錯", etc.
    moodEmoji: Optional[str] = None  # Emoji representation
    timestamp: Optional[int] = None  # Unix timestamp
    date: Optional[str] = None  # Formatted date string
    videoUri: Optional[str] = None  # Photo library URI or file path
    video_data: Optional[str] = None  # Base64 encoded video data for upload
    hasVideo: Optional[bool] = True
    location: Optional[Location] = None
    user_id: Optional[str] = None


class GPSCoordinate(BaseModel):
    latitude: float
    longitude: float
    timestamp: str  # ISO format timestamp
    accuracy: Optional[float] = None
    user_id: Optional[str] = None


# Legacy models for backward compatibility
class Sentiment(BaseModel):
    text: str
    sentiment_score: float  # -1 (negative) to 1 (positive)
    confidence: Optional[float] = None
    timestamp: datetime
    user_id: Optional[str] = None
    emotions: Optional[dict] = None


class Vlog(BaseModel):
    title: str
    description: Optional[str] = None
    video_url: Optional[str] = None
    video_data: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[float] = None
    timestamp: datetime
    user_id: Optional[str] = None
    location: Optional[Location] = None
    sentiment_analysis: Optional[Sentiment] = None


class DataExportRequest(BaseModel):
    data_type: str = Field(..., pattern="^(vlogs|sentiments|gps|all)$")
    format: str = Field(default="json", pattern="^(json|csv)$")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[str] = None


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    count: Optional[int] = None
