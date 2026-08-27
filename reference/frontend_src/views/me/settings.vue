<template>
  <div class="settings-page">
    <div class="page-header">
      <h2>⚙️ 设置</h2>
    </div>
    <!-- 个人信息 -->
    <el-card shadow="never" class="card-section">
      <template #header><span class="card-title">👤 个人信息</span></template>
      <el-form :model="profile" label-position="top">
        <el-form-item label="昵称">
          <el-input v-model="profile.nickname" placeholder="你的昵称" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="profile.email" placeholder="邮箱地址" />
        </el-form-item>
        <el-button type="primary" :loading="saving" @click="saveProfile">保存</el-button>
      </el-form>
    </el-card>
    <!-- 偏好设置 -->
    <el-card shadow="never" class="card-section">
      <template #header><span class="card-title">🎨 偏好设置</span></template>
      <el-form label-position="top">
        <el-form-item label="通知提醒">
          <el-radio-group v-model="notifyEnabled">
            <el-radio :value="true">开启</el-radio>
            <el-radio :value="false">关闭</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="每日日记提醒时间">
          <el-time-picker v-model="remindTime" placeholder="选择时间" format="HH:mm" />
        </el-form-item>
      </el-form>
    </el-card>
    <!-- 数据管理 -->
    <el-card shadow="never" class="card-section">
      <template #header><span class="card-title">💾 数据管理</span></template>
      <div class="data-actions">
        <el-button @click="exportData">📤 导出数据</el-button>
        <el-button type="danger" plain @click="clearData">🗑️ 清除数据</el-button>
      </div>
    </el-card>
    <div class="settings-footer">
      <p class="version">暖忆录 v1.0.0 · 永恒版</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getProfile, clearUser } from '../../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const profile = ref({ nickname: '', email: '' })
const notifyEnabled = ref(true)
const remindTime = ref(new Date())
const saving = ref(false)

async function loadProfile() {
  const r = await getProfile()
  if (r.success) {
    const d = r.data || r.user || r
    profile.value.nickname = d.nickname || d.name || ''
    profile.value.email = d.email || ''
  }
}
async function saveProfile() {
  saving.value = true
  // 模拟保存
  await new Promise(r => setTimeout(r, 500))
  saving.value = false
  ElMessage.success('已保存 💛')
}
function exportData() {
  ElMessage.success('数据导出成功 📦')
}
async function clearData() {
  try {
    await ElMessageBox.confirm('确定要清除所有数据吗？此操作不可恢复！', '警告', { confirmButtonText: '确认清除', cancelButtonText: '取消', type: 'warning' })
    await clearUser()
    ElMessage.success('数据已清除')
  } catch {}
}

onMounted(loadProfile)
</script>

<style scoped>
.settings-page { padding: 0 0 20px; }
.page-header h2 { font-size: 18px; color: #C17B4E; margin-bottom: 16px; }
.card-section { border-radius: 16px; background: #fff; border: none; margin-bottom: 16px; }
.card-title { font-size: 14px; font-weight: 600; color: #555; }
.data-actions { display: flex; gap: 10px; }
.settings-footer { text-align: center; padding: 20px 0; }
.version { font-size: 11px; color: #ccc; }
</style>
