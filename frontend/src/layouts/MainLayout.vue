<template>
  <div class="container">
    <div class="sidebar">
      <div v-if="currentUser" class="user-profile">
        <button class="profile-trigger" type="button" @click="showPersonalInfo = true">
          {{ currentUser.name }}
        </button>
        <p>{{ currentUser.email }}</p>
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
    <PersonalInfoModal :show="showPersonalInfo" @close="showPersonalInfo = false" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useMainStore } from '@/stores/main'
import { useRouter } from 'vue-router'
import PersonalInfoModal from '@/components/PersonalInfoModal.vue'

type CurrentUser = {
  name: string
  email: string
}

const store = useMainStore()
const router = useRouter()
const showPersonalInfo = ref(false)
const currentUser = computed(() => store.currentUser as CurrentUser | null)

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
