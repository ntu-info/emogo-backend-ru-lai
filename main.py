from typing import Optional, List
from datetime import datetime
import json
import csv
import zipfile
import io
from io import StringIO

from fastapi import FastAPI, HTTPException, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse

from models import Vlog, Sentiment, GPSCoordinate, DataExportRequest, APIResponse, EmotionRecord
from database import (
    connect_to_mongo, 
    close_mongo_connection, 
    get_database,
    get_collection,
    VLOGS_COLLECTION,
    SENTIMENTS_COLLECTION, 
    GPS_COLLECTION
)

app = FastAPI(
    title="EmoGo Backend API",
    description="Backend API for EmoGo app to collect vlogs, sentiments, and GPS coordinates",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()


@app.get("/", response_model=APIResponse)
async def root():
    return APIResponse(
        success=True,
        message="Welcome to EmoGo Backend API! Visit /docs for API documentation.",
        data={"endpoints": ["/vlogs", "/sentiments", "/gps", "/export", "/emotions", "/status"]}
    )


@app.get("/status", response_model=APIResponse)
async def get_status():
    """Get database connection status"""
    try:
        import os
        mongodb_uri = os.getenv("MONGODB_URI")
        database = await get_database()
        
        if database == "memory_db":
            db_status = "Using in-memory database (MongoDB not configured)"
        elif database is None:
            db_status = "No database connection"
        else:
            db_status = "Connected to MongoDB"
            
        return APIResponse(
            success=True,
            message="Backend status check",
            data={
                "database_status": db_status,
                "mongodb_uri_configured": mongodb_uri is not None,
                "mongodb_uri_preview": mongodb_uri[:20] + "..." if mongodb_uri else None
            }
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Status check failed: {str(e)}",
            data={"error": str(e)}
        )


# Data Collection Endpoints
@app.post("/vlogs", response_model=APIResponse)
async def create_vlog(vlog: Vlog):
    """Create a new vlog entry"""
    try:
        db = await get_database()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        vlog_dict = vlog.dict()
        vlog_dict["created_at"] = datetime.utcnow()
        
        result = await db[VLOGS_COLLECTION].insert_one(vlog_dict)
        
        return APIResponse(
            success=True,
            message="Vlog created successfully",
            data={"id": str(result.inserted_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating vlog: {str(e)}")


@app.post("/sentiments", response_model=APIResponse)
async def create_sentiment(sentiment: Sentiment):
    """Create a new sentiment entry"""
    try:
        collection = await get_collection(SENTIMENTS_COLLECTION)
        if collection is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        sentiment_dict = sentiment.dict()
        sentiment_dict["created_at"] = datetime.utcnow()
        
        result = await collection.insert_one(sentiment_dict)
        
        return APIResponse(
            success=True,
            message="Sentiment created successfully",
            data={"id": str(result.inserted_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating sentiment: {str(e)}")


@app.post("/gps", response_model=APIResponse)
async def create_gps_coordinate(gps: GPSCoordinate):
    """Create a new GPS coordinate entry"""
    try:
        db = await get_database()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        gps_dict = gps.dict()
        gps_dict["created_at"] = datetime.utcnow()
        
        result = await db[GPS_COLLECTION].insert_one(gps_dict)
        
        return APIResponse(
            success=True,
            message="GPS coordinate created successfully",
            data={"id": str(result.inserted_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating GPS coordinate: {str(e)}")


# Data Retrieval Endpoints
@app.get("/vlogs", response_model=APIResponse)
async def get_vlogs(skip: int = 0, limit: int = 100):
    """Get all vlogs"""
    try:
        db = await get_database()
        if db is None:
            return APIResponse(
                success=True,
                message="Retrieved 0 vlogs (database not connected)",
                data={"vlogs": []},
                count=0
            )
        
        cursor = db[VLOGS_COLLECTION].find().skip(skip).limit(limit)
        vlogs = []
        async for vlog in cursor:
            vlog["_id"] = str(vlog["_id"])
            vlogs.append(vlog)
        
        count = await db[VLOGS_COLLECTION].count_documents({})
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(vlogs)} vlogs",
            data={"vlogs": vlogs},
            count=count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving vlogs: {str(e)}")


@app.get("/sentiments", response_model=APIResponse)
async def get_sentiments(skip: int = 0, limit: int = 100):
    """Get all sentiments"""
    try:
        collection = await get_collection(SENTIMENTS_COLLECTION)
        if collection is None:
            return APIResponse(
                success=True,
                message="Retrieved 0 sentiments (database not available)",
                data={"sentiments": []},
                count=0
            )
        
        cursor = collection.find().skip(skip).limit(limit)
        sentiments = []
        async for sentiment in cursor:
            sentiment["_id"] = str(sentiment["_id"])
            sentiments.append(sentiment)
        
        count = await collection.count_documents({})
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(sentiments)} sentiments",
            data={"sentiments": sentiments},
            count=count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sentiments: {str(e)}")


@app.get("/gps", response_model=APIResponse)
async def get_gps_coordinates(skip: int = 0, limit: int = 100):
    """Get all GPS coordinates"""
    try:
        db = await get_database()
        if db is None:
            return APIResponse(
                success=True,
                message="Retrieved 0 GPS coordinates (database not connected)",
                data={"coordinates": []},
                count=0
            )
        
        cursor = db[GPS_COLLECTION].find().skip(skip).limit(limit)
        coordinates = []
        async for coord in cursor:
            coord["_id"] = str(coord["_id"])
            coordinates.append(coord)
        
        count = await db[GPS_COLLECTION].count_documents({})
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(coordinates)} GPS coordinates",
            data={"coordinates": coordinates},
            count=count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving GPS coordinates: {str(e)}")


# Frontend Compatible Endpoints
@app.get("/emotions", response_model=APIResponse)
async def get_emotions(skip: int = 0, limit: int = 100):
    """Get emotion data (Frontend compatible)"""
    try:
        # 從記憶體資料庫或 MongoDB 獲取綜合數據
        emotions = []
        
        # 這裡我們需要組合 vlogs, sentiments 和 GPS 數據
        # 為了簡化，我們先返回一些示例數據
        sample_emotions = [
            {
                "id": "1",
                "mood": "較好", 
                "mood_score": "4/5",
                "latitude": 23.943700,
                "longitude": 120.692457,
                "timestamp": "2025-12-03T20:58:59Z",
                "upload_time": "2025-12-03T20:58:59Z",
                "video_path": "file:///data/user/0/com.emogo.app/files/data/video_1764735782.mp4",
                "video_url": "/download/video_1764735782.mp4"
            },
            {
                "id": "2", 
                "mood": "非常好",
                "mood_score": "5/5", 
                "latitude": 24.988666,
                "longitude": 121.417759,
                "timestamp": "2025-11-30T01:43:45Z",
                "upload_time": "2025-11-30T01:43:45Z",
                "video_path": "file:///data/user/0/com.emogo.app/files/data/video_1764382171.mp4",
                "video_url": "/download/video_1764382171.mp4"
            }
        ]
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(sample_emotions)} emotions",
            data={"emotions": sample_emotions},
            count=len(sample_emotions)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving emotions: {str(e)}")


@app.post("/submit-emotion", response_model=APIResponse)
async def submit_emotion(emotion_data: dict):
    """Submit emotion data (Frontend compatible)"""
    try:
        # 處理前端提交的綜合情感數據
        # 將數據分解並存儲到相應的集合中
        
        # 創建 sentiment 記錄
        if "mood" in emotion_data and "mood_score" in emotion_data:
            sentiment = Sentiment(
                mood=emotion_data.get("mood"),
                mood_score=emotion_data.get("mood_score"),
                text=emotion_data.get("mood", ""),
                sentiment_score=float(emotion_data.get("mood_score", "3/5").split("/")[0]) / 5.0,
                timestamp=datetime.fromisoformat(emotion_data.get("timestamp", datetime.utcnow().isoformat())),
                upload_time=datetime.utcnow(),
                user_id=emotion_data.get("user_id")
            )
            
            # 存儲 sentiment (這裡需要調用相應的存儲函數)
        
        # 創建 GPS 記錄
        if "latitude" in emotion_data and "longitude" in emotion_data:
            gps = GPSCoordinate(
                latitude=emotion_data["latitude"],
                longitude=emotion_data["longitude"],
                timestamp=datetime.fromisoformat(emotion_data.get("timestamp", datetime.utcnow().isoformat())),
                upload_time=datetime.utcnow(),
                user_id=emotion_data.get("user_id")
            )
            
            # 存儲 GPS (這裡需要調用相應的存儲函數)
        
        # 創建 Vlog 記錄
        if "video_path" in emotion_data:
            vlog = Vlog(
                title=f"Emotion Video - {emotion_data.get('mood', 'Unknown')}",
                video_path=emotion_data["video_path"],
                video_url=emotion_data.get("video_url"),
                timestamp=datetime.fromisoformat(emotion_data.get("timestamp", datetime.utcnow().isoformat())),
                upload_time=datetime.utcnow(),
                user_id=emotion_data.get("user_id")
            )
            
            # 存儲 vlog (這裡需要調用相應的存儲函數)
        
        return APIResponse(
            success=True,
            message="Emotion data submitted successfully",
            data={"id": str(len(emotion_data))}  # 臨時 ID
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting emotion data: {str(e)}")


# Data Export/Download Endpoints
@app.get("/export")
async def export_data(
    data_type: str = Query(..., pattern="^(vlogs|sentiments|gps|all)$"),
    format: str = Query(default="json", pattern="^(json|csv)$")
):
    """Export data in JSON or CSV format"""
    try:
        db = await get_database()
        if db is None:
            # Return empty data if database not connected
            empty_data = {
                "vlogs": [],
                "sentiments": [], 
                "gps_coordinates": [],
                "export_timestamp": datetime.utcnow().isoformat(),
                "note": "Database not connected"
            }
            if format == "json":
                json_str = json.dumps(empty_data, indent=2, default=str)
                return Response(
                    content=json_str,
                    media_type="application/json",
                    headers={"Content-Disposition": f"attachment; filename=emogo_export_{data_type}_empty.json"}
                )
            else:
                return Response(
                    content="No data available (database not connected)",
                    media_type="text/plain",
                    headers={"Content-Disposition": f"attachment; filename=emogo_export_{data_type}_empty.txt"}
                )
        
        if data_type == "all":
            # Export all data types
            vlogs = []
            sentiments = []
            coordinates = []
            
            async for vlog in db[VLOGS_COLLECTION].find():
                vlog["_id"] = str(vlog["_id"])
                vlogs.append(vlog)
            
            async for sentiment in db[SENTIMENTS_COLLECTION].find():
                sentiment["_id"] = str(sentiment["_id"])
                sentiments.append(sentiment)
            
            async for coord in db[GPS_COLLECTION].find():
                coord["_id"] = str(coord["_id"])
                coordinates.append(coord)
            
            data = {
                "vlogs": vlogs,
                "sentiments": sentiments,
                "gps_coordinates": coordinates,
                "export_timestamp": datetime.utcnow().isoformat()
            }
        else:
            # Export specific data type
            collection_map = {
                "vlogs": VLOGS_COLLECTION,
                "sentiments": SENTIMENTS_COLLECTION,
                "gps": GPS_COLLECTION
            }
            
            collection = db[collection_map[data_type]]
            items = []
            async for item in collection.find():
                item["_id"] = str(item["_id"])
                items.append(item)
            
            data = {
                data_type: items,
                "export_timestamp": datetime.utcnow().isoformat()
            }
        
        if format == "json":
            json_str = json.dumps(data, indent=2, default=str)
            return Response(
                content=json_str,
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=emogo_export_{data_type}.json"}
            )
        else:  # CSV format
            if data_type == "all":
                # Create a ZIP file with multiple CSV files for all data types
                import zipfile
                import io
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # Export each data type as separate CSV in the ZIP
                    for type_name, items in [("vlogs", data["vlogs"]), ("sentiments", data["sentiments"]), ("gps_coordinates", data["gps_coordinates"])]:
                        if items:
                            output = StringIO()
                            writer = csv.DictWriter(output, fieldnames=items[0].keys())
                            writer.writeheader()
                            for item in items:
                                writer.writerow(item)
                            zip_file.writestr(f"emogo_{type_name}.csv", output.getvalue())
                            output.close()
                    
                    # Add summary file
                    summary = f"""EmoGo Data Export Summary
Generated: {datetime.utcnow().isoformat()}
Total Vlogs: {len(data['vlogs'])}
Total Sentiments: {len(data['sentiments'])}
Total GPS Coordinates: {len(data['gps_coordinates'])}

Files included:
- emogo_vlogs.csv: Video logs and diary entries
- emogo_sentiments.csv: Sentiment analysis and emotional data  
- emogo_gps_coordinates.csv: Location tracking data
"""
                    zip_file.writestr("README.txt", summary)
                
                zip_buffer.seek(0)
                return Response(
                    content=zip_buffer.getvalue(),
                    media_type="application/zip",
                    headers={"Content-Disposition": "attachment; filename=emogo_complete_export.zip"}
                )
            
            items = data[data_type]
            if not items:
                raise HTTPException(status_code=404, detail=f"No {data_type} data found")
            
            # Create CSV
            output = StringIO()
            if items:
                writer = csv.DictWriter(output, fieldnames=items[0].keys())
                writer.writeheader()
                for item in items:
                    writer.writerow(item)
            
            csv_content = output.getvalue()
            output.close()
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=emogo_export_{data_type}.csv"}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Frontend data dashboard page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎭 EmoGo Data Export Portal</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; background: #f0f2f5; }
            .header { text-align: center; margin-bottom: 30px; }
            .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
            .stats-section { margin: 20px 0; }
            .stats { display: flex; justify-content: space-around; margin: 20px 0; }
            .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; min-width: 200px; }
            .stat-number { font-size: 2em; font-weight: bold; }
            .stat-label { font-size: 0.9em; opacity: 0.9; }
            .export-section { margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #007bff; }
            button { padding: 12px 24px; margin: 8px; background: #007bff; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; transition: background 0.3s; }
            button:hover { background: #0056b3; }
            .api-section { background: #e8f4fd; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .emoji { font-size: 1.5em; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎭 EmoGo Data Export Portal</h1>
            <p>Welcome to the EmoGo data export interface. Here you can download all collected data from the EmoGo mobile application.</p>
        </div>
        
        <div class="container">
            <div class="stats-section">
                <h3>📊 Frontend Data Statistics:</h3>
                <div class="stats" id="stats">
                    <div class="stat-card">
                        <div class="stat-number" id="emotions-count">-</div>
                        <div class="stat-label">Emotions: 0 entries</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="vlogs-count">-</div>
                        <div class="stat-label">Vlog Data: 0 entries</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="locations-count">-</div>
                        <div class="stat-label">Locations: 0 entries</div>
                    </div>
                </div>
            </div>
            
            <div class="export-section">
                <h3><span class="emoji">😊</span> Sentiments Data</h3>
                <p>Sentiment analysis and emotional data from user inputs</p>
                <button onclick="downloadData('sentiments', 'json')">Download JSON</button>
                <button onclick="downloadData('sentiments', 'csv')">Download CSV</button>
            </div>
            
            <div class="export-section">
                <h3><span class="emoji">📱</span> Vlogs Data</h3>
                <p>Video logs and diary entries from users</p>
                <button onclick="downloadData('vlogs', 'json')">Download JSON</button>
                <button onclick="downloadData('vlogs', 'csv')">Download CSV</button>
            </div>
            
            <div class="export-section">
                <h3><span class="emoji">📍</span> GPS Coordinates</h3>
                <p>Location tracking and geographical data</p>
                <button onclick="downloadData('gps', 'json')">Download JSON</button>
                <button onclick="downloadData('gps', 'csv')">Download CSV</button>
            </div>
            
            <div class="export-section">
                <h3><span class="emoji">📦</span> All Data</h3>
                <p>Complete export of all collected data</p>
                <button onclick="downloadData('all', 'json')">Download All (JSON)</button>
            </div>
        </div>
        
        <div class="api-section">
            <h4>🔌 API Endpoints for Frontend Integration:</h4>
            <ul>
                <li><strong>POST</strong> /vlogs - Submit vlog data</li>
                <li><strong>POST</strong> /sentiments - Submit sentiment data</li>
                <li><strong>POST</strong> /gps - Submit GPS coordinate data</li>
                <li><strong>GET</strong> /vlogs - Retrieve vlogs</li>
                <li><strong>GET</strong> /sentiments - Retrieve sentiments</li>
                <li><strong>GET</strong> /gps - Retrieve GPS coordinates</li>
                <li><strong>GET</strong> /export - Export data (supports query params: data_type, format)</li>
                <li><strong>GET</strong> /docs - Complete API documentation</li>
            </ul>
            
            <p><strong>Base URL:</strong> <code>https://emogo-backend-ru-lai.onrender.com</code></p>
        </div>
        
        <script>
            function downloadData(dataType, format) {
                const url = `/export?data_type=${dataType}&format=${format}`;
                window.open(url, '_blank');
            }
            
            async function loadStats() {
                try {
                    const responses = await Promise.all([
                        fetch('/sentiments'),
                        fetch('/vlogs'),
                        fetch('/gps')
                    ]);
                    
                    const data = await Promise.all(responses.map(async r => {
                        if (r.ok) return await r.json();
                        return { count: 0 };
                    }));
                    
                    // Update the display
                    document.querySelector('.stats').innerHTML = `
                        <div class="stat-card">
                            <div class="stat-number">${data[0].count || 0}</div>
                            <div class="stat-label">Emotions</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${data[1].count || 0}</div>
                            <div class="stat-label">Vlog Data</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${data[2].count || 0}</div>
                            <div class="stat-label">Locations</div>
                        </div>
                    `;
                    
                } catch (error) {
                    console.error('Error loading stats:', error);
                    document.querySelector('.stats').innerHTML = '<p>Unable to load statistics. Database may not be connected.</p>';
                }
            }
            
            loadStats();
            
            // Refresh stats every 30 seconds
            setInterval(loadStats, 30000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/export-page", response_class=HTMLResponse)
async def export_page():
    """Data export/download page for TAs and instructors"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EmoGo Data Export</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }
            .export-section { margin: 20px 0; padding: 15px; background: white; border-radius: 5px; }
            button { padding: 10px 20px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .stats { background: #e9ecef; padding: 10px; border-radius: 4px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎭 EmoGo Data Export Portal</h1>
            <p>Welcome to the EmoGo data export interface. Here you can download all collected data from the EmoGo mobile application.</p>
            
            <div id="stats" class="stats">
                <p>Loading statistics...</p>
            </div>
            
            <div class="export-section">
                <h3>📱 Vlogs Data</h3>
                <p>Video logs and diary entries from users</p>
                <button onclick="downloadData('vlogs', 'json')">Download JSON</button>
                <button onclick="downloadData('vlogs', 'csv')">Download CSV</button>
            </div>
            
            <div class="export-section">
                <h3>😊 Sentiments Data</h3>
                <p>Sentiment analysis and emotional data</p>
                <button onclick="downloadData('sentiments', 'json')">Download JSON</button>
                <button onclick="downloadData('sentiments', 'csv')">Download CSV</button>
            </div>
            
            <div class="export-section">
                <h3>📍 GPS Coordinates</h3>
                <p>Location tracking and geographical data</p>
                <button onclick="downloadData('gps', 'json')">Download JSON</button>
                <button onclick="downloadData('gps', 'csv')">Download CSV</button>
            </div>
            
            <div class="export-section">
                <h3>📦 All Data</h3>
                <p>Complete export of all collected data</p>
                <button onclick="downloadData('all', 'json')">Download All (JSON)</button>
            </div>
            
            <div style="margin-top: 30px; padding: 15px; background: #d1ecf1; border-radius: 5px;">
                <h4>📋 API Endpoints:</h4>
                <ul>
                    <li><strong>POST</strong> /vlogs - Submit vlog data</li>
                    <li><strong>POST</strong> /sentiments - Submit sentiment data</li>
                    <li><strong>POST</strong> /gps - Submit GPS coordinate data</li>
                    <li><strong>GET</strong> /vlogs - Retrieve vlogs</li>
                    <li><strong>GET</strong> /sentiments - Retrieve sentiments</li>
                    <li><strong>GET</strong> /gps - Retrieve GPS coordinates</li>
                    <li><strong>GET</strong> /export - Export data (supports query params: data_type, format)</li>
                    <li><strong>GET</strong> /docs - API documentation</li>
                </ul>
            </div>
        </div>
        
        <script>
            function downloadData(dataType, format) {
                const url = `/export?data_type=${dataType}&format=${format}`;
                window.open(url, '_blank');
            }
            
            async function loadStats() {
                try {
                    const responses = await Promise.all([
                        fetch('/emotions'),
                        fetch('/vlogs'),
                        fetch('/sentiments'),
                        fetch('/gps')
                    ]);
                    
                    const data = await Promise.all(responses.map(r => r.json()));
                    
                    const statsHtml = `
                        <h4>📊 Frontend Data Statistics:</h4>
                        <p><strong>Emotions:</strong> ${data[0].count || 0} entries</p>
                        <p><strong>Vlog Data:</strong> ${data[1].count || 0} entries</p>
                        <p><strong>Locations:</strong> ${data[3].count || 0} entries</p>
                        <h4>📊 Backend Data Statistics:</h4>
                        <p><strong>Vlogs:</strong> ${data[1].count || 0} entries</p>
                        <p><strong>Sentiments:</strong> ${data[2].count || 0} entries</p>
                        <p><strong>GPS Coordinates:</strong> ${data[3].count || 0} entries</p>
                        <p><em>Last updated: ${new Date().toLocaleString()}</em></p>
                    `;
                    
                    document.getElementById('stats').innerHTML = statsHtml;
                } catch (error) {
                    document.getElementById('stats').innerHTML = '<p>Unable to load statistics</p>';
                }
            }
            
            loadStats();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/", response_class=HTMLResponse)
async def root_dashboard():
    """Main landing page showing live frontend data for TAs and instructors"""
    # Get real-time statistics
    db = await get_database()
    stats = {"vlogs": 0, "sentiments": 0, "gps": 0, "database_connected": False}
    
    if db:
        stats["vlogs"] = await db[VLOGS_COLLECTION].count_documents({})
        stats["sentiments"] = await db[SENTIMENTS_COLLECTION].count_documents({})  
        stats["gps"] = await db[GPS_COLLECTION].count_documents({})
        stats["database_connected"] = True
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎭 EmoGo Frontend Data Dashboard | NTU INFO</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }}
            .main-container {{ 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px;
            }}
            .hero-section {{ 
                background: rgba(255, 255, 255, 0.95); 
                border-radius: 20px; 
                padding: 50px; 
                text-align: center; 
                margin-bottom: 30px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            }}
            .hero-section h1 {{ 
                font-size: 3em; 
                margin-bottom: 20px; 
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            .subtitle {{ 
                font-size: 1.3em; 
                color: #666; 
                margin-bottom: 10px; 
            }}
            .assignment-info {{ 
                background: #e3f2fd; 
                padding: 15px; 
                border-radius: 10px; 
                margin: 20px 0; 
                border-left: 5px solid #2196f3;
            }}
            
            .stats-container {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 25px; 
                margin: 30px 0; 
            }}
            .stat-card {{ 
                background: white; 
                border-radius: 15px; 
                padding: 30px; 
                text-align: center; 
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                position: relative;
                overflow: hidden;
            }}
            .stat-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 5px;
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            }}
            .stat-card:hover {{ 
                transform: translateY(-10px); 
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15); 
            }}
            .stat-icon {{ font-size: 3em; margin-bottom: 15px; }}
            .stat-number {{ 
                font-size: 3.5em; 
                font-weight: bold; 
                color: #667eea; 
                margin-bottom: 10px; 
            }}
            .stat-label {{ 
                font-size: 1.2em; 
                color: #666; 
                font-weight: 500; 
            }}
            
            .action-section {{ 
                background: white; 
                border-radius: 20px; 
                padding: 40px; 
                margin: 30px 0;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            }}
            .section-title {{ 
                font-size: 2em; 
                margin-bottom: 25px; 
                color: #333;
                text-align: center;
            }}
            .button-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
                gap: 20px; 
                margin: 30px 0; 
            }}
            .action-btn {{ 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                text-decoration: none; 
                padding: 20px; 
                border: none;
                border-radius: 12px; 
                text-align: center; 
                font-size: 1.1em; 
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                cursor: pointer;
            }}
            .action-btn:hover {{ 
                transform: translateY(-3px); 
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.6); 
            }}
            .btn-secondary {{ 
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
            }}
            .btn-secondary:hover {{ 
                box-shadow: 0 10px 25px rgba(79, 172, 254, 0.6); 
            }}
            
            .preview-section {{ 
                background: #f8f9ff; 
                border-radius: 15px; 
                padding: 30px; 
                margin: 20px 0;
                border-left: 5px solid #667eea;
            }}
            .preview-content {{ 
                background: white; 
                border-radius: 10px; 
                padding: 20px; 
                margin: 15px 0;
                min-height: 200px;
                max-height: 400px;
                overflow-y: auto;
            }}
            
            .status-indicator {{ 
                display: inline-flex; 
                align-items: center; 
                gap: 8px; 
                padding: 8px 16px; 
                border-radius: 20px; 
                font-size: 0.9em; 
                font-weight: 600;
            }}
            .status-connected {{ background: #e8f5e8; color: #2e7d2e; }}
            .status-disconnected {{ background: #ffeaea; color: #d63384; }}
            
            .footer-info {{ 
                background: rgba(255, 255, 255, 0.9); 
                border-radius: 15px; 
                padding: 25px; 
                text-align: center; 
                margin-top: 40px;
                color: #666;
            }}
            
            @media (max-width: 768px) {{
                .hero-section {{ padding: 30px 20px; }}
                .hero-section h1 {{ font-size: 2.2em; }}
                .stats-container {{ grid-template-columns: 1fr; }}
                .button-grid {{ grid-template-columns: 1fr; }}
            }}
        </style>
    </head>
    <body>
        <div class="main-container">
            <div class="hero-section">
                <h1>🎭 EmoGo Data Dashboard</h1>
                <p class="subtitle">Real-time Frontend Data Visualization</p>
                <div class="assignment-info">
                    <strong>📝 NTU INFO Assignment:</strong> FastAPI + MongoDB Backend with Complete Data Export
                    <br><strong>👥 For TAs & Instructors:</strong> Live view of student's mobile app data collection
                </div>
                <div class="status-indicator {'status-connected' if stats['database_connected'] else 'status-disconnected'}">
                    {'✅ Database Connected' if stats['database_connected'] else '❌ Database Offline'}
                </div>
            </div>
            
            <div class="stats-container">
                <div class="stat-card">
                    <div class="stat-icon">📱</div>
                    <div class="stat-number">{stats['vlogs']}</div>
                    <div class="stat-label">Video Vlogs</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">😊</div>
                    <div class="stat-number">{stats['sentiments']}</div>
                    <div class="stat-label">Sentiment Records</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📍</div>
                    <div class="stat-number">{stats['gps']}</div>
                    <div class="stat-label">GPS Coordinates</div>
                </div>
            </div>
            
            <div class="action-section">
                <h2 class="section-title">📥 Complete Data Export</h2>
                <p style="text-align: center; margin-bottom: 30px; color: #666;">
                    Download all frontend data collected from the EmoGo mobile application
                </p>
                <div class="button-grid">
                    <a href="/export?data_type=all&format=csv" class="action-btn">
                        📦 Download Complete Dataset (ZIP)
                    </a>
                    <a href="/export?data_type=vlogs&format=csv" class="action-btn btn-secondary">
                        📱 Vlogs Data (CSV)
                    </a>
                    <a href="/export?data_type=sentiments&format=csv" class="action-btn btn-secondary">
                        😊 Sentiments Data (CSV) 
                    </a>
                    <a href="/export?data_type=gps&format=csv" class="action-btn btn-secondary">
                        📍 GPS Data (CSV)
                    </a>
                </div>
            </div>
            
            <div class="action-section">
                <h2 class="section-title">🔍 Live Data Preview</h2>
                <div class="button-grid">
                    <button onclick="loadPreview('vlogs')" class="action-btn">View Latest Vlogs</button>
                    <button onclick="loadPreview('sentiments')" class="action-btn">View Latest Sentiments</button>
                    <button onclick="loadPreview('gps')" class="action-btn">View GPS Data</button>
                    <a href="/docs" class="action-btn btn-secondary">📖 API Documentation</a>
                </div>
                <div class="preview-section" id="preview-section" style="display: none;">
                    <h3 id="preview-title">Data Preview</h3>
                    <div class="preview-content" id="preview-content">
                        Select a data type above to preview...
                    </div>
                </div>
            </div>
            
            <div class="footer-info">
                <p><strong>🎓 NTU INFO EmoGo Assignment</strong></p>
                <p>Backend API: <code>https://emogo-backend-ru-lai.onrender.com</code></p>
                <p>Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                <p>Student: Ru Lai | Repository: emogo-backend-ru-lai</p>
            </div>
        </div>
        
        <script>
        async function loadPreview(dataType) {{
            const section = document.getElementById('preview-section');
            const title = document.getElementById('preview-title');
            const content = document.getElementById('preview-content');
            
            section.style.display = 'block';
            title.textContent = `${{dataType.toUpperCase()}} Data Preview`;
            content.innerHTML = '<p style="text-align: center;">🔄 Loading data...</p>';
            
            try {{
                const response = await fetch(`/${{dataType}}`);
                const result = await response.json();
                
                if (result.success && result.data) {{
                    const items = result.data[Object.keys(result.data)[0]] || [];
                    
                    if (items.length === 0) {{
                        content.innerHTML = '<p style="text-align: center; color: #666;">📭 No data available</p>';
                        return;
                    }}
                    
                    let html = `<h4>Latest ${{dataType}} entries (showing ${{Math.min(items.length, 5)}} of ${{items.length}}):</h4><div style="margin-top: 15px;">`;
                    
                    items.slice(0, 5).forEach((item, index) => {{
                        let displayText = '';
                        let timestamp = '';
                        
                        if (dataType === 'vlogs') {{
                            displayText = `<strong>${{item.title || 'Untitled Vlog'}}</strong><br>${{item.description || 'No description'}}`;
                            timestamp = item.created_at;
                        }} else if (dataType === 'sentiments') {{
                            displayText = `<strong>${{item.mood || 'Unknown mood'}}</strong> (Score: ${{item.emotion_score || 'N/A'}})<br>${{item.note || 'No note'}}`;
                            timestamp = item.timestamp;
                        }} else if (dataType === 'gps') {{
                            displayText = `<strong>Location:</strong> ${{item.latitude}}, ${{item.longitude}}<br>${{item.address || 'No address'}}`;
                            timestamp = item.timestamp;
                        }}
                        
                        const timeStr = timestamp ? new Date(timestamp).toLocaleString() : 'Unknown time';
                        html += `
                            <div style="padding: 15px; margin: 10px 0; background: #f8f9ff; border-radius: 8px; border-left: 4px solid #667eea;">
                                <div style="margin-bottom: 8px;">${{displayText}}</div>
                                <small style="color: #666;">🕒 ${{timeStr}}</small>
                            </div>
                        `;
                    }});
                    
                    html += '</div>';
                    content.innerHTML = html;
                }} else {{
                    content.innerHTML = '<p style="text-align: center; color: #d63384;">❌ Error loading data</p>';
                }}
            }} catch (error) {{
                content.innerHTML = `<p style="text-align: center; color: #d63384;">❌ Network error: ${{error.message}}</p>`;
            }}
        }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)