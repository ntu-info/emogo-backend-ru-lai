from typing import Optional, List
from datetime import datetime
import json
import csv
from io import StringIO

from fastapi import FastAPI, HTTPException, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse

from models import Vlog, Sentiment, GPSCoordinate, DataExportRequest, APIResponse
from database import (
    connect_to_mongo, 
    close_mongo_connection, 
    get_database,
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
        data={"endpoints": ["/vlogs", "/sentiments", "/gps", "/export"]}
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
        db = await get_database()
        if db is None:
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
        db = await get_database()
        if db is None:
            return APIResponse(
                success=True,
                message="Retrieved 0 sentiments (database not connected)",
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
                        fetch('/vlogs'),
                        fetch('/sentiments'),
                        fetch('/gps')
                    ]);
                    
                    const data = await Promise.all(responses.map(r => r.json()));
                    
                    const statsHtml = `
                        <h4>📊 Data Statistics:</h4>
                        <p><strong>Vlogs:</strong> ${data[0].count || 0} entries</p>
                        <p><strong>Sentiments:</strong> ${data[1].count || 0} entries</p>
                        <p><strong>GPS Coordinates:</strong> ${data[2].count || 0} entries</p>
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