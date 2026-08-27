<template>
  <div class="diary-page">
    <div class="page-header">
      <h2>👨‍👩‍👧‍👦 家庭日记</h2>
    </div>
    <el-card shadow="never" class="card-section">
      <template #header><span class="card-title">📝 生成家庭日记</span></template>
      <p class="section-hint">记录家人一起的美好时光</p>
      <el-button type="primary" :loading="generating" @click="generateDiary" round>
        ✨ 生成今日家庭日记
      </el-button>
    </el-card>
    <div v-if="diaryContent" class="diary-result">
      <p class="diary-label">📖 家庭日记</p>
      <p class="diary-text">{{ diaryContent }}</p>
    </div>
    <el-card shadow="never" class="card-section">
      <template #header><span class="card-title">📋 历史日记</span></template>
      <div v-if="diaries.length" class="diary-list">
        <div v-for="(d, i) in diaries" :key="i" class="diary-item">
          <p class="diary-excerpt">{{ d.content ? d.content.slice(0, 60) + '...' : '--' }}</p>
          <span class="diary-date">{{ d.created_at }}</span>
        </div>
      </div>
      <el-empty v-else description="暂无家庭日记" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { familyDiary, chatHistory } from '../../api'
import { ElMessage } from 'element-plus'

const generating = ref(false)
const diaryContent = ref('')
const diaries = ref([])
const familyId = ref(localStorage.getItem('nuan_family_id') || '')

async function generateDiary() {
  generating.value = true
  const r = await familyDiary(familyId.value)
  generating.value = false
  if (r.success) {
    diaryContent.value = r.content || r.data || ''
    diaries.value.unshift({ content: diaryContent.value, created_at: new Date().toLocaleString() })
    ElMessage.success('家庭日记已生成 💛')
  } else {
    ElMessage.error('生成失败')
  }
}

async function loadHistory() {
  const r = await chatHistory()
  if (r.success) {
    diaries.value = (r.data || []).filter(d => d.family_id || d.family).map(d => ({
      content: d.content,
      created_at: d.created_at || ''
    }))
  }
}

onMounted(loadHistory)
</script>

<style scoped>
.diary-page { padding: 0 0 20px; }
.page-header h2 { font-size: 18px; color: #C17B4E; margin-bottom: 16px; }
.card-section { border-radius: 16px; background: #fff; border: none; margin-bottom: 16px; }
.card-title { font-size: 14px; font-weight: 600; color: #555; }
.section-hint { font-size: 13px; color: #b0a89a; margin-bottom: 12px; }
.diary-result { background: #faf5f0; border-radius: 16px; padding: 20px; margin-bottom: 16px; }
.diary-label { font-size: 14px; font-weight: 600; color: #C17B4E; margin-bottom: 8px; }
.diary-text { font-size: 15px; line-height: 1.8; color: #444; white-space: pre-wrap; }
.diary-list { display: flex; flex-direction: column; gap: 8px; }
.diary-item { padding: 10px 0; border-bottom: 1px solid #f5ede6; }
.diary-item:last-child { border-bottom: none; }
.diary-excerpt { font-size: 14px; color: #444; }
.diary-date { font-size: 11px; color: #b0a89a; }
</style>
