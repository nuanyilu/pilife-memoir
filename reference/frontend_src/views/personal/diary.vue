<template>
  <div class="diary-page">
    <div class="page-header">
      <h2>📝 今日日记</h2>
    </div>
    <!-- 今日日记卡片 -->
    <el-card v-if="todayDiary" shadow="never" class="diary-card">
      <div class="diary-date">{{ todayDate }}</div>
      <p class="diary-content">{{ todayDiary }}</p>
    </el-card>
    <el-card v-else shadow="never" class="diary-card empty-card">
      <el-empty description="今天还没有日记" />
    </el-card>
    <!-- 生成日记按钮 -->
    <div class="action-area">
      <el-button type="primary" :loading="generating" @click="generateDiary" round size="large">
        ✨ 生成今日日记
      </el-button>
    </div>
    <div v-if="generatedContent" class="generated-card">
      <p class="gen-label">✨ 暖暖为你写的日记</p>
      <p class="gen-content">{{ generatedContent }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { diaryToday, diaryGenerate } from '../../api'
import { ElMessage } from 'element-plus'

const todayDiary = ref('')
const generating = ref(false)
const generatedContent = ref('')
const todayDate = computed(() => new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }))

async function loadToday() {
  const r = await diaryToday()
  if (r.success) todayDiary.value = r.content || r.data || ''
}
async function generateDiary() {
  generating.value = true
  const r = await diaryGenerate()
  generating.value = false
  if (r.success) {
    generatedContent.value = r.content || r.data || ''
    todayDiary.value = generatedContent.value
    ElMessage.success('日记已生成 💛')
  } else {
    ElMessage.error('生成失败，请重试')
  }
}
onMounted(loadToday)
</script>

<style scoped>
.diary-page { padding: 0 0 20px; }
.page-header h2 { font-size: 18px; color: #C17B4E; margin-bottom: 16px; }
.diary-card { border-radius: 16px; background: #fff; border: none; margin-bottom: 16px; }
.diary-date { font-size: 14px; color: #b0a89a; margin-bottom: 8px; }
.diary-content { font-size: 15px; line-height: 1.8; color: #444; white-space: pre-wrap; }
.empty-card :deep(.el-empty__description) { color: #b0a89a; }
.action-area { text-align: center; margin: 20px 0; }
.generated-card { background: #faf5f0; border-radius: 16px; padding: 20px; margin-top: 12px; }
.gen-label { font-size: 13px; color: #C17B4E; font-weight: 500; margin-bottom: 8px; }
.gen-content { font-size: 15px; line-height: 1.8; color: #444; white-space: pre-wrap; }
</style>
