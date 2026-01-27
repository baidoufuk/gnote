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

    <div class="px-2 py-4">
      <div class="text-gray-700 text-base leading-relaxed whitespace-pre-wrap break-words">
        {{ post.content }}
      </div>
      <div v-if="post.image_path && post.image_path.trim()" class="mt-6 rounded-2xl overflow-hidden shadow-lg border border-gray-100">
        <img
          :src="`${API_BASE_URL}/uploads/${post.image_path}`"
          alt="内容配图"
          loading="lazy"
          class="w-full h-auto"
        />
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
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

watch(() => props.modelValue, (newVal) => {
  dialogVisible.value = newVal
})

watch(dialogVisible, (newVal) => {
  emit('update:modelValue', newVal)
})
</script>

<style>
.custom-dialog .el-dialog {
  border-radius: 1.5rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.custom-dialog .el-dialog__header {
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 1px solid #f3f4f6;
}

.custom-dialog .el-dialog__body {
  padding: 0 1.5rem 1.5rem;
}
</style>
