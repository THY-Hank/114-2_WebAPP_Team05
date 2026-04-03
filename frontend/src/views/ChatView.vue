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
        <input v-model="newRoomName" placeholder="New room name" class="room-name-input" />
        <button @click="showMemberModal = true" class="select-members-btn">
          {{ selectedMemberIds.length > 0 ? `${selectedMemberIds.length} members selected` : 'Select Members (optional)' }}
        </button>
        <button @click="createChatRoom" class="create-btn">Create Room</button>
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
          <div
            v-if="message.codeSnippet"
            class="code-snippet"
            @click="viewCodeSnippet(message.codeSnippet)"
          >
            <div class="code-snippet-header">
              <strong>{{ message.codeSnippet.fileName }}</strong>
              <span class="line-range">
                {{
                  message.codeSnippet.startLine
                    ? `Lines ${message.codeSnippet.startLine}-${message.codeSnippet.endLine}`
                    : `Line ${message.codeSnippet.line || 1}`
                }}
              </span>
            </div>
            <pre v-if="message.codeSnippet.content" class="code-snippet-content"><code>{{ message.codeSnippet.content }}</code></pre>
          </div>
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
    
    <!-- Member Selection Modal -->
    <div v-if="showMemberModal" class="modal-overlay" @click.self="showMemberModal = false">
      <div class="modal">
        <h3>Select Members for Room</h3>
        <p v-if="projectMembers.length === 0" class="no-members">No members available</p>
        <div v-else class="member-list-modal">
          <div 
            v-for="member in projectMembers" 
            :key="member.id"
            class="member-option"
            :class="{ 'member-option--selected': selectedMemberIds.includes(member.id) }"
            @click="toggleMember(member.id)"
          >
            <span class="member-option-name">{{ member.name || member.email }}</span>
            <span v-if="selectedMemberIds.includes(member.id)" class="member-option-checkmark">✓</span>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="showMemberModal = false" class="primary-btn">Done</button>
          <button v-if="selectedMemberIds.length > 0" @click="selectedMemberIds = []" class="cancel-btn">Clear All</button>
        </div>
      </div>
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
const showMemberModal = ref(false)
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

const toggleMember = (memberId: number) => {
  const index = selectedMemberIds.value.indexOf(memberId)
  if (index > -1) {
    selectedMemberIds.value.splice(index, 1)
  } else {
    selectedMemberIds.value.push(memberId)
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
    query: { 
      file: codeSnippet.fileName, 
      line: codeSnippet.startLine || codeSnippet.line || 1 
    },
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

.room-name-input {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: border-color 0.2s;
  margin-bottom: 0.5rem;
}

.room-name-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 4px rgba(76, 175, 80, 0.2);
}

.select-members-btn {
  width: 100%;
  padding: 0.6rem;
  margin-bottom: 0.5rem;
  background: white;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.select-members-btn:hover {
  background: #f5f5f5;
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.create-btn {
  width: 100%;
  padding: 0.7rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.create-btn:hover {
  background: #45a049;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.modal h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.2rem;
  color: #333;
}

.no-members {
  text-align: center;
  color: #999;
  padding: 1rem;
}

.member-list-modal {
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.member-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.member-option:hover {
  background: #f0f0f0;
  border-color: #d0d0d0;
}

.member-option--selected {
  background: #e8f5e9;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 1px var(--primary-color);
}

.member-option-name {
  font-weight: 500;
  color: #333;
}

.member-option--selected .member-option-name {
  color: #1b5e20;
  font-weight: 600;
}

.member-option-checkmark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: bold;
}

.modal-actions {
  display: flex;
  gap: 0.5rem;
}

.primary-btn {
  flex: 1;
  padding: 0.6rem 1rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.primary-btn:hover {
  background: #45a049;
}

.cancel-btn {
  flex: 1;
  padding: 0.6rem 1rem;
  background: #fff;
  color: #666;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: #f5f5f5;
  border-color: #999;
}
</style>
