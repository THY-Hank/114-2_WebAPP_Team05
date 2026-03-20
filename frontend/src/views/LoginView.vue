<template>
  <div class="login-page">
    <div class="form">
      <h2>Chatdev</h2>
      <form class="login-form" @submit.prevent="login">
        <input type="email" placeholder="email" v-model="email" />
        <input type="password" placeholder="password" v-model="password" />
        <button type="submit" class="login-button">login</button>
      </form>
      <p class="register-link">
        <router-link to="/register">Create an account</router-link>
      </p>
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

const login = () => {
  if (store.login(email.value, password.value)) {
    router.push('/main/code')
  } else {
    alert('Invalid email or password')
  }
}
</script>

<style scoped>
@import '@/assets/login.css';
</style>
