from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class GPSCoordinate(BaseModel):
    id: Optional[str] = None
    latitude: float  # 緯度
    longitude: float  # 經度
    timestamp: datetime  # 記錄時間
    upload_time: Optional[datetime] = None  # 上傳時間
    accuracy: Optional[float] = None
    user_id: Optional[str] = None


class Sentiment(BaseModel):
    id: Optional[str] = None
    text: str
    mood: Optional[str] = None  # 心情 (如: 非常好, 較好)
    mood_score: Optional[str] = None  # 心情值 (如: 5/5, 4/5)
    sentiment_score: float  # -1 (negative) to 1 (positive)
    confidence: Optional[float] = None
    timestamp: datetime  # 記錄時間
    upload_time: Optional[datetime] = None  # 上傳時間
    user_id: Optional[str] = None
    emotions: Optional[dict] = None  # e.g., {"joy": 0.8, "sadness": 0.2}


class Vlog(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    video_url: Optional[str] = None  # URL to stored video file
    video_path: Optional[str] = None  # 影片路徑
    video_data: Optional[str] = None  # Base64 encoded video data
    thumbnail_url: Optional[str] = None
    duration: Optional[float] = None  # in seconds
    timestamp: datetime  # 記錄時間
    upload_time: Optional[datetime] = None  # 上傳時間
    user_id: Optional[str] = None
    location: Optional[GPSCoordinate] = None
    sentiment_analysis: Optional[Sentiment] = None


class DataExportRequest(BaseModel):
    data_type: str = Field(..., pattern="^(vlogs|sentiments|gps|all)$")
    format: str = Field(default="json", pattern="^(json|csv)$")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[str] = None


# 前端表格顯示的綜合數據模型
class EmotionRecord(BaseModel):
    id: Optional[str] = None
    mood: str  # 心情
    mood_score: str  # 心情值 (如: 5/5)
    latitude: float  # 緯度
    longitude: float  # 經度
    timestamp: datetime  # 記錄時間
    upload_time: datetime  # 上傳時間
    video_path: Optional[str] = None  # 影片路徑
    video_url: Optional[str] = None  # 影片下載連結


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    count: Optional[int] = None
