<template>
  <div class="min-h-screen bg-gradient-to-br from-[#667eea] to-[#764ba2] flex items-center justify-center px-4 py-8">
    <!-- 登录卡片 -->
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8 space-y-6">
      <!-- Logo 和标题 -->
      <div class="text-center">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-[#667eea] to-[#764ba2] rounded-full mb-4">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-gray-800">欢迎回来</h1>
        <p class="text-gray-500 text-sm mt-2">请登录您的账号</p>
      </div>

      <!-- 错误提示 -->
      <div v-if="errorMessage" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
        {{ errorMessage }}
      </div>

      <!-- 登录表单 -->
      <form @submit.prevent="handleLogin" class="space-y-4">
        <!-- 用户名输入 -->
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
            用户名
          </label>
          <input
            id="username"
            v-model="username"
            type="text"
            required
            autocomplete="username"
            :disabled="loading"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#667eea] focus:border-transparent transition-all disabled:bg-gray-100 disabled:cursor-not-allowed"
            placeholder="请输入用户名"
          />
        </div>

        <!-- 密码输入 -->
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
            密码
          </label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            autocomplete="current-password"
            :disabled="loading"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#667eea] focus:border-transparent transition-all disabled:bg-gray-100 disabled:cursor-not-allowed"
            placeholder="请输入密码"
          />
        </div>

        <!-- 登录按钮 -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-gradient-to-r from-[#667eea] to-[#764ba2] text-white py-3 px-4 rounded-lg font-medium hover:shadow-lg transform hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center"
        >
          <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <!-- 底部提示 -->
      <div class="text-center text-sm text-gray-500 pt-4 border-t">
        <p>如需账号请联系管理员</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { collectFingerprint, generateFingerprintHash } from '@/utils/fingerprint'

const router = useRouter()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  // 清空错误信息
  errorMessage.value = ''
  loading.value = true

  try {
    // 1. 收集设备指纹
    const fingerprint = collectFingerprint()
    const fingerprintHash = await generateFingerprintHash(fingerprint)

    // 2. 调用登录 API（这里需要实现）
    // TODO: 实现登录逻辑
    console.log('Login attempt:', {
      username: username.value,
      fingerprint,
      fingerprintHash
    })

    // 临时：模拟登录成功
    await new Promise(resolve => setTimeout(resolve, 1000))

    // 3. 登录成功，跳转到首页
    router.push('/')
  } catch (error) {
    console.error('Login error:', error)
    errorMessage.value = error.message || '登录失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>
