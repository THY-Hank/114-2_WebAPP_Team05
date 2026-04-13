/* eslint-disable @typescript-eslint/no-explicit-any */
import { defineStore } from 'pinia'
import { authApi } from '@/api/auth'
import { projectsApi } from '@/api/projects'
import { chatApi } from '@/api/chat'
import { clearAuthToken, getAuthToken, setAuthToken } from '@/api/http'

export const useMainStore = defineStore('main', {
  state: () => ({
    users: [],
    currentUser: null as any,
    files: [] as any[],
    chatRooms: [] as any[],
    invitations: [] as any[],
    chatSocket: null as WebSocket | null,
    notificationSocket: null as WebSocket | null,
    notifications: [] as any[],
    onlineUserIds: [] as number[],
    typingUsersByRoom: {} as Record<number, Array<{ userId: number; userName: string }>>,
  }),
  getters: {
    isLoggedIn: (state) => !!state.currentUser,
    getUserProjects: (state) => {
      if (state.currentUser) {
        return state.currentUser.projects
      }
      return []
    },
    getProjectFiles: (state) => (projectId: number) => {
      return state.files.filter((file) => file.projectId === projectId)
    },
  },
  actions: {
    async loadDashboardData() {
      try {
        let res = await authApi.fetchMe()
        if (res.ok) {
          const userData = await res.json()
          this.currentUser = {
            ...this.currentUser,
            ...userData,
            projects: userData.projects || [],
          }
        } else {
          clearAuthToken()
          this.currentUser = null
          return
        }
        res = await projectsApi.fetchInvitations()
        if (res.ok) {
          this.invitations = await res.json()
        }
        await this.loadNotifications()
        this.connectNotificationSocket()
      } catch (err) {
        console.error("Failed to load dashboard data", err)
      }
    },
    async loadProjectFiles(projectId: number) {
      try {
        const res = await projectsApi.fetchProjectFiles(projectId)
        if (res.ok) {
          const fetchedFiles = await res.json()
          this.files = [
            ...this.files.filter((f) => f.projectId !== projectId),
            ...fetchedFiles
          ]
        }
      } catch (err) {
        console.error("Failed to load project files", err)
      }
    },
    async login(email: string, password: string) {
      try {
        const response = await authApi.login(email, password)
        const data = await response.json()
        if (response.ok) {
          if (data.accessToken) {
            setAuthToken(data.accessToken)
          }
          this.currentUser = data.user
          await this.loadDashboardData()
          return true
        }
        clearAuthToken()
        console.error('Login failed:', data.error)
        return false
      } catch (err) {
        clearAuthToken()
        console.error('Login error:', err)
        return false
      }
    },
    async logout() {
      try {
        await authApi.logout()
        clearAuthToken()
        this.currentUser = null
        this.files = []
        this.chatRooms = []
        this.invitations = []
        this.notifications = []
        this.onlineUserIds = []
        this.typingUsersByRoom = {}
        if (this.chatSocket) {
          this.chatSocket.close()
          this.chatSocket = null
        }
        if (this.notificationSocket) {
          this.notificationSocket.close()
          this.notificationSocket = null
        }
      } catch (err) {
        console.error('Logout error:', err)
      }
    },
    async register(name: string, email: string, password: string) {
      try {
        const response = await authApi.register(name, email, password)
        const data = await response.json()
        if (response.ok) {
          return true
        }
        // 顯示後端返回的具體錯誤
        console.error('Register failed:', data.error)
        return false
      } catch (err) {
        console.error('Register error:', err)
        return false
      }
    },
    async addFile(projectId: number, file: { name: string, filepath?: string, content: string }) {
      try {
        const response = await projectsApi.addFile(projectId, file)
        if (response.ok) {
          const newFile = await response.json()
          newFile.projectId = projectId // 補上遺失的 projectId 屬性供 getProjectFiles 篩選
          this.files.push(newFile)
        }
      } catch (err) {
        console.error("Add file error", err)
      }
    },
    async addComment(fileId: number, comment: string) {
      try {
        const response = await projectsApi.addComment(fileId, comment)
        if (response.ok) {
          const newComment = await response.json()
          const file = this.files.find((f) => f.id === fileId)
          if (file) {
            file.comments.push(newComment)
          }
        }
      } catch (err) {
        console.error("Add comment error", err)
      }
    },
    async createProject(name: string) {
      try {
        const res = await projectsApi.createProject(name)
        if (res.ok) {
          const newProj = await res.json()
          this.currentUser.projects.push(newProj)
          return true
        }
      } catch (err) {
        console.error("Create project error", err)
      }
      return false
    },
    async addProjectMember(projectId: number, email: string) {
      try {
        const res = await projectsApi.addProjectMember(projectId, email)
        return res.ok;
      } catch (err) {
        console.error("Add project member error", err)
      }
      return false
    },
    async fetchInvitations() {
      try {
        const res = await projectsApi.fetchInvitations()
        if (res.ok) {
          this.invitations = await res.json()
        }
      } catch (err) {
        console.error("Fetch invitations error", err)
      }
    },
    async respondInvitation(invitationId: number, action: 'accept' | 'decline') {
      try {
        const res = await projectsApi.respondInvitation(invitationId, action)
        if (res.ok) {
          this.invitations = this.invitations.filter((inv) => inv.id !== invitationId)
          if (action === 'accept') {
            await this.loadDashboardData() // Reload projects into currentUser bounding
          }
          return true
        }
      } catch (err) {
        console.error("Respond invitation error", err)
      }
      return false
    },
    async deleteFile(fileId: number) {
      try {
        const response = await projectsApi.deleteFile(fileId)
        if (response.ok) {
          this.files = this.files.filter((f: any) => f.id !== fileId)
          return true
        }
      } catch (err) {
        console.error("Delete file error", err)
      }
      return false
    },
    async deleteProject(projectId: number) {
      try {
        const response = await projectsApi.deleteProject(projectId)
        if (response.ok) {
          if (this.currentUser) {
            this.currentUser.projects = this.currentUser.projects.filter((p: any) => p.id !== projectId)
          }
          return true
        }
      } catch (err) {
        console.error("Delete project error", err)
      }
      return false
    },
    async loadProjectChatRooms(projectId: number) {
      try {
        const response = await chatApi.fetchChatRooms(projectId)
        if (response.ok) {
          this.chatRooms = await response.json()
        } else {
          this.chatRooms = []
        }
      } catch (err) {
        this.chatRooms = []
        console.error("Load chatrooms error", err)
      }
    },
    async addChatRoom(projectId: number, name: string, memberIds?: number[]) {
      try {
        const response = await chatApi.addChatRoom(projectId, name, memberIds)
        if (response.ok) {
          const newRoom = await response.json()
          this.chatRooms.push(newRoom)
        }
      } catch (err) {
        console.error("Add chatroom error", err)
      }
    },
    async renameChatRoom(projectId: number, roomId: number, name: string) {
      try {
        const response = await chatApi.renameChatRoom(projectId, roomId, name)
        if (response.ok) {
          const updatedRoom = await response.json()
          const roomIndex = this.chatRooms.findIndex((r) => r.id === roomId)
          if (roomIndex !== -1) {
            this.chatRooms[roomIndex] = updatedRoom
          }
          return updatedRoom
        }
      } catch (err) {
        console.error("Rename chatroom error", err)
      }
      return null
    },
    async deleteChatRoom(projectId: number, roomId: number) {
      try {
        const response = await chatApi.deleteChatRoom(projectId, roomId)
        if (response.ok) {
          this.chatRooms = this.chatRooms.filter((room) => room.id !== roomId)
          return true
        }
      } catch (err) {
        console.error("Delete chatroom error", err)
      }
      return false
    },
    async addChatMessage(projectId: number, roomId: number, payload: { text?: string; replyToMessageId?: number | null; attachment?: File | null }) {
      try {
        const response = await chatApi.addChatMessage(projectId, roomId, payload)
        if (response.ok) {
          const newMsg = await response.json()
          const room = this.chatRooms.find((r) => r.id === roomId)
          if (room) {
            const exists = room.messages.some((m: any) => m.id === newMsg.id)
            if (!exists) {
              room.messages.push(newMsg)
            }
            room.unreadCount = 0
          }
        }
      } catch (err) {
        console.error("Add chat message error", err)
      }
    },
    async updateChatMessage(projectId: number, roomId: number, messageId: number, text: string) {
      try {
        const response = await chatApi.updateChatMessage(projectId, roomId, messageId, text)
        if (response.ok) {
          const updated = await response.json()
          const room = this.chatRooms.find((r) => r.id === roomId)
          if (room) {
            const index = room.messages.findIndex((m: any) => m.id === messageId)
            if (index !== -1) {
              room.messages[index] = updated
            }
          }
          return updated
        }
      } catch (err) {
        console.error('Update chat message error', err)
      }
      return null
    },
    async deleteChatMessage(projectId: number, roomId: number, messageId: number) {
      try {
        const response = await chatApi.deleteChatMessage(projectId, roomId, messageId)
        if (response.ok || response.status === 204) {
          const room = this.chatRooms.find((r) => r.id === roomId)
          if (room) {
            const index = room.messages.findIndex((m: any) => m.id === messageId)
            if (index !== -1) {
              room.messages[index] = {
                ...room.messages[index],
                text: 'This message was deleted.',
                isDeleted: true,
                attachment: null,
                codeSnippet: null,
              }
            }
          }
          return true
        }
      } catch (err) {
        console.error('Delete chat message error', err)
      }
      return false
    },
    async addCodeSnippetMessage(projectId: number, roomId: number, codeSnippet: { fileName: string, line?: number }) {
      try {
        const response = await chatApi.addCodeSnippetMessage(projectId, roomId, codeSnippet)
        if (response.ok) {
          const newMsg = await response.json()
          const room = this.chatRooms.find((r) => r.id === roomId)
          if (room) {
            const exists = room.messages.some((m: any) => m.id === newMsg.id)
            if (!exists) {
              room.messages.push(newMsg)
            }
            room.unreadCount = 0
          }
        }
      } catch (err) {
        console.error("Add code snippet error", err)
      }
    },
    async addLineComment(fileId: number, data: { text: string; startLine: number; endLine: number }) {
      try {
        const response = await projectsApi.addLineComment(fileId, data)
        if (response.ok) {
          const newComment = await response.json()
          const file = this.files.find((f) => f.id === fileId)
          if (file) {
            if (!file.comments) {
              file.comments = []
            }
            file.comments.push(newComment)
          }
        }
      } catch (err) {
        console.error("Add line comment error", err)
      }
    },
    async addLineCodeSnippetMessage(projectId: number, roomId: number, codeSnippet: { fileName: string, startLine: number, endLine: number, content: string }) {
      try {
        const response = await chatApi.addLineCodeSnippetMessage(projectId, roomId, codeSnippet)
        if (response.ok) {
          const newMsg = await response.json()
          const room = this.chatRooms.find((r) => r.id === roomId)
          if (room) {
            const exists = room.messages.some((m: any) => m.id === newMsg.id)
            if (!exists) {
              room.messages.push(newMsg)
            }
            room.unreadCount = 0
          }
        }
      } catch (err) {
        console.error("Add line code snippet error", err)
      }
    },
    async updateFileContent(fileId: number, content: string, note = '') {
      try {
        const response = await projectsApi.updateFileContent(fileId, content, note)
        const data = await response.json()
        if (response.ok) {
          const file = this.files.find((f) => f.id === fileId)
          if (file) {
            file.content = content
            file.sizeBytes = data.sizeBytes
          }
          return { success: true, data }
        }
        return { success: false, error: data.error || 'Failed to save file' }
      } catch (err) {
        console.error('Update file content error', err)
        return { success: false, error: 'Failed to save file' }
      }
    },
    async fetchFileVersions(fileId: number) {
      try {
        const response = await projectsApi.fetchFileVersions(fileId)
        if (response.ok) {
          return { success: true, data: await response.json() }
        }
        const data = await response.json()
        return { success: false, error: data.error || 'Failed to load versions', data: [] }
      } catch (err) {
        console.error('Fetch versions error', err)
        return { success: false, error: 'Failed to load versions', data: [] }
      }
    },
    async fetchFileVersionDiff(fileId: number, fromVersionId: number, toVersionId: number) {
      try {
        const response = await projectsApi.fetchFileVersionDiff(fileId, fromVersionId, toVersionId)
        if (response.ok) {
          return { success: true, data: await response.json() }
        }
        const data = await response.json()
        return { success: false, error: data.error || 'Failed to load diff' }
      } catch (err) {
        console.error('Fetch diff error', err)
        return { success: false, error: 'Failed to load diff' }
      }
    },
    async revertFileVersion(fileId: number, versionId: number, note = '') {
      try {
        const response = await projectsApi.revertFileVersion(fileId, versionId, note)
        const data = await response.json()
        if (response.ok) {
          const file = this.files.find((f) => f.id === fileId)
          if (file) {
            file.content = data.content
          }
          return { success: true, data }
        }
        return { success: false, error: data.error || 'Failed to revert version' }
      } catch (err) {
        console.error('Revert version error', err)
        return { success: false, error: 'Failed to revert version' }
      }
    },
    async markVersionSnapshot(fileId: number, versionId: number, tagName = '', isSnapshot = true) {
      try {
        const response = await projectsApi.markVersionSnapshot(fileId, versionId, tagName, isSnapshot)
        const data = await response.json()
        if (response.ok) {
          return { success: true, data }
        }
        return { success: false, error: data.error || 'Failed to mark snapshot' }
      } catch (err) {
        console.error('Mark snapshot error', err)
        return { success: false, error: 'Failed to mark snapshot' }
      }
    },
    async markChatRoomRead(projectId: number, roomId: number) {
      try {
        const response = await chatApi.markChatRoomRead(projectId, roomId)
        if (response.ok) {
          const data = await response.json()
          const room = this.chatRooms.find((r) => r.id === roomId)
          if (room) {
            room.unreadCount = data.unreadCount
            room.messages = room.messages.map((message: any) => ({
              ...message,
              isReadByCurrentUser: true,
            }))
          }
        }
      } catch (err) {
        console.error("Mark chatroom read error", err)
      }
    },
    async pinChatMessage(projectId: number, roomId: number, messageId: number, isPinned: boolean) {
      try {
        const response = await chatApi.pinChatMessage(projectId, roomId, messageId, isPinned)
        if (response.ok) {
          const updatedMessage = await response.json()
          const room = this.chatRooms.find((r) => r.id === roomId)
          if (room) {
            const idx = room.messages.findIndex((m: any) => m.id === messageId)
            if (idx !== -1) {
              room.messages[idx] = updatedMessage
            }
          }
          return updatedMessage
        }
      } catch (err) {
        console.error("Pin chat message error", err)
      }
      return null
    },
    async loadNotifications() {
      try {
        const response = await chatApi.fetchNotifications()
        if (response.ok) {
          this.notifications = await response.json()
        }
      } catch (err) {
        console.error('Load notifications error', err)
      }
    },
    async markNotificationRead(notificationId: number) {
      try {
        const response = await chatApi.markNotificationRead(notificationId)
        if (response.ok) {
          const updated = await response.json()
          const index = this.notifications.findIndex((notification: any) => notification.id === notificationId)
          if (index !== -1) {
            this.notifications[index] = updated
          }
          return updated
        }
      } catch (err) {
        console.error('Mark notification read error', err)
      }
      return null
    },
    connectNotificationSocket() {
      if (this.notificationSocket || !this.currentUser) {
        return
      }
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const token = getAuthToken()
      const wsUrl = token
        ? `${protocol}//${window.location.host}/ws/notifications/?token=${encodeURIComponent(token)}`
        : `${protocol}//${window.location.host}/ws/notifications/`
      this.notificationSocket = new WebSocket(wsUrl)
      this.notificationSocket.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.action === 'notification_created') {
          this.notifications.unshift(data.payload)
        }
      }
      this.notificationSocket.onclose = () => {
        this.notificationSocket = null
      }
    },
    sendTyping(roomId: number, isTyping: boolean) {
      if (!this.chatSocket || this.chatSocket.readyState !== WebSocket.OPEN) {
        return
      }
      this.chatSocket.send(JSON.stringify({
        action: 'typing',
        isTyping,
      }))
      if (!isTyping) {
        this.typingUsersByRoom[roomId] = (this.typingUsersByRoom[roomId] || []).filter(
          (entry) => entry.userId !== this.currentUser?.id
        )
      }
    },
    connectWebSocket(roomId: number) {
      if (this.chatSocket) {
        this.chatSocket.close()
      }
      
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const token = getAuthToken()
      const wsUrl = token
        ? `${protocol}//${window.location.host}/ws/chat/${roomId}/?token=${encodeURIComponent(token)}`
        : `${protocol}//${window.location.host}/ws/chat/${roomId}/`
      this.chatSocket = new WebSocket(wsUrl)
      
      this.chatSocket.onmessage = (event) => {
        const data = JSON.parse(event.data)
        const room = this.chatRooms.find((r) => r.id === roomId)
        if (!room) {
          return
        }

        if (data.action === 'new_message') {
          const exists = room.messages.some((m: any) => m.id === data.payload.id)
          if (!exists) {
            room.messages.push(data.payload)
          }
          room.lastMessageAt = data.payload.createdAt
        } else if (data.action === 'message_updated') {
          const messageIndex = room.messages.findIndex((m: any) => m.id === data.payload.id)
          if (messageIndex !== -1) {
            room.messages[messageIndex] = data.payload
          }
        } else if (data.action === 'presence') {
          this.onlineUserIds = data.payload.onlineUserIds || []
        } else if (data.action === 'typing') {
          const entries = this.typingUsersByRoom[roomId] || []
          const filtered = entries.filter((entry) => entry.userId !== data.payload.userId)
          if (data.payload.isTyping && data.payload.userId !== this.currentUser?.id) {
            filtered.push({
              userId: data.payload.userId,
              userName: data.payload.userName,
            })
          }
          this.typingUsersByRoom[roomId] = filtered
        }
      }
      
      this.chatSocket.onerror = (error) => {
        console.error("WebSocket error:", error)
      }
      this.chatSocket.onclose = () => {
        this.chatSocket = null
      }
    },
  },
})
