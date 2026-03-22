<template>
  <div v-if="show && user" class="personal-modal-overlay" @click.self="$emit('close')">
    <div class="personal-modal">
      <header class="personal-header">
        <button class="personal-close" type="button" @click="$emit('close')">x</button>
        <h1>Personal Information</h1>
        <p>View your profile and project details.</p>
      </header>

      <main class="personal-main">
        <section class="personal-card">
          <h2>Profile</h2>
          <p><strong>User ID:</strong> {{ user.id }}</p>
          <p><strong>Email:</strong> {{ user.email }}</p>
          <p><strong>Current Name:</strong> {{ displayName }}</p>
          <form class="personal-name-form" @submit.prevent="saveName">
            <label class="personal-label" for="personal-name">Name</label>
            <div class="personal-name-row">
              <input id="personal-name" v-model="editableName" type="text" class="personal-input" />
              <button type="submit" class="personal-save">Save</button>
            </div>
          </form>
        </section>

        <section class="personal-card">
          <h2>Projects</h2>
          <ul v-if="user.projects.length > 0">
            <li v-for="project in user.projects" :key="project.id">{{ project.name }}</li>
          </ul>
          <p v-else>No projects yet.</p>
        </section>

        <section class="personal-card">
          <h2>Activity</h2>
          <p><strong>Uploaded files:</strong> {{ projectFilesCount }}</p>
          <p><strong>Chat rooms:</strong> {{ chatRoomCount }}</p>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useMainStore } from '@/stores/main'

type Project = {
  id: number
  name: string
}

type UserProfile = {
  id: number
  name: string
  email: string
  projects: Project[]
}

defineProps<{
  show: boolean
}>()

defineEmits(['close'])

const store = useMainStore()

const user = computed(() => store.currentUser as UserProfile | null)
const editableName = ref('')
const displayName = ref('')

watch(
  user,
  (value) => {
    editableName.value = value?.name ?? ''
    displayName.value = value?.name ?? ''
  },
  { immediate: true },
)

const projectFilesCount = computed(() => {
  if (!user.value) {
    return 0
  }

  const projectIds = new Set(user.value.projects.map((project) => project.id))
  return store.files.filter((file) => projectIds.has(file.projectId)).length
})

const chatRoomCount = computed(() => store.chatRooms.length)

const saveName = () => {
  const trimmedName = editableName.value.trim()
  if (trimmedName !== '') {
    displayName.value = trimmedName
    editableName.value = trimmedName
  }
}
</script>

<style scoped>
@import '@/assets/personal-information.css';
</style>
