# Backend — Django API 文件

這個資料夾包含 ChatDev 的 Django 後端，以 **ASGI / Daphne** 運行，同時支援 HTTP REST API 與 WebSocket 即時通訊。

---

## 🏗️ App 結構

| App | 職責 |
|---|---|
| `user/` | 使用者認證（註冊 / 登入 / 登出）；自訂 `CustomUser` model |
| `core/` | 核心業務：Project、CodeFile、FileComment、ProjectInvitation |
| `chat/` | 聊天室：ChatRoom、ChatMessage、REST views、WebSocket Consumer |

---

## 🌐 REST API

所有 API 皆接受 `Content-Type: application/json`，回傳 JSON。  
需要登入的端點，未登入時回傳 `401 Unauthorized`。

### 使用者認證 (`/api/user/`)

| Method | URL | 說明 | 需登入 |
|---|---|---|---|
| POST | `/api/user/register/` | 建立新帳號 | ✗ |
| POST | `/api/user/login/` | 登入（Session Cookie） | ✗ |
| POST | `/api/user/logout/` | 登出 | ✓ |
| GET  | `/api/user/me/` | 取得目前使用者資訊與專案列表 | ✓ |

**密碼加密**：前端先以 AES-CBC 加密密碼後再傳送；後端解密後以 PBKDF2 儲存，任何時刻都不以明文傳輸或儲存。

<details>
<summary>Request / Response 範例</summary>

**POST /api/user/register/**
```json
// Request
{ "email": "user@example.com", "password": "<AES encrypted>", "name": "王小明" }

// 201 Created
{ "message": "User registered successfully!", "user": { "email": "user@example.com", "name": "王小明" } }
```

**POST /api/user/login/**
```json
// Request
{ "email": "user@example.com", "password": "<AES encrypted>" }

// 200 OK
{ "message": "Login successful!", "user": { "email": "user@example.com", "name": "王小明" } }
```

**GET /api/user/me/**
```json
// 200 OK
{
  "id": 1, "email": "user@example.com", "name": "王小明",
  "projects": [{ "id": 1, "name": "My Project", "owner_id": 1, "members": [...] }]
}
```
</details>

---

### 邀請系統 (`/api/invitations/`)

| Method | URL | 說明 |
|---|---|---|
| GET | `/api/invitations/` | 取得目前使用者收到的邀請列表 |
| POST | `/api/invitations/<id>/respond/` | 接受 (`accept`) 或拒絕 (`decline`) 邀請 |

---

### 專案管理 (`/api/projects/`)

| Method | URL | 說明 |
|---|---|---|
| GET / POST | `/api/projects/` | 列出所有專案 / 建立新專案 |
| GET / DELETE | `/api/projects/<id>/` | 取得 / 刪除專案（刪除需為 Owner） |
| GET / PUT / DELETE | `/api/projects/<id>/settings/` | 取得設定 / 改名（Owner）/ 移除成員（Owner） |
| POST | `/api/projects/<id>/members/` | 邀請成員（發送邀請，非強制加入） |
| GET / POST | `/api/projects/<id>/files/` | 取得檔案列表 / 上傳新檔案 |

---

### 程式碼與留言 (`/api/files/`)

| Method | URL | 說明 |
|---|---|---|
| GET / DELETE | `/api/files/<id>/` | 取得 / 刪除檔案 |
| GET / POST | `/api/files/<id>/comments/` | 取得全域留言 / 新增留言 |
| GET / POST | `/api/files/<id>/line-comments/` | 取得行級留言 / 新增行級留言 |

**行級留言 Request：**
```json
{ "text": "這段需要重構", "startLine": 5, "endLine": 12 }
```

---

### 聊天室 (`/api/<project_id>/chatrooms/`)

| Method | URL | 說明 |
|---|---|---|
| GET / POST | `/api/<project_id>/chatrooms/` | 取得聊天室列表 / 建立新聊天室 |
| POST | `/api/<project_id>/chatrooms/<room_id>/messages/` | 發送訊息（文字 或 Code Snippet） |

**Code Snippet 訊息 Request：**
```json
{
  "text": "看這段：",
  "codeSnippetFile": "src/main.py",
  "codeSnippetStartLine": 10,
  "codeSnippetEndLine": 15,
  "codeSnippetContent": "def foo():\n    return 42"
}
```

---

## 🔌 WebSocket API

採用 **Django Channels + InMemoryChannelLayer**。

| URL | 說明 |
|---|---|
| `ws://127.0.0.1:8001/ws/chat/<room_id>/` | 連線聊天室。有新訊息時伺服器主動推播，無需前端輪詢。 |

**推播格式：**
```json
{
  "action": "new_message",
  "payload": {
    "id": 42,
    "author": "王小明",
    "text": "Hello!",
    "createdAt": "2026-04-03T10:00:00Z"
  }
}
```

---

## 🧪 測試

共有三個測試模組，CI 統一執行 `python manage.py test user chat core`：

| 模組 | 測試類別 | 涵蓋範圍 |
|---|---|---|
| `user/tests.py` | `UserAuthenticationTests` | 註冊、重複註冊、登入、錯誤密碼、登出 |
| `chat/tests.py` | `ChatRoomModelTest`<br>`ChatMessageModelTest`<br>`ProjectChatroomsViewTest`<br>`AddChatMessageViewTest`<br>`ChatConsumerTest` | 模型 `__str__`、REST CRUD、權限守衛、WebSocket 連線與廣播 |
| `core/tests.py` | `CoreAPITests` | 專案 CRUD、成員邀請流程、RBAC 删除、檔案上傳留言、行級留言、Settings API |

```bash
# 執行所有後端測試
cd backend
../venv/Scripts/activate
python manage.py test user chat core --verbosity=2
```

---

## ⚙️ 開發環境設置

1. **虛擬環境**（位於專案根目錄）：
   ```bash
   ../venv/Scripts/activate     # Windows
   # source ../venv/bin/activate  # macOS / Linux
   ```

2. **環境變數**：在 `backend/` 下建立 `.env`：
   ```
   SECRET_KEY=your_secure_django_key_here
   DEBUG=True
   AES_KEY=team05_secret_key_12345678901234
   AES_IV=team05_shared_iv
   ```

3. **資料庫遷移**：
   ```bash
   python manage.py migrate
   ```

4. **啟動伺服器**：
   ```bash
   python manage.py runserver 8001
   ```
   Daphne (ASGI) 已加入 `INSTALLED_APPS`，直接用 `runserver` 即可支援 WebSocket。

5. **建立管理員**：
   ```bash
   python manage.py createsuperuser
   ```
