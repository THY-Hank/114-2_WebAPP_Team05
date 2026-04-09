# reCAPTCHA v3 防止機器人驗證設置指南

## 📋 概述

已為登入和註冊系統集成 **智能雙模式 CAPTCHA** 系統：
- **開發環境**：自動使用本地演示模式（無需任何配置）
- **生產環境**：自動切換到 Google reCAPTCHA v3（需配置 API 密鑰）

### 特點：
- ✅ **開箱即用**：開發環境無需配置，立即可用
- ✅ **無縫驗證**：用户無感知，不需要額外互動
- ✅ **AI 驅動**：Google 的機器學習檢測可疑行為
- ✅ **分數制**：0.0（機器人）- 1.0（真實用户）
- ✅ **自動環境檢測**：根據配置自動切換模式

---

## 🚀 快速開始

### 方案 A：本地開發（無需任何配置）

**狀態**：✅ **已準備就緒**

```bash
# 開發階段：直接啟動應用
cd frontend && npm run dev
cd backend && python manage.py runserver
```

**結果**：
- ✅ 登入頁面會顯示：🛡️ 本地演示模式（開發測試）
- ✅ 可以正常登入和註冊
- ✅ CAPTCHA 驗證在後端自動進行（演示分數：0.8）

### 方案 B：生產環境（需配置 Google reCAPTCHA v3）

#### 1️⃣ 獲取 API 密鑰

訪問 [Google reCAPTCHA Admin Console](https://www.google.com/recaptcha/admin)

**步驟：**
1. 使用 Google 帳號登入
2. 點擊「建立」或「+」按鈕
3. 輸入網站標籤（例如：`Chatdev Bot Protection`）
4. 選擇 **reCAPTCHA v3**
5. 輸入你的**生產域名**（例如：`chatdev.example.com`）
6. 接受服務條款
7. 點擊「建立」

**複製以下密鑰：**
```
Site Key:   xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx（前端使用）
Secret Key: yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy（後端使用，保密）
```

#### 2️⃣ 配置環境變數

##### 後端配置 (Django)
編輯 `backend/.env` 檔案：

```bash
# Django 設置
DEBUG=False

# reCAPTCHA 後端密鑰（生產環境必須）
RECAPTCHA_SECRET_KEY=your_secret_key_here

# reCAPTCHA 最低分數閾值（可選，默認 0.5）
# 1.0 = 確定真實用户，0.0 = 確定機器人
RECAPTCHA_MIN_SCORE=0.5
```

##### 前端配置 (Vue)
編輯 `frontend/.env.production` 或 `frontend/.env` 檔案：

```bash
# 使用生產和開發環境特定文件：frontend/.env.production

# reCAPTCHA 前端公鑰（生產環境）
VITE_RECAPTCHA_SITE_KEY=your_site_key_here
```

#### 3️⃣ 部署和驗證

```bash
# 後端
cd backend
pip install -r requirements.txt
python manage.py check
python manage.py runserver  # 或使用 Daphne

# 前端
cd frontend
npm install
npm run build
# 部署 dist/ 文件夾到生產服務器
```

登入時應該看到：✅ 🛡️ 受 reCAPTCHA 保護

---

## 🔧 技術實現細節

### 自動環境檢測邏輯

```
系統啟動
    ↓
檢查環境變數：
  - DEBUG=False 且 RECAPTCHA_SECRET_KEY 已設置？
  - YES → 生產模式（Google reCAPTCHA v3）
  - NO  → 開發模式（本地演示）
    ↓
前端加載相應的 CAPTCHA 系統
後端使用相應的驗證邏輯
```

### 開發環境流程（演示模式）

```
使用者提交登入表單
    ↓
前端調用 getRecaptchaToken('login')
    ↓
因為沒有 Site Key → 生成演示令牌
    ↓
將令牌發送到後端
    ↓
後端接收到 CAPTCHA 令牌
    ↓
檢查 RECAPTCHA_SECRET_KEY 是否配置
    ↓
沒有配置 → 使用演示驗證（自動通過，分數 0.8）
    ↓
✅ 允許登入
```

### 生產環境流程（Google reCAPTCHA v3）

```
使用者提交登入表單
    ↓
前端調用 getRecaptchaToken('login')
    ↓
因為有 Site Key → 呼叫 Google reCAPTCHA API
    ↓
Google 分析用户行為 → 返回風險分數
    ↓
將 Google 令牌發送到後端
    ↓
後端接收到 CAPTCHA 令牌
    ↓
檢查 RECAPTCHA_SECRET_KEY 是否配置
    ↓
已配置 → 驗證 Google reCAPTCHA v3 令牌
    ↓
向 Google API 驗證 → 獲取分數
    ↓
分數 ≥ 0.5 → ✅ 允許登入
分數 < 0.5  → ❌ 拒絕（可疑行為）
```

### 關鍵檔案

| 檔案 | 用途 | 改動 |
|-----|-----|-----|
| `backend/user/captcha.py` | 雙模式 CAPTCHA 驗證 | 新建 |
| `frontend/src/api/captcha.ts` | 雙模式 CAPTCHA 前端客户端 | 新建 |
| `backend/user/views.py` | 登入/註冊端點 | 添加 CAPTCHA 驗證 |
| `frontend/src/api/auth.ts` | 認証 API 呼叫 | 添加令牌獲取 |
| `frontend/src/views/LoginView.vue` | 登入頁面 | 添加 CAPTCHA 支持 |
| `frontend/src/views/RegisterView.vue` | 註冊頁面 | 添加 CAPTCHA 支持 |
| `requirements.txt` | Python 依賴 | 添加 `requests==2.32.3` |

---

## 📊 環境設置矩陣

| 方面 | 開發環境 | 生產環境 |
|-----|--------|--------|
| **DEBUG** | True | False |
| **RECAPTCHA_SECRET_KEY** | 不需要（或空） | 必須 |
| **VITE_RECAPTCHA_SITE_KEY** | 不需要（或空） | 必須 |
| **前端提示** | 🛡️ 本地演示模式 | 🛡️ 受 reCAPTCHA 保護 |
| **CAPTCHA 類型** | 本地演示 | Google v3 |
| **域名要求** | 無（localhost 可用） | 真實域名 |
| **網路連線** | 不需要 | 需要（呼叫 Google API） |

---

## 🔒 安全最佳實踐

### 本地開發（演示模式）
1. ✅ 可以在任何環境使用（localhost、127.0.0.1 等）
2. ✅ 無需網路連線
3. ⚠️ 不適合生產環境

### 生產環境（Google reCAPTCHA v3）
1. ✅ **Secret Key 保密**
   - 僅在後端 `.env` 中使用
   - 絕不在前端或公開版本控制中暴露
   
2. ✅ **Site Key 公開**
   - 前端 `.env` 或環境變數中使用
   - 可在前端代碼中公開

3. ✅ **HTTPS 推薦**
   - 生產環境應使用 HTTPS
   - reCAPTCHA v3 在 HTTP 時會給出警告

4. ✅ **監控 reCAPTCHA Admin Console**
   - 定期檢查活動日誌
   - 監控風險分數趨勢

---

## 🐛 故障排除

### 問題：我在本地開發，想測試 Google reCAPTCHA

**解決方案：**
1. 獲取 API 密鑰（見上文）
2. 在 `backend/.env` 設置：
   ```bash
   DEBUG=False
   RECAPTCHA_SECRET_KEY=your_secret_key_here
   ```
3. 在 `frontend/.env.local` 設置：
   ```bash
   VITE_RECAPTCHA_SITE_KEY=your_site_key_here
   ```
4. **重啟開發伺服器**

### 問題：本地開發時收到 Google reCAPTCHA 域名錯誤

**原因：** Google 不認可 `localhost` 或 `127.0.0.1`

**解決方案：**
1. 移除 `RECAPTCHA_SECRET_KEY` 或設置 `DEBUG=True`
2. 回到開發模式（本地演示）

### 問題：登入時分數總是低於閾值

**原因：** 可能是開發環境被識別為可疑，或 Google 與你的 IP 衝突

**臨時解決方案：**
```python
# backend/user/captcha.py
min_score = 0.3  # 降低閾值用於開發測試
```

### 問題：「CAPTCHA 未加載」

**原因：** 可能是網路問題或 Google API 不可用

**解決方案：**
1. 檢查瀏覽器控制台錯誤
2. 確認網路連線正常
3. 清空瀏覽器快取重新加載
4. 降級到開發模式（移除 Secret Key 配置）

---

## 📈 監控和分析

### Google reCAPTCHA Admin Console 中（生產環境）

1. **分析圖表**
   - 顯示每日驗證次數和風險分數分佈
   
2. **環境設置**
   - 檢視已授權的域名
   - 檢視 API 使用統計

3. **設置和風險**
   - 檢視被拒絕請求的詳情
   - 調整風險管理策略

---

## 🔄 在模式之間切換

### 從開發模式切換到生產模式

```bash
# 後端
echo "DEBUG=False" >> backend/.env
echo "RECAPTCHA_SECRET_KEY=your_secret_key_here" >> backend/.env

# 前端
echo "VITE_RECAPTCHA_SITE_KEY=your_site_key_here" >> frontend/.env.local

# 重啟服務
```

### 從生產模式切換回開發模式

```bash
# 後端
echo "DEBUG=True" >> backend/.env
# 留空或移除 RECAPTCHA_SECRET_KEY

# 前端
# 移除 VITE_RECAPTCHA_SITE_KEY 或設置空值

# 重啟服務
```

---

## 📝 部署檢查清單

部署到生產環境前：

- [ ] 在 Google reCAPTCHA 中註冊生產域名
- [ ] 在生產服務器上設置 `RECAPTCHA_SECRET_KEY` 環境變數
- [ ] 在生產前端設置 `VITE_RECAPTCHA_SITE_KEY` 環境變數
- [ ] 設置 `DEBUG=False` 在生產環境
- [ ] 測試登入和註冊
- [ ] 檢查 Google reCAPTCHA Admin Console 中的活動
- [ ] 設置 HTTPS（推薦）
- [ ] 監控分數分佈，必要時調整 `min_score`
- [ ] 設置告警：分數過低時通知管理員

---

## 🎯 典型配置示例

### 開發配置（演示模式）

**backend/.env**
```bash
# 開發環境
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
# RECAPTCHA_SECRET_KEY 未設置（使用演示模式）
```

**frontend/.env.local**
```bash
# 開發環境
VITE_API_URL=http://localhost:8000
# VITE_RECAPTCHA_SITE_KEY 未設置（使用演示模式）
```

**結果：** 🛡️ 本地演示模式

---

### 生產配置（Google reCAPTCHA v3）

**backend/.env** (生產服務器)
```bash
# 生產環境
DEBUG=False
DATABASE_URL=postgresql://user:pass@localhost/chatdev
RECAPTCHA_SECRET_KEY=abcdef123456789...
RECAPTCHA_MIN_SCORE=0.5
```

**frontend/.env.production**
```bash
# 生產環境
VITE_API_URL=https://api.chatdev.example.com
VITE_RECAPTCHA_SITE_KEY=xyz789...
```

**結果：** 🛡️ 受 reCAPTCHA 保護

---

## 📚 參考資源

- [Google reCAPTCHA v3 官方文檔](https://developers.google.com/recaptcha/docs/v3)
- [reCAPTCHA Admin Console](https://www.google.com/recaptcha/admin)
- [reCAPTCHA 檢查 API](https://developers.google.com/recaptcha/docs/verify)

---

## 💡 常見問題 (FAQ)

**Q: 開發環境真的不需要任何配置嗎？**
A: 是的！開發模式完全自動，無需任何配置。

**Q: 可以在開發環境測試真實的 Google reCAPTCHA 嗎？**
A: 可以，但需要配置 API 密鑰。Google 不支持 localhost，所以你需要使用真實域名或使用隧道工具（如 ngrok）。

**Q: 演示模式的分數是硬編碼的嗎？**
A: 是的，演示模式返回固定的 0.8 分數（模擬真實用户）。這對開發測試足夠。

**Q: 生產環境中如果 Google API 不可用會怎樣？**
A: 驗證會失敗並返回 400 錯誤。建議設置監控告警。

**Q: 如何調整風險容限？**
A: 修改 `backend/user/views.py` 中 `is_valid_recaptcha()` 的 `min_score` 參數。

---

若有疑問，請檢查 Chrome DevTools Console 和後端日誌。


