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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMainStore } from '@/stores/main'
import ShareModal from '@/components/ShareModal.vue'

const store = useMainStore()
const router = useRouter()

const selectedRoom = ref<any>(null)
const newRoomName = ref('')
const newMessage = ref('')
const showShareModal = ref(false)

const selectChatRoom = (room: any) => {
  selectedRoom.value = room
}

const createChatRoom = () => {
  if (newRoomName.value.trim() !== '') {
    store.addChatRoom(newRoomName.value)
    newRoomName.value = ''
  }
}

const sendMessage = () => {
  if (newMessage.value.trim() !== '' && selectedRoom.value) {
    store.addChatMessage(selectedRoom.value.id, newMessage.value)
    newMessage.value = ''
  }
}

const viewCodeSnippet = (codeSnippet: any) => {
  router.push({
    name: 'code',
    query: { file: codeSnippet.fileName, line: codeSnippet.line },
  })
}

const handleShare = (file: any) => {
  if (selectedRoom.value) {
    store.addCodeSnippetMessage(selectedRoom.value.id, {
      fileName: file.name
    })
  }
  showShareModal.value = false
}
</script>

<style scoped>
@import '@/assets/chat.css';
</style>
