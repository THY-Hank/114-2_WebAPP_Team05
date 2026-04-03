/* eslint-disable @typescript-eslint/no-explicit-any */
import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useMainStore } from '@/stores/main'
import { projectsApi } from '@/api/projects'

vi.mock('@/api/projects', () => ({
  projectsApi: {
    createProject: vi.fn(),
    addProjectMember: vi.fn(),
    deleteFile: vi.fn(),
    deleteProject: vi.fn(),
    fetchInvitations: vi.fn(),
    respondInvitation: vi.fn(),
    addLineComment: vi.fn(),
    fetchLineComments: vi.fn(),
  }
}))

describe('Project Store Actions', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('creates a project successfully', async () => {
    const store = useMainStore()
    // 預設為空殼
    store.currentUser = { id: 1, email: 'test@example.com', projects: [] } as any
    
    ;(projectsApi.createProject as any).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 99, name: 'New Project' })
    })

    const result = await store.createProject('New Project')
    expect(result).toBe(true)
    expect(store.currentUser?.projects.length).toBe(1)
    expect(store.currentUser?.projects[0].name).toBe('New Project')
  })

  it('adds a project member successfully', async () => {
    const store = useMainStore()
    ;(projectsApi.addProjectMember as any).mockResolvedValue({ ok: true })

    const result = await store.addProjectMember(99, 'partner@example.com')
    expect(result).toBe(true)
  })

  it('deletes a file successfully', async () => {
    const store = useMainStore()
    store.files = [{ id: 1, name: 'test.txt' }] as any[]
    ;(projectsApi.deleteFile as any).mockResolvedValue({ ok: true })

    const result = await store.deleteFile(1)
    expect(result).toBe(true)
    expect(store.files.length).toBe(0)
  })

  it('deletes a project successfully', async () => {
    const store = useMainStore()
    store.currentUser = { projects: [{ id: 99, name: 'Proj' }] } as any
    ;(projectsApi.deleteProject as any).mockResolvedValue({ ok: true })

    const result = await store.deleteProject(99)
    expect(result).toBe(true)
    expect(store.currentUser?.projects.length).toBe(0)
  })

  it('responds to an invitation', async () => {
    const store = useMainStore()
    store.invitations = [{ id: 10, project_name: 'InvProj' }] as any[]
    ;(projectsApi.respondInvitation as any).mockResolvedValue({ ok: true })

    const result = await store.respondInvitation(10, 'decline')
    expect(result).toBe(true)
    expect(store.invitations.length).toBe(0)
  })
})
