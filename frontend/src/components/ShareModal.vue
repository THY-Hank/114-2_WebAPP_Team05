<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h3>Share a File Snippet</h3>
      <div class="file-list">
        <ul>
          <li
            v-for="file in files"
            :key="file.id"
            @click="selectedFile = file"
            :class="{ 'active-file': selectedFile && selectedFile.id === file.id }"
          >
            {{ file.name }}
          </li>
        </ul>
      </div>
      <div class="modal-actions">
        <button @click="$emit('close')">Cancel</button>
        <button @click="share" :disabled="!selectedFile">Share</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useMainStore } from '@/stores/main'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close', 'share'])

const store = useMainStore()
const files = computed(() => store.files)
const selectedFile = ref<any>(null)

const share = () => {
  if (selectedFile.value) {
    emit('share', selectedFile.value)
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: var(--border-radius);
  width: 90%;
  max-width: 500px;
}

.file-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid var(--medium-gray);
  border-radius: var(--border-radius);
  margin: 1rem 0;
}

.file-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.file-list li {
  padding: 0.5rem 1rem;
  cursor: pointer;
}

.file-list li:hover {
  background: var(--light-gray);
}

.file-list .active-file {
  background-color: var(--primary-color);
  color: white;
}

.modal-actions {
  text-align: right;
  margin-top: 1rem;
}

.modal-actions button {
  margin-left: 1rem;
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius);
  border: 1px solid var(--medium-gray);
  cursor: pointer;
}

.modal-actions button:last-child {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}
</style>
