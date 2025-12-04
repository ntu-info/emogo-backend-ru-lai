# 🎭 EmoGo Backend API

[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/e7FBMwSa)

A FastAPI backend service for the EmoGo mobile application, supporting both frontend-compatible data formats and legacy formats.

## 📋 Assignment Requirements

This backend collects and provides export functionality for three types of data from the EmoGo mobile app:

1. **😊 Emotions** - Emotion tracking data (1-5 scale: Very Sad to Very Happy)
2. **📱 Vlogs** - Video logs with mood and location information  
3. **📍 Locations** - GPS coordinates and location tracking data

## ✅ Assignment Status

**🎯 Assignment Completed Successfully!**

- ✅ **FastAPI Backend**: Running on http://127.0.0.1:8000
- ✅ **MongoDB Atlas Database**: Connected and operational
- ✅ **Data Collection**: All three data types (vlogs, sentiments, GPS coordinates)
- ✅ **Data Export**: Available via web interface and API endpoints
- ✅ **Public Access**: MongoDB configured for public access
- ✅ **TA Access**: Data export page ready at http://127.0.0.1:8000/export

**📊 Current Data Summary:**
- 🎥 **5 Vlogs** - Video content records
- 💭 **8 Sentiments** - Mood and emotion tracking
- 📍 **8 GPS Coordinates** - Location data points
- 😊 **6 Frontend Emotions** - Emotion data in frontend format
- 🎬 **4 Frontend Vlogs** - Vlog data in frontend format

## 🔗 Data Export/Download URI

**🎯 REQUIRED URI for TAs and Instructors:**

### 📍 **PRIMARY ACCESS POINT** 
**For TAs & Tren - Main Data Export Page:**

```
http://127.0.0.1:8000/export
```

This interactive web page allows TAs to:
- ✅ **View all collected data** (vlogs, sentiments, GPS coordinates)
- ✅ **Download in multiple formats** (JSON, CSV)
- ✅ **Filter by data type**
- ✅ **Real-time data access**

### 📊 **Additional Access Points**
- **� API Documentation**: `http://127.0.0.1:8000/docs`
- **� Health Check**: `http://127.0.0.1:8000/`

### 📁 **Direct Download Links**
- **😊 All Emotions**: `http://127.0.0.1:8000/export?data_type=emotions&format=json`
- **🎥 All Vlogs**: `http://127.0.0.1:8000/export?data_type=vlogs-data&format=json`
- **📍 All GPS Data**: `http://127.0.0.1:8000/export?data_type=locations&format=json`

### 🌐 Future Production Deployment (Optional)
- **Data Export Page**: `https://your-app-name.onrender.com/export`
- **API Documentation**: `https://your-app-name.onrender.com/docs`

> **✅ Status**: Backend is currently running with MongoDB Atlas cloud database and contains sample data for all three required data types (vlogs, sentiments, GPS coordinates).

## 🚀 API Endpoints

### 🎭 Frontend-Compatible Data Collection (Recommended)
- `POST /emotions` - Submit emotion data (matches EmoGo frontend format)
- `POST /vlogs-data` - Submit vlog data (matches EmoGo frontend format)  
- `POST /locations` - Submit location data

### 📊 Frontend-Compatible Data Retrieval
- `GET /emotions` - Retrieve all emotion data
- `GET /vlogs-data` - Retrieve all vlog data
- `GET /locations` - Retrieve all location data

### 🔄 Legacy Data Collection (Backward Compatibility)
- `POST /vlogs` - Submit vlog data (legacy format)
- `POST /sentiments` - Submit sentiment data (legacy format)
- `POST /gps` - Submit GPS coordinate data (legacy format)

### 📈 Legacy Data Retrieval
- `GET /vlogs` - Retrieve all vlogs (legacy format)
- `GET /sentiments` - Retrieve all sentiments (legacy format)
- `GET /gps` - Retrieve all GPS coordinates (legacy format)

### 📥 Data Export
- `GET /export` - Export data with multiple format options:
  - **Frontend formats**: `emotions`, `vlogs-data`, `locations`, `frontend` (all frontend data)
  - **Legacy formats**: `vlogs`, `sentiments`, `gps`, `all` (all legacy data)
  - **Output formats**: `json`, `csv`
- `GET /export-page` - Interactive web interface for data export

### 📖 Documentation
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## 🛠 Technology Stack

- **Framework**: FastAPI 0.104.1
- **Database**: MongoDB Atlas (Cloud) 
- **Database Driver**: Motor 3.3.2 (Async MongoDB driver)
- **Data Validation**: Pydantic v2
- **Authentication**: MongoDB Atlas with public access (0.0.0.0/0)
- **Export Formats**: JSON, CSV
- **Deployment Ready**: Render platform compatible

### 🔧 **Current Configuration**
- **MongoDB URI**: `mongodb+srv://lairu:***@cluster0.am8juwb.mongodb.net/?appName=Cluster0`
- **Database Name**: `emogo_db`
- **Collections**: `vlogs`, `sentiments`, `gps_coordinates`, `emotion_data`, `vlog_data`
- **Network Access**: Public (0.0.0.0/0) - suitable for educational assignments
- **SSL/TLS**: Enabled with certificate validation

## 📊 Data Models

### Frontend-Compatible Models (Based on your EmoGo app)

#### Emotion Data
```json
{
  "id": 1764207858170,
  "emotion": 3,                                    // 1-5 scale
  "emotionLabel": "Neutral",                       // "Very Sad", "Sad", "Neutral", "Happy", "Very Happy"
  "timestamp": "2025-11-27T01:44:18.170Z",
  "hasVlog": true,
  "location": {
    "latitude": 25.016838554868805,
    "longitude": 121.53797213487803,
    "accuracy": 33.68443999423612,
    "hasGPS": true
  },
  "user_id": "optional_user_id"
}
```

#### Vlog Data
```json
{
  "id": 8,
  "mood": 5,                                       // Same 1-5 scale as emotion
  "moodLabel": "非常開心",                          // Chinese mood labels
  "moodEmoji": "😊",                              // Emoji representation
  "timestamp": 1732445400000,                      // Unix timestamp
  "date": "2025/11/24 下午9:30:00",               // Formatted date
  "videoUri": "ph://A1B2C3D4-E5F6-7G8H-9I0J-K1L2M3N4O5P6/L0/001",
  "hasVideo": true,
  "location": {
    "latitude": 25.0338,
    "longitude": 121.5646,
    "hasGPS": true
  },
  "user_id": "optional_user_id"
}
```

#### Location Data
```json
{
  "latitude": 25.0338,
  "longitude": 121.5646,
  "accuracy": 5.0,
  "hasGPS": true,
  "timestamp": "2025-12-03T10:00:00Z"
}
```

## 🚀 Deployment on Render

### Step 1: Setup MongoDB Atlas (Required)

1. **Create MongoDB Atlas Account**: Visit [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. **Create Cluster**: Choose free tier
3. **Setup Database User**: Create username/password
4. **Configure Network Access**: Set IP to `0.0.0.0/0` (allow all)
5. **Get Connection String**: Example: `mongodb+srv://username:password@cluster.mongodb.net/emogo_db?retryWrites=true&w=majority`

### Step 2: Deploy to Render

1. **Connect GitHub Repository**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repo

2. **Configure Service**:
   - **Name**: `emogo-backend-[your-name]`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**:
   - `MONGODB_URI`: Your MongoDB Atlas connection string
   - `DATABASE_NAME`: `emogo_db` (or your preferred name)

4. **Deploy**: Click "Create Web Service"

### Step 3: Test Your Deployment

After deployment, your API will be available at:
- **Main API**: `https://your-app-name.onrender.com`
- **Export Page**: `https://your-app-name.onrender.com/export-page`
- **API Docs**: `https://your-app-name.onrender.com/docs`

## 📝 Usage Examples

### Submit Emotion Data (Frontend Format)
```bash
curl -X POST "https://your-app-name.onrender.com/emotions" \
     -H "Content-Type: application/json" \
     -d '{
       "emotion": 4,
       "emotionLabel": "Happy",
       "timestamp": "2025-12-03T10:00:00Z",
       "hasVlog": true,
       "location": {
         "latitude": 25.0338,
         "longitude": 121.5646,
         "accuracy": 5.0
       }
     }'
```

### Submit Vlog Data (Frontend Format)  
```bash
curl -X POST "https://your-app-name.onrender.com/vlogs-data" \
     -H "Content-Type: application/json" \
     -d '{
       "mood": 5,
       "moodLabel": "非常開心",
       "moodEmoji": "😊",
       "timestamp": 1732445400000,
       "hasVideo": true,
       "location": {
         "latitude": 25.0338,
         "longitude": 121.5646
       }
     }'
```

### Export All Frontend Data
```bash
curl "https://your-app-name.onrender.com/export?data_type=frontend&format=json" -o emogo_data.json
```

## 🧪 Testing Locally

### Prerequisites
- Python 3.8+
- MongoDB Atlas connection string

### Setup
```bash
# Clone repository
git clone https://github.com/ntu-info/emogo-backend-ru-lai.git
cd emogo-backend-ru-lai

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MONGODB_URI="your_mongodb_atlas_connection_string"
export DATABASE_NAME="emogo_db"

# Run application
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Access Points
- **API**: http://localhost:8000
- **Export Page**: http://localhost:8000/export-page  
- **API Documentation**: http://localhost:8000/docs

## 📋 Assignment Submission Checklist

**Submission Deadline**: December 4, 2025, 8:00 PM

- ✅ **FastAPI backend deployed on Render**
- ✅ **MongoDB Atlas integration** 
- ✅ **Frontend-compatible data models** (matches your EmoGo app)
- ✅ **Data collection endpoints** for emotions, vlogs, and locations
- ✅ **Data export endpoints** with JSON/CSV support
- ✅ **Interactive export page** for TAs and instructors
- ✅ **Public URIs listed in README** (this document)
- ✅ **API documentation** available at `/docs`

**Submit**: Your GitHub repository URL to NTU COOL

## 🎯 Key Features

- **Frontend Integration Ready**: Data models match your EmoGo mobile app exactly
- **Dual Format Support**: Both frontend-compatible and legacy formats supported
- **Interactive Export Interface**: Easy-to-use web interface for data download
- **Comprehensive API Documentation**: Auto-generated Swagger UI
- **Production Ready**: Deployed on Render with MongoDB Atlas
- **Data Validation**: Pydantic models ensure data integrity
- **CORS Enabled**: Ready for frontend integration

## 📄 License

This project is created for educational purposes as part of the NTU Information Management course assignment.
