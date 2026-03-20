<template>
  <div class="container">
    <div class="sidebar">
      <div v-if="store.currentUser" class="user-profile">
        <h4>{{ store.currentUser.name }}</h4>
        <p>{{ store.currentUser.email }}</p>
        <button @click="logout">Logout</button>
      </div>

      <nav class="navigation">
        <ul>
          <li><router-link to="/main/code">Code</router-link></li>
          <li><router-link to="/main/chat">Chat</router-link></li>
        </ul>
      </nav>
    </div>
    <div class="content">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useMainStore } from '@/stores/main'
import { useRouter } from 'vue-router'

const store = useMainStore()
const router = useRouter()

onMounted(() => {
  if (!store.isLoggedIn) {
    router.push('/login')
  }
})

const logout = () => {
  store.logout()
  router.push('/login')
}
</script>

<style scoped>
@import '@/assets/layout.css';
</style>
