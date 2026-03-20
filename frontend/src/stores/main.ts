import { defineStore } from 'pinia'

export const useMainStore = defineStore('main', {
  state: () => ({
    users: [
      {
        id: 1,
        name: 'Alice',
        email: 'alice@example.com',
        password: 'password',
        projects: [
          { id: 1, name: 'Project Alpha' },
          { id: 2, name: 'Project Beta' },
        ],
      },
      {
        id: 2,
        name: 'Bob',
        email: 'bob@example.com',
        password: 'password',
        projects: [{ id: 3, name: 'Project Gamma' }],
      },
    ],
    currentUser: null,
    files: [
      {
        id: 1,
        projectId: 1,
        name: 'main.js',
        content: 'console.log("Hello, World!");',
        comments: [
          { id: 1, author: 'Alice', text: 'This looks good.' },
          { id: 2, author: 'Bob', text: 'Could you add a comment explaining this line?' },
        ],
      },
      {
        id: 2,
        projectId: 1,
        name: 'index.html',
        content: '<h1>Hello, World!</h1>',
        comments: [],
      },
    ],
    chatRooms: [
      {
        id: 1,
        name: 'Project Alpha',
        messages: [
          { id: 1, author: 'Alice', text: 'Hey everyone!' },
          { id: 2, author: 'Bob', text: 'Hi Alice!' },
        ],
      },
      {
        id: 2,
        name: 'Private - Charlie',
        messages: [],
      },
    ],
  }),
  getters: {
    isLoggedIn: (state) => !!state.currentUser,
    getUserProjects: (state) => {
      if (state.currentUser) {
        return state.currentUser.projects
      }
      return []
    },
    getProjectFiles: (state) => (projectId) => {
      return state.files.filter((file) => file.projectId === projectId)
    },
  },
  actions: {
    login(email, password) {
      const user = this.users.find((user) => user.email === email && user.password === password)
      if (user) {
        this.currentUser = user
        return true
      }
      return false
    },
    logout() {
      this.currentUser = null
    },
    register(name, email, password) {
      const newUser = {
        id: this.users.length + 1,
        name,
        email,
        password,
        projects: [],
      }
      this.users.push(newUser)
    },
    addFile(projectId, file) {
      const newFile = {
        id: this.files.length + 1,
        projectId,
        name: file.name,
        content: file.content,
        comments: [],
      }
      this.files.push(newFile)
    },
    addComment(fileId, comment) {
      const file = this.files.find((f) => f.id === fileId)
      if (file) {
        const newComment = {
          id: file.comments.length + 1,
          author: this.currentUser.name,
          text: comment,
        }
        file.comments.push(newComment)
      }
    },
    addChatRoom(name) {
      const newRoom = {
        id: this.chatRooms.length + 1,
        name,
        messages: [],
      }
      this.chatRooms.push(newRoom)
    },
    addChatMessage(roomId, message) {
      const room = this.chatRooms.find((r) => r.id === roomId)
      if (room) {
        const newMessage = {
          id: room.messages.length + 1,
          author: this.currentUser.name,
          text: message,
        }
        room.messages.push(newMessage)
      }
    },
    addCodeSnippetMessage(roomId, codeSnippet) {
      const room = this.chatRooms.find((r) => r.id === roomId)
      if (room) {
        const newMessage = {
          id: room.messages.length + 1,
          author: this.currentUser.name,
          codeSnippet,
        }
        room.messages.push(newMessage)
      }
    },
  },
})
