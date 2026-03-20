<template>
  <div class="register-container">
    <div class="register-box">
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
        />

        <label for="email">電子郵件</label>
        <input type="email" id="email" name="email" placeholder="請輸入電子郵件" v-model="email" />

        <label for="password">密碼</label>
        <input
          type="password"
          id="password"
          name="password"
          placeholder="請輸入密碼"
          v-model="password"
        />

        <label for="confirm-password">確認密碼</label>
        <input
          type="password"
          id="confirm-password"
          name="confirm-password"
          placeholder="請再次輸入密碼"
          v-model="confirmPassword"
        />

        <button type="submit">註冊</button>
      </form>

      <p class="login-link">已經有帳號了嗎？<router-link to="/login">前往登入</router-link></p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMainStore } from '@/stores/main'

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const router = useRouter()
const store = useMainStore()

const register = () => {
  if (password.value !== confirmPassword.value) {
    alert('Passwords do not match')
    return
  }
  if (username.value && email.value && password.value) {
    store.register(username.value, email.value, password.value)
    router.push('/login')
  } else {
    alert('Please fill in all fields')
  }
}
</script>

<style scoped>
@import '@/assets/register.css';
</style>
