<template>
  <el-dialog
    v-model="dialogVisible"
    width="90%"
    :style="{ maxWidth: '700px' }"
    :show-close="true"
    class="custom-dialog"
  >
    <template #header>
      <div class="flex items-center gap-2 px-2">
        <div class="flex items-center justify-center w-8 h-8 bg-gradient-to-br from-[#667eea]/20 to-[#764ba2]/20 rounded-lg">
          <svg class="w-4 h-4 text-[#667eea]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <div class="text-sm text-gray-600">{{ formatDateTimeFull(post.created_at) }}</div>
      </div>
    </template>

    <div class="px-2 py-3">
      <div class="text-gray-800 text-[15px] leading-[1.75] whitespace-pre-wrap break-words font-medium">
        {{ post.content }}
      </div>
      <div v-if="hasImage" class="mt-5 rounded-xl overflow-hidden shadow-md border border-gray-100">
        <img
          :src="imageUrl"
          alt="内容配图"
          loading="lazy"
          class="w-full h-auto"
        />
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { formatDateTimeFull } from '@/utils/format'
import { API_BASE_URL } from '@/utils/api'

const props = defineProps({
  post: {
    type: Object,
    required: true
  },
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const dialogVisible = ref(props.modelValue)

// 检查是否有图片
const hasImage = computed(() =>
  typeof props.post?.image_path === 'string' && props.post.image_path.trim().length > 0
)

// 智能处理图片 URL：如果是完整 URL 直接使用，否则拼接 uploads 路径
const imageUrl = computed(() => {
  if (!hasImage.value) return ''
  const trimmedPath = props.post.image_path.trim()
  // 检查是否已经是完整的 HTTP(S) URL
  return /^https?:\/\//i.test(trimmedPath)
    ? trimmedPath
    : `${API_BASE_URL}/uploads/${trimmedPath.replace(/^\/+/, '')}`
})

watch(() => props.modelValue, (newVal) => {
  dialogVisible.value = newVal
})

watch(dialogVisible, (newVal) => {
  emit('update:modelValue', newVal)
})
</script>

<style>
.custom-dialog .el-dialog {
  border-radius: 1.25rem;
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.2);
  margin-top: 5vh !important;
}

.custom-dialog .el-dialog__header {
  padding: 1.25rem 1.25rem 0.875rem;
  border-bottom: 1px solid #f3f4f6;
}

.custom-dialog .el-dialog__body {
  padding: 0 1.25rem 1.25rem;
}
</style>
