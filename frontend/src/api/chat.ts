export const chatApi = {
  fetchChatRooms: async (projectId: number) => {
    return fetch(`/api/projects/${projectId}/chatrooms/`)
  },

  addChatRoom: async (projectId: number, name: string) => {
    return fetch(`/api/projects/${projectId}/chatrooms/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    })
  },

  addChatMessage: async (projectId: number, roomId: number, text: string) => {
    return fetch(`/api/projects/${projectId}/chatrooms/${roomId}/messages/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    })
  },

  addCodeSnippetMessage: async (projectId: number, roomId: number, codeSnippet: { fileName: string, line?: number }) => {
    return fetch(`/api/projects/${projectId}/chatrooms/${roomId}/messages/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        codeSnippetFile: codeSnippet.fileName,
        codeSnippetLine: codeSnippet.line || 1
      })
    })
  }
}
