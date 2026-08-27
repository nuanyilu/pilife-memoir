<template>
  <div class="security-page">
    <div class="page-header">
      <h2>🔐 安全中心</h2>
      <p class="page-desc">保障你的数据安全与隐私</p>
    </div>
    <!-- 隐私标识 -->
    <el-card shadow="never" class="card-section">
      <template #header><span class="card-title">🛡️ 隐私保护</span></template>
      <div class="privacy-info">
        <div class="privacy-item">
          <span class="privacy-icon">🔒</span>
          <div class="privacy-detail">
            <p class="privacy-title">端到端加密</p>
            <p class="privacy-desc">你的所有聊天和日记数据都经过端到端加密</p>
          </div>
        </div>
        <div class="privacy-item">
          <span class="privacy-icon">🔐</span>
          <div class="privacy-detail">
            <p class="privacy-title">数据隔离</p>
            <p class="privacy-desc">每人数据独立存储，互不可见</p>
          </div>
        </div>
        <div class="privacy-item">
          <span class="privacy-icon">🗑️</span>
          <div class="privacy-detail">
            <p class="privacy-title">数据可删除</p>
            <p class="privacy-desc">你随时可以清除所有个人数据</p>
          </div>
        </div>
      </div>
    </el-card>
    <!-- 登录信息 -->
    <el-card shadow="never" class="card-section">
      <template #header><span class="card-title">🔑 登录信息</span></template>
      <el-form label-position="top">
        <el-form-item label="登录方式">
          <el-tag>{{ loginTypeLabel }}</el-tag>
        </el-form-item>
        <el-form-item label="用户ID">
          <el-input :model-value="userId" disabled>
            <template #append>
              <el-button @click="copyId">复制</el-button>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
    </el-card>
    <!-- 安全操作 -->
    <el-card shadow="never" class="card-section">
      <template #header><span class="card-title">⚠️ 安全操作</span></template>
      <div class="security-actions">
        <el-button type="primary" plain @click="changeLogin">🔄 切换登录方式</el-button>
        <el-button type="danger" plain @click="doClearData">🗑️ 清除所有数据</el-button>
        <el-button type="danger" plain @click="doLogout">🚪 退出登录</el-button>
      </div>
    </el-card>
    <!-- 安全提示 -->
    <el-alert title="安全提示" type="warning" :closable="false" description="请勿将你的用户ID和Token泄露给他人。暖忆录不会以任何理由向你索要密码。" show-icon />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { clearUser, logout as apiLogout } from '../../api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const userId = ref(localStorage.getItem('nuan_user_id') || '--')
const loginType = ref(localStorage.getItem('nuan_login_type') || '')
const loginTypeLabel = computed(() => ({ email: '📧 邮箱登录', guest: '👤 访客模式', pinetwork: '🥧 Pi网络', wallet: '🔗 钱包' }[loginType.value] || '👤 访客'))

function copyId() {
  navigator.clipboard.writeText(userId.value)
  ElMessage.success('已复制用户ID')
}
function changeLogin() {
  apiLogout()
  router.push('/')
  window.location.reload()
}
async function doClearData() {
  try {
    await ElMessageBox.confirm('确定要清除所有数据吗？此操作不可恢复！', '警告', { confirmButtonText: '确认', cancelButtonText: '取消', type: 'warning' })
    const r = await clearUser()
    if (r.success) ElMessage.success('所有数据已清除')
    else ElMessage.error('清除失败')
  } catch {}
}
async function doLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', { confirmButtonText: '退出', cancelButtonText: '取消', type: 'warning' })
    apiLogout()
    router.push('/')
    window.location.reload()
  } catch {}
}
</script>

<style scoped>
.security-page { padding: 0 0 20px; }
.page-header h2 { font-size: 18px; color: #C17B4E; margin-bottom: 4px; }
.page-desc { font-size: 13px; color: #b0a89a; margin-bottom: 16px; }
.card-section { border-radius: 16px; background: #fff; border: none; margin-bottom: 16px; }
.card-title { font-size: 14px; font-weight: 600; color: #555; }
.privacy-info { display: flex; flex-direction: column; gap: 14px; }
.privacy-item { display: flex; gap: 12px; align-items: flex-start; }
.privacy-icon { font-size: 28px; }
.privacy-detail { flex: 1; }
.privacy-title { font-size: 14px; font-weight: 600; color: #444; }
.privacy-desc { font-size: 12px; color: #b0a89a; margin-top: 2px; }
.security-actions { display: flex; flex-direction: column; gap: 10px; }
.security-actions .el-button { width: 100%; }
</style>
