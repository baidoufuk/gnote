<template>
  <div class="min-h-screen bg-gradient-to-br from-[#667eea] via-[#764ba2] to-[#667eea] p-4 sm:p-3 relative overflow-hidden">
    <!-- 装饰性背景元素 -->
    <div class="absolute top-0 left-0 w-96 h-96 bg-white/5 rounded-full -ml-48 -mt-48 blur-3xl animate-pulse"></div>
    <div class="absolute bottom-0 right-0 w-96 h-96 bg-white/5 rounded-full -mr-48 -mb-48 blur-3xl animate-pulse" style="animation-delay: 1s;"></div>
    <div class="absolute top-1/2 left-1/2 w-64 h-64 bg-white/3 rounded-full -ml-32 -mt-32 blur-2xl"></div>

    <div class="max-w-[750px] mx-auto relative z-10">
      <Header />

      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-12 sm:py-8">
        <div class="inline-flex items-center justify-center w-16 h-16 sm:w-14 sm:h-14 bg-white/20 backdrop-blur-md rounded-2xl shadow-xl mb-3">
          <el-icon class="is-loading" :size="36" color="#fff">
            <Loading />
          </el-icon>
        </div>
        <p class="text-white text-base sm:text-sm font-medium">加载中...</p>
      </div>

      <!-- 内容列表 -->
      <PostList v-else-if="posts.length > 0" :posts="posts" />

      <!-- 免责声明 -->
      <div class="relative bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl mt-12 sm:mt-8 px-5 py-4 sm:px-4 sm:py-3 text-center text-xs text-white/90 leading-relaxed shadow-xl">
        <div class="flex items-center justify-center gap-2 font-bold text-white mb-2.5 sm:mb-2">
          <div class="flex items-center justify-center w-5 h-5 sm:w-4 sm:h-4 bg-white/20 rounded-lg">
            <svg class="w-3 h-3 sm:w-2.5 sm:h-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <span class="text-sm sm:text-xs">免责声明</span>
        </div>
        <p class="mb-2.5 sm:mb-2 opacity-90 text-[11px] sm:text-[10px]">
          本平台所有内容均为个人信息分享，仅供参考学习，不构成任何投资、法律、医疗或其他专业建议。访问者应根据自身情况独立判断，并自行承担由此产生的一切责任。内容发布者不对任何因使用本平台信息而产生的直接或间接损失承担责任。
        </p>
        <div class="flex items-center justify-center gap-2 text-white/70 text-[10px] sm:text-[9px]">
          <span>© 2026 阿K的分享</span>
          <span>·</span>
          <span>仅供参考</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import Header from './components/Header.vue'
import PostList from './components/PostList.vue'
import { usePosts } from './composables/usePosts'

const { posts, loading, fetchPosts } = usePosts()

onMounted(() => {
  fetchPosts()
})
</script>
