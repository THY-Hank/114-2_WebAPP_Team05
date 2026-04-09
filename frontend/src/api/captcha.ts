/**
 * CAPTCHA 客户端集成（支持 Google reCAPTCHA v3 和本地演示模式）
 * 自动检测环境：
 * - 开发环境（无 Site Key）：使用本地演示模式
 * - 生产环境（有 Site Key）：使用 Google reCAPTCHA v3
 */

declare global {
  interface Window {
    grecaptcha: {
      execute: (siteKey: string, options: { action: string }) => Promise<string>
    }
  }
}

const RECAPTCHA_SITE_KEY = import.meta.env.VITE_RECAPTCHA_SITE_KEY || ''
const IS_DEMO_MODE = !RECAPTCHA_SITE_KEY

/**
 * 生成演示 CAPTCHA 令牌（用于开发环境）
 * 模拟 Google reCAPTCHA v3 的令牌格式
 */
const generateDemoToken = (): string => {
  // 生成一个演示令牌（随机字符串）
  const timestamp = Date.now()
  const random = Math.random().toString(36).substring(2, 15)
  return `demo_token_dev_${timestamp}_${random}`
}

/**
 * 加载 reCAPTCHA 脚本
 */
export const loadRecaptcha = (): Promise<void> => {
  return new Promise((resolve) => {
    if (IS_DEMO_MODE) {
      // 演示模式：无需加载脚本
      console.debug('[CAPTCHA] 本地演示模式，无需加载 Google reCAPTCHA 脚本')
      resolve()
      return
    }

    if (document.getElementById('recaptcha-script')) {
      resolve()
      return
    }

    const script = document.createElement('script')
    script.id = 'recaptcha-script'
    script.src = 'https://www.google.com/recaptcha/api.js'
    script.async = true
    script.defer = true
    script.onload = () => {
      console.debug('[CAPTCHA] Google reCAPTCHA 脚本加载成功')
      resolve()
    }
    script.onerror = () => {
      console.warn('[CAPTCHA] Google reCAPTCHA 脚本加载失败，将继续')
      resolve()
    }
    document.head.appendChild(script)
  })
}

/**
 * 获取 CAPTCHA 令牌
 * @param action - CAPTCHA 操作名称（'login', 'register' 等）
 * @returns 返回 CAPTCHA 令牌或 null
 */
export const getRecaptchaToken = async (action: string): Promise<string | null> => {
  try {
    // 确保脚本已加载
    await loadRecaptcha()

    // 演示模式：直接返回演示令牌
    if (IS_DEMO_MODE) {
      console.debug(`[CAPTCHA] 演示模式：为操作 '${action}' 返回演示令牌`)
      return generateDemoToken()
    }

    // 生产模式：使用 Google reCAPTCHA v3
    const token = await new Promise<string>((resolve, reject) => {
      if (window.grecaptcha) {
        window.grecaptcha
          .execute(RECAPTCHA_SITE_KEY, { action })
          .then((token) => {
            console.debug(`[CAPTCHA] Google reCAPTCHA 令牌获取成功，操作: ${action}`)
            resolve(token)
          })
          .catch((error) => reject(error))
      } else {
        reject(new Error('reCAPTCHA 未加载'))
      }
    })

    return token
  } catch (error) {
    console.error('[CAPTCHA] 获取令牌失败:', error)
    return null
  }
}

/**
 * 检查是否已配置 Google reCAPTCHA
 */
export const isRecaptchaConfigured = (): boolean => {
  return !!RECAPTCHA_SITE_KEY
}

/**
 * 检查是否使用演示模式
 */
export const isDemoMode = (): boolean => {
  return IS_DEMO_MODE
}

/**
 * 获取 CAPTCHA 模式信息
 */
export const getCaptchaMode = (): {
  isDemoMode: boolean
  isConfigured: boolean
  message: string
} => {
  return {
    isDemoMode: IS_DEMO_MODE,
    isConfigured: !!RECAPTCHA_SITE_KEY,
    message: IS_DEMO_MODE ? '本地演示模式（开发环境）' : 'Google reCAPTCHA v3（生产环境）'
  }
}
