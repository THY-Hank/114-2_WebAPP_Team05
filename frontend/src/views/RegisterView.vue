<template>
  <div class="register-container">
    <div class="register-box">
      <h2 style="text-align: center; color: var(--text-color); margin-top: 0;">Chatdev</h2>
      <h1>建立帳號</h1>
      <p class="subtitle">註冊你的帳號以開始使用聊天室</p>

      <form @submit.prevent="register">
        <label for="username">使用者名稱</label>
        <input
          type="text"
          id="username"
          name="username"
          placeholder="請輸入使用者名稱"
          v-model="username"
          :disabled="isLoading"
        />

        <label for="email">電子郵件</label>
        <input
          type="email"
          id="email"
          name="email"
          placeholder="請輸入電子郵件"
          v-model="email"
          :disabled="isLoading"
        />

        <label for="password">密碼</label>
        <input
          type="password"
          id="password"
          name="password"
          placeholder="請輸入密碼"
          v-model="password"
          :disabled="isLoading"
        />

        <label for="confirm-password">確認密碼</label>
        <input
          type="password"
          id="confirm-password"
          name="confirm-password"
          placeholder="請再次輸入密碼"
          v-model="confirmPassword"
          :disabled="isLoading"
        />

        <button type="submit" :disabled="isLoading">
          {{ isLoading ? '驗證中...' : '註冊' }}
        </button>

        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
      </form>

      <p class="login-link">已經有帳號了嗎？<router-link to="/login">前往登入</router-link></p>
      <p v-if="captchaMode" class="captcha-disclaimer">
        <span v-if="captchaMode.isDemoMode">🛡️ 本地演示模式（開發測試）</span>
        <span v-else>🛡️ 受 reCAPTCHA 保護</span>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMainStore } from '@/stores/main'
import { loadRecaptcha, getCaptchaMode } from '@/api/captcha'

interface CaptchaMode {
  isDemoMode: boolean
  isConfigured: boolean
  message: string
}

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const router = useRouter()
const store = useMainStore()
const isLoading = ref(false)
const errorMessage = ref('')
const captchaMode = ref<CaptchaMode | null>(null)

onMounted(async () => {
  captchaMode.value = getCaptchaMode()
  try {
    await loadRecaptcha()
  } catch (error) {
    console.error('Failed to load CAPTCHA:', error)
  }
})

const register = async () => {
  errorMessage.value = ''

  if (!username.value || !email.value || !password.value || !confirmPassword.value) {
    errorMessage.value = '請填寫所有欄位'
    return
  }

  if (password.value !== confirmPassword.value) {
    errorMessage.value = '密碼不一致'
    return
  }

  isLoading.value = true
  try {
    const success = await store.register(username.value, email.value, password.value)
    if (success) {
      router.push('/login')
    } else {
      // 由於 store 已記錄詳細錯誤，這裡只顯示通用消息或更好地從 store 取得錯誤
      errorMessage.value = '註冊失敗，請檢查瀏覽器控制台以取得詳細信息'
    }
  } catch (error) {
    errorMessage.value = '註冊失敗，請稍後重試'
    console.error('Register error:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
@import '@/assets/register.css';

.error-message {
  color: #e74c3c;
  font-size: 14px;
  margin-top: 10px;
  padding: 10px;
  border-radius: 4px;
  background-color: rgba(231, 76, 60, 0.1);
  text-align: center;
}

.captcha-disclaimer {
  font-size: 12px;
  color: var(--text-color-secondary, #888);
  margin-top: 15px;
  text-align: center;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
