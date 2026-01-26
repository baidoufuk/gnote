<template>
  <div class="relative mb-8 sm:mb-6 group">
    <div class="timeline-dot"></div>
    <div
      class="relative bg-white/95 backdrop-blur-sm rounded-2xl p-5 sm:p-4 shadow-lg hover:shadow-2xl hover:translate-x-2 hover:-translate-y-1 transition-all duration-500 cursor-pointer border border-white/50 overflow-hidden"
      @click="$emit('open-modal', post)"
    >
      <!-- 装饰性渐变背景 -->
      <div class="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-[#667eea]/10 to-transparent rounded-full -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-700"></div>

      <!-- 时间标签 -->
      <div class="relative inline-flex items-center gap-1.5 sm:gap-1 px-2.5 py-1 sm:px-2 sm:py-0.5 bg-gradient-to-r from-[#667eea]/10 to-[#764ba2]/10 rounded-full mb-2.5 sm:mb-2 border border-[#667eea]/20">
        <svg class="w-3.5 h-3.5 sm:w-3 sm:h-3 text-[#667eea]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <span class="text-[#667eea] text-xs sm:text-[11px] font-semibold">{{ formatDateTime(post.created_at) }}</span>
      </div>

      <!-- 内容 -->
      <div class="relative text-gray-700 text-[15px] sm:text-sm leading-relaxed line-clamp-3 group-hover:text-gray-900 transition-colors duration-300">
        {{ post.content }}
      </div>

      <!-- 阅读更多提示 -->
      <div class="relative mt-3 sm:mt-2 flex items-center gap-1.5 text-[#667eea] text-xs sm:text-[11px] font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <span>阅读更多</span>
        <svg class="w-3.5 h-3.5 sm:w-3 sm:h-3 transform group-hover:translate-x-1 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatDateTime } from '@/utils/format'

defineProps({
  post: {
    type: Object,
    required: true
  }
})

defineEmits(['open-modal'])
</script>

<style scoped>
.timeline-dot {
  position: absolute;
  left: -33px;
  top: 10px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: 2.5px solid white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2), 0 3px 10px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
  z-index: 10;
}

.group:hover .timeline-dot {
  transform: scale(1.25);
  box-shadow: 0 0 0 5px rgba(102, 126, 234, 0.3), 0 5px 16px rgba(102, 126, 234, 0.5);
}

@media (max-width: 640px) {
  .timeline-dot {
    left: -26px;
    width: 10px;
    height: 10px;
    border: 2px solid white;
    top: 8px;
  }
}
</style>