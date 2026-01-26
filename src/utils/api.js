import axios from 'axios'

const API_BASE_URL = 'http://tofuali.top'

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
