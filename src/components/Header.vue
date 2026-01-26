<template>
  <div class="relative overflow-hidden bg-white/10 backdrop-blur-md rounded-3xl px-6 py-6 sm:px-4 sm:py-5 mb-8 sm:mb-6 shadow-2xl text-center border border-white/20 transition-all duration-500 hover:shadow-[0_20px_60px_rgba(102,126,234,0.4)]">
    <!-- 装饰性背景元素 -->
    <div class="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -mr-16 -mt-16 blur-2xl"></div>
    <div class="absolute bottom-0 left-0 w-40 h-40 bg-white/5 rounded-full -ml-20 -mb-20 blur-2xl"></div>

    <!-- 图标容器 -->
    <div class="relative inline-flex items-center justify-center w-14 h-14 sm:w-12 sm:h-12 mb-3 sm:mb-2 bg-white/20 backdrop-blur-sm rounded-2xl shadow-lg">
      <svg class="w-7 h-7 sm:w-6 sm:h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"></path>
      </svg>
    </div>

    <!-- 标题 -->
    <h1 class="relative text-3xl sm:text-2xl font-extrabold text-white mb-2 sm:mb-1.5 tracking-tight">
      阿K的分享
    </h1>

    <!-- 副标题 -->
    <p class="relative text-white/80 text-sm sm:text-xs font-light tracking-wide">
      个人分享信息，不做各种决策建议
    </p>

    <!-- 装饰线 -->
    <div class="relative mt-4 sm:mt-3 flex items-center justify-center gap-2">
      <div class="w-12 h-0.5 bg-gradient-to-r from-transparent to-white/30 rounded-full"></div>
      <div class="w-2 h-2 bg-white/40 rounded-full"></div>
      <div class="w-12 h-0.5 bg-gradient-to-l from-transparent to-white/30 rounded-full"></div>
    </div>
  </div>
</template>

<script setup>
</script>
