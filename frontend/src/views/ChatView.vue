<template>
  <div class="chat-layout">
    <div class="sidebar">
      <div class="chat-list">
        <h3>Chat Rooms</h3>
        <ul>
          <li v-for="room in store.chatRooms" :key="room.id" @click="selectChatRoom(room)">
            {{ room.name }}
          </li>
        </ul>
      </div>
      <div class="new-chat-form">
        <input v-model="newRoomName" placeholder="New room name" />
        <div v-if="projectMembers.length > 0" class="member-selection">
          <p>Private Room Members (optional):</p>
          <label v-for="member in projectMembers" :key="member.id">
            <input type="checkbox" :value="member.id" v-model="selectedMemberIds" />
            {{ member.name || member.email }}
          </label>
        </div>
        <button @click="createChatRoom">Create Room</button>
      </div>
    </div>
    <div class="chat-container" v-if="selectedRoom">
      <h2>{{ selectedRoom.name }}</h2>
      <div class="chat-box">
        <div v-for="message in selectedRoom.messages" :key="message.id" class="message">
          <p>
            <strong class="author">{{ message.author }}</strong>
          </p>
          <p v-if="message.text">{{ message.text }}</p>
          <p
            v-if="message.codeSnippet"
            class="code-snippet"
            @click="viewCodeSnippet(message.codeSnippet)"
          >
            {{ message.codeSnippet.fileName }}:{{ message.codeSnippet.line || 'file' }}
          </p>
        </div>
      </div>
      <div class="chat-input">
        <input v-model="newMessage" placeholder="Type a message..." @keyup.enter="sendMessage" />
        <button @click="sendMessage">Send</button>
        <button @click="showShareModal = true">Share Snippet</button>
      </div>
    </div>
    <div class="chat-container" v-else>
      <p>Select a chat room to start chatting.</p>
    </div>
    <ShareModal :show="showShareModal" @close="showShareModal = false" @share="handleShare" />
  </div>
</template>

<script setup lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import { computed, ref, watch, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMainStore } from '@/stores/main'
import ShareModal from '@/components/ShareModal.vue'

const store = useMainStore()
const router = useRouter()
const route = useRoute()

const selectedRoom = ref<any>(null)
const newRoomName = ref('')
const newMessage = ref('')
const showShareModal = ref(false)
const projectId = computed(() => Number(route.params.projectId))

watch(() => projectId.value, async (newProjectId) => {
  if (!newProjectId) {
    selectedRoom.value = null
    store.chatRooms = []
    return
  }

  await store.loadProjectChatRooms(newProjectId)
  selectedRoom.value = store.chatRooms[0] || null
}, { immediate: true })

const selectChatRoom = (room: any) => {
  selectedRoom.value = room
}

const selectedMemberIds = ref<number[]>([])

const projectMembers = computed(() => {
  if (!store.currentUser) return []
  const proj = store.currentUser.projects.find((p: any) => p.id === projectId.value)
  return proj ? proj.members || [] : []
})

const createChatRoom = async () => {
  if (newRoomName.value.trim() !== '') {
    const mems = selectedMemberIds.value.length > 0 ? selectedMemberIds.value : undefined
    await store.addChatRoom(projectId.value, newRoomName.value, mems)
    selectedRoom.value = store.chatRooms[store.chatRooms.length - 1] || selectedRoom.value
    newRoomName.value = ''
    selectedMemberIds.value = []
  }
}

const sendMessage = async () => {
  if (newMessage.value.trim() !== '' && selectedRoom.value) {
    await store.addChatMessage(projectId.value, selectedRoom.value.id, newMessage.value)
    newMessage.value = ''
  }
}

const viewCodeSnippet = (codeSnippet: any) => {
  router.push({
    name: 'code',
    params: { projectId: projectId.value },
    query: { file: codeSnippet.fileName, line: codeSnippet.line },
  })
}

const handleShare = (file: any) => {
  if (selectedRoom.value) {
    store.addCodeSnippetMessage(projectId.value, selectedRoom.value.id, {
      fileName: file.name
    })
  }
  showShareModal.value = false
}

watch(() => selectedRoom.value, (newRoom) => {
  if (newRoom) {
    store.connectWebSocket(newRoom.id)
  }
})

onUnmounted(() => {
  if (store.chatSocket) {
    store.chatSocket.close()
    store.chatSocket = null
  }
})
</script>

<style scoped>
@import '@/assets/chat.css';

.member-selection {
  margin: 10px 0;
  max-height: 150px;
  overflow-y: auto;
  font-size: 0.9em;
}

.member-selection label {
  display: block;
  margin-bottom: 5px;
  cursor: pointer;
}
</style>
