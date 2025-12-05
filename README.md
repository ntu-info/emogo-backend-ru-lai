# Data 資料夾說明

此資料夾用於存放從 EmoGo 應用程式匯出的數據檔案，以滿足作業第三項要求。

## 📁 檔案要求

### 作業要求第三項：
> "data" folder storing exported data (3+ records for each data type w/ Tlast-T1st > 12 hours)

### 📊 數據類型要求：
- **情緒記錄**: 至少 3 筆
- **Vlog 記錄**: 至少 3 筆  
- **GPS 記錄**: 至少 3 筆
- **時間跨度**: 最後一筆 - 第一筆 > 12 小時

### 📱 數據來源：
1. 使用 EmoGo 應用程式記錄情緒 + vlog + GPS
2. 在應用程式中點擊「📤 匯出數據」
3. 透過 AirDrop 將 JSON 檔案傳送到電腦
4. 將檔案放入此 `data/` 資料夾

### 📄 預期檔案格式：
- `emogo_export_YYYY-MM-DD.json` - 主要數據匯出檔案
- 包含完整的 metadata、emotionData、statistics

## 🔍 數據驗證
匯出的數據會自動驗證是否滿足作業要求，包括：
- 記錄數量檢查
- 時間跨度驗證
- 數據完整性確認

## 📝 使用說明
1. 在手機上使用 EmoGo 應用程式記錄至少 3 筆數據
2. 確保記錄時間跨度超過 12 小時
3. 點擊「匯出數據」按鈕
4. 使用 AirDrop 傳送 JSON 檔案到此資料夾
5. 提交作業時確保此資料夾包含完整的數據檔案
