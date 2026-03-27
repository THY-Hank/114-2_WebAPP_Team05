<template>
  <div class="project-list-container">
    <h2>Your Projects</h2>
    <div class="project-cards">
      <div 
        v-for="project in store.currentUser?.projects || []" 
        :key="project.id" 
        class="card"
        @click="goToProject(project.id)"
      >
        <h3>{{ project.name }}</h3>
        <p>Click to open workspace</p>
      </div>
      <div v-if="(store.currentUser?.projects || []).length === 0" class="empty-state">
        You don't have any projects yet. Create one through the sidebar!
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMainStore } from '@/stores/main'

const store = useMainStore()
const router = useRouter()

onMounted(async () => {
  if (!store.currentUser) {
    // 若重整網頁遺失狀態，自動再撈取一次確保有帶上 cookie 去拿資料
    await store.loadDashboardData()
    // 若撈完還是沒有 currentUser，代表沒登入，踢回 login
    if (!store.currentUser) {
      router.push('/login')
    }
  }
})

const goToProject = (projectId: number) => {
  router.push(`/projects/${projectId}/code`)
}
</script>

<style scoped>
.project-list-container {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}
.project-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}
.card {
  padding: 1.5rem;
  border: 1px solid var(--medium-gray);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  background: white;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: var(--primary-color);
}
.empty-state {
  color: var(--dark-gray);
  font-style: italic;
  padding: 1rem;
}
</style>
