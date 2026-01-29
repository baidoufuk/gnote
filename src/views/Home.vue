<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <Header />

    <div class="flex-grow max-w-3xl mx-auto px-6 sm:px-4 py-12 sm:py-8 w-full">
      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-12 sm:py-8">
        <div class="inline-flex items-center justify-center w-16 h-16 sm:w-14 sm:h-14 bg-white rounded-2xl shadow-lg mb-3">
          <el-icon class="is-loading" :size="36" color="#667eea">
            <Loading />
          </el-icon>
        </div>
        <p class="text-gray-600 text-base sm:text-sm font-medium">加载中...</p>
      </div>

      <!-- 内容列表 -->
      <PostList v-else-if="posts.length > 0" :posts="posts" />
    </div>

    <!-- 免责声明 -->
    <footer class="bg-gray-100 border-t border-gray-200 py-6 flex-none">
      <div class="max-w-3xl mx-auto px-6 text-center space-y-2">
        <p class="text-xs text-gray-500 font-medium">免责声明</p>
        <p class="text-[10px] text-gray-400 leading-relaxed max-w-xl mx-auto">
          本平台所有内容均为个人信息分享，仅供参考学习，不构成任何投资、法律、医疗或其他专业建议。访问者应根据自身情况独立判断，并自行承担由此产生的一切责任。内容发布者不对任何因使用本平台信息而产生的直接或间接损失承担责任。
        </p>
        <div class="flex items-center justify-center gap-2 text-gray-400 text-[9px]">
          <span>© 2026 阿K的分享</span>
          <span>·</span>
          <span>仅供参考</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import Header from '@/components/Header.vue'
import PostList from '@/components/PostList.vue'
import { usePosts } from '@/composables/usePosts'

const { posts, loading, fetchPosts } = usePosts()

const showTipDialog = () => {
  ElMessageBox.alert(
    '每次都要系好安全带，\\n切勿盲目跟车，\\n错过就等待下一班公交，\\n公交永远都有，不差这一班。',
    '友情提示',
    {
      confirmButtonText: '我知道了',
      center: true,
      customClass: 'tip-message-box',
      closeOnClickModal: false,
      closeOnPressEscape: false,
      showClose: false,
      dangerouslyUseHTMLString: false
    }
  )
}

onMounted(() => {
  fetchPosts()
  // 显示友情提示弹窗
  showTipDialog()
})
</script>

<style>
.tip-message-box {
  border-radius: 1rem;
  padding: 2rem;
  max-w: 500px;
}

.tip-message-box .el-message-box__header {
  padding-bottom: 1rem;
}

.tip-message-box .el-message-box__title {
  font-size: 1.5rem;
  font-weight: bold;
  color: #667eea;
}

.tip-message-box .el-message-box__content {
  padding: 1.5rem 0;
}

.tip-message-box .el-message-box__message {
  font-size: 1rem;
  line-height: 1.8;
  color: #4b5563;
  white-space: pre-line;
}

.tip-message-box .el-message-box__btns {
  padding-top: 1rem;
}

.tip-message-box .el-button--primary {
  background: linear-gradient(to right, #667eea, #764ba2);
  border: none;
  padding: 0.75rem 2rem;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 0.75rem;
  transition: all 0.3s;
}

.tip-message-box .el-button--primary:hover {
  transform: scale(1.05);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
}
</style>
