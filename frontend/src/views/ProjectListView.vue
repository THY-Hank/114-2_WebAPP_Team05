<template>
  <div class="project-list-container">
    <div class="project-list-header">
      <p class="eyebrow">Dashboard</p>
      <h2>Your Projects</h2>
      <p class="description">選擇一個專案繼續協作，或從左側建立新的工作空間。</p>
    </div>

    <div class="project-cards">
      <div
        v-for="project in store.currentUser?.projects || []"
        :key="project.id"
        class="card"
        @click="goToProject(project.id)"
      >
        <div class="card-glow" aria-hidden="true"></div>
        <h3>{{ project.name }}</h3>
        <p>Open workspace and continue code, comments, and project chat.</p>
      </div>
      <div v-if="(store.currentUser?.projects || []).length === 0" class="empty-state">
        <p class="empty-title">No projects yet</p>
        <p>You don't have any projects yet. Create one through the sidebar to get started.</p>
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
  position: relative;
  overflow: hidden;
  max-width: 1040px;
  margin: 0 auto;
  padding: 2.5rem;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 28px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.03), transparent 24%),
    rgba(11, 18, 32, 0.76);
  box-shadow:
    0 24px 80px rgba(0, 0, 0, 0.24),
    inset 0 1px 0 rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(16px);
}

.project-list-header {
  position: relative;
  z-index: 1;
  margin-bottom: 2rem;
}

.eyebrow {
  margin: 0 0 0.6rem;
  color: #7dd3fc;
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.3em;
  text-transform: uppercase;
}

.project-list-container h2 {
  margin: 0;
  color: #f8fafc;
  font-size: clamp(2rem, 3vw, 2.8rem);
  line-height: 1.05;
}

.description {
  max-width: 36rem;
  margin: 0.9rem 0 0;
  color: #94a3b8;
  font-size: 1rem;
  line-height: 1.7;
}

.project-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.25rem;
}

.card {
  position: relative;
  overflow: hidden;
  min-height: 180px;
  padding: 1.5rem;
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 22px;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    border-color 0.2s ease;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.03), transparent),
    rgba(15, 23, 42, 0.9);
}

.card-glow {
  position: absolute;
  top: -48px;
  right: -32px;
  width: 140px;
  height: 140px;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.2) 0%, rgba(56, 189, 248, 0) 72%);
  pointer-events: none;
}

.card h3,
.card p {
  position: relative;
  z-index: 1;
}

.card h3 {
  margin: 0 0 0.85rem;
  color: #f8fafc;
  font-size: 1.2rem;
}

.card p {
  margin: 0;
  color: #94a3b8;
  line-height: 1.6;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.34);
  border-color: rgba(56, 189, 248, 0.28);
}

.empty-state {
  grid-column: 1 / -1;
  padding: 2rem;
  border: 1px dashed rgba(148, 163, 184, 0.24);
  border-radius: 22px;
  background: rgba(15, 23, 42, 0.55);
  color: #94a3b8;
}

.empty-title {
  margin: 0 0 0.5rem;
  color: #f8fafc;
  font-size: 1.1rem;
  font-weight: 700;
}

.empty-state p:last-child {
  margin: 0;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .project-list-container {
    padding: 1.6rem;
    border-radius: 22px;
  }

  .project-cards {
    grid-template-columns: 1fr;
  }
}
</style>
