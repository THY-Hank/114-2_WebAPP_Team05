<template>
  <div class="settings-container">
    <h2>Project Settings</h2>
    
    <div class="members-section">
      <h3>Access Permissions</h3>
      <p>Project memberships are currently controlled globally. Only the Creator mapped to the Owner ID dictates sweeping rights over this workspace.</p>
      <p v-if="isOwner" class="owner-badge">You are the Owner of this Project.</p>
    </div>

    <!-- Danger Zone strictly visible if user is Owner -->
    <div v-if="isOwner" class="danger-zone">
      <h3>Danger Zone</h3>
      <p>Deleting this project is irreversible. It will destroy all associated code files, comments, and member assignments permanently.</p>
      <button class="delete-project-btn" @click="handleDeleteProject">Delete Project</button>
    </div>
    <div v-else class="danger-zone warning">
      <h3>Restricted Danger Zone</h3>
      <p>Only the owner of this project can authorize a catastrophic deletion.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMainStore } from '@/stores/main'

const store = useMainStore()
const router = useRouter()
const route = useRoute()

const projectId = computed(() => Number(route.params.projectId))

// Retrieve the project from the current user bounds
const currentProject = computed(() => {
  if (!store.currentUser) return null
  return store.currentUser.projects.find((p: any) => p.id === projectId.value)
})

const isOwner = computed(() => {
  if (!store.currentUser || !currentProject.value) return false
  return currentProject.value.owner_id === store.currentUser.id
})

const handleDeleteProject = async () => {
  const confirmed = confirm(`Are you absolutely sure you want to delete this workspace? This action CANNOT be undone.`)
  if (confirmed) {
    const success = await store.deleteProject(projectId.value)
    if (success) {
      router.push('/projects')
    } else {
      alert('Failed to delete project. You may not be the owner or a network error occurred.')
    }
  }
}
</script>

<style scoped>
.settings-container {
  padding: 2rem;
  max-width: 800px;
}

.members-section {
  background: white;
  padding: 1.5rem;
  border-radius: var(--border-radius);
  border: 1px solid var(--medium-gray);
  margin-bottom: 2rem;
}
.owner-badge {
  color: var(--primary-color);
  font-weight: 600;
  margin-top: 1rem;
}

.danger-zone {
  background: #fff5f5;
  border: 1px solid #fc8181;
  padding: 1.5rem;
  border-radius: var(--border-radius);
}

.danger-zone h3 {
  color: #c53030;
  margin-top: 0;
}

.danger-zone.warning {
  border-color: #f6ad55;
  background: #fffaf0;
}
.danger-zone.warning h3 {
  color: #dd6b20;
}

.delete-project-btn {
  background: #e53e3e;
  color: white;
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: var(--border-radius);
  font-weight: bold;
  cursor: pointer;
  margin-top: 1rem;
}
.delete-project-btn:hover {
  background: #c53030;
}
</style>
