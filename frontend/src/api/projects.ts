import { authFetch } from './http'

export const projectsApi = {
  fetchProjectFiles: async (projectId: number) => {
    return authFetch(`/api/projects/${projectId}/files/`)
  },

  addFile: async (
    projectId: number,
    file: {
      name: string
      filepath?: string
      content: string
      contentType?: string
      sizeBytes?: number
      isBinary?: boolean
    },
  ) => {
    return authFetch(`/api/projects/${projectId}/files/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(file)
    })
  },

  addComment: async (fileId: number, text: string) => {
    return authFetch(`/api/files/${fileId}/comments/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    })
  },

  addLineComment: async (fileId: number, data: { text: string; startLine: number; endLine: number }) => {
    return authFetch(`/api/files/${fileId}/line-comments/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
  },

  fetchLineComments: async (fileId: number) => {
    return authFetch(`/api/files/${fileId}/line-comments/`)
  },

  updateFileContent: async (fileId: number, content: string, note = '') => {
    return authFetch(`/api/files/${fileId}/content/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, note })
    })
  },

  fetchFileVersions: async (fileId: number) => {
    return authFetch(`/api/files/${fileId}/versions/`)
  },

  fetchFileVersionDiff: async (fileId: number, fromVersionId: number, toVersionId: number) => {
    return authFetch(`/api/files/${fileId}/versions/diff/?fromVersionId=${fromVersionId}&toVersionId=${toVersionId}`)
  },

  revertFileVersion: async (fileId: number, versionId: number, note = '') => {
    return authFetch(`/api/files/${fileId}/revert/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ versionId, note })
    })
  },

  markVersionSnapshot: async (fileId: number, versionId: number, tagName = '', isSnapshot = true) => {
    return authFetch(`/api/files/${fileId}/versions/${versionId}/snapshot/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tagName, isSnapshot })
    })
  },

  createProject: async (name: string) => {
    return authFetch('/api/projects/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    })
  },

  addProjectMember: async (projectId: number, email: string) => {
    return authFetch(`/api/projects/${projectId}/members/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    })
  },

  deleteFile: async (fileId: number) => {
    return authFetch(`/api/files/${fileId}/`, {
      method: 'DELETE'
    })
  },

  deleteProject: async (projectId: number) => {
    return authFetch(`/api/projects/${projectId}/`, {
      method: 'DELETE'
    })
  },

  fetchInvitations: async () => {
    return authFetch('/api/invitations/')
  },

  respondInvitation: async (invitationId: number, action: 'accept' | 'decline') => {
    return authFetch(`/api/invitations/${invitationId}/respond/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action })
    })
  },

  fetchProjectSettings: async (projectId: number) => {
    return authFetch(`/api/projects/${projectId}/settings/`)
  },

  updateProjectName: async (projectId: number, name: string) => {
    return authFetch(`/api/projects/${projectId}/settings/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    })
  },

  removeProjectMember: async (projectId: number, memberId: number) => {
    return authFetch(`/api/projects/${projectId}/settings/`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ member_id: memberId })
    })
  },
}
