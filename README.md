# Team05HW — 多專案協作平台 (ChatDev)

這是一個具備高度隔離性、支援多人即時協作與權限管理的 **GitHub-Style 多專案管理與聊天應用程式**。  
前端使用 **Vue 3 (Composition API) + Vite**，後端使用 **Django 6 + Django Channels**，透過 WebSocket 實現即時通訊。

---

## 🌟 核心功能 (Key Features)

| 功能 | 說明 |
|---|---|
| **GitHub 風格專案工作區** | 無限建立獨立 Project，透過 Dashboard 總覽所有專案 |
| **邀請制成員管理** | Email 邀請；受邀者在收件匣自行 Accept / Decline |
| **身分與刪除權限 (RBAC)** | Owner 可刪除整個專案（Cascade）；Member 只能刪除自己的檔案 |
| **專案設定頁** | Owner 可修改專案名稱、移除成員（同步踢出所有聊天室） |
| **即時聊天室** | Django Channels + WebSocket；可自訂成員或開放全專案 |
| **Share to Chat** | 從程式碼檢視區選取行數後直接分享至聊天室，可點擊跳回指定行 |
| **行級留言** | 在程式碼旁對指定行範圍留言，支援多行選取 |
| **個人頁面** | 登入後查看 Email、名稱、所屬專案列表 |
| **RWD 響應式佈局** | 全 Flexbox / Viewport 自適應；> 900px 左右分屏，手機端折疊 |

---

## 🔒 安全性設計 (Security Architecture)

- **敏感金鑰解耦 (`.env`)** — `SECRET_KEY`、`AES_KEY`、`AES_IV`、`DEBUG` 均由環境變數掛載，不進版控。  
- **AES-CBC 密碼加密** — 前端以 AES CBC Padding 加密後再傳送；後端解密後再以 PBKDF2 儲存。  
- **Session-based Auth** — Django Session 保持登入狀態；CSRF 豁免僅限開發環境 API（`@csrf_exempt`）。

---

## 🚀 CI/CD 自動化管線 (GitHub Actions)

`.github/workflows/CI.yaml` 在每次 `push` / `pull_request` 到 `main` / `master` 時觸發三個並行任務：

| Job | 內容 |
|---|---|
| **Backend Tests & Lint** | Python 3.12、flake8 語法檢查、`python manage.py test user chat core` |
| **Frontend Code Quality** | Node 20、TypeScript 型別檢查、ESLint、`npm run build` |
| **Frontend Unit Tests** | Vitest + Pinia mock；測試所有前端 store action 與 UI 元件 |

---

## 💻 快速啟動 (Quick Start)

### 前置條件

> 專案的 Python 虛擬環境位於 **根目錄 `venv/`**，請統一使用此環境。

```bash
# 建立虛擬環境（僅首次）
python -m venv venv

# 安裝所有後端依賴
venv/Scripts/activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

### 1. 後端啟動 (Django / Daphne ASGI)

```bash
cd backend

# 建立 .env（僅首次）
# 內容格式：
# SECRET_KEY=your_secure_django_key_here
# DEBUG=True
# AES_KEY=team05_secret_key_12345678901234
# AES_IV=team05_shared_iv

# 遷移資料庫
../venv/Scripts/activate
python manage.py migrate

# 啟動伺服器（port 8001）
python manage.py runserver 8001
```

### 2. 前端啟動 (Vue 3 + Vite)

```bash
cd frontend

# 建立 .env（僅首次）
# 內容格式：
# VITE_AES_KEY=team05_secret_key_12345678901234
# VITE_AES_IV=team05_shared_iv

npm install
npm run dev
# 預設運行於 http://localhost:5173
```

> **注意**：前端透過 Vite Proxy 將 `/api/` 及 `/ws/` 轉發至 `http://127.0.0.1:8001`，請確保後端同時運行。

### 3. 執行測試

```bash
# 後端全部測試（user + chat + core，共 ~70 個）
cd backend
../venv/Scripts/activate
python manage.py test user chat core --verbosity=2

# 前端測試
cd frontend
npm run test:unit
```

---

## 📁 專案結構 (Project Structure)

```
Team05HW/
├── venv/                   # Python 虛擬環境（共用）
├── requirements.txt        # Python 依賴套件
├── backend/                # Django 後端
│   ├── backend/            # 專案設定 (settings.py, urls.py, asgi.py)
│   ├── user/               # 使用者認證 App (register / login / logout)
│   ├── core/               # 核心業務 App (projects, files, comments, invitations)
│   ├── chat/               # 聊天室 App (REST + WebSocket consumer)
│   └── manage.py
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── api/            # fetch 封裝 (auth.ts, projects.ts, chat.ts)
│   │   ├── components/     # 可複用元件
│   │   ├── layouts/        # 主框架 MainLayout.vue
│   │   ├── router/         # Vue Router 路由設定
│   │   ├── stores/         # Pinia 狀態管理 (main.ts)
│   │   └── views/          # 各頁面元件
│   └── src/__tests__/      # Vitest 前端單元測試
└── .github/workflows/      # GitHub Actions CI
```