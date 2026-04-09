<template>
  <div class="code-view-container">
    <div class="code-sidebar">
      <!-- File Upload Section Component -->
      <FileUploadSection />
      
      <!-- File Explorer Component -->
      <FileExplorer @select-file="selectFile" />
    </div>
    
    <div class="code-content">
      <!-- Code Viewer Component -->
      <CodeViewer 
        :selectedFile="selectedFile"
        @share-full-file="showFullShareModal = true"
        @delete-file="handleDeleteFile"
        @comment-lines="handleLineComment"
        @share-lines="handleLineShare"
        @save-file="handleSaveFile"
      />

      <div v-if="selectedFile" class="version-panel">
        <div class="version-header">
          <h3>Version History</h3>
          <button class="primary-btn" @click="loadVersions">Refresh</button>
        </div>
        <div class="version-controls">
          <label>Compare</label>
          <select v-model="diffFromId" class="room-select">
            <option :value="null" disabled>From version</option>
            <option v-for="v in versions" :key="`from-${v.id}`" :value="v.id">v{{ v.versionNumber }}</option>
          </select>
          <select v-model="diffToId" class="room-select">
            <option :value="null" disabled>To version</option>
            <option v-for="v in versions" :key="`to-${v.id}`" :value="v.id">v{{ v.versionNumber }}</option>
          </select>
          <button class="primary-btn" @click="loadDiff" :disabled="!diffFromId || !diffToId">Show Diff</button>
        </div>
        <pre v-if="versionDiff" class="diff-box">{{ versionDiff }}</pre>
        <ul class="version-list">
          <li v-for="v in versions" :key="v.id" class="version-item">
            <div class="version-main">
              <strong>v{{ v.versionNumber }}</strong>
              <span class="meta">{{ v.changedBy }} · {{ formatTime(v.createdAt) }}</span>
            </div>
            <div class="version-note">{{ v.note || 'No note' }}</div>
            <div class="version-tags" v-if="v.isSnapshot || v.tagName">
              <span v-if="v.isSnapshot" class="tag-pill">Snapshot</span>
              <span v-if="v.tagName" class="tag-pill">{{ v.tagName }}</span>
            </div>
            <div class="version-actions">
              <button
                class="primary-btn"
                v-if="isCurrentProjectOwner"
                @click="markSnapshot(v.id)"
              >Tag/Snapshot</button>
              <button
                class="danger-btn"
                v-if="isCurrentProjectOwner"
                @click="revertToVersion(v.id, v.versionNumber)"
              >Revert</button>
            </div>
          </li>
        </ul>
      </div>
      
      <!-- Comment Section Component -->
      <CommentSection 
        v-if="selectedFile"
        :selectedFile="selectedFile"
        @add-comment="addComment"
      />

      <!-- Line Comment Input Modal -->
      <div v-if="showLineCommentForm" class="modal-overlay" @click.self="showLineCommentForm = false">
        <div class="modal">
          <h3>Add Comment to Lines {{ lineCommentData.start }}-{{ lineCommentData.end }}</h3>
          <textarea v-model="newLineComment" placeholder="Add your comment..."></textarea>
          <div class="modal-actions">
            <button @click="addLineComment" class="primary-btn">Add Comment</button>
            <button @click="showLineCommentForm = false">Cancel</button>
          </div>
        </div>
      </div>

      <!-- Line Share Modal -->
      <div v-if="showLineShareModal" class="modal-overlay" @click.self="showLineShareModal = false">
        <div class="modal">
          <h3>Share Lines {{ lineShareData.start }}-{{ lineShareData.end }} to Chat</h3>
          <p>Select a chat room:</p>
          <select v-model="selectedLineShareRoomId" class="room-select">
            <option disabled :value="null">Choose a room</option>
            <option v-for="room in store.chatRooms" :key="room.id" :value="room.id">
              {{ room.name }}
            </option>
          </select>
          <div class="modal-actions">
            <button @click="shareLineToChat" :disabled="!selectedLineShareRoomId" class="primary-btn">Share</button>
            <button @click="showLineShareModal = false">Cancel</button>
          </div>
        </div>
      </div>

      <!-- Full File Share Modal -->
      <div v-if="showFullShareModal" class="modal-overlay" @click.self="showFullShareModal = false">
        <div class="modal">
          <h3>Share Full File to Chat</h3>
          <p>Select a chat room:</p>
          <select v-model="selectedRoomId" class="room-select">
            <option disabled :value="null">Choose a room</option>
            <option v-for="room in store.chatRooms" :key="room.id" :value="room.id">
              {{ room.name }}
            </option>
          </select>
          <div class="modal-actions">
            <button @click="handleShareToChat" :disabled="!selectedRoomId" class="primary-btn">Share</button>
            <button @click="showFullShareModal = false">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import { computed, ref, watch } from 'vue'
import { useMainStore } from '@/stores/main'
import { useRoute } from 'vue-router'
import FileUploadSection from '@/components/FileUploadSection.vue'
import FileExplorer from '@/components/FileExplorer.vue'
import CodeViewer from '@/components/CodeViewer.vue'
import CommentSection from '@/components/CommentSection.vue'

const store = useMainStore()
const route = useRoute()

const selectedFile = ref<any>(null)
const newLineComment = ref('')

const projectId = computed(() => Number(route.params.projectId))

// Modal states
const showFullShareModal = ref(false)
const showLineCommentForm = ref(false)
const showLineShareModal = ref(false)
const selectedRoomId = ref<number | null>(null)
const selectedLineShareRoomId = ref<number | null>(null)

// Line comment data
const lineCommentData = ref({ start: 0, end: 0 })
const lineShareData = ref({ start: 0, end: 0 })
const versions = ref<any[]>([])
const diffFromId = ref<number | null>(null)
const diffToId = ref<number | null>(null)
const versionDiff = ref('')

const currentProject = computed(() => {
  const list = store.currentUser?.projects || []
  return list.find((p: any) => p.id === projectId.value) || null
})

const isCurrentProjectOwner = computed(() => {
  return !!currentProject.value && currentProject.value.owner_id === store.currentUser?.id
})

const normalizeRange = (start: number, end: number) => ({
  start: Math.min(start, end),
  end: Math.max(start, end),
})

const syncRouteSelection = () => {
  const fileName = route.query.file
  if (fileName) {
    const file = store.files.find((f) => (f.filepath || f.name) === fileName)
    if (file) {
      selectFile(file)
    }
  }
}

watch(() => projectId.value, async (newId) => {
  if (newId) {
    await store.loadProjectFiles(newId)
    await store.loadProjectChatRooms(newId)
    syncRouteSelection()
  }
}, { immediate: true })

watch(() => route.query.file, () => {
  syncRouteSelection()
})

const selectFile = (file: any) => {
  selectedFile.value = file
  loadVersions()
}

const loadVersions = async () => {
  if (!selectedFile.value) {
    versions.value = []
    return
  }
  const result = await store.fetchFileVersions(selectedFile.value.id)
  versions.value = result.success ? result.data : []
}

const formatTime = (isoString: string) => {
  const date = new Date(isoString)
  return date.toLocaleString()
}

const handleSaveFile = async (payload: { content: string; note: string }) => {
  if (!selectedFile.value) return
  const result = await store.updateFileContent(selectedFile.value.id, payload.content, payload.note)
  if (!result.success) {
    alert(result.error || 'Save failed')
    return
  }
  selectedFile.value.content = payload.content
  await loadVersions()
}

const loadDiff = async () => {
  if (!selectedFile.value || !diffFromId.value || !diffToId.value) return
  const result = await store.fetchFileVersionDiff(selectedFile.value.id, diffFromId.value, diffToId.value)
  if (result.success) {
    versionDiff.value = result.data.diff || 'No diff'
    return
  }
  alert(result.error || 'Failed to load diff')
}

const markSnapshot = async (versionId: number) => {
  if (!selectedFile.value) return
  const tagName = prompt('Tag name (optional):', '') || ''
  const result = await store.markVersionSnapshot(selectedFile.value.id, versionId, tagName, true)
  if (!result.success) {
    alert(result.error || 'Failed to tag version')
    return
  }
  await loadVersions()
}

const revertToVersion = async (versionId: number, versionNumber: number) => {
  if (!selectedFile.value) return
  const ok = confirm(`Revert file to version v${versionNumber}?`)
  if (!ok) return
  const note = prompt('Revert note (optional):', `Reverted to version ${versionNumber}`) || ''
  const result = await store.revertFileVersion(selectedFile.value.id, versionId, note)
  if (!result.success) {
    alert(result.error || 'Failed to revert version')
    return
  }
  selectedFile.value.content = result.data.content
  await loadVersions()
}

const addComment = (text: string) => {
  if (text.trim() !== '' && selectedFile.value) {
    store.addComment(selectedFile.value.id, text)
  }
}

const handleDeleteFile = async () => {
  if (!selectedFile.value) return
  if (confirm(`Are you sure you want to delete ${selectedFile.value.name}?`)) {
    const success = await store.deleteFile(selectedFile.value.id)
    if (success) {
      selectedFile.value = null
    } else {
      alert('Failed to delete file. You may lack sufficient permissions.')
    }
  }
}

const handleLineComment = (payload: { start: number; end: number }) => {
  lineCommentData.value = normalizeRange(payload.start, payload.end)
  showLineCommentForm.value = true
}

const handleLineShare = (payload: { start: number; end: number }) => {
  lineShareData.value = normalizeRange(payload.start, payload.end)
  showLineShareModal.value = true
}

const addLineComment = async () => {
  if (!newLineComment.value.trim() || !selectedFile.value) {
    return
  }

  const normalizedRange = normalizeRange(lineCommentData.value.start, lineCommentData.value.end)
  
  await store.addLineComment(selectedFile.value.id, {
    text: newLineComment.value,
    startLine: normalizedRange.start,
    endLine: normalizedRange.end
  })
  
  newLineComment.value = ''
  showLineCommentForm.value = false
}

const shareLineToChat = async () => {
  if (!selectedLineShareRoomId.value || !selectedFile.value) {
    return
  }

  const normalizedRange = normalizeRange(lineShareData.value.start, lineShareData.value.end)
  
  const codeLines = selectedFile.value.content?.split('\n') || []
  const snippetContent = codeLines
    .slice(normalizedRange.start - 1, normalizedRange.end)
    .join('\n')
  
  await store.addLineCodeSnippetMessage(projectId.value, selectedLineShareRoomId.value, {
    fileName: selectedFile.value.filepath || selectedFile.value.name,
    startLine: normalizedRange.start,
    endLine: normalizedRange.end,
    content: snippetContent
  })
  
  alert('Code snippet shared successfully!')
  showLineShareModal.value = false
  selectedLineShareRoomId.value = null
}

const handleShareToChat = async () => {
  if (selectedRoomId.value && selectedFile.value) {
    await store.addCodeSnippetMessage(projectId.value, selectedRoomId.value, {
      fileName: selectedFile.value.filepath || selectedFile.value.name,
      line: 1
    })
    alert('Code shared successfully!')
    showFullShareModal.value = false
    selectedRoomId.value = null
  }
}
</script>

<style scoped>
.code-view-container {
  display: flex;
  flex-direction: row;
  gap: 2rem;
  height: 100%;
  align-items: flex-start;
}

.code-sidebar {
  width: 350px;
  flex-shrink: 0;
  background: #fdfdfd;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-height: 100vh;
  overflow-y: auto;
}

.code-content {
  flex: 1;
  overflow-y: auto;
  max-height: 100vh;
}

.version-panel {
  margin-top: 1rem;
  background: #ffffff;
  border: 1px solid #dbe3ee;
  border-radius: 8px;
  padding: 1rem;
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.version-header h3 {
  margin: 0;
}

.version-controls {
  display: grid;
  grid-template-columns: auto 1fr 1fr auto;
  gap: 0.5rem;
  align-items: center;
}

.version-list {
  margin: 1rem 0 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.version-item {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 0.6rem;
  background: #f9fafb;
}

.version-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.meta {
  color: #64748b;
  font-size: 0.85rem;
}

.version-note {
  margin-top: 0.3rem;
  color: #334155;
  font-size: 0.9rem;
}

.version-tags {
  margin-top: 0.35rem;
  display: flex;
  gap: 0.35rem;
}

.tag-pill {
  font-size: 0.75rem;
  background: #dbeafe;
  color: #1d4ed8;
  padding: 0.2rem 0.45rem;
  border-radius: 999px;
}

.version-actions {
  margin-top: 0.45rem;
  display: flex;
  gap: 0.4rem;
}

.danger-btn {
  padding: 0.45rem 0.7rem;
  border: none;
  border-radius: 4px;
  color: #fff;
  background: #dc2626;
  cursor: pointer;
}

.diff-box {
  margin-top: 0.8rem;
  background: #0f172a;
  color: #e2e8f0;
  padding: 0.75rem;
  border-radius: 6px;
  max-height: 280px;
  overflow: auto;
  font-size: 0.83rem;
}

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
  z-index: 1000;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
}

.modal h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #333;
}

.modal textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  resize: vertical;
  min-height: 80px;
  box-sizing: border-box;
}

.modal textarea:focus {
  outline: none;
  border-color: #4caf50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
}

.room-select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin: 1rem 0;
  box-sizing: border-box;
  font-size: 0.9rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
}

.primary-btn {
  padding: 0.6rem 1.5rem;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.primary-btn:hover:not(:disabled) {
  background: #45a049;
}

.primary-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.modal-actions button:not(.primary-btn) {
  padding: 0.6rem 1rem;
  border: 1px solid #ddd;
  background: #f0f0f0;
  color: #333;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.modal-actions button:not(.primary-btn):hover {
  background: #e0e0e0;
  border-color: #999;
}

@media (max-width: 900px) {
  .code-view-container {
    flex-direction: column;
  }
  .code-sidebar {
    width: 100%;
  }
}
</style>
