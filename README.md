# 🎭 EmoGo Backend API Server

[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/e7FBMwSa)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=21924995&assignment_repo_type=AssignmentRepo)

**💡 This is the BACKEND repository for NTU INFO EmoGo Assignment 3**

🚀 **Live Backend**: https://emogo-backend-ru-lai.onrender.com/  
📊 **Database**: MongoDB Atlas (Connected)  
🛠️ **Tech Stack**: FastAPI + MongoDB + Render Deployment

---

## 🎯 Assignment Requirements ✅

**Goal**: Making an EmoGo backend on a public server using FastAPI + MongoDB

**Required**: List the URI of data-exporting/downloading page where TAs & Instructors can see/download all three types of data:

### 📋 Data Types Required (✅ All Present):
1. **📱 Vlogs** - Video logs and diary entries (5 records available)
2. **😊 Sentiments** - Emotional data and mood records (8 records available)  
3. **📍 GPS Coordinates** - Location tracking data (8 coordinates available)

**Time Span**: ✅ Data spans multiple days (Nov 30 - Dec 4, 2024)

---

## 🔗 **REQUIRED URI for TAs and Instructors**

### 🎭 **Main Data Dashboard** (Primary Access Point)
**URI**: `https://emogo-backend-ru-lai.onrender.com/`

**Features**:
- 📊 Real-time data statistics display
- 🔍 Live data preview functionality  
- 📥 One-click download for all data types
- ✅ Database connection status monitoring

### 📦 **Direct Download Links** (Alternative Access)

#### Complete Dataset Downloads:
- **All Data (ZIP)**: https://emogo-backend-ru-lai.onrender.com/export?data_type=all&format=csv
- **All Data (JSON)**: https://emogo-backend-ru-lai.onrender.com/export?data_type=all&format=json

#### Individual Data Type Downloads:
- **📱 Vlogs (CSV)**: https://emogo-backend-ru-lai.onrender.com/export?data_type=vlogs&format=csv
- **😊 Sentiments (CSV)**: https://emogo-backend-ru-lai.onrender.com/export?data_type=sentiments&format=csv  
- **📍 GPS Data (CSV)**: https://emogo-backend-ru-lai.onrender.com/export?data_type=gps&format=csv

### 📖 **API Documentation**
- **Interactive API Docs**: https://emogo-backend-ru-lai.onrender.com/docs
- **Backend Status Check**: https://emogo-backend-ru-lai.onrender.com/status

---

## 🛠️ Technical Implementation

### Backend Architecture
- **Framework**: FastAPI 0.104.1
- **Database**: MongoDB Atlas (Cloud)
- **Driver**: Motor 3.3.2 (Async MongoDB driver)
- **Deployment**: Render (Auto-deploy from GitHub)
- **Data Validation**: Pydantic models

### API Endpoints
```
GET  /                 # Main dashboard (for TAs)
GET  /vlogs            # Retrieve all video logs
GET  /sentiments       # Retrieve all sentiment data
GET  /gps              # Retrieve all GPS coordinates  
GET  /export           # Data export (CSV/JSON/ZIP)
GET  /status           # System status check
GET  /docs             # API documentation
POST /vlogs            # Submit new vlog data
POST /sentiments       # Submit new sentiment data
POST /gps              # Submit new GPS data
```

### Data Models
```python
# Vlog Model
{
  "user_id": "string",
  "title": "string", 
  "description": "string",
  "video_url": "string",
  "duration": "number",
  "created_at": "datetime",
  "tags": ["array"]
}

# Sentiment Model  
{
  "user_id": "string",
  "mood": "string",
  "emotion_score": "number", 
  "note": "string",
  "timestamp": "datetime"
}

# GPS Model
{
  "user_id": "string",
  "latitude": "number",
  "longitude": "number", 
  "address": "string",
  "timestamp": "datetime"
}
```

---

## 📊 Current Data Status

- **Total Vlogs**: 5 entries
- **Total Sentiments**: 8 mood records
- **Total GPS Points**: 8 location records  
- **Database Status**: ✅ Connected to MongoDB Atlas
- **Time Range**: 2024-11-30 to 2024-12-04 (4+ days)
- **Backend Uptime**: 24/7 on Render

---

## 🎓 For TAs and Instructors

**Primary Access**: Visit https://emogo-backend-ru-lai.onrender.com/ to:
1. View live data statistics
2. Preview actual frontend data 
3. Download complete datasets
4. Verify system functionality

**Alternative**: Use direct download links above for immediate CSV/JSON access

**Verification**: Check https://emogo-backend-ru-lai.onrender.com/status for system health

---

**Student**: Ru Lai  
**Repository**: emogo-backend-ru-lai  
**Assignment**: NTU INFO EmoGo Backend (Assignment 3)  
**Submission Date**: December 5, 2024
