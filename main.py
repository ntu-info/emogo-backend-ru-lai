from typing import Optional, List
from datetime import datetime
import json
import csv
from io import StringIO

from fastapi import FastAPI, HTTPException, Response, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse

from models import (
    Vlog, Sentiment, GPSCoordinate, DataExportRequest, APIResponse,
    EmotionData, VlogData, Location
)
from database import (
    connect_to_mongo, 
    close_mongo_connection, 
    get_database
)

# Collection names
VLOGS_COLLECTION = "vlogs"
SENTIMENTS_COLLECTION = "sentiments"
GPS_COLLECTION = "gps_coordinates"

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
    await connect_to_mongo(app)


@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection(app)


@app.get("/", response_model=APIResponse)
async def root():
    return APIResponse(
        success=True,
        message="Welcome to EmoGo Backend API! Visit /docs for API documentation.",
        data={"endpoints": ["/vlogs", "/sentiments", "/gps", "/export", "/dashboard", "/docs"]}
    )


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Dashboard for TAs and instructors - alternative to /export"""
    return await export_page()


# Frontend-Compatible Data Collection Endpoints
@app.post("/emotions", response_model=APIResponse)
async def create_emotion_data(emotion: EmotionData):
    """Create a new emotion data entry (Frontend compatible)"""
    try:
        db = get_database(app)
        if not db:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        emotion_dict = emotion.dict()
        emotion_dict["created_at"] = datetime.utcnow()
        
        result = await db["emotions"].insert_one(emotion_dict)
        
        return APIResponse(
            success=True,
            message="Emotion data created successfully",
            data={"id": str(result.inserted_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating emotion data: {str(e)}")


@app.post("/vlogs-data", response_model=APIResponse)
async def create_vlog_data(vlog: VlogData):
    """Create a new vlog data entry (Frontend compatible)"""
    try:
        db = get_database(app)
        if not db:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        vlog_dict = vlog.dict()
        vlog_dict["created_at"] = datetime.utcnow()
        
        result = await db["vlogs_data"].insert_one(vlog_dict)
        
        return APIResponse(
            success=True,
            message="Vlog data created successfully",
            data={"id": str(result.inserted_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating vlog data: {str(e)}")


@app.post("/locations", response_model=APIResponse)
async def create_location_data(location: Location):
    """Create a new location data entry"""
    try:
        db = get_database(app)
        if not db:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        location_dict = location.dict()
        location_dict["created_at"] = datetime.utcnow()
        location_dict["timestamp"] = datetime.utcnow().isoformat()
        
        result = await db["locations"].insert_one(location_dict)
        
        return APIResponse(
            success=True,
            message="Location data created successfully",
            data={"id": str(result.inserted_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating location data: {str(e)}")


# Legacy Data Collection Endpoints (for backward compatibility)
@app.post("/vlogs", response_model=APIResponse)
async def create_vlog(vlog: Vlog):
    """Create a new vlog entry"""
    try:
        db = get_database(app)
        if not db:
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
        db = get_database(app)
        if not db:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        sentiment_dict = sentiment.dict()
        sentiment_dict["created_at"] = datetime.utcnow()
        
        result = await db[SENTIMENTS_COLLECTION].insert_one(sentiment_dict)
        
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
        db = get_database(app)
        if not db:
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


# Frontend-Compatible Data Retrieval Endpoints
@app.get("/emotions", response_model=APIResponse)
async def get_emotions(skip: int = 0, limit: int = 100):
    """Get all emotion data (Frontend compatible)"""
    try:
        db = get_database(app)
        if not db:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        cursor = db["emotion_data"].find().skip(skip).limit(limit)
        emotions = []
        async for emotion in cursor:
            emotion["_id"] = str(emotion["_id"])
            emotions.append(emotion)
        
        count = await db["emotion_data"].count_documents({})
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(emotions)} emotions",
            data={"emotions": emotions},
            count=count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving emotions: {str(e)}")


@app.get("/vlogs-data", response_model=APIResponse)
async def get_vlogs_data(skip: int = 0, limit: int = 100):
    """Get all vlog data (Frontend compatible)"""
    try:
        db = get_database(app)
        if not db:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        cursor = db["vlogs_data"].find().skip(skip).limit(limit)
        vlogs = []
        async for vlog in cursor:
            vlog["_id"] = str(vlog["_id"])
            vlogs.append(vlog)
        
        count = await db["vlogs_data"].count_documents({})
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(vlogs)} vlog data entries",
            data={"vlogs": vlogs},
            count=count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving vlog data: {str(e)}")


@app.get("/locations", response_model=APIResponse)
async def get_locations(skip: int = 0, limit: int = 100):
    """Get all location data"""
    try:
        db = get_database(app)
        if not db:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        cursor = db["locations"].find().skip(skip).limit(limit)
        locations = []
        async for location in cursor:
            location["_id"] = str(location["_id"])
            locations.append(location)
        
        count = await db["locations"].count_documents({})
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(locations)} location entries",
            data={"locations": locations},
            count=count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving locations: {str(e)}")


# Legacy Data Retrieval Endpoints (for backward compatibility)
@app.get("/vlogs", response_model=APIResponse)
async def get_vlogs(skip: int = 0, limit: int = 100):
    """Get all vlogs"""
    try:
        db = get_database(app)
        if not db:
            return APIResponse(
                success=False,
                message="Database not connected",
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
        db = get_database(app)
        if not db:
            return APIResponse(
                success=False,
                message="Database not connected",
                data={"sentiments": []},
                count=0
            )
        
        cursor = db[SENTIMENTS_COLLECTION].find().skip(skip).limit(limit)
        sentiments = []
        async for sentiment in cursor:
            sentiment["_id"] = str(sentiment["_id"])
            sentiments.append(sentiment)
        
        count = await db[SENTIMENTS_COLLECTION].count_documents({})
        
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
        db = get_database(app)
        if not db:
            return APIResponse(
                success=False,
                message="Database not connected",
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


# Data Export/Download Endpoints
@app.get("/export")
async def export_data(
    request: Request,
    data_type: Optional[str] = Query(None, pattern="^(vlogs|sentiments|gps|emotions|vlogs-data|locations|all|frontend)$"),
    format: str = Query(default="json", pattern="^(json|csv)$")
):
    """Export data in JSON or CSV format, or show export page"""
    # If no data_type is specified and it's a browser request, show HTML page
    if data_type is None:
        accept_header = request.headers.get("accept", "")
        if "text/html" in accept_header:
            return await export_page()
        # Default to frontend data for API calls without data_type
        data_type = "frontend"
    
    try:
        db = get_database(app)
        if not db:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        if data_type == "all":
            # Export legacy data types
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
        elif data_type == "frontend":
            # Export frontend-compatible data types
            emotions = []
            vlogs_data = []
            locations = []
            
            async for emotion in db["emotions"].find():
                emotion["_id"] = str(emotion["_id"])
                emotions.append(emotion)
            
            async for vlog in db["vlogs_data"].find():
                vlog["_id"] = str(vlog["_id"])
                vlogs_data.append(vlog)
            
            async for location in db["locations"].find():
                location["_id"] = str(location["_id"])
                locations.append(location)
            
            data = {
                "emotionData": emotions,
                "vlogData": vlogs_data,
                "locationData": locations,
                "metadata": {
                    "appName": "EmoGo",
                    "exportDate": datetime.utcnow().isoformat(),
                    "totalRecords": len(emotions) + len(vlogs_data) + len(locations),
                    "emotionRecords": len(emotions),
                    "vlogRecords": len(vlogs_data),
                    "locationRecords": len(locations)
                }
            }
        else:
            # Export specific data type
            collection_map = {
                "vlogs": VLOGS_COLLECTION,
                "sentiments": SENTIMENTS_COLLECTION,
                "gps": GPS_COLLECTION,
                "emotions": "emotions",
                "vlogs-data": "vlogs_data",
                "locations": "locations"
            }
            
            collection_name = collection_map.get(data_type)
            if not collection_name:
                raise HTTPException(status_code=400, detail=f"Invalid data type: {data_type}")
            
            collection = db[collection_name]
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
                raise HTTPException(status_code=400, detail="CSV format not supported for 'all' data type")
            
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


@app.get("/api/export/{data_type}")
async def simple_export_data(data_type: str, format: str = "json"):
    """Simple export data endpoint without complex Query validation"""
    try:
        db = get_database(app)
        if not db:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        # Validate data_type
        valid_types = ["vlogs", "sentiments", "gps", "emotions", "vlogs-data", "locations", "all", "frontend"]
        if data_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid data_type. Must be one of: {valid_types}")
        
        if data_type == "frontend":
            # Export all frontend data types
            emotions = []
            vlogs_data = []
            locations = []
            
            async for emotion in db["emotion_data"].find():
                emotion["_id"] = str(emotion["_id"])
                emotions.append(emotion)
            
            async for vlog in db["vlog_data"].find():
                vlog["_id"] = str(vlog["_id"])
                vlogs_data.append(vlog)
                
            async for location in db["locations"].find():
                location["_id"] = str(location["_id"])
                locations.append(location)
            
            return {
                "success": True,
                "data": {
                    "emotions": emotions,
                    "vlogs_data": vlogs_data,
                    "locations": locations
                },
                "count": {
                    "emotions": len(emotions),
                    "vlogs_data": len(vlogs_data),
                    "locations": len(locations)
                },
                "export_timestamp": datetime.utcnow().isoformat()
            }
        
        # Handle other data types...
        collection_map = {
            "vlogs": VLOGS_COLLECTION,
            "sentiments": SENTIMENTS_COLLECTION,
            "gps": GPS_COLLECTION,
            "emotions": "emotion_data",
            "vlogs-data": "vlog_data",
            "locations": "locations"
        }
        
        collection_name = collection_map.get(data_type)
        if not collection_name:
            raise HTTPException(status_code=400, detail="Invalid data type")
        
        data = []
        async for doc in db[collection_name].find():
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        
        return {
            "success": True,
            "data": data,
            "count": len(data),
            "export_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")


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
                <h3>🎭 Frontend Data (EmoGo Compatible)</h3>
                <p>Complete EmoGo app data in frontend format</p>
                <button onclick="downloadData('frontend', 'json')">Download Frontend Data (JSON)</button>
            </div>
            
            <div class="export-section">
                <h3>😊 Emotion Data</h3>
                <p>User emotion tracking data with mood scales</p>
                <button onclick="downloadData('emotions', 'json')">Download JSON</button>
                <button onclick="downloadData('emotions', 'csv')">Download CSV</button>
            </div>
            
            <div class="export-section">
                <h3>📱 Vlog Data</h3>
                <p>Video logs with mood and location information</p>
                <button onclick="downloadData('vlogs-data', 'json')">Download JSON</button>
                <button onclick="downloadData('vlogs-data', 'csv')">Download CSV</button>
            </div>
            
            <div class="export-section">
                <h3>📍 Location Data</h3>
                <p>GPS coordinates and location tracking</p>
                <button onclick="downloadData('locations', 'json')">Download JSON</button>
                <button onclick="downloadData('locations', 'csv')">Download CSV</button>
            </div>
            
            <hr style="margin: 20px 0;">
            <h4 style="color: #666;">Legacy Data Formats:</h4>
            
            <div class="export-section">
                <h3>📱 Vlogs (Legacy)</h3>
                <p>Video logs and diary entries from users</p>
                <button onclick="downloadData('vlogs', 'json')">Download JSON</button>
                <button onclick="downloadData('vlogs', 'csv')">Download CSV</button>
            </div>
            
            <div class="export-section">
                <h3>😊 Sentiments (Legacy)</h3>
                <p>Sentiment analysis and emotional data</p>
                <button onclick="downloadData('sentiments', 'json')">Download JSON</button>
                <button onclick="downloadData('sentiments', 'csv')">Download CSV</button>
            </div>
            
            <div class="export-section">
                <h3>📍 GPS Coordinates (Legacy)</h3>
                <p>Location tracking and geographical data</p>
                <button onclick="downloadData('gps', 'json')">Download JSON</button>
                <button onclick="downloadData('gps', 'csv')">Download CSV</button>
            </div>
            
            <div class="export-section">
                <h3>📦 All Legacy Data</h3>
                <p>Complete export of legacy format data</p>
                <button onclick="downloadData('all', 'json')">Download All (JSON)</button>
            </div>
            
            <div style="margin-top: 30px; padding: 15px; background: #d1ecf1; border-radius: 5px;">
                <h4>📋 Frontend-Compatible API Endpoints:</h4>
                <ul>
                    <li><strong>POST</strong> /emotions - Submit emotion data (Frontend format)</li>
                    <li><strong>POST</strong> /vlogs-data - Submit vlog data (Frontend format)</li>
                    <li><strong>POST</strong> /locations - Submit location data</li>
                    <li><strong>GET</strong> /emotions - Retrieve emotion data</li>
                    <li><strong>GET</strong> /vlogs-data - Retrieve vlog data</li>
                    <li><strong>GET</strong> /locations - Retrieve location data</li>
                </ul>
                <h4>📋 Legacy API Endpoints:</h4>
                <ul>
                    <li><strong>POST</strong> /vlogs - Submit vlog data (Legacy)</li>
                    <li><strong>POST</strong> /sentiments - Submit sentiment data (Legacy)</li>
                    <li><strong>POST</strong> /gps - Submit GPS coordinate data (Legacy)</li>
                    <li><strong>GET</strong> /vlogs - Retrieve vlogs (Legacy)</li>
                    <li><strong>GET</strong> /sentiments - Retrieve sentiments (Legacy)</li>
                    <li><strong>GET</strong> /gps - Retrieve GPS coordinates (Legacy)</li>
                    <li><strong>GET</strong> /export - Export data (supports: emotions, vlogs-data, locations, frontend, all, legacy types)</li>
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
                        fetch('/vlogs-data'),
                        fetch('/locations'),
                        fetch('/vlogs'),
                        fetch('/sentiments'),
                        fetch('/gps')
                    ]);
                    
                    const data = await Promise.all(responses.map(r => r.json()));
                    
                    const statsHtml = `
                        <h4>📊 Frontend Data Statistics:</h4>
                        <p><strong>Emotions:</strong> ${data[0].count || 0} entries</p>
                        <p><strong>Vlog Data:</strong> ${data[1].count || 0} entries</p>
                        <p><strong>Locations:</strong> ${data[2].count || 0} entries</p>
                        <hr>
                        <h4>📊 Legacy Data Statistics:</h4>
                        <p><strong>Vlogs (Legacy):</strong> ${data[3].count || 0} entries</p>
                        <p><strong>Sentiments (Legacy):</strong> ${data[4].count || 0} entries</p>
                        <p><strong>GPS Coordinates (Legacy):</strong> ${data[5].count || 0} entries</p>
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