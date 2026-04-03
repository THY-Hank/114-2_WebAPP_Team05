<template>
  <div class="file-explorer">
    <h3>📁 Files</h3>
    <div v-for="folderPath in sortedFolders" :key="folderPath" class="folder-section">
      <div 
        class="folder-header" 
        @click="toggleFolder(folderPath)"
        :class="{ 'expanded': expandedFolders.has(folderPath) }"
      >
        <span class="folder-toggle">{{ expandedFolders.has(folderPath) ? '▼' : '▶' }}</span>
        <span class="folder-name">{{ folderPath === 'root' ? '📁 root' : '📁 ' + folderPath }}</span>
      </div>
      
      <div v-if="expandedFolders.has(folderPath)" class="folder-files">
        <div
          v-for="file in getFilesInFolder(folderPath)"
          :key="file.id"
          class="file-item"
          @click="selectFile(file)"
        >
          <span class="file-icon">{{ getFileIcon(file.name) }}</span>
          <span class="file-item-name">{{ file.name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useMainStore } from '@/stores/main'

const route = useRoute()
const store = useMainStore()

const expandedFolders = ref(new Set<string>(['root']))

const emit = defineEmits<{
  'select-file': [file: any]
}>()

const projectId = computed(() => parseInt(route.params.projectId as string, 10))

const projectFiles = computed(() => {
  return store.getProjectFiles(projectId.value)
})

const groupedFiles = computed(() => {
  const groups: Record<string, any[]> = {}
  projectFiles.value.forEach((file) => {
    const folderPath = file.filepath ? file.filepath.split('/').slice(0, -1).join('/') || 'root' : 'root'
    if (!groups[folderPath]) {
      groups[folderPath] = []
    }
    groups[folderPath].push(file)
  })
  return groups
})

const sortedFolders = computed(() => {
  return Object.keys(groupedFiles.value).sort((a, b) => {
    if (a === 'root') return -1
    if (b === 'root') return 1
    return a.localeCompare(b)
  })
})

const getFilesInFolder = (folderPath: string) => {
  return groupedFiles.value[folderPath] || []
}

const toggleFolder = (folderPath: string) => {
  if (expandedFolders.value.has(folderPath)) {
    expandedFolders.value.delete(folderPath)
  } else {
    expandedFolders.value.add(folderPath)
  }
}

const selectFile = (file: any) => {
  emit('select-file', file)
}

const getFileIcon = (fileName: string) => {
  const ext = fileName.split('.').pop()?.toLowerCase()
  const iconMap: Record<string, string> = {
    'ts': '🔵',
    'tsx': '⚛️',
    'vue': '💚',
    'js': '🟨',
    'jsx': '⚛️',
    'py': '🐍',
    'java': '☕',
    'cpp': '⬜',
    'c': '⬜',
    'h': '⬜',
    'cs': '🔷',
    'rb': '💎',
    'go': '🐹',
    'rs': '🦀',
    'html': '🌐',
    'css': '🎨',
    'json': '📋',
    'xml': '📄',
    'yaml': '⚙️',
    'yml': '⚙️',
    'md': '📝',
  }
  return iconMap[ext || ''] || '📄'
}
</script>

<style scoped>
.file-explorer {
  flex-grow: 1;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 1rem;
  background: white;
}

.file-explorer h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  color: #333;
}

.folder-section {
  margin-bottom: 0.5rem;
}

.folder-header {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
  user-select: none;
}

.folder-header:hover {
  background: #f0f0f0;
}

.folder-header.expanded {
  background: #e8f5e9;
}

.folder-toggle {
  display: inline-block;
  width: 1rem;
  text-align: center;
  margin-right: 0.3rem;
  font-size: 0.8rem;
}

.folder-name {
  font-weight: 500;
  color: #333;
}

.folder-files {
  margin-left: 1rem;
  margin-top: 0.25rem;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 0.4rem 0.5rem;
  margin: 0.25rem 0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-item:hover {
  background: #f5f5f5;
}

.file-item.file-selected {
  background: #4caf50;
  color: white;
}

.file-icon {
  margin-right: 0.4rem;
  flex-shrink: 0;
}

.file-item-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
