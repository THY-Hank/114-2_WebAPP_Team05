import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
/* eslint-disable @typescript-eslint/no-explicit-any */
import { setActivePinia, createPinia } from 'pinia'
import { useMainStore } from '@/stores/main'

describe('Auth Store (main.ts) Authentication Actions', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    // 模擬 fetch API (Mock fetch)
    global.fetch = vi.fn()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('successful login sets currentUser and returns true', async () => {
    const store = useMainStore()
    const mockUser = { email: 'test@example.com', name: 'Test User' }
    
    // 模擬成功的登入與依序取得環境資料的回應
    ;(global.fetch as any).mockImplementation((url: string, _init: any) => {
      if (url.includes('/login/')) {
        return Promise.resolve({ ok: true, json: async () => ({ message: 'Login successful!', user: mockUser }) })
      }
      if (url.includes('/me/')) {
        return Promise.resolve({ ok: true, json: async () => ({ id: 1, email: 'test@example.com', projects: [] }) })
      }
      if (url.includes('/chatrooms/')) {
        return Promise.resolve({ ok: true, json: async () => ([]) })
      }
      return Promise.resolve({ ok: false })
    })

    const result = await store.login('test@example.com', 'password123')
    
    expect(result).toBe(true)
    expect(store.currentUser).toEqual(mockUser)
    
    // 驗證 fetch 有被正確呼叫
    expect(global.fetch).toHaveBeenCalledWith('/api/user/login/', expect.objectContaining({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }))
  })

  it('failed login returns false and does not set currentUser', async () => {
    const store = useMainStore()
    
    // 模擬失敗的登入回應 (例如密碼錯誤)
    ;(global.fetch as any).mockResolvedValue({
      ok: false,
      json: async () => ({
        error: 'Invalid credentials'
      })
    })

    const result = await store.login('wrong@example.com', 'wrongpassword')
    
    expect(result).toBe(false)
    expect(store.currentUser).toBeNull()
  })

  it('successful register returns true', async () => {
    const store = useMainStore()
    
    // 模擬成功的註冊回應
    ;(global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        message: 'User registered successfully!'
      })
    })

    const result = await store.register('New User', 'new@example.com', 'password123')
    
    expect(result).toBe(true)
    expect(global.fetch).toHaveBeenCalledWith('/api/user/register/', expect.objectContaining({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }))
  })

  it('failed register returns false', async () => {
    const store = useMainStore()
    
    // 模擬失敗的註冊回應
    ;(global.fetch as any).mockResolvedValue({
      ok: false,
      json: async () => ({
        error: 'Registration failed'
      })
    })

    const result = await store.register('New User', 'existing@example.com', 'password123')
    
    expect(result).toBe(false)
  })

  it('logout clears currentUser globally', async () => {
    const store = useMainStore()
    // 先假裝我們有一個登入的使用者
    ;(store.currentUser as any) = { email: 'test@example.com', name: 'Test User' }

    // 模擬登出回應
    ;(global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({ message: 'Logout successful!' })
    })

    await store.logout()

    // 驗證使用者已被清除
    expect(store.currentUser).toBeNull()
    expect(global.fetch).toHaveBeenCalledWith('/api/user/logout/', expect.objectContaining({
      method: 'POST'
    }))
  })
})
