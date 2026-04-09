<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-glow" aria-hidden="true"></div>
      <p class="brand">Chatdev</p>
      <h1>登入</h1>
      <p class="subtitle">登入你的帳號以進入專案儀表板</p>

      <form class="login-form" @submit.prevent="login">
        <label for="email">電子郵件</label>
        <input 
          type="email" 
          id="email" 
          name="email" 
          autocomplete="email" 
          placeholder="請輸入電子郵件" 
          v-model="email"
          :disabled="isLoading"
        />

        <label for="password">密碼</label>
        <input 
          type="password" 
          id="password" 
          name="password" 
          autocomplete="current-password" 
          placeholder="請輸入密碼" 
          v-model="password"
          :disabled="isLoading"
        />

        <button type="submit" :disabled="isLoading">
          {{ isLoading ? '驗證中...' : '登入' }}
        </button>

        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
      </form>

      <p class="login-link">還沒有帳號嗎？<router-link to="/register">建立帳號</router-link></p>
      <p class="login-note">Collaborate on code, comments, and chat in one workspace.</p>
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

const email = ref('')
const password = ref('')
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

const login = async () => {
  errorMessage.value = ''
  
  if (!email.value || !password.value) {
    errorMessage.value = '請輸入電子郵件和密碼'
    return
  }

  isLoading.value = true
  try {
    const success = await store.login(email.value, password.value)
    if (success) {
      router.push('/projects')
    } else {
      errorMessage.value = '登入失敗，請檢查瀏覽器控制台以取得詳細信息'
    }
  } catch (error) {
    errorMessage.value = '登入失敗，請稍後重試'
    console.error('Login error:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
@import '@/assets/login.css';

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
