# Frontend — Vue 3 + Vite

這個資料夾包含 ChatDev 的前端，使用 **Vue 3 Composition API + TypeScript + Vite**。  
以 SPA（Single Page Application）形式運行，透過 Vite Proxy 與後端 Django API 及 WebSocket 溝通。

---

## 🚀 快速啟動

```bash
# 1. 進入前端目錄
cd frontend

# 2. 建立 .env（僅首次）
#    VITE_AES_KEY=team05_secret_key_12345678901234
#    VITE_AES_IV=team05_shared_iv

# 3. 安裝依賴
npm install

# 4. 啟動開發伺服器（http://localhost:5173）
npm run dev
```

> Vite 會自動將 `/api/*` 及 `/ws/*` 代理至 `http://127.0.0.1:8001`，請確保後端同時運行。

---

## 📁 目錄結構

```
src/
├── api/                    # fetch 封裝（與後端溝通的薄層）
│   ├── auth.ts             # 登入 / 登出 / 取得使用者資訊
│   ├── projects.ts         # 專案 CRUD / 檔案 / 留言 / 邀請
│   └── chat.ts             # 聊天室 / 訊息 API
│
├── assets/                 # 全局與元件專用 CSS
│   ├── main.css            # CSS 變數、字型、全局 reset
│   ├── layout.css          # MainLayout 側欄樣式
│   ├── chat.css            # ChatView 樣式
│   ├── code.css            # CodeView 樣式
│   ├── register.css        # 註冊頁樣式
│   └── ...
│
├── components/             # 可複用 UI 元件
│   ├── CodeViewer.vue      # 程式碼高亮顯示（含行號、行選取）
│   ├── CommentSection.vue  # 全域留言列表與輸入框
│   ├── FileExplorer.vue    # 左側樹狀檔案瀏覽器
│   ├── FileUploadSection.vue # 拖曳 / 貼上上傳檔案
│   ├── PersonalInfoModal.vue # 個人資訊彈窗
│   └── ShareModal.vue      # Share to Chat 彈窗
│
├── layouts/
│   └── MainLayout.vue      # 登入後的主框架（側欄 + router-view）
│
├── router/
│   └── index.ts            # Vue Router：路由定義與 Navigation Guard
│
├── stores/
│   └── main.ts             # Pinia 核心 store（全域狀態 + API actions）
│
├── views/                  # 各頁面元件
│   ├── LoginView.vue       # 登入頁
│   ├── RegisterView.vue    # 註冊頁
│   ├── ProjectListView.vue # 專案列表 Dashboard
│   ├── CreateProjectView.vue # 建立新專案
│   ├── CodeView.vue        # 程式碼瀏覽、上傳、留言
│   ├── ChatView.vue        # 即時聊天室
│   ├── InvitationsView.vue # 收件匣（邀請管理）
│   └── ProjectSettingsView.vue # 專案設定（改名、成員管理）
│
└── __tests__/              # Vitest 單元測試
    ├── App.spec.ts
    ├── auth.spec.ts
    ├── chat.spec.ts
    ├── lineComments.spec.ts
    ├── projectSettings.spec.ts
    └── projects.spec.ts
```

---

## 🧩 核心功能說明

### 狀態管理 (`stores/main.ts`)
Pinia store 是整個應用的**唯一資料來源**。所有 API 呼叫都透過 store actions 執行，元件只讀取 state 或呼叫 actions，不直接發出 fetch。

### 路由 (`router/index.ts`)
- 未登入的使用者會被 Navigation Guard 重導至 `/login`
- 登入後路由走 `MainLayout`（側欄持續顯示），子路由包含 Code、Chat、Settings 等頁面

### API 層 (`api/`)
三個模組各負責一塊業務，保持 fetch 邏輯與元件完全解耦：

| 模組 | 負責 |
|---|---|
| `auth.ts` | 登入 / 登出 / me |
| `projects.ts` | 專案 CRUD、檔案上傳 / 刪除、全域留言、行級留言、邀請流程 |
| `chat.ts` | 聊天室 CRUD、發送訊息（文字 / Code Snippet） |

### WebSocket（即時聊天）
`ChatView.vue` 直接建立 `WebSocket` 連線至 `ws://.../ws/chat/<room_id>/`，監聽伺服器推播的 `new_message` 事件，無需輪詢即可即時顯示新訊息。

### Share to Chat
1. 在 `CodeView` 選取行範圍後點擊「Share」
2. `ShareModal.vue` 彈出讓使用者選取目標聊天室
3. 訊息送出後，聊天中顯示程式碼預覽
4. 點擊訊息中的 code snippet → 自動跳回 `CodeView` 並捲動至對應行

### 行級留言
`CodeViewer.vue` 支援滑鼠選取行範圍，觸發行級留言輸入；`CommentSection.vue` 顯示留言並可點擊跳至對應行。

---

## 🧪 測試

測試使用 **Vitest** + `@pinia/testing` mock store。

```bash
npm run test:unit       # 執行所有單元測試
npm run type-check      # TypeScript 型別檢查
npm run lint:eslint     # ESLint 語法檢查
npm run build           # 生產環境打包
```

| 測試檔案 | 涵蓋範圍 |
|---|---|
| `auth.spec.ts` | 登入 / 登出 / 取得使用者資訊的 store actions |
| `projects.spec.ts` | 專案 CRUD、檔案上傳 store actions |
| `chat.spec.ts` | 聊天室建立、訊息發送 store actions |
| `lineComments.spec.ts` | 行級留言 API 呼叫與資料流 |
| `projectSettings.spec.ts` | 專案設定（改名、移除成員、刪除專案）|
| `App.spec.ts` | App 根元件基礎渲染 |

---

## 🔧 開發指引

- **新增頁面**：在 `views/` 建立 `.vue` 元件，在 `router/index.ts` 新增路由。
- **新增狀態 / 資料操作**：在 `stores/main.ts` 新增 state 欄位與 action。
- **新增 API 呼叫**：在對應的 `api/*.ts` 封裝 fetch，再從 action 呼叫。
- **可複用 UI**：放入 `components/`。
- **全局樣式**：加入 `assets/main.css`；頁面專屬樣式建立獨立 `.css` 檔案並在元件中 `import`。
- 修改任何功能前，務必先查閱 `stores/main.ts` 了解現有資料結構。
