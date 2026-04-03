<template>
  <div class="upload-container">
    <h3>📤 Upload Files</h3>
    <div class="upload-zone" 
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="onFileDrop"
      :class="{ 'drag-over': isDragging }">
      <p>Drag files here</p>
      <p style="font-size: 0.85rem; color: #999;">or</p>
      <input 
        type="file" 
        multiple 
        @change="onFileChange" 
        ref="fileInput"
        style="display: none;"
      />
      <button type="button" @click="browseFiles" class="browse-btn">
        Browse Files
      </button>
    </div>
    
    <!-- File List Preview -->
    <div v-if="selectedFilesList.length > 0" class="file-list-preview">
      <p class="preview-title">{{ (selectedFilesList as File[]).length }} file(s) selected:</p>
      <ul class="preview-list">
        <li v-for="(file, i) in (selectedFilesList as File[])" :key="i" class="preview-item">
          <span class="file-icon">📄</span>
          <span class="file-info">
            <div class="file-name">{{ file.name }}</div>
            <div class="file-size">{{ (file.size / 1024).toFixed(1) }} KB</div>
          </span>
          <button @click="removeFile(i)" class="remove-btn" type="button">✕</button>
        </li>
      </ul>
      <button 
        @click="uploadFile" 
        class="upload-btn"
        :disabled="uploading"
      >
        {{ uploading ? 'Uploading...' : 'Upload All' }}
      </button>
      <button 
        @click="clearFileSelection" 
        class="cancel-btn"
        type="button"
      >
        Clear Selection
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useMainStore } from '@/stores/main'
import { projectsApi } from '@/api/projects'

const route = useRoute()
const store = useMainStore()

const isDragging = ref(false)
const selectedFilesList = ref<File[]>([])
const uploading = ref(false)
const fileInput = ref<HTMLInputElement>()

const projectId = computed(() => parseInt(route.params.projectId as string, 10))

const onFileDrop = (event: DragEvent) => {
  isDragging.value = false
  const files = event.dataTransfer?.files
  if (files) {
    selectedFilesList.value = Array.from(files)
  }
}

const onFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files) {
    selectedFilesList.value = Array.from(files)
  }
}

const browseFiles = () => {
  fileInput.value?.click()
}

const removeFile = (index: number) => {
  selectedFilesList.value.splice(index, 1)
}

const clearFileSelection = () => {
  selectedFilesList.value = []
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const uploadFile = async () => {
  if (selectedFilesList.value.length === 0) return

  uploading.value = true
  try {
    const uploadPromises = (selectedFilesList.value as File[]).map((file) => {
      return new Promise<string>((resolve) => {
        const reader = new FileReader()
        reader.onload = (event) => {
          const content = event.target?.result as string
          resolve(content)
        }
        reader.readAsText(file)
      }).then((content) => {
        const filepath = file.name
        return projectsApi.addFile(projectId.value, {
          name: file.name,
          filepath: filepath,
          content: content,
        })
      })
    })

    await Promise.all(uploadPromises)
    selectedFilesList.value = []
    if (fileInput.value) {
      fileInput.value.value = ''
    }
    await store.loadProjectFiles(projectId.value)
  } catch (error) {
    console.error('Upload error:', error)
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.upload-container {
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #f9f9f9;
}

.upload-container h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  color: #333;
}

.upload-zone {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 2rem 1rem;
  text-align: center;
  background: white;
  transition: all 0.3s ease;
  cursor: pointer;
}

.upload-zone:hover {
  border-color: #4caf50;
  background: #f0f8f0;
}

.upload-zone.drag-over {
  border-color: #4caf50;
  background: #e8f5e9;
  box-shadow: 0 0 8px rgba(76, 175, 80, 0.2);
}

.upload-zone p {
  margin: 0.5rem 0;
  color: #666;
  font-size: 0.9rem;
}

.browse-btn {
  padding: 0.6rem 1.2rem;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.browse-btn:hover {
  background: #45a049;
}

.file-list-preview {
  margin-top: 1rem;
  padding: 1rem;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
}

.preview-title {
  margin: 0 0 0.75rem 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
}

.preview-list {
  list-style: none;
  padding: 0;
  margin: 0 0 1rem 0;
  max-height: 150px;
  overflow-y: auto;
}

.preview-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.8rem;
  background: #f5f5f5;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  border: 1px solid #e0e0e0;
}

.file-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  width: 0;
}

.file-name {
  color: #333;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  color: #999;
  font-size: 0.8rem;
  margin-top: 0.2rem;
  white-space: nowrap;
}

.remove-btn {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  padding: 0;
  margin: 0;
  border: none;
  background: rgba(255, 82, 82, 0.6);
  color: white;
  border-radius: 50%;
  cursor: pointer;
  font-size: 0.7rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  line-height: 1;
}

.remove-btn:hover {
  background: rgba(255, 82, 82, 0.9);
  transform: scale(1.1);
}

.upload-btn {
  width: 100%;
  padding: 0.7rem;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 0.5rem;
}

.upload-btn:hover:not(:disabled) {
  background: #45a049;
}

.upload-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.cancel-btn {
  width: 100%;
  padding: 0.6rem;
  background: #f0f0f0;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.cancel-btn:hover {
  background: #e0e0e0;
}
</style>
