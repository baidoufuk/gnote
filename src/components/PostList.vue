<template>
  <div class="space-y-8">
    <!-- 日期分组 -->
    <div
      v-for="(group, date) in groupedPosts"
      :key="date"
      class="space-y-3"
    >
      <!-- 日期标题 -->
      <div class="text-sm text-gray-400 font-medium pl-1">
        {{ date }}
      </div>

      <!-- 当天的消息列表 -->
      <div class="space-y-2">
        <div
          v-for="post in group"
          :key="post.id"
          @click="openModal(post)"
          class="group bg-white
                 px-4 py-3
                 rounded-md border border-gray-100
                 cursor-pointer
                 transition-colors duration-150
                 hover:border-gray-200"
        >
          <!-- 时间 + 标题 -->
          <div class="flex items-start gap-3">
            <!-- 时间（徽章样式） -->
            <span class="inline-flex items-center justify-center
                         min-w-[42px] px-2 py-0.5
                         text-[10px] font-medium text-gray-600
                         bg-gray-100 rounded
                         whitespace-nowrap">
              {{ formatTime(post.created_at) }}
            </span>

            <h3
              class="text-[15px] font-medium text-gray-800
                     leading-snug group-hover:text-gray-900 flex-1"
            >
              {{ getTitle(post.content) }}
            </h3>
          </div>

          <!-- 预览内容 -->
          <p
            v-if="getPreview(post.content)"
            class="mt-1 text-[13px] text-gray-500
                   leading-relaxed line-clamp-2"
          >
            {{ getPreview(post.content) }}
          </p>
        </div>
      </div>
    </div>
  </div>

  <PostModal
    v-if="selectedPost"
    v-model="modalVisible"
    :post="selectedPost"
  />
</template>

<script setup>
import { ref, computed } from 'vue'
import PostModal from './PostModal.vue'
import { formatDateTime } from '@/utils/format'

const props = defineProps({
  posts: {
    type: Array,
    required: true
  }
})

const selectedPost = ref(null)
const modalVisible = ref(false)

const openModal = (post) => {
  selectedPost.value = post
  modalVisible.value = true
}

/**
 * 按日期分组（最新日期在最上）
 */
const groupedPosts = computed(() => {
  const groups = {}

  // 先按时间倒序（确保最新在前）
  const sorted = [...props.posts].sort(
    (a, b) => new Date(b.created_at) - new Date(a.created_at)
  )

  for (const post of sorted) {
    const dateKey = formatDate(post.created_at)
    if (!groups[dateKey]) {
      groups[dateKey] = []
    }
    groups[dateKey].push(post)
  }

  return groups
})

// 只显示日期（YYYY-MM-DD）
const formatDate = (datetime) => {
  return formatDateTime(datetime).split(' ')[0]
}

// 只显示时间（HH:mm）
const formatTime = (datetime) => {
  const parts = formatDateTime(datetime).split(' ')
  return parts[1] || ''
}

// ===== 原有逻辑，未改 =====

const getTitle = (content) => {
  if (!content) return ''
  const lines = content.split('\n').filter(line => line.trim())
  if (lines.length > 1) {
    const firstLine = lines[0].trim()
    return firstLine.length > 40 ? firstLine.substring(0, 40) + '...' : firstLine
  }
  if (content.length > 50) {
    return content.substring(0, 40).trim() + '...'
  }
  return content.trim()
}

const getPreview = (content) => {
  if (!content) return ''
  const lines = content.split('\n').filter(line => line.trim())
  if (lines.length > 1) {
    return lines.slice(1).join('\n').trim()
  }
  if (content.length > 50) {
    return content.substring(40).trim()
  }
  return ''
}
</script>

<style scoped>
/* 整体背景干净，像 Notion / 日志 */
</style>