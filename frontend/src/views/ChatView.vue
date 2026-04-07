<template>
  <div class="chat-layout">
    <aside class="sidebar">
      <div class="chat-sidebar-header">
        <div>
          <p class="sidebar-eyebrow">Rooms</p>
          <h3>Team Chat</h3>
        </div>
        <p class="sidebar-meta">{{ store.chatRooms.length }} room(s)</p>
      </div>

      <div class="chat-list">
        <ul>
          <li
            v-for="room in store.chatRooms"
            :key="room.id"
            class="chat-room-item"
            :class="{ active: selectedRoom?.id === room.id }"
            @click="selectChatRoom(room)"
          >
            <div>
              <strong>{{ room.name }}</strong>
              <p>{{ room.unreadCount ? `${room.unreadCount} unread` : 'Up to date' }}</p>
            </div>
            <span v-if="room.unreadCount" class="room-badge">{{ room.unreadCount }}</span>
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
    </aside>

    <section v-if="selectedRoom" class="chat-container">
      <header class="chat-header">
        <div>
          <div class="chat-header-title-row">
            <h2 v-if="!isEditingRoomName">{{ selectedRoom.name }}</h2>
            <input
              v-else
              v-model="editedRoomName"
              class="room-edit-input"
              @keyup.enter="saveRoomName"
            />
            <button class="subtle-btn" @click="toggleRoomEdit">
              {{ isEditingRoomName ? 'Cancel' : 'Rename' }}
            </button>
            <button
              v-if="isEditingRoomName"
              class="subtle-btn"
              :disabled="!editedRoomName.trim()"
              @click="saveRoomName"
            >
              Save
            </button>
            <button
              v-if="selectedRoom.name !== 'General'"
              class="danger-link"
              @click="removeRoom"
            >
              Delete
            </button>
          </div>
          <p class="chat-header-meta">
            {{ pinnedMessages.length }} pinned · {{ filteredMessages.length }} visible messages
          </p>
        </div>
        <div class="chat-tools">
          <input
            v-model="searchQuery"
            placeholder="Search messages, snippets, mentions"
            class="search-input"
          />
          <button class="secondary-tool-btn" @click="showShareModal = true">Share Snippet</button>
        </div>
      </header>

      <div v-if="pinnedMessages.length" class="pinned-strip">
        <div v-for="message in pinnedMessages" :key="`pinned-${message.id}`" class="pinned-card">
          <span class="pinned-label">Pinned</span>
          <strong>{{ message.author }}</strong>
          <p>{{ message.text || message.codeSnippet?.fileName }}</p>
        </div>
      </div>

      <div class="chat-box">
        <div v-for="message in filteredMessages" :key="message.id" class="message">
          <div class="message-header">
            <div>
              <strong class="author">{{ message.author }}</strong>
              <span class="message-meta">
                {{ formatTimestamp(message.createdAt) }}
                <span v-if="message.readByCount"> · read by {{ message.readByCount }}</span>
              </span>
            </div>
            <button class="pin-btn" @click="togglePinned(message)">
              {{ message.isPinned ? 'Unpin' : 'Pin' }}
            </button>
          </div>

          <p v-if="message.text" class="message-text">
            <template v-for="(segment, index) in highlightMentions(message.text)" :key="`${message.id}-${index}`">
              <span v-if="segment.isMention" class="mention-chip">{{ segment.value }}</span>
              <span v-else>{{ segment.value }}</span>
            </template>
          </p>

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

      <div v-if="mentionSuggestions.length" class="mention-suggestions">
        <button
          v-for="member in mentionSuggestions"
          :key="member.id"
          type="button"
          class="mention-option"
          @click="applyMention(member)"
        >
          @{{ member.name || member.email.split('@')[0] }}
        </button>
      </div>

      <div class="chat-input">
        <input
          v-model="newMessage"
          placeholder="Type a message... try @teammate"
          @keyup.enter="sendMessage"
        />
        <button @click="sendMessage">Send</button>
      </div>
    </section>

    <section v-else class="chat-container empty-chat">
      <p>Select a chat room to start chatting.</p>
    </section>

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
import { computed, onUnmounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMainStore } from '@/stores/main'
import ShareModal from '@/components/ShareModal.vue'

const store = useMainStore()
const router = useRouter()
const route = useRoute()

const selectedRoomId = ref<number | null>(null)
const newRoomName = ref('')
const newMessage = ref('')
const searchQuery = ref('')
const showShareModal = ref(false)
const showMemberModal = ref(false)
const isEditingRoomName = ref(false)
const editedRoomName = ref('')
const selectedMemberIds = ref<number[]>([])

const projectId = computed(() => Number(route.params.projectId))
const selectedRoom = computed(() => store.chatRooms.find((room) => room.id === selectedRoomId.value) || null)

watch(() => projectId.value, async (newProjectId) => {
  if (!newProjectId) {
    selectedRoomId.value = null
    store.chatRooms = []
    return
  }

  await store.loadProjectChatRooms(newProjectId)
  selectedRoomId.value = store.chatRooms[0]?.id || null
}, { immediate: true })

watch(selectedRoomId, async (roomId) => {
  if (roomId) {
    store.connectWebSocket(roomId)
    await store.markChatRoomRead(projectId.value, roomId)
  }
})

const projectMembers = computed(() => {
  if (!store.currentUser) return []
  const proj = store.currentUser.projects.find((p: any) => p.id === projectId.value)
  return proj ? proj.members || [] : []
})

const pinnedMessages = computed(() => (selectedRoom.value?.messages || []).filter((message: any) => message.isPinned))

const filteredMessages = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  const messages = selectedRoom.value?.messages || []
  if (!query) {
    return messages
  }

  return messages.filter((message: any) => {
    const haystack = [
      message.author,
      message.text,
      message.codeSnippet?.fileName,
      message.codeSnippet?.content,
      ...(message.mentions || []).map((mention: any) => mention.label),
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return haystack.includes(query)
  })
})

const mentionSuggestions = computed(() => {
  const match = newMessage.value.match(/(?:^|\s)@([A-Za-z0-9._-]*)$/)
  if (!match) {
    return []
  }

  const token = (match[1] || '').toLowerCase()
  return projectMembers.value
    .filter((member: any) => {
      const nickname = (member.name || member.email.split('@')[0] || '').toLowerCase()
      const emailToken = member.email.toLowerCase()
      return !token || nickname.includes(token) || emailToken.includes(token)
    })
    .slice(0, 5)
})

const selectChatRoom = (room: any) => {
  selectedRoomId.value = room.id
}

const createChatRoom = async () => {
  if (newRoomName.value.trim() !== '') {
    const members = selectedMemberIds.value.length > 0 ? selectedMemberIds.value : undefined
    await store.addChatRoom(projectId.value, newRoomName.value, members)
    selectedRoomId.value = store.chatRooms[store.chatRooms.length - 1]?.id || selectedRoomId.value
    newRoomName.value = ''
    selectedMemberIds.value = []
    showMemberModal.value = false
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
    await store.markChatRoomRead(projectId.value, selectedRoom.value.id)
  }
}

const viewCodeSnippet = (codeSnippet: any) => {
  router.push({
    name: 'code',
    params: { projectId: projectId.value },
    query: {
      file: codeSnippet.fileName,
      line: codeSnippet.startLine || codeSnippet.line || 1,
    },
  })
}

const handleShare = async (file: any) => {
  if (selectedRoom.value) {
    await store.addCodeSnippetMessage(projectId.value, selectedRoom.value.id, {
      fileName: file.filepath || file.name,
    })
    await store.markChatRoomRead(projectId.value, selectedRoom.value.id)
  }
  showShareModal.value = false
}

const toggleRoomEdit = () => {
  if (!selectedRoom.value) return
  isEditingRoomName.value = !isEditingRoomName.value
  editedRoomName.value = selectedRoom.value.name
}

const saveRoomName = async () => {
  if (!selectedRoom.value || !editedRoomName.value.trim()) return
  const updated = await store.renameChatRoom(projectId.value, selectedRoom.value.id, editedRoomName.value.trim())
  if (updated) {
    isEditingRoomName.value = false
  }
}

const removeRoom = async () => {
  if (!selectedRoom.value) return
  const confirmed = confirm(`Delete room "${selectedRoom.value.name}"?`)
  if (!confirmed) return

  const currentRoomId = selectedRoom.value.id
  const success = await store.deleteChatRoom(projectId.value, currentRoomId)
  if (success) {
    selectedRoomId.value = store.chatRooms[0]?.id || null
  }
}

const togglePinned = async (message: any) => {
  if (!selectedRoom.value) return
  await store.pinChatMessage(projectId.value, selectedRoom.value.id, message.id, !message.isPinned)
}

const applyMention = (member: any) => {
  const mentionLabel = member.name || member.email.split('@')[0]
  newMessage.value = newMessage.value.replace(/@([A-Za-z0-9._-]*)$/, `@${mentionLabel} `)
}

const highlightMentions = (text: string) => {
  return text.split(/(@[A-Za-z0-9._-]+)/g).filter(Boolean).map((segment) => ({
    value: segment,
    isMention: segment.startsWith('@'),
  }))
}

const formatTimestamp = (value: string) => {
  return new Date(value).toLocaleString()
}

onUnmounted(() => {
  if (store.chatSocket) {
    store.chatSocket.close()
    store.chatSocket = null
  }
})
</script>

<style scoped>
@import '@/assets/chat.css';

.chat-sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 1rem;
}

.sidebar-eyebrow {
  margin: 0 0 0.3rem;
  font-size: 0.72rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #6a87a2;
}

.chat-sidebar-header h3 {
  margin: 0;
}

.sidebar-meta {
  margin: 0;
  color: #70859a;
  font-size: 0.82rem;
}

.chat-room-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
}

.chat-room-item strong {
  display: block;
  color: #16304a;
}

.chat-room-item p {
  margin: 0.2rem 0 0;
  font-size: 0.82rem;
  color: #6f8094;
}

.chat-room-item.active {
  background: #dceefc;
}

.room-badge {
  min-width: 1.55rem;
  padding: 0.2rem 0.4rem;
  border-radius: 999px;
  background: #d14f3f;
  color: white;
  text-align: center;
  font-size: 0.75rem;
  font-weight: 700;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.chat-header-title-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.chat-header-title-row h2 {
  margin: 0;
}

.chat-header-meta {
  margin: 0.4rem 0 0;
  color: #70859a;
  font-size: 0.88rem;
}

.chat-tools {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.search-input,
.room-edit-input,
.room-name-input,
.chat-input input {
  border: 1px solid #d4dde8;
  border-radius: 12px;
  padding: 0.75rem 0.9rem;
  background: white;
}

.search-input {
  min-width: 280px;
}

.subtle-btn,
.secondary-tool-btn,
.pin-btn,
.create-btn,
.select-members-btn {
  border-radius: 999px;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.2s ease;
}

.subtle-btn,
.pin-btn {
  border: 1px solid #cad6e2;
  background: white;
  color: #34526d;
  padding: 0.45rem 0.8rem;
}

.secondary-tool-btn {
  border: none;
  background: #1e88a8;
  color: white;
  padding: 0.75rem 1rem;
}

.danger-link {
  border: none;
  background: transparent;
  color: #c0504d;
  cursor: pointer;
  font-weight: 600;
}

.pinned-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.pinned-card {
  padding: 0.85rem 0.95rem;
  border-radius: 16px;
  background: linear-gradient(135deg, #fff9df, #fff4c2);
  border: 1px solid #ecd98e;
}

.pinned-label {
  display: inline-block;
  margin-bottom: 0.4rem;
  font-size: 0.72rem;
  font-weight: 700;
  color: #8c6a07;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.pinned-card p {
  margin: 0.35rem 0 0;
  color: #5a4a1e;
}

.message {
  padding: 0.9rem 1rem;
  border: 1px solid #e3ebf3;
  border-radius: 16px;
  background: white;
}

.message + .message {
  margin-top: 0.8rem;
}

.message-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
}

.message-meta {
  margin-left: 0.45rem;
  color: #7a8ea2;
  font-size: 0.82rem;
}

.message-text {
  margin: 0.65rem 0 0;
  color: #23384d;
  line-height: 1.6;
}

.mention-chip {
  display: inline-block;
  padding: 0.02rem 0.38rem;
  border-radius: 999px;
  background: #e0f3ff;
  color: #0f6392;
  font-weight: 600;
}

.mention-suggestions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 0.9rem;
}

.mention-option {
  border: 1px solid #cfe3f0;
  background: #f4fbff;
  color: #1a6e94;
  border-radius: 999px;
  padding: 0.45rem 0.8rem;
  cursor: pointer;
}

.chat-input {
  grid-template-columns: 1fr auto;
}

.empty-chat {
  display: grid;
  place-items: center;
  color: #6d8195;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
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
  background: #f9fbfd;
  border: 1px solid #dce5ef;
  border-radius: 12px;
  cursor: pointer;
}

.member-option--selected {
  background: #e7f6ef;
  border-color: #82c8a8;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.primary-btn,
.cancel-btn {
  border-radius: 999px;
  padding: 0.7rem 1rem;
  cursor: pointer;
}

.primary-btn {
  border: none;
  background: #1f8c72;
  color: white;
}

.cancel-btn {
  border: 1px solid #ced8e2;
  background: white;
}

@media (max-width: 960px) {
  .chat-header {
    flex-direction: column;
  }

  .search-input {
    min-width: 0;
    width: 100%;
  }
}
</style>
