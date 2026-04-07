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
        />

        <label for="password">密碼</label>
        <input 
          type="password" 
          id="password" 
          name="password" 
          autocomplete="current-password" 
          placeholder="請輸入密碼" 
          v-model="password" 
        />

        <button type="submit">登入</button>
      </form>

      <p class="login-link">還沒有帳號嗎？<router-link to="/register">建立帳號</router-link></p>
      <p class="login-note">Collaborate on code, comments, and chat in one workspace.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMainStore } from '@/stores/main'

const email = ref('')
const password = ref('')
const router = useRouter()
const store = useMainStore()

const login = async () => {
  const success = await store.login(email.value, password.value)
  if (success) {
    router.push('/projects')
  } else {
    alert('電子郵件或密碼錯誤 (Invalid email or password)')
  }
}
</script>

<style scoped>
@import '@/assets/login.css';
</style>
