export const chatApi = {
  fetchChatRooms: async () => {
    return fetch('/api/chatrooms/')
  },

  addChatRoom: async (name: string) => {
    return fetch('/api/chatrooms/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    })
  },

  addChatMessage: async (roomId: number, text: string) => {
    return fetch(`/api/chatrooms/${roomId}/messages/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    })
  },

  addCodeSnippetMessage: async (roomId: number, codeSnippet: { fileName: string, line?: number }) => {
    return fetch(`/api/chatrooms/${roomId}/messages/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        codeSnippetFile: codeSnippet.fileName,
        codeSnippetLine: codeSnippet.line || 1
      })
    })
  }
}
