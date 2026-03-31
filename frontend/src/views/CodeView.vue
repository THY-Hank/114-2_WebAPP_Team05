<template>
  <div class="code-view-container">
    <div class="code-sidebar">
      <div class="upload-container">
        <h3>Upload Files</h3>
        <form @submit.prevent="uploadFile">
          <input type="file" multiple @change="onFileChange" ref="fileInput" />
          <button type="submit">Upload All</button>
        </form>
      </div>
      <div class="file-explorer">
        <h3>Files</h3>
        <ul v-if="store.currentUser && store.currentUser.projects.length > 0">
          <li
            v-for="file in standaloneFiles"
            :key="file.id"
            @click="selectFile(file)"
            :class="{ 'active-file': selectedFile && selectedFile.id === file.id }"
          >
            {{ file.name }}
          </li>
          <li>
            <button class="folder-toggle" type="button" @click="isFolderOpen = !isFolderOpen">
              <span>{{ isFolderOpen ? 'v' : '>' }}</span>
              <span>src</span>
            </button>
            <ul v-if="isFolderOpen" class="folder-children">
              <li
                v-for="file in folderFiles"
                :key="file.id"
                @click="selectFile(file)"
                :class="{ 'active-file': selectedFile && selectedFile.id === file.id }"
              >
                {{ file.name }}
              </li>
            </ul>
          </li>
        </ul>
      </div>
      <div class="invite-container">
        <h3>Invite Member</h3>
        <div class="invite-form">
          <input v-model="newMemberEmail" placeholder="User Email" @keyup.enter="handleInvite" />
          <button @click="handleInvite">Add</button>
        </div>
      </div>
    </div>
    <div class="code-content">
      <div v-if="selectedFile" class="code-view">
        <div class="code-header" style="display: flex; justify-content: space-between; align-items: center;">
          <h3>{{ selectedFile.name }}</h3>
          <div>
            <button class="share-btn" @click="showShareModal = true">Share to Chat</button>
            <button class="delete-file-btn" @click="handleDeleteFile">Delete File</button>
          </div>
        </div>
        <pre><code>{{ selectedFile.content }}</code></pre>
        <div class="comments-section">
          <h4>Comments</h4>
          <div v-for="comment in selectedFile.comments" :key="comment.id" class="comment">
            <p>
              <strong>{{ comment.author }}</strong>
            </p>
            <p>{{ comment.text }}</p>
          </div>
          <div class="comment-form">
            <textarea v-model="newComment" placeholder="Add a comment..."></textarea>
            <button @click="addComment">Add Comment</button>
          </div>
        </div>
      </div>
      <div v-else>
        <p>Select a file to view its content and comments.</p>
      </div>

      <!-- Share Modal -->
      <div v-if="showShareModal" class="share-modal-overlay">
        <div class="share-modal">
          <h3>Share to Chat</h3>
          <p>Select a chat room:</p>
          <select v-model="selectedRoomId" class="room-select">
            <option disabled :value="null">Choose a room</option>
            <option v-for="room in store.chatRooms" :key="room.id" :value="room.id">
              {{ room.name }}
            </option>
          </select>
          <div class="modal-actions">
            <button @click="handleShareToChat" :disabled="!selectedRoomId" class="primary-btn">Share</button>
            <button @click="showShareModal = false">Cancel</button>
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
import { useRoute, useRouter } from 'vue-router'

const store = useMainStore()
const router = useRouter()
const route = useRoute()
const selectedFile = ref<any>(null)
const newComment = ref('')
const isFolderOpen = ref(true)

let selectedFilesList: File[] = []
const fileInput = ref<any>(null)

const projectId = computed(() => Number(route.params.projectId))
const newMemberEmail = ref('')

const showShareModal = ref(false)
const selectedRoomId = ref<number | null>(null)

watch(() => projectId.value, (newId) => {
  if (newId) {
    store.loadProjectFiles(newId)
    store.loadProjectChatRooms(newId)
  }
}, { immediate: true })

const standaloneFiles = computed(() => {
  if (!store.currentUser) {
    return []
  }
  return store.getProjectFiles(projectId.value).filter((file: any) => file.name === 'test.c')
})

const folderFiles = computed(() => {
  if (!store.currentUser) {
    return []
  }
  return store.getProjectFiles(projectId.value).filter((file: any) => file.name !== 'test.c')
})

onMounted(() => {
  const fileName = route.query.file
  if (fileName) {
    const file = store.files.find((f) => f.name === fileName)
    if (file) {
      selectFile(file)
    }
  }
})

const onFileChange = (e: any) => {
  selectedFilesList = Array.from(e.target?.files || [])
}

const uploadFile = () => {
  if (selectedFilesList.length > 0 && store.currentUser) {
    selectedFilesList.forEach((file) => {
      const reader = new FileReader()
      reader.onload = (e: any) => {
        store.addFile(projectId.value, {
          name: file.name,
          content: e.target?.result as string,
        })
      }
      reader.readAsText(file)
    })
    
    // Clear selections
    selectedFilesList = []
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  } else {
    alert('Please select at least one file to upload.')
  }
}

const handleInvite = async () => {
  if (newMemberEmail.value.trim() !== '') {
    const success = await store.addProjectMember(projectId.value, newMemberEmail.value)
    if (success) {
      alert('Member invited successfully!')
      newMemberEmail.value = ''
    } else {
      alert('Failed to invite member. Make sure the email is correct and exists.')
    }
  }
}

const selectFile = (file: any) => {
  selectedFile.value = file
}

const addComment = () => {
  if (newComment.value.trim() !== '' && selectedFile.value) {
    store.addComment(selectedFile.value.id, newComment.value)
    newComment.value = ''
  }
}

const handleDeleteFile = async () => {
  if (confirm(`Are you sure you want to delete ${selectedFile.value.name}?`)) {
    const success = await store.deleteFile(selectedFile.value.id)
    if (success) {
      selectedFile.value = null
    } else {
      alert('Failed to delete file. You may lack sufficient permissions.')
    }
  }
}

const handleShareToChat = async () => {
  if (selectedRoomId.value && selectedFile.value) {
    await store.addCodeSnippetMessage(projectId.value, selectedRoomId.value, {
      fileName: selectedFile.value.name,
      line: 1
    })
    alert('Code shared successfully!')
    showShareModal.value = false
    selectedRoomId.value = null
  }
}
</script>

<style scoped>
@import '@/assets/code.css';

.code-view-container {
  display: flex;
  flex-direction: row;
  gap: 2rem;
  height: 100%;
  align-items: flex-start;
}
.code-sidebar {
  width: 250px;
  flex-shrink: 0;
  background: #fdfdfd;
  padding: 1rem;
  border-radius: var(--border-radius);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.invite-container h3 {
  margin-bottom: 0.5rem;
}

.invite-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.delete-file-btn {
  background: var(--dark-red, #dc3545);
  color: white;
  padding: 0.3rem 0.8rem;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
}
.delete-file-btn:hover { opacity: 0.9; }

.invite-form input {
  padding: 0.4rem;
  border: 1px solid var(--medium-gray);
  border-radius: 4px;
}

.invite-form button {
  padding: 0.4rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

@media (max-width: 900px) {
  .code-view-container {
    flex-direction: column;
  }
  .code-sidebar {
    width: 100%;
  }
}

.share-modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000;
}
.share-modal {
  background: white; padding: 20px; border-radius: 8px; width: 300px;
}
.room-select {
  width: 100%; padding: 8px; margin: 10px 0; border: 1px solid var(--medium-gray); border-radius: 4px;
}
.modal-actions { margin-top: 15px; display: flex; gap: 10px; justify-content: flex-end; }
.modal-actions button { padding: 6px 12px; border-radius: 4px; border: none; cursor: pointer; }
.primary-btn { background: var(--primary-color); color: white; }
.primary-btn:disabled { background: var(--medium-gray); cursor: not-allowed; }
.share-btn { margin-right: 10px; padding: 0.3rem 0.8rem; background: var(--primary-color); color: white; border: none; border-radius: var(--border-radius); cursor: pointer; }
</style>
