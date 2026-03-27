export const projectsApi = {
  fetchProjectFiles: async (projectId: number) => {
    return fetch(`/api/projects/${projectId}/files/`)
  },

  addFile: async (projectId: number, file: { name: string, content: string }) => {
    return fetch(`/api/projects/${projectId}/files/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(file)
    })
  },

  addComment: async (fileId: number, text: string) => {
    return fetch(`/api/files/${fileId}/comments/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    })
  },

  createProject: async (name: string) => {
    return fetch('/api/projects/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    })
  },

  addProjectMember: async (projectId: number, email: string) => {
    return fetch(`/api/projects/${projectId}/members/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    })
  },

  deleteFile: async (fileId: number) => {
    return fetch(`/api/files/${fileId}/`, {
      method: 'DELETE'
    })
  },

  deleteProject: async (projectId: number) => {
    return fetch(`/api/projects/${projectId}/`, {
      method: 'DELETE'
    })
  },

  fetchInvitations: async () => {
    return fetch('/api/invitations/')
  },

  respondInvitation: async (invitationId: number, action: 'accept' | 'decline') => {
    return fetch(`/api/invitations/${invitationId}/respond/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action })
    })
  },
}
