<template>
  <el-timeline>
    <el-timeline-item
      v-for="post in posts"
      :key="post.id"
      :timestamp="formatDateTime(post.created_at)"
      placement="top"
      color="#667eea"
      size="large"
    >
      <div
        @click="openModal(post)"
        class="group relative bg-white p-5 sm:p-4 rounded-lg border border-gray-100 shadow-sm cursor-pointer transition-all duration-200 hover:shadow-md hover:border-[#667eea]/40 hover:-translate-y-0.5"
      >
        <h3 class="text-base font-bold text-gray-800 mb-2 group-hover:text-[#667eea] transition-colors pr-4">
          {{ getTitle(post.content) }}
        </h3>

        <p v-if="getPreview(post.content)" class="text-sm text-gray-500 line-clamp-2 leading-relaxed">
          {{ getPreview(post.content) }}
        </p>
      </div>
    </el-timeline-item>
  </el-timeline>

  <PostModal
    v-if="selectedPost"
    v-model="modalVisible"
    :post="selectedPost"
  />
</template>

<script setup>
import { ref } from 'vue'
import PostModal from './PostModal.vue'
import { formatDateTime } from '@/utils/format'

defineProps({
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

// 从内容中提取标题（第一行或前40个字符）
const getTitle = (content) => {
  if (!content) return ''

  // 如果有换行符，使用第一行作为标题
  const lines = content.split('\n').filter(line => line.trim())
  if (lines.length > 1) {
    const firstLine = lines[0].trim()
    return firstLine.length > 40 ? firstLine.substring(0, 40) + '...' : firstLine
  }

  // 如果内容较长，截取前40个字符作为标题
  if (content.length > 50) {
    return content.substring(0, 40).trim() + '...'
  }

  // 如果内容较短，直接作为标题
  return content.trim()
}

// 获取内容预览（跳过第一行，或显示剩余内容）
const getPreview = (content) => {
  if (!content) return ''

  // 如果有换行符，显示第一行之后的内容
  const lines = content.split('\n').filter(line => line.trim())
  if (lines.length > 1) {
    return lines.slice(1).join('\n').trim()
  }

  // 如果内容较长，显示标题之后的内容
  if (content.length > 50) {
    return content.substring(40).trim()
  }

  // 如果内容较短，不显示预览（避免重复）
  return ''
}
</script>

<style>
/* 全局样式：强制覆盖 Element Plus 的 timeline padding */
@media (max-width: 640px) {
  .el-timeline.is-start {
    padding-left: 0 !important;
  }
}
</style>

<style scoped>
/* 调整 Timeline 线条颜色 */
:deep(.el-timeline-item__tail) {
  border-left: 2px solid #e5e7eb;
}

/* 调整节点光晕：增加了一点点透明度，让它看起来更精致 */
:deep(.el-timeline-item__node) {
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
}

/* 强制覆盖时间戳的字体，保持一致性 */
:deep(.el-timeline-item__timestamp) {
  font-family: inherit;
}

/* 移动端优化：时间轴与标题左对齐 */
@media (max-width: 640px) {
  /* 移除时间轴容器的默认 padding */
  :deep(.el-timeline),
  :deep(.el-timeline.is-start) {
    padding-left: 0 !important;
  }

  /* 时间戳样式 - 极度压缩 */
  :deep(.el-timeline-item__timestamp) {
    font-size: 8px !important;
    padding-right: 2px !important;
    max-width: 32px !important;
    line-height: 1.1 !important;
    opacity: 0.7;
  }

  /* 时间轴节点 - 对齐到标题位置 */
  :deep(.el-timeline-item__node) {
    width: 8px !important;
    height: 8px !important;
    left: 32px !important;
  }

  /* 时间轴线条 - 对齐到标题位置 */
  :deep(.el-timeline-item__tail) {
    left: 32px !important;
  }

  /* 时间轴项目 */
  :deep(.el-timeline-item) {
    padding-left: 0 !important;
  }

  /* 内容区域 - 让卡片从节点位置开始，卡片内 padding 会让标题与节点对齐 */
  :deep(.el-timeline-item__wrapper) {
    padding-left: 8px !important;
    margin-left: 32px !important;
  }
}
</style>