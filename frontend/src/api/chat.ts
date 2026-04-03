export const chatApi = {
  fetchChatRooms: async (projectId: number) => {
    return fetch(`/api/projects/${projectId}/chatrooms/`)
  },

  addChatRoom: async (projectId: number, name: string, memberIds?: number[]) => {
    return fetch(`/api/projects/${projectId}/chatrooms/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, memberIds })
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
  },

  addLineCodeSnippetMessage: async (projectId: number, roomId: number, codeSnippet: { fileName: string, startLine: number, endLine: number, content: string }) => {
    return fetch(`/api/projects/${projectId}/chatrooms/${roomId}/messages/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        codeSnippetFile: codeSnippet.fileName,
        codeSnippetStartLine: codeSnippet.startLine,
        codeSnippetEndLine: codeSnippet.endLine,
        codeSnippetContent: codeSnippet.content
      })
    })
  }
}
