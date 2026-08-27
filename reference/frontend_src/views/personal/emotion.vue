<template>
  <div class="emotion-page">
    <div class="page-header">
      <h2>📊 情绪回顾</h2>
    </div>
    <!-- 情绪概览 -->
    <el-card shadow="never" class="card-section">
      <template #header><span class="card-title">📈 情绪概览</span></template>
      <div v-if="overview" class="overview-grid">
        <div v-for="(val, key) in overview" :key="key" class="overview-item">
          <el-tag :type="emotionTag(key)" size="small">{{ key }}</el-tag>
          <span class="overview-count">{{ val }}</span>
        </div>
      </div>
      <div class="overview-control">
        <el-radio-group v-model="overviewDays" @change="loadOverview">
          <el-radio-button :value="7">7天</el-radio-button>
          <el-radio-button :value="30">30天</el-radio-button>
          <el-radio-button :value="90">90天</el-radio-button>
        </el-radio-group>
      </div>
    </el-card>
    <!-- 情绪时间线 -->
    <el-card shadow="never" class="card-section">
      <template #header><span class="card-title">⏳ 情绪时间线</span></template>
      <div v-if="timeline.length" class="timeline-list">
        <div v-for="(item, i) in timeline" :key="i" class="timeline-item">
          <div class="tl-dot" :style="{ background: emotionColor(item.emotion) }"></div>
          <div class="tl-content">
            <el-tag :type="emotionTag(item.emotion)" size="small">{{ item.emotion }}</el-tag>
            <span class="tl-text">{{ item.content }}</span>
            <span class="tl-time">{{ item.created_at }}</span>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无情绪记录" />
      <div class="overview-control">
        <el-radio-group v-model="timelineDays" @change="loadTimeline">
          <el-radio-button :value="7">7天</el-radio-button>
          <el-radio-button :value="30">30天</el-radio-button>
          <el-radio-button :value="90">90天</el-radio-button>
        </el-radio-group>
      </div>
    </el-card>
    <!-- 实时情绪匹配 -->
    <el-card shadow="never" class="card-section">
      <template #header><span class="card-title">🔮 实时情绪匹配</span></template>
      <div class="match-row">
        <el-input v-model="matchText" placeholder="输入文字，识别你的情绪..." />
        <el-button type="primary" :loading="matching" @click="doMatch">匹配</el-button>
      </div>
      <div v-if="matchResult" class="match-result">
        <el-tag :type="emotionTag(matchResult)" size="large">{{ matchResult }}</el-tag>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { emotionOverview, emotionTimeline, matchEmotion } from '../../api'
import { ElMessage } from 'element-plus'

const overview = ref(null)
const overviewDays = ref(30)
const timeline = ref([])
const timelineDays = ref(30)
const matchText = ref('')
const matching = ref(false)
const matchResult = ref('')

function emotionTag(e) {
  const map = { 开心: 'success', 快乐: 'success', 喜悦: 'success', 悲伤: 'danger', 难过: 'danger', 生气: 'warning', 愤怒: 'warning', 平静: 'info', 焦虑: 'danger', 恐惧: 'danger', 惊讶: 'primary', 爱: 'success', 浪漫: 'success' }
  return map[e] || ''
}
function emotionColor(e) {
  const map = { 开心: '#67C23A', 快乐: '#67C23A', 悲伤: '#F56C6C', 难过: '#F56C6C', 生气: '#E6A23C', 平静: '#909399', 焦虑: '#F56C6C', 惊讶: '#409EFF', 爱: '#C17B4E', 浪漫: '#C17B4E' }
  return map[e] || '#C17B4E'
}

async function loadOverview() {
  const r = await emotionOverview(overviewDays.value)
  if (r.success) overview.value = r.data || r
}
async function loadTimeline() {
  const r = await emotionTimeline(timelineDays.value)
  if (r.success) timeline.value = r.data || []
}
async function doMatch() {
  if (!matchText.value) return
  matching.value = true
  const r = await matchEmotion(matchText.value)
  matching.value = false
  if (r.success) matchResult.value = r.emotion || r.data || r.content || ''
  else ElMessage.error('匹配失败')
}
onMounted(() => { loadOverview(); loadTimeline() })
</script>

<style scoped>
.emotion-page { padding: 0 0 20px; }
.page-header h2 { font-size: 18px; color: #C17B4E; margin-bottom: 16px; }
.card-section { border-radius: 16px; background: #fff; border: none; margin-bottom: 16px; }
.card-title { font-size: 14px; font-weight: 600; color: #555; }
.overview-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.overview-item { display: flex; align-items: center; gap: 6px; padding: 4px 0; }
.overview-count { font-size: 16px; font-weight: 600; color: #333; }
.overview-control { margin-top: 12px; }
.timeline-list { display: flex; flex-direction: column; gap: 12px; }
.timeline-item { display: flex; gap: 10px; }
.tl-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; margin-top: 4px; }
.tl-content { display: flex; flex-direction: column; gap: 2px; }
.tl-text { font-size: 14px; color: #444; }
.tl-time { font-size: 11px; color: #b0a89a; }
.match-row { display: flex; gap: 8px; }
.match-result { margin-top: 12px; text-align: center; }
</style>
