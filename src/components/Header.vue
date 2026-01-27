<template>
  <div class="relative overflow-hidden bg-white/10 backdrop-blur-md rounded-3xl px-5 py-4 sm:px-4 sm:py-3 mb-6 sm:mb-4 shadow-2xl text-center border border-white/20 transition-all duration-500 hover:shadow-[0_20px_60px_rgba(102,126,234,0.4)]">
    <!-- 装饰性背景元素 -->
    <div class="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -mr-16 -mt-16 blur-2xl"></div>
    <div class="absolute bottom-0 left-0 w-40 h-40 bg-white/5 rounded-full -ml-20 -mb-20 blur-2xl"></div>

    <!-- 图标容器 -->
    <div class="relative inline-flex items-center justify-center w-10 h-10 sm:w-9 sm:h-9 mb-2 sm:mb-1.5 bg-white/20 backdrop-blur-sm rounded-2xl shadow-lg">
      <svg class="w-5 h-5 sm:w-4.5 sm:h-4.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"></path>
      </svg>
    </div>

    <!-- 标题 -->
    <h1 class="relative text-2xl sm:text-xl font-extrabold text-white mb-1 sm:mb-0.5 tracking-tight">
      阿K的分享
    </h1>

    <!-- 副标题 -->
    <p class="relative text-white/80 text-xs sm:text-[11px] font-light tracking-wide">
      个人分享信息，不做各种决策建议
    </p>

    <!-- 装饰线 -->
    <div class="relative mt-2.5 sm:mt-2 flex items-center justify-center gap-2">
      <div class="w-10 h-0.5 bg-gradient-to-r from-transparent to-white/30 rounded-full"></div>
      <div class="w-1.5 h-1.5 bg-white/40 rounded-full"></div>
      <div class="w-10 h-0.5 bg-gradient-to-l from-transparent to-white/30 rounded-full"></div>
    </div>
  </div>
</template>

<script setup>
</script>
