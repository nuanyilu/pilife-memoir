<template>
  <div class="life-archive-page">
    <el-card shadow="never" style="border-radius:16px;border:none;margin-bottom:12px">
      <h4 style="margin-bottom:12px">📖 人生档案</h4>
      <el-button :loading="loading" @click="loadArchive" round>📖 生成人生档案总结</el-button>
      <div v-if="archive" class="archive-content">{{ archive }}</div>
    </el-card>
    <el-card shadow="never" class="timeline-card">
      <h4 style="margin-bottom:12px">📅 时光长廊</h4>
      <div style="display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap">
        <el-input v-model="newYear" placeholder="年份" size="small" style="width:100px" />
        <el-input v-model="newTitle" placeholder="事件标题" size="small" style="flex:1;min-width:120px" />
        <el-input v-model="newDesc" placeholder="描述(可选)" size="small" style="flex:1;min-width:120px" />
        <el-button type="primary" size="small" @click="addEvent">➕ 添加</el-button>
      </div>
      <div v-if="events.length===0" style="text-align:center;color:#999;padding:20px">还没有记录人生事件</div>
      <div v-for="item in events" :key="item.id" class="event-item">
        <span class="event-year">{{ item.year }}</span>
        <div style="flex:1">
          <span style="font-weight:500">{{ item.title }}</span>
          <p v-if="item.description" style="font-size:12px;color:#999;margin-top:4px">{{ item.description }}</p>
        </div>
        <el-button text size="small" type="danger" @click="delEvent(item.id)">🗑️</el-button>
      </div>
    </el-card>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { lifeArchive, lifeTimeline, lifeEventCreate, lifeEventDelete } from '../../api'

const events = ref([])
const archive = ref(''); const loading = ref(false)
const newYear = ref(''); const newTitle = ref(''); const newDesc = ref('')

async function loadTimeline() { const r = await lifeTimeline(); if (r.success) events.value = r.events || [] }
async function loadArchive() {
  loading.value = true
  const r = await lifeArchive()
  if (r.success) archive.value = r.content
  loading.value = false
}
async function addEvent() {
  if (!newYear.value || !newTitle.value) return
  await lifeEventCreate(newYear.value, newTitle.value, newDesc.value, 'milestone')
  newYear.value = ''; newTitle.value = ''; newDesc.value = ''
  loadTimeline()
}
async function delEvent(id) { await lifeEventDelete(id); loadTimeline() }
onMounted(() => { loadTimeline(); loadArchive() })
</script>
<style scoped>
.life-archive-page { padding: 0 0 20px; }
.timeline-card { border-radius: 16px; border: none; }
.archive-content { background: #faf5f0; border-radius: 16px; padding: 20px; margin-top: 12px; font-size: 14px; line-height: 1.8; white-space: pre-wrap; }
.event-item { display: flex; align-items: flex-start; gap: 12px; padding: 10px 0; border-bottom: 1px solid #f5ede6; }
.event-year { font-weight: 700; color: #C17B4E; font-size: 14px; min-width: 40px; }
</style>
