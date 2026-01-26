import { ref } from 'vue'
import { getPosts } from '@/utils/api'
import { ElMessage } from 'element-plus'

export function usePosts() {
  const posts = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchPosts = async () => {
    loading.value = true
    error.value = null
    try {
      const data = await getPosts()
      posts.value = data
    } catch (err) {
      error.value = err.message
      ElMessage.error(`无法连接到服务器，请检查后端 API 是否正常运行。错误信息: ${err.message}`)
    } finally {
      loading.value = false
    }
  }

  return {
    posts,
    loading,
    error,
    fetchPosts
  }
}
