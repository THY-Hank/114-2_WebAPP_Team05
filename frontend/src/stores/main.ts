/* eslint-disable @typescript-eslint/no-explicit-any */
import { defineStore } from 'pinia'
import { authApi } from '@/api/auth'
import { projectsApi } from '@/api/projects'
import { chatApi } from '@/api/chat'

export const useMainStore = defineStore('main', {
  state: () => ({
    users: [],
    currentUser: null as any,
    files: [] as any[],
    chatRooms: [] as any[],
    invitations: [] as any[],
    chatSocket: null as WebSocket | null,
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
            ...(this.currentUser || {}),
            ...userData,
            projects: userData.projects || [],
          }
        } else {
          this.currentUser = null
          return
        }
        res = await projectsApi.fetchInvitations()
        if (res.ok) {
          this.invitations = await res.json()
        }
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
          this.currentUser = data.user
          await this.loadDashboardData()
          return true
        }
        console.error(data.error)
        return false
      } catch (err) {
        console.error('Login error:', err)
        return false
      }
    },
    async logout() {
      try {
        await authApi.logout()
        this.currentUser = null
        this.files = []
        this.chatRooms = []
        this.invitations = []
        if (this.chatSocket) {
          this.chatSocket.close()
          this.chatSocket = null
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
        console.error(data.error)
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
    async addChatMessage(projectId: number, roomId: number, message: string) {
      try {
        const response = await chatApi.addChatMessage(projectId, roomId, message)
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
    connectWebSocket(roomId: number) {
      if (this.chatSocket) {
        this.chatSocket.close()
      }
      
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.host}/ws/chat/${roomId}/`
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
        } else if (data.action === 'message_updated') {
          const messageIndex = room.messages.findIndex((m: any) => m.id === data.payload.id)
          if (messageIndex !== -1) {
            room.messages[messageIndex] = data.payload
          }
        }
      }
      
      this.chatSocket.onerror = (error) => {
        console.error("WebSocket error:", error)
      }
    },
  },
})
