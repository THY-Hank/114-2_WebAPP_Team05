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
          <li><router-link to="/projects">Project Dashboard</router-link></li>
          <li><router-link to="/projects/new">New Project</router-link></li>
          <li v-if="projectId"><router-link :to="`/projects/${projectId}/code`">Current Code View</router-link></li>
          <li v-if="projectId"><router-link :to="`/projects/${projectId}/settings`">Project Settings</router-link></li>
          <li>
            <router-link to="/invitations">
              Invitations Inbox
              <span v-if="store.invitations.length" class="badge">({{ store.invitations.length }})</span>
            </router-link>
          </li>
          <li v-if="projectId"><router-link :to="`/projects/${projectId}/chat`">Project Chatroom</router-link></li>
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
import { useRouter, useRoute } from 'vue-router'
import PersonalInfoModal from '@/components/PersonalInfoModal.vue'

type CurrentUser = {
  name: string
  email: string
}

const store = useMainStore()
const router = useRouter()
const route = useRoute()
const showPersonalInfo = ref(false)
const currentUser = computed(() => store.currentUser as CurrentUser | null)
const projectId = computed(() => route.params.projectId)

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
