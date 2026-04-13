/* eslint-disable @typescript-eslint/no-explicit-any */
import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useMainStore } from '@/stores/main'
import { chatApi } from '@/api/chat'

vi.mock('@/api/chat', () => ({
  chatApi: {
    fetchChatRooms: vi.fn(),
    addChatRoom: vi.fn(),
    addChatMessage: vi.fn(),
    addCodeSnippetMessage: vi.fn(),
    addLineCodeSnippetMessage: vi.fn(),
  }
}))

describe('Chat Store Actions', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('loads chat rooms successfully', async () => {
    const store = useMainStore()
    ;(chatApi.fetchChatRooms as any).mockResolvedValue({
      ok: true,
      json: async () => [{ id: 1, name: 'Room 1' }]
    })

    await store.loadProjectChatRooms(1)
    expect(store.chatRooms.length).toBe(1)
    expect(store.chatRooms[0].name).toBe('Room 1')
  })

  it('adds a chat room successfully', async () => {
    const store = useMainStore()
    ;(chatApi.addChatRoom as any).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 2, name: 'New Room' })
    })

    await store.addChatRoom(1, 'New Room')
    expect(store.chatRooms.length).toBe(1)
    expect(store.chatRooms[0].name).toBe('New Room')
  })

  it('adds a chat message successfully', async () => {
    const store = useMainStore()
    store.chatRooms = [{ id: 1, name: 'Room 1', messages: [] }] as any[]
    ;(chatApi.addChatMessage as any).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 10, text: 'Hello' })
    })

    await store.addChatMessage(1, 1, { text: 'Hello' })
    expect(store.chatRooms[0].messages.length).toBe(1)
    expect(store.chatRooms[0].messages[0].text).toBe('Hello')
  })

  it('adds a code snippet message successfully', async () => {
    const store = useMainStore()
    store.chatRooms = [{ id: 1, name: 'Room 1', messages: [] }] as any[]
    ;(chatApi.addCodeSnippetMessage as any).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 11, codeSnippet: { fileName: 'test.py', line: 1 } })
    })

    await store.addCodeSnippetMessage(1, 1, { fileName: 'test.py', line: 1 })
    expect(store.chatRooms[0].messages.length).toBe(1)
    expect(store.chatRooms[0].messages[0].codeSnippet.fileName).toBe('test.py')
  })
})
