<template>
  <div class="dream-page">
    <el-card shadow="never" style="border-radius:16px;border:none;margin-bottom:12px">
      <h4 style="margin-bottom:12px">🌙 梦境记录与分析</h4>
      <el-input v-model="dream" type="textarea" :rows="4" placeholder="描述你的梦境..." style="margin-bottom:12px" />
      <el-button type="primary" :loading="loading" @click="analyze" round>🔮 分析梦境</el-button>
    </el-card>
    <el-card v-if="result" shadow="never" class="result-card">
      <div class="result-content">{{ result }}</div>
    </el-card>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { dreamAnalyze } from '../../api'
const dream = ref(''); const result = ref(''); const loading = ref(false)
async function analyze() {
  if (!dream.value) return
  loading.value = true
  const r = await dreamAnalyze(dream.value)
  if (r.success) result.value = r.content
  loading.value = false
}
</script>
<style scoped>
.dream-page { padding: 0 0 20px; }
.result-card { border-radius: 16px; border: none; }
.result-content { font-size: 14px; line-height: 1.8; white-space: pre-wrap; color: #555; }
</style>
