import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

// 全局认证状态
const user = ref(null)
const session = ref(null)
const loading = ref(false)
const error = ref(null)

// 心跳定时器
let heartbeatInterval = null

export function useAuth() {
  const router = useRouter()

  // 计算属性
  const isAuthenticated = computed(() => !!user.value)
  const isLoading = computed(() => loading.value)

  /**
   * 登录
   * @param {string} username - 用户名
   * @param {string} password - 密码
   * @param {object} fingerprint - 设备指纹原始数据
   * @param {string} fingerprintHash - 设备指纹哈希
   */
  const login = async (username, password, fingerprint, fingerprintHash) => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username,
          password,
          fingerprint_raw: fingerprint,
          fingerprint_hash: fingerprintHash
        })
      })

      const result = await response.json()

      if (!response.ok) {
        throw new Error(result.error || '登录失败')
      }

      if (!result.success) {
        throw new Error(result.error || '登录失败')
      }

      // 保存用户信息和会话
      user.value = result.data.user
      session.value = result.data.session

      // 保存到 localStorage
      localStorage.setItem('auth_user', JSON.stringify(result.data.user))
      localStorage.setItem('auth_session', JSON.stringify(result.data.session))

      // 启动心跳
      startHeartbeat()

      return result.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 登出
   */
  const logout = async () => {
    loading.value = true
    error.value = null

    try {
      // 停止心跳
      stopHeartbeat()

      // 调用登出 API
      if (session.value?.id) {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            session_id: session.value.id
          })
        })
      }

      // 清除本地状态
      user.value = null
      session.value = null
      localStorage.removeItem('auth_user')
      localStorage.removeItem('auth_session')

      // 跳转到登录页
      router.push('/login')
    } catch (err) {
      error.value = err.message
      console.error('Logout error:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 启动心跳
   */
  const startHeartbeat = () => {
    // 清除旧的心跳
    stopHeartbeat()

    // 每 60 秒发送一次心跳
    heartbeatInterval = setInterval(async () => {
      if (!session.value?.id) {
        stopHeartbeat()
        return
      }

      try {
        const response = await fetch('/api/auth/heartbeat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            session_id: session.value.id
          })
        })

        const result = await response.json()

        // 如果账号被封禁，强制登出
        if (result.force_logout) {
          await logout()
          error.value = result.message || '您的账号已被限制访问'
        }
      } catch (err) {
        console.error('Heartbeat error:', err)
      }
    }, 60000) // 60 秒
  }

  /**
   * 停止心跳
   */
  const stopHeartbeat = () => {
    if (heartbeatInterval) {
      clearInterval(heartbeatInterval)
      heartbeatInterval = null
    }
  }

  /**
   * 从 localStorage 恢复会话
   */
  const restoreSession = () => {
    try {
      const savedUser = localStorage.getItem('auth_user')
      const savedSession = localStorage.getItem('auth_session')

      if (savedUser && savedSession) {
        user.value = JSON.parse(savedUser)
        session.value = JSON.parse(savedSession)

        // 启动心跳
        startHeartbeat()

        return true
      }
    } catch (err) {
      console.error('Failed to restore session:', err)
      localStorage.removeItem('auth_user')
      localStorage.removeItem('auth_session')
    }

    return false
  }

  /**
   * 检查认证状态
   */
  const checkAuth = () => {
    if (!isAuthenticated.value) {
      restoreSession()
    }
    return isAuthenticated.value
  }

  return {
    // 状态
    user,
    session,
    loading,
    error,
    isAuthenticated,
    isLoading,

    // 方法
    login,
    logout,
    restoreSession,
    checkAuth
  }
}
