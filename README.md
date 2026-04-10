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
| **檔案版本歷史** | 每次儲存產生新版本；可查歷史、比對任兩版差異、回復舊版 |
| **版本標記 (Tag/Snapshot)** | 可替版本加註記與里程碑標籤，快速定位重要版本 |
| **個人頁面** | 登入後查看 Email、名稱、所屬專案列表 |
| **RWD 響應式佈局** | 全 Flexbox / Viewport 自適應；> 900px 左右分屏，手機端折疊 |

---

## 🔒 安全性設計 (Security Architecture)

- **敏感金鑰解耦 (`.env`)** — `SECRET_KEY`、`AES_KEY`、`AES_IV`、`DEBUG` 均由環境變數掛載，不進版控。  
- **AES-CBC 密碼加密** — 前端以 AES CBC Padding 加密後再傳送；後端解密後再以 PBKDF2 儲存。  
- **JWT-based Auth** — 登入後取得 Access Token，前端以 `Authorization: Bearer <token>` 呼叫受保護 API。
- **CAPTCHA 雙模式** — 開發環境使用本地 demo CAPTCHA；生產環境切換 Google reCAPTCHA v3。


## 檔案版本歷史（使用者功能）

- 新增 `CodeFileVersion` 模型，記錄版本號、內容、變更者、備註、Tag、Snapshot、時間。
- 每次在 Code Viewer 按下 Save 會建立新版本。
- 舊檔案若沒有歷史，首次開啟版本頁會自動補一筆初始版本（backfill）。

## 版本比較 / 回復 / 里程碑

- 支援任兩版 Diff（unified diff）。
- 支援一鍵 Revert 到任一歷史版本（回復後會新增一筆回復版本，保留完整審計軌跡）。
- 支援版本備註與 Tag/Snapshot 標記。

## 權限規則（安全）

- 只有專案成員可查看版本歷史與 Diff。
- 只有專案 Owner 可回復版本。
- 只有專案 Owner 可設定 Tag/Snapshot。

## reCAPTCHA 登入/註冊防機器人

- 前端登入/註冊加入 CAPTCHA token 流程。
- 後端驗證 `recaptchaToken`，開發環境可無縫使用 demo 模式。


---

## 🚀 CI/CD 自動化管線 (GitHub Actions)

`.github/workflows/CI.yaml` 在每次 `push` / `pull_request` 到 `main` / `master` 時觸發三個並行任務：

| Job | 內容 |
|---|---|
| **Backend Tests & Lint** | Python 3.12、flake8 語法檢查、`python manage.py test user chat core` |
| **Frontend Code Quality** | Node 20、TypeScript 型別檢查、ESLint、`npm run build` |
| **Frontend Unit Tests** | Vitest + Pinia mock；測試所有前端 store action 與 UI 元件 |

### Docker + Kubernetes CD（新增）

本專案已加入完整容器化與 K8s 部署骨架：

- `docker-compose.yml`：本地一次啟動 `frontend + backend + postgres`
- `backend/Dockerfile`：Django/Channels（Daphne）映像
- `frontend/Dockerfile` + `frontend/nginx.conf`：Vue build 後由 Nginx 服務，並反向代理 `/api`、`/ws`
- `k8s/base`：共用 manifests（namespace、configmap、postgres、backend、frontend、ingress）
- `k8s/overlays/dev`：本機開發環境 patch（本機 image、單副本、DEBUG=True）
- `k8s/overlays/prod`：正式環境 patch（GHCR image、多副本、DEBUG=False）
- `.github/workflows/CD.yaml`：push 到 `main/master` 後自動 Build 映像、推送 GHCR、部署 `k8s/overlays/prod`

---

## 🐳 本地 Docker 驗證

```bash
docker compose up --build -d
```

服務：

- 前端：http://localhost:8080
- 後端（由前端代理）：`/api/*`
- WebSocket（由前端代理）：`/ws/*`

關閉：

```bash
docker compose down
```

---

## ☸️ Kubernetes 部署

1. 先建立 `k8s/secret.yaml`（可參考 `k8s/secret.example.yaml`）。
2. 修改 `k8s/overlays/dev/patch-ingress.yaml` 與 `k8s/overlays/prod/patch-ingress.yaml` 的 host。
3. 本機（dev overlay）部署：

```bash
kubectl apply -f k8s/secret.yaml
kubectl apply -k k8s/overlays/dev
```

4. 正式（prod overlay）手動部署：

```bash
kubectl apply -f k8s/secret.yaml
kubectl apply -k k8s/overlays/prod
```

> `k8s/overlays/prod/patch-backend.yaml` 與 `k8s/overlays/prod/patch-frontend.yaml` 的 image 預設是 placeholder：
> `ghcr.io/OWNER/Team05HW-backend:latest`、`ghcr.io/OWNER/Team05HW-frontend:latest`

### 本機 Dev 一鍵腳本

安全建議（避免外洩）：

1. 複製範本：`cp .env.k8s.dev.example .env.k8s.dev`
2. 在 `.env.k8s.dev` 填入你自己的值
3. 再執行 `bash scripts/k8s-dev-up.sh`

`.gitignore` 已包含 `.env.*`，所以 `.env.k8s.dev` 不會被 push 到 GitHub。

若你偏好 CI/terminal 注入，也可在執行前設定環境變數：

- `SECRET_KEY`
- `DB_PASSWORD`
- `JWT_SECRET`
- `AES_KEY`
- `AES_IV`

---

可用以下腳本快速操作本機 K8s dev 環境：

- `bash scripts/k8s-dev-up.sh`：讀取 `.env.k8s.dev` 建立/更新 secret，套用 `k8s/overlays/dev`，檢查 rollout
- `bash scripts/k8s-dev-up.sh --port-forward`：同上，最後直接啟動 port-forward 到 `http://localhost:8080`
- `bash scripts/k8s-dev-up.sh --secret-file <path>`：指定其他本機 secret 檔
- `bash scripts/k8s-dev-status.sh`：查看 pod / service / ingress 狀態
- `bash scripts/k8s-dev-down.sh`：刪除 dev overlay 資源
- `bash scripts/k8s-dev-down.sh --purge-secret`：刪除 dev overlay 資源並移除 secret



## 🔐 GitHub Actions CD 需要的 Secrets(未完成)

`CD.yaml` 會使用以下 repository secrets：

- `KUBE_CONFIG`：叢集 kubeconfig 的 base64 內容
- `SECRET_KEY`
- `DB_PASSWORD`
- `JWT_SECRET`
- `AES_KEY`
- `AES_IV`

並透過 `GITHUB_TOKEN` 將映像推送到 GHCR（需保留 workflow 的 `packages: write` 權限）。

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
# DB_NAME=chatdev
# DB_USER=postgres
# DB_PASSWORD=your_postgres_password
# DB_HOST=127.0.0.1
# DB_PORT=5432
# JWT_SECRET=your_jwt_secret
# JWT_ACCESS_MINUTES=60

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