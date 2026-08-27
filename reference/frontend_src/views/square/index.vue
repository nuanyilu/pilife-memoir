<template>
  <div class="square-page">
    <div class="page-header">
      <h2>🌊 回响谷</h2>
      <p class="page-desc">分享你的心声，聆听他人的回响</p>
    </div>
    <!-- 发帖表单 -->
    <el-card shadow="never" class="card-section">
      <template #header><span class="card-title">✍️ 发布想法</span></template>
      <el-form :model="postForm" label-position="top">
        <el-form-item label="内容">
          <el-input v-model="postForm.content" type="textarea" :rows="3" placeholder="此刻你想分享什么？" maxlength="500" show-word-limit />
        </el-form-item>
        <el-form-item label="情感标签">
          <el-select v-model="postForm.emotion_tag" placeholder="选择情绪标签" clearable>
            <el-option label="开心 😊" value="开心" />
            <el-option label="感动 😭" value="感动" />
            <el-option label="思考 🤔" value="思考" />
            <el-option label="难过 😢" value="难过" />
            <el-option label="鼓励 💪" value="鼓励" />
            <el-option label="日常 ☕" value="日常" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="话题">
          <el-select v-model="postForm.topic" placeholder="选择话题" clearable>
            <el-option v-for="t in topics" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-button type="primary" :loading="posting" @click="doPost">发布</el-button>
      </el-form>
    </el-card>
    <!-- 话题过滤 -->
    <div class="topic-bar">
      <el-tag :type="selectedTopic === '' ? 'primary' : ''" @click="filterTopic('')" style="cursor:pointer">全部</el-tag>
      <el-tag v-for="t in topics" :key="t" :type="selectedTopic === t ? 'primary' : ''" @click="filterTopic(t)" style="cursor:pointer;margin-left:4px">{{ t }}</el-tag>
    </div>
    <!-- 帖子列表 -->
    <div v-if="posts.length" class="posts-list">
      <el-card v-for="p in posts" :key="p.id" shadow="never" class="post-card" @click="$router.push('/square/post?id=' + p.id)">
        <div class="post-header">
          <span class="post-author">{{ p.author || '匿名' }}</span>
          <el-tag v-if="p.emotion_tag" :type="emotionType(p.emotion_tag)" size="small">{{ p.emotion_tag }}</el-tag>
          <el-tag v-if="p.topic" size="small" style="margin-left:4px">{{ p.topic }}</el-tag>
        </div>
        <p class="post-content">{{ p.content }}</p>
        <div class="post-footer">
          <span class="post-time">{{ p.created_at }}</span>
          <div class="post-actions">
            <span class="action-btn" @click.stop="toggleLike(p)">
              {{ p.liked ? '❤️' : '🤍' }} {{ p.likes || 0 }}
            </span>
            <span class="action-btn">💬 {{ p.comments || 0 }}</span>
          </div>
        </div>
      </el-card>
    </div>
    <el-empty v-else description="还没有帖子，来发第一条吧 🌊" />
    <!-- 分页 -->
    <div v-if="totalPages > 1" class="pagination-bar">
      <el-pagination
        v-model:current-page="currentPage"
        :total="total"
        :page-size="20"
        layout="prev, pager, next"
        background
        @current-change="loadPosts"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { squarePosts, squareCreate, squareToggleLike, squareTopics } from '../../api'
import { ElMessage } from 'element-plus'

const postForm = ref({ content: '', emotion_tag: '', topic: '' })
const posting = ref(false)
const posts = ref([])
const topics = ref([])
const selectedTopic = ref('')
const currentPage = ref(1)
const total = ref(0)
const totalPages = ref(1)

function emotionType(e) {
  const map = { 开心: 'success', 感动: 'warning', 思考: 'info', 难过: 'danger', 鼓励: 'primary', 日常: '' }
  return map[e] || ''
}

async function loadTopics() {
  const r = await squareTopics()
  if (r.success) topics.value = r.data || []
}
async function loadPosts() {
  const r = await squarePosts(currentPage.value, selectedTopic.value || undefined)
  if (r.success) {
    posts.value = r.data || []
    total.value = r.total || r.data?.length || 0
    totalPages.value = Math.ceil(total.value / 20) || 1
  }
}
async function doPost() {
  if (!postForm.value.content) { ElMessage.warning('请输入内容'); return }
  posting.value = true
  const r = await squareCreate(postForm.value.content, postForm.value.emotion_tag, postForm.value.topic)
  posting.value = false
  if (r.success) {
    ElMessage.success('发布成功 🎉')
    postForm.value = { content: '', emotion_tag: '', topic: '' }
    loadPosts()
  } else {
    ElMessage.error('发布失败')
  }
}
async function toggleLike(p) {
  const r = await squareToggleLike(p.id)
  if (r.success) { p.liked = !p.liked; p.likes = (p.likes || 0) + (p.liked ? 1 : -1) }
}
function filterTopic(t) { selectedTopic.value = t; currentPage.value = 1; loadPosts() }

onMounted(() => { loadTopics(); loadPosts() })
</script>

<style scoped>
.square-page { padding: 0 0 20px; }
.page-header h2 { font-size: 18px; color: #C17B4E; margin-bottom: 4px; }
.page-desc { font-size: 13px; color: #b0a89a; margin-bottom: 16px; }
.card-section { border-radius: 16px; background: #fff; border: none; margin-bottom: 16px; }
.card-title { font-size: 14px; font-weight: 600; color: #555; }
.topic-bar { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; padding: 0 0 8px; overflow-x: auto; }
.posts-list { display: flex; flex-direction: column; gap: 10px; }
.post-card { border-radius: 16px; background: #fff; border: none; cursor: pointer; transition: .2s; }
.post-card:hover { transform: translateY(-1px); }
.post-header { display: flex; align-items: center; gap: 6px; margin-bottom: 8px; }
.post-author { font-size: 13px; font-weight: 500; color: #C17B4E; }
.post-content { font-size: 14px; line-height: 1.6; color: #444; margin-bottom: 10px; word-break: break-word; }
.post-footer { display: flex; justify-content: space-between; align-items: center; }
.post-time { font-size: 11px; color: #b0a89a; }
.post-actions { display: flex; gap: 12px; }
.action-btn { font-size: 13px; color: #888; cursor: pointer; user-select: none; }
.action-btn:hover { color: #C17B4E; }
.pagination-bar { margin-top: 16px; display: flex; justify-content: center; }
</style>
