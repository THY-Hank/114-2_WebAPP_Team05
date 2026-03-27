<template>
  <div class="create-project-container">
    <h2>Create New Project</h2>
    <div class="form-row">
      <input v-model="newProjectName" placeholder="Project Name" @keyup.enter="handleCreate" />
      <button @click="handleCreate">Create Workspace</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMainStore } from '@/stores/main'

const store = useMainStore()
const router = useRouter()
const newProjectName = ref('')

const handleCreate = async () => {
  if (newProjectName.value.trim() !== '') {
    const success = await store.createProject(newProjectName.value)
    if (success) {
      newProjectName.value = ''
      router.push('/projects')
    } else {
      alert('Failed to create project.')
    }
  }
}
</script>

<style scoped>
.create-project-container {
  padding: 2.5rem;
  max-width: 600px;
  background: white;
  border-radius: var(--border-radius);
  border: 1px solid var(--medium-gray);
  margin: 2rem 0;
}
.form-row {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}
.form-row input {
  flex: 1;
  padding: 0.8rem;
  border: 1px solid var(--medium-gray);
  border-radius: var(--border-radius);
  font-size: 1rem;
}
.form-row button {
  padding: 0.8rem 1.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-weight: 600;
  transition: opacity 0.2s;
}
.form-row button:hover {
  opacity: 0.9;
}
</style>
