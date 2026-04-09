import { authFetch } from './http'

export const chatApi = {
  fetchChatRooms: async (projectId: number) => {
    return authFetch(`/api/projects/${projectId}/chatrooms/`)
  },

  addChatRoom: async (projectId: number, name: string, memberIds?: number[]) => {
    return authFetch(`/api/projects/${projectId}/chatrooms/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, memberIds })
    })
  },

  renameChatRoom: async (projectId: number, roomId: number, name: string) => {
    return authFetch(`/api/projects/${projectId}/chatrooms/${roomId}/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    })
  },

  deleteChatRoom: async (projectId: number, roomId: number) => {
    return authFetch(`/api/projects/${projectId}/chatrooms/${roomId}/`, {
      method: 'DELETE',
    })
  },

  addChatMessage: async (projectId: number, roomId: number, text: string) => {
    return authFetch(`/api/projects/${projectId}/chatrooms/${roomId}/messages/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    })
  },

  addCodeSnippetMessage: async (projectId: number, roomId: number, codeSnippet: { fileName: string, line?: number }) => {
    return authFetch(`/api/projects/${projectId}/chatrooms/${roomId}/messages/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        codeSnippetFile: codeSnippet.fileName,
        codeSnippetLine: codeSnippet.line || 1
      })
    })
  },

  addLineCodeSnippetMessage: async (projectId: number, roomId: number, codeSnippet: { fileName: string, startLine: number, endLine: number, content: string }) => {
    return authFetch(`/api/projects/${projectId}/chatrooms/${roomId}/messages/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        codeSnippetFile: codeSnippet.fileName,
        codeSnippetStartLine: codeSnippet.startLine,
        codeSnippetEndLine: codeSnippet.endLine,
        codeSnippetContent: codeSnippet.content
      })
    })
  },

  markChatRoomRead: async (projectId: number, roomId: number) => {
    return authFetch(`/api/projects/${projectId}/chatrooms/${roomId}/read/`, {
      method: 'POST',
    })
  },

  pinChatMessage: async (projectId: number, roomId: number, messageId: number, isPinned: boolean) => {
    return authFetch(`/api/projects/${projectId}/chatrooms/${roomId}/messages/${messageId}/pin/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ isPinned }),
    })
  },
}
