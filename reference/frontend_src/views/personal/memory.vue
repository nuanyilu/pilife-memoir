<template>
  <div class="memory-page">
    <div class="page-header">
      <h2>🧠 暖暖的记忆</h2>
    </div>
    <!-- 事实列表 -->
    <el-card shadow="never" class="card-section">
      <template #header><span class="card-title">📋 已存储的事实</span></template>
      <div v-if="facts.length" class="facts-list">
        <div v-for="(f, i) in facts" :key="i" class="fact-item">
          <el-tag :type="tagType(f.type)" size="small">{{ f.type }}</el-tag>
          <span class="fact-value">{{ f.value }}</span>
        </div>
      </div>
      <el-empty v-else description="暂无存储的事实" />
    </el-card>
    <!-- 新增事实表单 -->
    <el-card shadow="never" class="card-section">
      <template #header><span class="card-title">➕ 新增事实</span></template>
      <el-form :model="factForm" label-position="top">
        <el-form-item label="类型">
          <el-select v-model="factForm.type" placeholder="选择事实类型">
            <el-option label="姓名 (name)" value="name" />
            <el-option label="生日 (birthday)" value="birthday" />
            <el-option label="宠物 (pet)" value="pet" />
            <el-option label="爱好 (hobby)" value="hobby" />
            <el-option label="职业 (job)" value="job" />
            <el-option label="其他 (other)" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="factForm.value" placeholder="输入事实内容" />
        </el-form-item>
        <el-button type="primary" :loading="saving" @click="saveFact">保存</el-button>
      </el-form>
    </el-card>
    <!-- 记忆检索 -->
    <el-card shadow="never" class="card-section">
      <template #header><span class="card-title">🔍 记忆检索</span></template>
      <div class="recall-row">
        <el-input v-model="recallQuery" placeholder="搜索你的记忆..." />
        <el-button type="primary" :loading="recalling" @click="doRecall">搜索</el-button>
      </div>
      <div v-if="recallResult" class="recall-result">
        <p>{{ recallResult }}</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getFacts, setFact, memoryRecall } from '../../api'
import { ElMessage } from 'element-plus'

const facts = ref([])
const factForm = ref({ type: '', value: '' })
const saving = ref(false)
const recallQuery = ref('')
const recalling = ref(false)
const recallResult = ref('')

function tagType(type) {
  const map = { name: 'success', birthday: 'warning', pet: 'danger', hobby: 'info', job: 'primary', other: '' }
  return map[type] || ''
}

async function loadFacts() {
  const r = await getFacts()
  if (r.success) facts.value = r.data || []
}
async function saveFact() {
  if (!factForm.value.type || !factForm.value.value) { ElMessage.warning('请填写完整'); return }
  saving.value = true
  const r = await setFact(factForm.value.type, factForm.value.value)
  saving.value = false
  if (r.success) { ElMessage.success('已保存'); factForm.value = { type: '', value: '' }; loadFacts() }
  else ElMessage.error('保存失败')
}
async function doRecall() {
  if (!recallQuery.value) return
  recalling.value = true
  const r = await memoryRecall(recallQuery.value)
  recalling.value = false
  if (r.success) recallResult.value = r.content || r.data || '未找到相关记忆'
  else recallResult.value = '检索失败'
}
onMounted(loadFacts)
</script>

<style scoped>
.memory-page { padding: 0 0 20px; }
.page-header h2 { font-size: 18px; color: #C17B4E; margin-bottom: 16px; }
.card-section { border-radius: 16px; background: #fff; border: none; margin-bottom: 16px; }
.card-title { font-size: 14px; font-weight: 600; color: #555; }
.facts-list { display: flex; flex-direction: column; gap: 8px; }
.fact-item { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid #f5ede6; }
.fact-item:last-child { border-bottom: none; }
.fact-value { font-size: 14px; color: #444; }
.recall-row { display: flex; gap: 8px; }
.recall-result { background: #faf5f0; border-radius: 12px; padding: 14px; margin-top: 12px; font-size: 14px; line-height: 1.6; color: #555; }
</style>
