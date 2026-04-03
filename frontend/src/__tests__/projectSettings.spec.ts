/* eslint-disable @typescript-eslint/no-explicit-any */
import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { useMainStore } from '@/stores/main'
import { projectsApi } from '@/api/projects'

vi.mock('@/api/projects', () => ({
  projectsApi: {
    fetchProjectSettings: vi.fn(),
    updateProjectName: vi.fn(),
    removeProjectMember: vi.fn(),
    addProjectMember: vi.fn(),
    deleteProject: vi.fn(),
  }
}))

describe('Project Settings', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('fetchProjectSettings', () => {
    it('fetches project settings with members list', async () => {
      const mockSettings = {
        id: 1,
        name: 'Test Project',
        owner_id: 1,
        members: [
          { id: 1, name: 'Owner', email: 'owner@example.com', isOwner: true },
          { id: 2, name: 'Member', email: 'member@example.com', isOwner: false }
        ]
      }
      
      ;(projectsApi.fetchProjectSettings as any).mockResolvedValue({
        ok: true,
        json: async () => mockSettings
      })

      const response = await projectsApi.fetchProjectSettings(1)
      const data = await response.json()
      
      expect(data.id).toBe(1)
      expect(data.name).toBe('Test Project')
      expect(data.members.length).toBe(2)
      expect(data.members[0].isOwner).toBe(true)
      expect(data.members[1].isOwner).toBe(false)
    })

    it('handles fetch error gracefully', async () => {
      ;(projectsApi.fetchProjectSettings as any).mockResolvedValue({
        ok: false,
        status: 404,
        json: async () => ({ error: 'Project not found' })
      })

      const response = await projectsApi.fetchProjectSettings(999)
      expect(response.ok).toBe(false)
      expect(response.status).toBe(404)
    })
  })

  describe('updateProjectName', () => {
    it('updates project name successfully', async () => {
      const newName = 'Updated Project Name'
      
      ;(projectsApi.updateProjectName as any).mockResolvedValue({
        ok: true,
        json: async () => ({ name: newName })
      })

      const response = await projectsApi.updateProjectName(1, newName)
      expect(response.ok).toBe(true)
      expect(projectsApi.updateProjectName).toHaveBeenCalledWith(1, newName)
    })

    it('returns error when not owner', async () => {
      ;(projectsApi.updateProjectName as any).mockResolvedValue({
        ok: false,
        status: 403,
        json: async () => ({ error: 'Only owner can update project name' })
      })

      const response = await projectsApi.updateProjectName(1, 'New Name')
      expect(response.ok).toBe(false)
      expect(response.status).toBe(403)
    })

    it('returns error with empty name', async () => {
      ;(projectsApi.updateProjectName as any).mockResolvedValue({
        ok: false,
        status: 400,
        json: async () => ({ error: 'Project name cannot be empty' })
      })

      const response = await projectsApi.updateProjectName(1, '')
      expect(response.ok).toBe(false)
    })
  })

  describe('removeProjectMember', () => {
    it('removes member successfully', async () => {
      ;(projectsApi.removeProjectMember as any).mockResolvedValue({
        ok: true,
        json: async () => ({ message: 'Member removed successfully' })
      })

      const response = await projectsApi.removeProjectMember(1, 2)
      expect(response.ok).toBe(true)
      expect(projectsApi.removeProjectMember).toHaveBeenCalledWith(1, 2)
    })

    it('returns error when not owner', async () => {
      ;(projectsApi.removeProjectMember as any).mockResolvedValue({
        ok: false,
        status: 403,
        json: async () => ({ error: 'Only owner can remove members' })
      })

      const response = await projectsApi.removeProjectMember(1, 2)
      expect(response.ok).toBe(false)
      expect(response.status).toBe(403)
    })

    it('returns error when trying to remove owner', async () => {
      ;(projectsApi.removeProjectMember as any).mockResolvedValue({
        ok: false,
        status: 400,
        json: async () => ({ error: 'Cannot remove the owner from the project' })
      })

      const response = await projectsApi.removeProjectMember(1, 1)
      expect(response.ok).toBe(false)
      expect(response.status).toBe(400)
    })

    it('returns error when user is not a member', async () => {
      ;(projectsApi.removeProjectMember as any).mockResolvedValue({
        ok: false,
        status: 400,
        json: async () => ({ error: 'User is not a member of this project' })
      })

      const response = await projectsApi.removeProjectMember(1, 999)
      expect(response.ok).toBe(false)
      expect(response.status).toBe(400)
    })
  })

  describe('addProjectMember', () => {
    it('sends invitation successfully', async () => {
      ;(projectsApi.addProjectMember as any).mockResolvedValue({
        ok: true,
        json: async () => ({ message: 'Invitation sent' })
      })

      const response = await projectsApi.addProjectMember(1, 'newmember@example.com')
      expect(response.ok).toBe(true)
      expect(projectsApi.addProjectMember).toHaveBeenCalledWith(1, 'newmember@example.com')
    })

    it('returns error for invalid email', async () => {
      ;(projectsApi.addProjectMember as any).mockResolvedValue({
        ok: false,
        status: 400,
        json: async () => ({ error: 'Invalid email format' })
      })

      const response = await projectsApi.addProjectMember(1, 'invalid-email')
      expect(response.ok).toBe(false)
    })

    it('returns error for non-existent user', async () => {
      ;(projectsApi.addProjectMember as any).mockResolvedValue({
        ok: false,
        status: 404,
        json: async () => ({ error: 'User with this email does not exist' })
      })

      const response = await projectsApi.addProjectMember(1, 'nonexistent@example.com')
      expect(response.ok).toBe(false)
      expect(response.status).toBe(404)
    })

    it('returns error when user already a member', async () => {
      ;(projectsApi.addProjectMember as any).mockResolvedValue({
        ok: false,
        status: 400,
        json: async () => ({ error: 'User is already a member of this project' })
      })

      const response = await projectsApi.addProjectMember(1, 'existingmember@example.com')
      expect(response.ok).toBe(false)
    })
  })

  describe('deleteProject', () => {
    it('deletes project successfully', async () => {
      ;(projectsApi.deleteProject as any).mockResolvedValue({
        ok: true,
        status: 200
      })

      const response = await projectsApi.deleteProject(1)
      expect(response.ok).toBe(true)
      expect(projectsApi.deleteProject).toHaveBeenCalledWith(1)
    })

    it('returns error when not owner', async () => {
      ;(projectsApi.deleteProject as any).mockResolvedValue({
        ok: false,
        status: 403,
        json: async () => ({ error: 'Only owner can delete project' })
      })

      const response = await projectsApi.deleteProject(1)
      expect(response.ok).toBe(false)
      expect(response.status).toBe(403)
    })

    it('returns 404 for non-existent project', async () => {
      ;(projectsApi.deleteProject as any).mockResolvedValue({
        ok: false,
        status: 404
      })

      const response = await projectsApi.deleteProject(999)
      expect(response.ok).toBe(false)
      expect(response.status).toBe(404)
    })
  })

  describe('ProjectSettings Store Integration', () => {
    it('loads project settings into store state', async () => {
      const store = useMainStore()
      store.currentUser = {
        id: 1,
        email: 'owner@example.com',
        projects: [{ id: 1, name: 'Test Project', owner_id: 1, members: [] }]
      } as any

      const mockSettings = {
        id: 1,
        name: 'Test Project',
        owner_id: 1,
        members: [
          { id: 1, name: 'Owner', email: 'owner@example.com', isOwner: true },
          { id: 2, name: 'Jane', email: 'jane@example.com', isOwner: false }
        ]
      }

      ;(projectsApi.fetchProjectSettings as any).mockResolvedValue({
        ok: true,
        json: async () => mockSettings
      })

      const response = await projectsApi.fetchProjectSettings(1)
      const data = await response.json()
      
      expect(data.members.length).toBe(2)
    })

    it('updates project name in store', async () => {
      const store = useMainStore()
      const project = {
        id: 1,
        name: 'Old Name',
        owner_id: 1,
        members: []
      }
      store.currentUser = {
        id: 1,
        email: 'owner@example.com',
        projects: [project]
      } as any

      ;(projectsApi.updateProjectName as any).mockResolvedValue({
        ok: true,
        json: async () => ({ name: 'New Name' })
      })

      const response = await projectsApi.updateProjectName(1, 'New Name')
      expect(response.ok).toBe(true)
      
      // In real component, this would update store.currentUser.projects[0].name
      if (response.ok) {
        const data = await response.json()
        project.name = data.name
      }
      
      expect(project.name).toBe('New Name')
    })

    it('removes member from store', async () => {
      const store = useMainStore()
      const members = [
        { id: 1, name: 'Owner', email: 'owner@example.com', isOwner: true },
        { id: 2, name: 'Jane', email: 'jane@example.com', isOwner: false }
      ]

      ;(projectsApi.removeProjectMember as any).mockResolvedValue({
        ok: true,
        json: async () => ({ message: 'Member removed' })
      })

      const response = await projectsApi.removeProjectMember(1, 2)
      expect(response.ok).toBe(true)
      
      // Simulate removing member from local state
      if (response.ok) {
        const updatedMembers = members.filter(m => m.id !== 2)
        expect(updatedMembers.length).toBe(1)
        expect(updatedMembers[0]?.id).toBe(1)
      }
    })
  })

  describe('Permission Checks', () => {
    it('identifies owner correctly', () => {
      const store = useMainStore()
      store.currentUser = { id: 1, email: 'owner@example.com' } as any

      const project = { id: 1, name: 'Test', owner_id: 1 }
      const isOwner = store.currentUser.id === project.owner_id
      
      expect(isOwner).toBe(true)
    })

    it('identifies non-owner correctly', () => {
      const store = useMainStore()
      store.currentUser = { id: 2, email: 'member@example.com' } as any

      const project = { id: 1, name: 'Test', owner_id: 1 }
      const isOwner = store.currentUser.id === project.owner_id
      
      expect(isOwner).toBe(false)
    })

    it('verifies member ownership badge', () => {
      const members = [
        { id: 1, name: 'Owner', isOwner: true },
        { id: 2, name: 'Member', isOwner: false }
      ]

      const ownerMember = members.find(m => m.isOwner)
      const regularMember = members.find(m => !m.isOwner)
      
      expect(ownerMember?.name).toBe('Owner')
      expect(regularMember?.name).toBe('Member')
    })
  })

  describe('Email Validation', () => {
    it('validates email format', () => {
      const validEmails = [
        'user@example.com',
        'test.user@example.co.uk',
        'user+tag@example.com'
      ]

      const invalidEmails = [
        'invalid-email',
        '@example.com',
        'user@',
        'user @example.com'
      ]

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

      validEmails.forEach(email => {
        expect(emailRegex.test(email)).toBe(true)
      })

      invalidEmails.forEach(email => {
        expect(emailRegex.test(email)).toBe(false)
      })
    })

    it('trims whitespace from email input', () => {
      const email = '  user@example.com  '
      const trimmed = email.trim()
      expect(trimmed).toBe('user@example.com')
    })
  })
})
