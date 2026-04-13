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
            <input v-else v-model="editedRoomName" class="room-edit-input" @keyup.enter="saveRoomName" />
            <button class="subtle-btn" @click="toggleRoomEdit">
              {{ isEditingRoomName ? 'Cancel' : 'Rename' }}
            </button>
            <button v-if="isEditingRoomName" class="subtle-btn" :disabled="!editedRoomName.trim()" @click="saveRoomName">
              Save
            </button>
            <button v-if="selectedRoom.name !== 'General'" class="danger-link" @click="removeRoom">
              Delete
            </button>
          </div>
          <p class="chat-header-meta">
            {{ pinnedMessages.length }} pinned · {{ filteredMessages.length }} visible · {{ onlineMembers.length }} online
          </p>
          <div class="online-strip">
            <span
              v-for="member in selectedRoom.members || []"
              :key="member.id"
              class="member-presence"
              :class="{ online: store.onlineUserIds.includes(member.id) }"
            >
              {{ member.name || member.email.split('@')[0] }}
            </span>
          </div>
        </div>
        <div class="chat-tools">
          <input v-model="searchQuery" placeholder="Search messages, snippets, mentions" class="search-input" />
          <button class="secondary-tool-btn" @click="showShareModal = true">Share Snippet</button>
        </div>
      </header>

      <div v-if="pinnedMessages.length" class="pinned-strip">
        <div v-for="message in pinnedMessages" :key="`pinned-${message.id}`" class="pinned-card">
          <span class="pinned-label">Pinned</span>
          <strong>{{ message.author }}</strong>
          <p>{{ message.text || message.codeSnippet?.fileName || message.attachment?.name }}</p>
        </div>
      </div>

      <div class="chat-box">
        <div v-for="message in filteredMessages" :key="message.id" class="message" :class="{ deleted: message.isDeleted }">
          <div v-if="message.replyTo" class="reply-preview">
            Replying to {{ message.replyTo.author }}: {{ message.replyTo.text }}
          </div>

          <div class="message-header">
            <div>
              <strong class="author">{{ message.author }}</strong>
              <span class="message-meta">
                {{ formatTimestamp(message.createdAt) }}
                <span v-if="message.editedAt"> · edited</span>
                <span v-if="message.readByCount"> · read by {{ message.readByCount }}</span>
              </span>
            </div>
            <div class="message-actions">
              <button class="pin-btn" @click="togglePinned(message)">
                {{ message.isPinned ? 'Unpin' : 'Pin' }}
              </button>
              <button class="pin-btn" :disabled="message.isDeleted" @click="startReply(message)">Reply</button>
              <button
                v-if="canManageMessage(message) && !message.isDeleted"
                class="pin-btn"
                @click="startEditMessage(message)"
              >
                Edit
              </button>
              <button
                v-if="canManageMessage(message) && !message.isDeleted"
                class="danger-link"
                @click="deleteMessage(message)"
              >
                Delete
              </button>
            </div>
          </div>

          <template v-if="editingMessageId === message.id">
            <textarea v-model="editingMessageText" class="message-edit-box" />
            <div class="inline-actions">
              <button class="secondary-tool-btn" @click="saveMessageEdit(message)">Save</button>
              <button class="subtle-btn" @click="cancelMessageEdit">Cancel</button>
            </div>
          </template>

          <p v-else-if="message.text" class="message-text">
            <template v-for="(segment, index) in highlightMentions(message.text)" :key="`${message.id}-${index}`">
              <span v-if="segment.isMention" class="mention-chip">{{ segment.value }}</span>
              <span v-else>{{ segment.value }}</span>
            </template>
          </p>

          <div v-if="message.codeSnippet" class="code-snippet" @click="viewCodeSnippet(message.codeSnippet)">
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

          <a
            v-if="message.attachment"
            class="attachment-card"
            :href="message.attachment.url"
            target="_blank"
            rel="noreferrer"
          >
            <img v-if="message.attachment.isImage" :src="message.attachment.url" :alt="message.attachment.name" class="attachment-preview" />
            <div>
              <strong>{{ message.attachment.name }}</strong>
              <p>{{ message.attachment.contentType || 'Attachment' }}</p>
            </div>
          </a>
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

      <p v-if="typingLabel" class="typing-label">{{ typingLabel }}</p>

      <div v-if="replyingToMessage" class="replying-banner">
        <span>Replying to {{ replyingToMessage.author }}: {{ (replyingToMessage.text || replyingToMessage.attachment?.name || '').slice(0, 80) }}</span>
        <button class="danger-link" @click="clearReply">Cancel</button>
      </div>

      <div v-if="selectedAttachment" class="attachment-pending">
        <span>Attachment ready: {{ selectedAttachment.name }}</span>
        <button class="danger-link" @click="clearAttachment">Remove</button>
      </div>

      <div class="chat-input-area">
        <textarea
          v-model="newMessage"
          placeholder="Type a message... try @teammate"
          class="chat-textarea"
          @input="handleMessageInput"
          @keydown.enter.exact.prevent="sendMessage"
        />
        <div class="chat-input-actions">
          <label class="attachment-btn">
            Attach
            <input type="file" class="hidden-input" @change="handleAttachmentChange" />
          </label>
          <button @click="sendMessage">Send</button>
        </div>
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
            <span v-if="selectedMemberIds.includes(member.id)" class="member-option-checkmark">Selected</span>
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
const replyingToMessage = ref<any | null>(null)
const selectedAttachment = ref<File | null>(null)
const editingMessageId = ref<number | null>(null)
const editingMessageText = ref('')
const typingTimeoutId = ref<number | null>(null)

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

const currentProject = computed(() => {
  if (!store.currentUser) return null
  return store.currentUser.projects.find((p: any) => p.id === projectId.value) || null
})

const onlineMembers = computed(() => {
  const members = selectedRoom.value?.members || []
  return members.filter((member: any) => store.onlineUserIds.includes(member.id))
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
      message.attachment?.name,
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

const typingLabel = computed(() => {
  const roomId = selectedRoomId.value
  if (!roomId) return ''
  const typingUsers = store.typingUsersByRoom[roomId] || []
  if (typingUsers.length === 0) return ''
  if (typingUsers.length === 1) return `${typingUsers[0]?.userName || 'Someone'} is typing...`
  return `${typingUsers.map((entry) => entry.userName).join(', ')} are typing...`
})

const selectChatRoom = (room: any) => {
  selectedRoomId.value = room.id
  clearReply()
  cancelMessageEdit()
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
  if ((!newMessage.value.trim() && !selectedAttachment.value) || !selectedRoom.value) {
    return
  }

  await store.addChatMessage(projectId.value, selectedRoom.value.id, {
    text: newMessage.value.trim() || undefined,
    replyToMessageId: replyingToMessage.value?.id || null,
    attachment: selectedAttachment.value,
  })
  newMessage.value = ''
  clearReply()
  clearAttachment()
  stopTyping()
  await store.markChatRoomRead(projectId.value, selectedRoom.value.id)
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

const startReply = (message: any) => {
  replyingToMessage.value = message
}

const clearReply = () => {
  replyingToMessage.value = null
}

const handleAttachmentChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  selectedAttachment.value = input.files?.[0] || null
}

const clearAttachment = () => {
  selectedAttachment.value = null
}

const startEditMessage = (message: any) => {
  editingMessageId.value = message.id
  editingMessageText.value = message.text || ''
}

const cancelMessageEdit = () => {
  editingMessageId.value = null
  editingMessageText.value = ''
}

const saveMessageEdit = async (message: any) => {
  if (!selectedRoom.value) return
  const updated = await store.updateChatMessage(projectId.value, selectedRoom.value.id, message.id, editingMessageText.value)
  if (updated) {
    cancelMessageEdit()
  }
}

const deleteMessage = async (message: any) => {
  if (!selectedRoom.value) return
  const confirmed = confirm('Delete this message?')
  if (!confirmed) return
  await store.deleteChatMessage(projectId.value, selectedRoom.value.id, message.id)
}

const canManageMessage = (message: any) => {
  const isOwner = currentProject.value?.owner_id === store.currentUser?.id
  return message.authorId === store.currentUser?.id || isOwner
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

const stopTyping = () => {
  if (!selectedRoom.value) return
  store.sendTyping(selectedRoom.value.id, false)
  if (typingTimeoutId.value) {
    window.clearTimeout(typingTimeoutId.value)
    typingTimeoutId.value = null
  }
}

const handleMessageInput = () => {
  if (!selectedRoom.value) return
  store.sendTyping(selectedRoom.value.id, !!newMessage.value.trim())
  if (typingTimeoutId.value) {
    window.clearTimeout(typingTimeoutId.value)
  }
  typingTimeoutId.value = window.setTimeout(() => {
    stopTyping()
  }, 1500)
}

onUnmounted(() => {
  stopTyping()
  if (store.chatSocket) {
    store.chatSocket.close()
    store.chatSocket = null
  }
})
</script>

<style scoped>
@import '@/assets/chat.css';

.chat-sidebar-header,
.chat-header,
.chat-header-title-row,
.chat-tools,
.message-header,
.message-actions,
.modal-actions,
.chat-input-actions,
.inline-actions {
  display: flex;
  gap: 0.75rem;
}

.chat-sidebar-header,
.message-header {
  justify-content: space-between;
  align-items: center;
}

.chat-header {
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.chat-header-title-row {
  align-items: center;
  flex-wrap: wrap;
}

.sidebar-eyebrow,
.pinned-label {
  margin: 0 0 0.3rem;
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.sidebar-eyebrow,
.sidebar-meta,
.chat-header-meta,
.message-meta,
.typing-label {
  color: #70859a;
}

.chat-room-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
}

.chat-room-item.active {
  background: #dceefc;
}

.room-badge,
.mention-chip,
.member-presence,
.attachment-btn {
  border-radius: 999px;
}

.room-badge {
  min-width: 1.55rem;
  padding: 0.2rem 0.4rem;
  background: #d14f3f;
  color: white;
  text-align: center;
  font-size: 0.75rem;
  font-weight: 700;
}

.online-strip,
.mention-suggestions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: 0.75rem;
}

.member-presence {
  padding: 0.28rem 0.65rem;
  background: #eef3f8;
  color: #5c7085;
  font-size: 0.78rem;
}

.member-presence.online {
  background: #ddf7ea;
  color: #146c4a;
}

.search-input,
.room-edit-input,
.room-name-input,
.chat-textarea,
.message-edit-box {
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
.select-members-btn,
.chat-input-actions button,
.primary-btn,
.cancel-btn {
  border-radius: 999px;
  cursor: pointer;
}

.subtle-btn,
.pin-btn,
.cancel-btn {
  border: 1px solid #cad6e2;
  background: white;
  color: #34526d;
  padding: 0.45rem 0.8rem;
}

.secondary-tool-btn,
.chat-input-actions button,
.primary-btn,
.attachment-btn {
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
  color: #8c6a07;
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

.message.deleted {
  background: #f9fbfd;
}

.message-text {
  margin: 0.65rem 0 0;
  color: #23384d;
  line-height: 1.6;
}

.mention-chip {
  display: inline-block;
  padding: 0.02rem 0.38rem;
  background: #e0f3ff;
  color: #0f6392;
  font-weight: 600;
}

.reply-preview,
.replying-banner,
.attachment-pending {
  margin-bottom: 0.75rem;
  padding: 0.7rem 0.9rem;
  border-radius: 14px;
  background: #f4f8fb;
  color: #486174;
  font-size: 0.9rem;
}

.message-edit-box,
.chat-textarea {
  width: 100%;
  box-sizing: border-box;
  min-height: 88px;
  resize: vertical;
}

.code-snippet,
.attachment-card {
  margin-top: 0.7rem;
  display: block;
  padding: 0.85rem 0.95rem;
  border-radius: 14px;
  border: 1px solid #dce5ef;
  background: #f8fbff;
  text-decoration: none;
  color: inherit;
}

.code-snippet-header {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
}

.code-snippet-content {
  margin: 0.65rem 0 0;
  white-space: pre-wrap;
}

.attachment-preview {
  width: 100%;
  max-height: 220px;
  object-fit: cover;
  border-radius: 10px;
  margin-bottom: 0.65rem;
}

.chat-input-area {
  display: grid;
  gap: 0.75rem;
  margin-top: 1rem;
}

.chat-input-actions {
  justify-content: flex-end;
}

.attachment-btn {
  display: inline-flex;
  align-items: center;
}

.hidden-input {
  display: none;
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
