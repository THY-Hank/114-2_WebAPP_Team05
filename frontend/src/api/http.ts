const AUTH_TOKEN_KEY = 'chatdev_access_token'

export const getAuthToken = (): string => {
  return localStorage.getItem(AUTH_TOKEN_KEY) || ''
}

export const setAuthToken = (token: string) => {
  localStorage.setItem(AUTH_TOKEN_KEY, token)
}

export const clearAuthToken = () => {
  localStorage.removeItem(AUTH_TOKEN_KEY)
}

export const authFetch = (input: RequestInfo | URL, init: RequestInit = {}) => {
  const token = getAuthToken()
  const headers = new Headers(init.headers || {})

  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  return fetch(input, {
    ...init,
    headers,
  })
}
