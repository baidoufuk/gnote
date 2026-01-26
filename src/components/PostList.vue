<template>
  <div class="relative pl-10 sm:pl-8">
    <PostCard
      v-for="post in posts"
      :key="post.id"
      :post="post"
      @open-modal="openModal(post)"
    />

    <PostModal
      v-if="selectedPost"
      v-model="modalVisible"
      :post="selectedPost"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import PostCard from './PostCard.vue'
import PostModal from './PostModal.vue'

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
</script>

<style scoped>
.relative::before {
  content: '';
  position: absolute;
  left: 16px;
  top: 0;
  bottom: 0;
  width: 2.5px;
  background: linear-gradient(180deg,
    rgba(102, 126, 234, 0.3) 0%,
    rgba(118, 75, 162, 0.3) 50%,
    rgba(102, 126, 234, 0.3) 100%
  );
  border-radius: 2px;
  box-shadow: 0 0 8px rgba(102, 126, 234, 0.2);
}

@media (max-width: 640px) {
  .relative::before {
    left: 13px;
    width: 2px;
  }
}
</style>
