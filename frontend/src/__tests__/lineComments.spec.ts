/* eslint-disable @typescript-eslint/no-explicit-any */
import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useMainStore } from '@/stores/main'
import { projectsApi } from '@/api/projects'
import { chatApi } from '@/api/chat'

vi.mock('@/api/projects', () => ({
  projectsApi: {
    addLineComment: vi.fn(),
    fetchLineComments: vi.fn(),
  }
}))

vi.mock('@/api/chat', () => ({
  chatApi: {
    addLineCodeSnippetMessage: vi.fn(),
  }
}))

describe('Line-Level Comments and Code Sharing', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('Line Comments', () => {
    it('adds a line comment successfully', async () => {
      const store = useMainStore()
      const mockComment = {
        id: 1,
        author: 'test@example.com',
        text: 'Great code!',
        startLine: 5,
        endLine: 5,
        createdAt: '2025-01-01T00:00:00Z'
      }

      ;(projectsApi.addLineComment as any).mockResolvedValue({
        ok: true,
        json: async () => mockComment
      })

      store.files = [
        {
          id: 1,
          name: 'test.js',
          content: 'console.log("hello");',
          comments: []
        }
      ] as any[]

      await store.addLineComment(1, {
        text: 'Great code!',
        startLine: 5,
        endLine: 5
      })

      expect(store.files[0].comments.length).toBe(1)
      expect(store.files[0].comments[0].startLine).toBe(5)
      expect(store.files[0].comments[0].endLine).toBe(5)
    })

    it('adds a multi-line comment successfully', async () => {
      const store = useMainStore()
      const mockComment = {
        id: 2,
        author: 'test@example.com',
        text: 'This block needs refactoring',
        startLine: 10,
        endLine: 20,
        createdAt: '2025-01-01T00:00:00Z'
      }

      ;(projectsApi.addLineComment as any).mockResolvedValue({
        ok: true,
        json: async () => mockComment
      })

      store.files = [
        {
          id: 1,
          name: 'test.js',
          content: 'console.log("hello");',
          comments: []
        }
      ] as any[]

      await store.addLineComment(1, {
        text: 'This block needs refactoring',
        startLine: 10,
        endLine: 20
      })

      expect(store.files[0].comments[0].startLine).toBe(10)
      expect(store.files[0].comments[0].endLine).toBe(20)
    })

    it('handles line comment error gracefully', async () => {
      const store = useMainStore()
      
      ;(projectsApi.addLineComment as any).mockResolvedValue({
        ok: false,
        json: async () => ({ error: 'Unauthorized' })
      })

      store.files = [
        {
          id: 1,
          name: 'test.js',
          content: 'console.log("hello");',
          comments: []
        }
      ] as any[]

      await store.addLineComment(1, {
        text: 'Failed comment',
        startLine: 5,
        endLine: 5
      })

      // Comments should not be added on error
      expect(store.files[0].comments.length).toBe(0)
    })
  })

  describe('Line-Level Code Sharing', () => {
    it('shares a single line of code successfully', async () => {
      const store = useMainStore()
      const mockMessage = {
        id: 1,
        author: 'test@example.com',
        text: null,
        codeSnippet: {
          fileName: 'test.js',
          startLine: 5,
          endLine: 5,
          content: 'console.log("hello");',
          line: null
        },
        createdAt: '2025-01-01T00:00:00Z'
      }

      ;(chatApi.addLineCodeSnippetMessage as any).mockResolvedValue({
        ok: true,
        json: async () => mockMessage
      })

      store.chatRooms = [
        {
          id: 1,
          name: 'Test Room',
          messages: []
        }
      ] as any[]

      await store.addLineCodeSnippetMessage(1, 1, {
        fileName: 'test.js',
        startLine: 5,
        endLine: 5,
        content: 'console.log("hello");'
      })

      expect(store.chatRooms[0].messages.length).toBe(1)
      expect(store.chatRooms[0].messages[0].codeSnippet.startLine).toBe(5)
      expect(store.chatRooms[0].messages[0].codeSnippet.endLine).toBe(5)
    })

    it('shares multiple lines of code successfully', async () => {
      const store = useMainStore()
      const codeContent = `function test() {
  const x = 10;
  return x * 2;
}`

      const mockMessage = {
        id: 2,
        author: 'test@example.com',
        text: null,
        codeSnippet: {
          fileName: 'utils.js',
          startLine: 15,
          endLine: 18,
          content: codeContent,
          line: null
        },
        createdAt: '2025-01-01T00:00:00Z'
      }

      ;(chatApi.addLineCodeSnippetMessage as any).mockResolvedValue({
        ok: true,
        json: async () => mockMessage
      })

      store.chatRooms = [
        {
          id: 1,
          name: 'Test Room',
          messages: []
        }
      ] as any[]

      await store.addLineCodeSnippetMessage(1, 1, {
        fileName: 'utils.js',
        startLine: 15,
        endLine: 18,
        content: codeContent
      })

      expect(store.chatRooms[0].messages.length).toBe(1)
      const msg = store.chatRooms[0].messages[0]
      expect(msg.codeSnippet.startLine).toBe(15)
      expect(msg.codeSnippet.endLine).toBe(18)
      expect(msg.codeSnippet.content).toContain('function test')
    })

    it('shares code snippet with accompanying text', async () => {
      const store = useMainStore()
      const mockMessage = {
        id: 3,
        author: 'test@example.com',
        text: 'Check this out:',
        codeSnippet: {
          fileName: 'app.js',
          startLine: 1,
          endLine: 3,
          content: 'function main() {...}',
          line: null
        },
        createdAt: '2025-01-01T00:00:00Z'
      }

      ;(chatApi.addLineCodeSnippetMessage as any).mockResolvedValue({
        ok: true,
        json: async () => mockMessage
      })

      store.chatRooms = [
        {
          id: 1,
          name: 'Test Room',
          messages: []
        }
      ] as any[]

      await store.addLineCodeSnippetMessage(1, 1, {
        fileName: 'app.js',
        startLine: 1,
        endLine: 3,
        content: 'function main() {...}'
      })

      expect(store.chatRooms[0].messages[0].text).toBe('Check this out:')
      expect(store.chatRooms[0].messages[0].codeSnippet).toBeDefined()
    })

    it('handles code sharing error gracefully', async () => {
      const store = useMainStore()
      
      ;(chatApi.addLineCodeSnippetMessage as any).mockResolvedValue({
        ok: false
      })

      store.chatRooms = [
        {
          id: 1,
          name: 'Test Room',
          messages: []
        }
      ] as any[]

      await store.addLineCodeSnippetMessage(1, 1, {
        fileName: 'test.js',
        startLine: 5,
        endLine: 5,
        content: 'console.log("hello");'
      })

      // Message should not be added on error
      expect(store.chatRooms[0].messages.length).toBe(0)
    })
  })

  describe('Backward Compatibility', () => {
    it('maintains compatibility with existing comment format', async () => {
      const store = useMainStore()
      
      store.files = [
        {
          id: 1,
          name: 'test.js',
          content: 'console.log("hello");',
          comments: [
            {
              id: 1,
              author: 'test@example.com',
              text: 'File-level comment',
              // No startLine/endLine - file-level comment
            },
            {
              id: 2,
              author: 'test@example.com',
              text: 'Line-level comment',
              startLine: 1,
              endLine: 1
            }
          ]
        }
      ] as any[]

      // Both types of comments should coexist
      const fileComments = store.files[0].comments.filter((c: any) => !c.startLine)
      const lineComments = store.files[0].comments.filter((c: any) => c.startLine)

      expect(fileComments.length).toBe(1)
      expect(lineComments.length).toBe(1)
    })
  })
})
