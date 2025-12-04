# 🎭 EmoGo Backend API

[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/e7FBMwSa)

A FastAPI backend service for the EmoGo mobile application, supporting both frontend-compatible data formats and legacy formats.

---

## 🎯 **FOR TAs & INSTRUCTORS - ASSIGNMENT SUBMISSION**

### 📋 **REQUIRED URI for Data Export/Download:**

```
https://emogo-backend-ru-lai.onrender.com/export
```

**This is the main URI where TAs can:**
- ✅ **View all collected data** (vlogs, sentiments, GPS coordinates)  
- ✅ **Download data in JSON/CSV formats**
- ✅ **Access real-time data from MongoDB Atlas**
- ✅ **Evaluate assignment completion**

### 🌐 **Additional Assignment URIs:**
- **API Documentation**: `https://emogo-backend-ru-lai.onrender.com/docs`
- **Health Check**: `https://emogo-backend-ru-lai.onrender.com/`
- **GitHub Repository**: `https://github.com/ntu-info/emogo-backend-ru-lai`

---

## 📋 Assignment Requirements

This backend collects and provides export functionality for three types of data from the EmoGo mobile app:

1. **😊 Emotions** - Emotion tracking data (1-5 scale: Very Sad to Very Happy)
2. **📱 Vlogs** - Video logs with mood and location information  
3. **📍 Locations** - GPS coordinates and location tracking data

## ✅ Assignment Status

**🎯 Assignment Completed Successfully!**

- ✅ **FastAPI Backend**: Deployed on Render Cloud Platform
- ✅ **MongoDB Atlas Database**: Connected and operational  
- ✅ **Data Collection**: All three data types (vlogs, sentiments, GPS coordinates)
- ✅ **Data Export**: Available via public web interface and API endpoints
- ✅ **Public Server**: Accessible from anywhere via HTTPS
- ✅ **TA Access**: **Public data export page ready at `https://emogo-backend-ru-lai.onrender.com/export`**

## 🔗 Data Export/Download URI

### 🎯 **MAIN DATA EXPORT URI** (Required for Assignment)

```
https://emogo-backend-ru-lai.onrender.com/export
```

**This is the primary URI for TAs and instructors to:**
- ✅ **View all collected data** (vlogs, sentiments, GPS coordinates)
- ✅ **Download in multiple formats** (JSON, CSV)  
- ✅ **Filter by data type**
- ✅ **Access real-time data from MongoDB Atlas cloud database**
- ✅ **Evaluate assignment completion**

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
- `GET /export` - Export data with multiple format options
- `GET /export-page` - Interactive web interface for data export

## 🛠 Technology Stack

- **Framework**: FastAPI 0.104.1
- **Database**: MongoDB Atlas (Cloud) 
- **Database Driver**: Motor 3.3.2 (Async MongoDB driver)
- **Data Validation**: Pydantic v2
- **Authentication**: MongoDB Atlas with public access (0.0.0.0/0)
- **Export Formats**: JSON, CSV
- **Deployment**: Render Platform

## ✅ Assignment Completion Checklist

**All requirements fulfilled:**

- ✅ **FastAPI backend deployed on public server** (Render)
- ✅ **MongoDB Atlas integration** with public access
- ✅ **Frontend-compatible data models** (matches EmoGo app)
- ✅ **Data collection endpoints** for emotions, vlogs, and locations
- ✅ **Data export endpoints** with JSON/CSV support
- ✅ **Interactive export page** for TAs and instructors
- ✅ **Public URIs listed in README** (this document)
- ✅ **API documentation** available at `/docs`
- ✅ **Chat conversation log** included (chat.json)
