# Team05HW - Backend API Documentation

這個資料夾包含了我們專案的 Django 後端原始碼。

## Authentication APIs (使用者認證接口)

以下皆為接受 JSON 格式請求與回應的 REST API。前端在呼叫 API 時應帶上 `Content-Type: application/json` 的標頭。所有密碼在後端接皆已由系統採用 PBKDF2 單向加密防護。

### 1. 註冊 (Register)
* **URL:** `/api/user/register/`
* **Method:** `POST`
* **功能:** 建立一個新的使用者帳號（使用 Email 作為帳號）。
* **Request Body (JSON):**
  ```json
  {
      "email": "example@email.com",
      "password": "strongPassword123",
      "name": "使用者名稱"
  }
  ```
* **Success Response:**
  * **Code:** 201 Created
  * **Content:**
    ```json
    {
        "message": "User registered successfully!",
        "user": {
            "email": "example@email.com",
            "name": "使用者名稱"
        }
    }
    ```

### 2. 登入 (Login)
* **URL:** `/api/user/login/`
* **Method:** `POST`
* **功能:** 驗證使用者的 `email` 與 `password`。成功後，Django 會自動使用 Session 或 Cookie 機制儲存登入狀態。
* **Request Body (JSON):**
  ```json
  {
      "email": "example@email.com",
      "password": "strongPassword123"
  }
  ```
* **Success Response:**
  * **Code:** 200 OK
  * **Content:**
    ```json
    {
        "message": "Login successful!",
        "user": {
            "email": "example@email.com",
            "name": "使用者名稱"
        }
    }
    ```

### 3. 登出 (Logout)
* **URL:** `/api/user/logout/`
* **Method:** `POST` (或 `GET`)
* **功能:** 清除當前使用者的登入 Session，使其登出。
* **Success Response:**
  * **Code:** 200 OK
  * **Content:**
    ```json
    {
        "message": "Logout successful!"
    }
    ```

## 開發環境設置
1. 開啟虛擬環境: 使用位於根目錄的 `venv` (`../venv/Scripts/activate`)。
2. 啟動伺服器: 在這層目錄下執行 `python manage.py runserver 8001` (搭配前端最新的 proxy 設定，伺服器請架設在 8001 port)。
3. 如果 `db.sqlite3` 變更或不存在，需執行 `python manage.py migrate`。



## superuser

If you need an admin account, create one with:

```powershell
python manage.py createsuperuser
```

If you need to reset a superuser password, use Django shell instead of storing credentials in this README.
