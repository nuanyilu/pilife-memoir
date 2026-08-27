<template>
  <div class="emotion-sign-page">
    <el-card shadow="never" class="sign-card">
      <div style="text-align:center;padding:10px 0">
        <div style="font-size:48px;margin-bottom:10px">🌸</div>
        <h3 style="color:#C17B4E">今日情绪签</h3>
        <p style="font-size:12px;color:#b0a89a;margin:4px 0 16px">{{ today }}</p>
        <el-button type="primary" :loading="loading" @click="generateSign" round>✨ 抽取今日情绪签</el-button>
      </div>
      <div v-if="sign" class="sign-content">
        <div v-for="(section, i) in signSections" :key="i" class="sign-section">
          <h4>{{ section.title }}</h4>
          <p>{{ section.content }}</p>
        </div>
      </div>
      <div v-else-if="!loading" style="text-align:center;color:#999;padding:30px">
        <p>点击上方按钮，获取今天的情绪洞察 🌙</p>
      </div>
    </el-card>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
import { emotionSign } from '../../api'

const loading = ref(false)
const sign = ref('')
const today = computed(() => new Date().toLocaleDateString('zh-CN', { year:'numeric',month:'long',day:'numeric',weekday:'long' }))
const signSections = computed(() => {
  if (!sign.value) return []
  const parts = sign.value.split(/【|】/).filter(Boolean)
  const sections = []
  let current = null
  for (const p of parts) {
    if (['情绪洞察','今日肯定','今日行动建议','金句收尾'].includes(p)) {
      if (current) sections.push(current)
      current = { title: `【${p}】`, content: '' }
    } else if (current) {
      current.content += p
    }
  }
  if (current) sections.push(current)
  return sections
})
async function generateSign() {
  loading.value = true
  const r = await emotionSign()
  if (r.success) sign.value = r.content
  loading.value = false
}
</script>
<style scoped>
.emotion-sign-page { padding: 0 0 20px; }
.sign-card { border-radius: 16px; border: none; }
.sign-content { background: #faf5f0; border-radius: 16px; padding: 20px; margin-top: 10px; }
.sign-section { margin-bottom: 16px; }
.sign-section h4 { color: #C17B4E; font-size: 14px; margin-bottom: 8px; }
.sign-section p { font-size: 14px; line-height: 1.8; color: #555; white-space: pre-wrap; }
</style>
