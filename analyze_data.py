import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import server_api
import json

async def analyze_data():
    try:
        # 連接資料庫
        uri = os.getenv('MONGODB_URI', 'mongodb+srv://lairu:emogo2025@cluster0.am8juwb.mongodb.net/?appName=Cluster0')
        client = AsyncIOMotorClient(
            uri,
            tls=True,
            tlsAllowInvalidCertificates=True,
            server_api=server_api.ServerApi('1')
        )
        db = client['emogo_db']
        
        print("🔍 **資料來源分析報告**\n")
        
        # 分析 emotion_data
        print("📊 **Emotion Data (前端格式)**:")
        async for doc in db['emotion_data'].find().limit(3):
            print(f"   - UserID: {doc.get('userId', 'N/A')}")
            print(f"   - Timestamp: {doc.get('timestamp', 'N/A')}")
            print(f"   - Emotion: {doc.get('emotion', 'N/A')}")
            print(f"   - Mood: {doc.get('mood', 'N/A')}")
            print(f"   - Location: {doc.get('location', 'N/A')}")
            print()
            
        # 分析 vlog_data
        print("🎬 **Vlog Data (前端格式)**:")
        async for doc in db['vlog_data'].find().limit(2):
            print(f"   - UserID: {doc.get('userId', 'N/A')}")
            print(f"   - Title: {doc.get('title', 'N/A')}")
            print(f"   - Content: {doc.get('content', 'N/A')[:50]}...")
            print(f"   - Mood: {doc.get('mood', 'N/A')}")
            print()
            
        # 分析傳統格式資料
        print("📱 **Legacy Vlogs**:")
        async for doc in db['vlogs'].find().limit(2):
            print(f"   - ID: {doc.get('id', 'N/A')}")
            print(f"   - Title: {doc.get('title', 'N/A')}")
            print(f"   - Content: {doc.get('content', 'N/A')[:50]}...")
            print()
            
        print("😊 **Legacy Sentiments**:")
        async for doc in db['sentiments'].find().limit(2):
            print(f"   - ID: {doc.get('id', 'N/A')}")
            print(f"   - Sentiment: {doc.get('sentiment', 'N/A')}")
            print(f"   - Score: {doc.get('score', 'N/A')}")
            print()
            
        print("📍 **GPS Coordinates**:")
        async for doc in db['gps_coordinates'].find().limit(2):
            print(f"   - ID: {doc.get('id', 'N/A')}")
            print(f"   - Lat: {doc.get('latitude', 'N/A')}")
            print(f"   - Lng: {doc.get('longitude', 'N/A')}")
            print(f"   - Timestamp: {doc.get('timestamp', 'N/A')}")
            print()
            
        # 判斷資料來源
        print("🕵️ **資料來源判斷**:")
        
        # 檢查 emotion_data 的 userId 模式
        emotion_users = []
        async for doc in db['emotion_data'].find({}, {"userId": 1}):
            emotion_users.append(doc.get('userId'))
            
        if all('frontend_user_' in str(user) for user in emotion_users):
            print("   ❌ **Emotion Data**: 模擬資料 (所有 userId 都是 'frontend_user_X' 格式)")
        else:
            print("   ✅ **Emotion Data**: 可能是真實前端資料")
            
        # 檢查時間戳模式
        emotion_count = await db['emotion_data'].count_documents({})
        vlog_count = await db['vlog_data'].count_documents({})
        
        print(f"   📊 **資料數量**: Emotions({emotion_count}), Vlogs({vlog_count})")
        
        if emotion_count < 20 and vlog_count < 10:
            print("   ❌ **數量判斷**: 資料量較少，可能是測試資料")
        else:
            print("   ✅ **數量判斷**: 資料量充足，可能是真實使用資料")
            
        client.close()
        
    except Exception as e:
        print(f"❌ 分析失敗: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_data())
