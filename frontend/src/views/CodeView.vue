<template>
  <div class="code-view-container">
    <div class="code-sidebar">
      <div class="upload-container">
        <h3>Upload File</h3>
        <form @submit.prevent="uploadFile">
          <input type="file" @change="onFileChange" />
          <button type="submit">Upload</button>
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
    </div>
    <div class="code-content">
      <div v-if="selectedFile" class="code-view">
        <h3>{{ selectedFile.name }}</h3>
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useMainStore } from '@/stores/main'
import { useRoute, useRouter } from 'vue-router'

const store = useMainStore()
const router = useRouter()
const route = useRoute()
const selectedFile = ref(null)
const newComment = ref('')
const isFolderOpen = ref(true)
let selectedFileObject = null

const standaloneFiles = computed(() => {
  if (!store.currentUser || store.currentUser.projects.length === 0) {
    return []
  }

  return store.getProjectFiles(store.currentUser.projects[0].id).filter((file) => file.name === 'test.c')
})

const folderFiles = computed(() => {
  if (!store.currentUser || store.currentUser.projects.length === 0) {
    return []
  }

  return store.getProjectFiles(store.currentUser.projects[0].id).filter((file) => file.name !== 'test.c')
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

const onFileChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    selectedFileObject = file
  }
}

const uploadFile = () => {
  if (selectedFileObject && store.currentUser && store.currentUser.projects.length > 0) {
    const reader = new FileReader()
    reader.onload = (e) => {
      store.addFile(store.currentUser.projects[0].id, {
        name: selectedFileObject.name,
        content: e.target.result,
      })
    }
    reader.readAsText(selectedFileObject)
  } else {
    alert('Please select a file and make sure a project is available.')
  }
}

const selectFile = (file) => {
  selectedFile.value = file
}

const addComment = () => {
  if (newComment.value.trim() !== '' && selectedFile.value) {
    store.addComment(selectedFile.value.id, newComment.value)
    newComment.value = ''
  }
}
</script>

<style scoped>
@import '@/assets/code.css';

.code-view-container {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 2rem;
  height: 100%;
}
.code-sidebar {
  background: #fdfdfd;
  padding: 1rem;
  border-radius: var(--border-radius);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
</style>
