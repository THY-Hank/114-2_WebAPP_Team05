<template>
  <div class="notification-center">
    <button class="notification-trigger" type="button" @click="isOpen = !isOpen">
      Notifications
      <span v-if="unreadCount" class="notification-badge">{{ unreadCount }}</span>
    </button>

    <div v-if="isOpen" class="notification-panel">
      <p class="notification-title">Recent updates</p>
      <button
        v-for="notification in store.notifications"
        :key="notification.id"
        class="notification-item"
        :class="{ unread: !notification.isRead }"
        @click="openNotification(notification)"
      >
        <strong>{{ labelMap[notification.type] || notification.type }}</strong>
        <span>{{ notification.text }}</span>
        <small>{{ formatTime(notification.createdAt) }}</small>
      </button>
      <p v-if="store.notifications.length === 0" class="notification-empty">No notifications yet.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMainStore } from '@/stores/main'

type NotificationItem = {
  id: number
  type: string
  text: string
  createdAt: string
  isRead: boolean
  roomId?: number | null
  projectId?: number | string | null
}

type ChatRoomPreview = {
  id: number
  projectId?: number | string | null
}

const store = useMainStore()
const router = useRouter()
const route = useRoute()
const isOpen = ref(false)

const labelMap: Record<string, string> = {
  mention: 'Mention',
  reply: 'Reply',
  room_invite: 'Room invite',
}

const unreadCount = computed(() =>
  (store.notifications as NotificationItem[]).filter((notification) => !notification.isRead).length
)

const formatTime = (value: string) => new Date(value).toLocaleString()

const openNotification = async (notification: NotificationItem) => {
  if (!notification.isRead) {
    await store.markNotificationRead(notification.id)
  }
  if (notification.roomId) {
    const projectId =
      notification.projectId ||
      route.params.projectId ||
      (store.chatRooms as ChatRoomPreview[]).find((room) => room.id === notification.roomId)?.projectId
    if (projectId) {
      router.push(`/projects/${projectId}/chat`)
    }
  }
  isOpen.value = false
}
</script>

<style scoped>
.notification-center {
  position: relative;
}

.notification-trigger {
  width: 100%;
  border: 1px solid #d5deea;
  border-radius: 999px;
  padding: 0.65rem 0.9rem;
  background: white;
  color: #24435f;
  cursor: pointer;
}

.notification-badge {
  margin-left: 0.4rem;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  background: #d14f3f;
  color: white;
  font-size: 0.75rem;
}

.notification-panel {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  right: 0;
  z-index: 20;
  background: white;
  border: 1px solid #d5deea;
  border-radius: 18px;
  padding: 0.75rem;
  box-shadow: 0 20px 35px rgba(21, 41, 66, 0.14);
}

.notification-title {
  margin: 0 0 0.6rem;
  color: #5a738f;
  font-size: 0.84rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.notification-item {
  width: 100%;
  display: grid;
  gap: 0.2rem;
  margin-bottom: 0.45rem;
  padding: 0.75rem;
  border: 1px solid #e4ebf3;
  border-radius: 14px;
  background: #fbfdff;
  text-align: left;
  cursor: pointer;
}

.notification-item.unread {
  background: #eef8ff;
  border-color: #b9dbef;
}

.notification-item strong {
  color: #1c4363;
}

.notification-item span,
.notification-item small,
.notification-empty {
  color: #5f778e;
}
</style>
