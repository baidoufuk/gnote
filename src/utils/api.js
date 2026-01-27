import axios from 'axios'

// 使用相对路径，部署到 Vercel 后会自动调用同域名下的 API
// 开发环境可以通过 VITE_API_BASE_URL 环境变量指定 API 地址
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const getPosts = async () => {
  const result = await apiClient.get('/api/posts')
  if (result.success && result.data) {
    return result.data
  }
  throw new Error('数据格式错误')
}

export { API_BASE_URL }
