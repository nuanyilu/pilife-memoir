<template>
  <div class="post-detail-page">
    <div v-if="post" class="post-card">
      <div class="post-header">
        <span class="post-author">🌊 {{ post.user_id?.slice(0,8) }}</span>
        <span class="post-time">{{ post.created_at?.slice(0,10) }}</span>
      </div>
      <div class="post-tags">
        <el-tag v-if="post.emotion_tag" size="small">{{ post.emotion_tag }}</el-tag>
        <el-tag v-if="post.topic" size="small" type="info">#{{ post.topic }}</el-tag>
      </div>
      <p class="post-content">{{ post.content }}</p>
      <div class="post-actions">
        <el-button text @click="toggleLike">
          {{ liked ? '❤️' : '🤍' }} {{ post.likes || 0 }}
        </el-button>
        <el-button text>💬 {{ post.comments_count || 0 }}</el-button>
      </div>
    </div>
    <div v-else class="loading">加载中...</div>

    <el-card v-if="post" shadow="never" class="comments-section">
      <h4 style="margin-bottom:12px">💬 评论 ({{ comments.length }})</h4>
      <div v-if="comments.length===0" style="color:#999;text-align:center;padding:20px">暂无评论</div>
      <div v-for="c in comments" :key="c.id" class="comment-item">
        <span class="comment-author">{{ c.user_id?.slice(0,8) }}</span>
        <span class="comment-text">{{ c.content }}</span>
        <span class="comment-time">{{ c.created_at?.slice(0,10) }}</span>
      </div>
      <div class="comment-input" style="margin-top:12px">
        <el-input v-model="commentText" placeholder="写下你的想法..." size="small" @keyup.enter="submitComment" />
        <el-button type="primary" size="small" @click="submitComment" style="margin-left:8px">发送</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { squarePosts, squareComment, squareToggleLike } from '../../api'

const route = useRoute()
const post = ref(null)
const comments = ref([])
const liked = ref(false)
const commentText = ref('')

async function loadPost() {
  const id = route.query.id
  if (!id) { post.value = { content: '帖子不存在' }; return }
  try {
    const r = await squarePosts(1)
    if (r.success) {
      const p = r.posts?.find(p => p.id === id)
      if (p) {
        post.value = p
        if (p.comments) comments.value = p.comments
      }
    }
  } catch (e) { post.value = { content: '加载失败' } }
}

async function toggleLike() {
  if (!post.value) return
  const r = await squareToggleLike(post.value.id)
  if (r.success) {
    liked.value = r.liked
    post.value.likes = r.likes
  }
}

async function submitComment() {
  if (!commentText.value || !post.value) return
  const r = await squareComment(post.value.id, commentText.value)
  if (r.success) {
    comments.value.push(r.comment)
    commentText.value = ''
    post.value.comments_count = (post.value.comments_count || 0) + 1
  }
}

onMounted(loadPost)
</script>
<style scoped>
.post-detail-page { padding: 0 0 20px; }
.post-card { background: #fff; border-radius: 16px; padding: 20px; margin-bottom: 12px; }
.post-header { display: flex; justify-content: space-between; margin-bottom: 8px; }
.post-author { font-weight: 600; color: #C17B4E; }
.post-time { font-size: 12px; color: #b0a89a; }
.post-tags { margin-bottom: 8px; }
.post-content { font-size: 15px; line-height: 1.8; color: #333; white-space: pre-wrap; }
.post-actions { margin-top: 16px; display: flex; gap: 8px; }
.comments-section { border-radius: 16px; border: none; }
.comment-item { padding: 8px 0; border-bottom: 1px solid #f5ede6; }
.comment-author { font-weight: 600; color: #C17B4E; font-size: 12px; margin-right: 8px; }
.comment-text { font-size: 14px; color: #444; }
.comment-time { float: right; font-size: 11px; color: #b0a89a; }
.comment-input { display: flex; }
.loading { text-align: center; padding: 40px; color: #999; }
</style>
