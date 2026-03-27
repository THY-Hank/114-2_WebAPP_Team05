# Team05HW - 多專案協作平台 (Chatdev)

這是一個具備高度隔離性、支援多人即時協作與權限管理的 **GitHub-Style 多專案管理與聊天應用程式**。
專案採用前後端分離架構，前端使用 Vue 3 (Composition API Payload) + Vite 進行響應式介面渲染，後端則使用 Django 搭建強健的 RESTful API 服務。

---

## 🌟 核心功能 (Key Features)
1. **GitHub 風格的專案隔離 (Project Workspaces)**：
   - 告別單一全域工作區，用戶可以建立無數個獨立的 Project。
   - 透過專屬 Dashboard 儀表板總覽個人所有專案。
2. **安全的邀請信箱系統 (Invitation Handshake)**：
   - 透過發送電子郵件進行成員邀請（不會強制拉人入群）。
   - 被邀請者擁有獨立的「收件匣 (Inbox)」，可自行決定 `Accept` (接受) 或 `Decline` (拒絕)。
3. **身分權限與檔案刪除 (RBAC & Deletion Guards)**：
   - **專案擁有者 (Owner)**：具備專案級別最高權限，可於設定頁面將整個專案及關聯資料強制刪除 (Cascade Delete)。
   - **一般成員 (Member)**：僅能針對特定 Code File 進行刪除，無法動搖專案根本。
4. **全域即時聊天室 (Global Chatroom)**：
   - 獨立於單一專案之外的全域聊天大廳，支援所有註冊成員進行廣播交流。
5. **RWD 響應式佈局 (Responsive Design)**：
   - 拋棄傳統的 PX 定位，全面採用 Flexbox / Viewport (%/vw/vh) 自適應延展。
   - 螢幕大於 900px 時自動展開左右分屏；在手機端則平滑摺疊為上下堆疊，確保不會破版。

---

## 🔒 安全性設計 (Security Architecture)
團隊在開發末期針對此系統進行了深度 **Security Hardening (安全性強化)**：
- **敏感金鑰解耦 (.env)**： 
  系統的 `SECRET_KEY`、`DEBUG` 模式旗標，以及用來雙向加密密碼的 `AES_KEY` 和 `AES_IV`，均已從原始碼中拔除，改為依賴伺服器環境的 `.env` 變數掛載，完美避免被 Push 到 GitHub 上遭到爬蟲濫用。
- **密碼高規隱私 (AES CBC Padding)**： 
  使用者密碼不以明文儲存，所有密碼寫入 SQLite 前皆會經過 AES Block Size Padding 強制加密，確保即便資料庫外洩，駭客也無法輕易取得明文資訊。
*(註：目前內部 API 為了降低 Vue Proxy Fetch 的耦合難度，開發環境暫時保留了 `@csrf_exempt` 豁免設定。若未來部署至正式生產環境 (Production)，建議將 Session Auth 替換為 JWT 以達完全無狀態化防護。)*

---

## 🚀 CI/CD 自動化管線 (GitHub Actions)
專案內建了 `.github/workflows/CI.yaml` 持續整合腳本。
只要有任何人向 `main` 或 `master` 發起 `Push` 或 `Pull Request`，GitHub 雲端機器人就會自動：
1. **Backend 測試任務**：載入 Python 3.12 核心，匯入 `requirements.txt` 環境，然後無頭自動通過 `python manage.py test core` 掃描檢測核心模型和資料庫權限邏輯。
2. **Frontend 測試任務**：掛載 Node.js 20 環境，透過 Vitest (Pinia Mocks) 對所有前端 UI 元件和狀態樹發出壓力測試確保綠燈。

---

## 💻 安裝與啟動指南 (Quick Start)

### 1. 後端啟動 (Django API)
```bash
# 1. 進入後端資料夾
cd backend

# 2. 建立虛擬環境 (建議) 並安裝依賴套件
python -m venv venv
source venv/Scripts/activate  # (Windows: venv\Scripts\activate)
pip install -r requirements.txt

# 3. 建立並補齊環境變數設定檔 (安全必須)
# 請在 backend/ 根目錄下建立 `.env` 檔案，內容格式如下：
# SECRET_KEY=your_secure_django_key_here
# DEBUG=True
# AES_KEY=team05_secret_key_12345678901234
# AES_IV=team05_shared_iv

# 4. 遷移資料庫與啟動
python manage.py migrate
python manage.py runserver 8001
```

### 2. 前端啟動 (Vue 3 Vite)
```bash
# 1. 進入前端資料夾
cd frontend

# 2. 安裝 Node Modules 依賴套件
npm install

# 3. 建立並補齊環境變數設定檔 (安全必須)
# 請在 frontend/ 根目錄下建立 `.env` 檔案，內容格式如下：
# VITE_AES_KEY=team05_secret_key_12345678901234
# VITE_AES_IV=team05_shared_iv

# 4. 啟動熱更動開發伺服器
npm run dev
# 伺服器通常會運行於 http://localhost:5173
```
> **注意**：前端的 API 會自動透過 Vite 的 Proxy 代理攔截 `/api/` 並轉發至 `http://127.0.0.1:8001`，因此前後端請確保皆在運行狀態才能正常登入與抓取資料。