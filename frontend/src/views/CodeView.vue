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
      />
      
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
import { computed, onMounted, ref, watch } from 'vue'
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

watch(() => projectId.value, (newId) => {
  if (newId) {
    store.loadProjectFiles(newId)
    store.loadProjectChatRooms(newId)
  }
}, { immediate: true })

onMounted(() => {
  const fileName = route.query.file
  if (fileName) {
    const file = store.files.find((f) => f.name === fileName)
    if (file) {
      selectFile(file)
    }
  }
})

const selectFile = (file: any) => {
  selectedFile.value = file
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
  lineCommentData.value = payload
  showLineCommentForm.value = true
}

const handleLineShare = (payload: { start: number; end: number }) => {
  lineShareData.value = payload
  showLineShareModal.value = true
}

const addLineComment = async () => {
  if (!newLineComment.value.trim() || !selectedFile.value) {
    return
  }
  
  await store.addLineComment(selectedFile.value.id, {
    text: newLineComment.value,
    startLine: lineCommentData.value.start,
    endLine: lineCommentData.value.end
  })
  
  newLineComment.value = ''
  showLineCommentForm.value = false
}

const shareLineToChat = async () => {
  if (!selectedLineShareRoomId.value || !selectedFile.value) {
    return
  }
  
  const codeLines = selectedFile.value.content?.split('\n') || []
  const snippetContent = codeLines
    .slice(lineShareData.value.start - 1, lineShareData.value.end)
    .join('\n')
  
  await store.addLineCodeSnippetMessage(projectId.value, selectedLineShareRoomId.value, {
    fileName: selectedFile.value.name,
    startLine: lineShareData.value.start,
    endLine: lineShareData.value.end,
    content: snippetContent
  })
  
  alert('Code snippet shared successfully!')
  showLineShareModal.value = false
  selectedLineShareRoomId.value = null
}

const handleShareToChat = async () => {
  if (selectedRoomId.value && selectedFile.value) {
    await store.addCodeSnippetMessage(projectId.value, selectedRoomId.value, {
      fileName: selectedFile.value.name,
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
