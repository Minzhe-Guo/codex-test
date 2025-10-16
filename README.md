# Leave Management System

這是一個使用 FastAPI 打造的簡易請假系統，提供員工資料管理、請假申請以及審核功能。資料會以 JSON 檔案儲存在專案根目錄的 `data.json` 檔案中，方便快速體驗與測試。

## 功能

- 建立與查詢員工資料
- 建立、查詢請假申請
- 審核請假申請（核准或駁回）
- 健康檢查端點 `/health`

## 環境需求

- Python 3.11 以上

## 安裝與執行

1. 建議使用虛擬環境：

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. 安裝依賴套件：

   ```bash
   pip install fastapi "uvicorn[standard]" "pydantic<2"
   ```

3. 啟動服務：

   ```bash
   uvicorn app.main:app --reload
   ```

4. 服務預設會在 `http://127.0.0.1:8000` 提供 API。可透過 `http://127.0.0.1:8000/docs` 使用自動生成的 Swagger 介面測試。

## API 範例

### 建立員工

```http
POST /employees
Content-Type: application/json

{
  "name": "王小明",
  "department": "工程部"
}
```

### 建立請假申請

```http
POST /leave-requests
Content-Type: application/json

{
  "employee_id": 1,
  "start_date": "2024-05-01",
  "end_date": "2024-05-03",
  "reason": "旅遊"
}
```

### 審核請假申請

```http
POST /leave-requests/1/decision
Content-Type: application/json

{
  "status": "approved",
  "reviewer": "張主管",
  "comment": "祝旅途愉快"
}
```

更多端點與欄位說明可參考 `/docs` 自動文件。

