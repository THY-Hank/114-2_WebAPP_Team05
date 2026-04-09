import CryptoJS from 'crypto-js'
import { authFetch } from './http'
import { getRecaptchaToken } from './captcha'

const SECRET_KEY = import.meta.env.VITE_AES_KEY || 'team05_secret_key_12345678901234'
const IV = import.meta.env.VITE_AES_IV || 'team05_shared_iv'

const encryptPassword = (password: string): string => {
  const keyStr = CryptoJS.enc.Utf8.parse(SECRET_KEY)
  const ivStr = CryptoJS.enc.Utf8.parse(IV)
  const encrypted = CryptoJS.AES.encrypt(password, keyStr, {
    iv: ivStr,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7,
  })
  return encrypted.toString()
}

export const authApi = {
  login: async (email: string, password: string) => {
    const encryptedPassword = encryptPassword(password)
    
    // 获取 reCAPTCHA 令牌
    const recaptchaToken = await getRecaptchaToken('login')
    
    const response = await fetch('/api/user/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email,
        password: encryptedPassword,
        recaptchaToken: recaptchaToken || ''
      })
    })
    return response
  },

  register: async (name: string, email: string, password: string) => {
    const encryptedPassword = encryptPassword(password)
    
    // 获取 reCAPTCHA 令牌
    const recaptchaToken = await getRecaptchaToken('register')
    
    const response = await fetch('/api/user/register/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name,
        email,
        password: encryptedPassword,
        recaptchaToken: recaptchaToken || ''
      })
    })
    return response
  },

  logout: async () => {
    return authFetch('/api/user/logout/', { method: 'POST' })
  },

  fetchMe: async () => {
    return authFetch('/api/user/me/')
  }
}
