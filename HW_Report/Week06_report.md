# 練習了哪些當週上課的主題
因為本週上課內容URL、MTV、html form前幾週已經有製作，
分別為:
html form: 登入註冊系統
URL: 前後端溝通
MTV: 基本資料儲存
所以本週將只補全網站功能
readme.md有所有的架構，frontend、backend各有一份

# 額外找了與當週上課的主題相關的程式技術
1. Pinia store 讀取既有檔案清單
2. 原生瀏覽器 File API、FileReader、Drag and Drop API
原本是readAsText方式，現在改成file的input方式。針對檔案數量和檔案大小有做控制，總體大小也有控制。相同名字原本是沒處理的，會有問題，所以在這裡也把它加上。
做到「資料夾上傳、保留路徑、樹狀預覽、大小限制、binary 標記、重名處理」，有支援zip上傳，但還沒做到可以zip解壓匯入
3. Regex mention parsing，主要作用在@mention上
聊天室原本是比較陽春版本，只有上傳文字。把聊天室整體處理的完整一點。
做到「訊息搜尋、未讀數、已讀狀態、@mention、置頂訊息、聊天室刪除/重新命名」

# 第五組組員分工情況
楊宗瀚 50%  改善上傳code、評論分享功能、專案設定功能

顧庭維 50%  聊天室增加細節、CSS、上傳檔案方式修改

片岡佳穗 退選