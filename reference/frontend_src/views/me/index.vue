<template>
  <div class="me-page">
    <!-- 用户信息卡片 -->
    <el-card shadow="never" class="profile-card">
      <div class="profile-row">
        <div class="profile-avatar">{{ avatar }}</div>
        <div class="profile-info">
          <p class="profile-name">{{ profile.nickname || profile.name || '暖暖用户' }}</p>
          <p class="profile-login">{{ loginLabel }} {{ profile.login_type || '' }}</p>
        </div>
        <el-button text @click="$router.push('/me/settings')">设置 ⚙️</el-button>
      </div>
    </el-card>
    <!-- 数据统计 -->
    <el-card shadow="never" class="stats-card">
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-num">{{ stats.diary_count || 0 }}</span>
          <span class="stat-label">累计日记</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">{{ stats.continuous_days || 0 }}</span>
          <span class="stat-label">连续记录</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">{{ stats.company_days || 0 }}</span>
          <span class="stat-label">暖暖陪伴</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">{{ stats.coins || 0 }}</span>
          <span class="stat-label">暖币余额</span>
        </div>
      </div>
    </el-card>
    <!-- 菜单列表 -->
    <el-card shadow="never" class="menu-card">
      <div class="menu-list">
        <div class="menu-item" @click="$router.push('/me/memory')">
          <span class="menu-icon">🧠</span>
          <span class="menu-label">暖暖的记忆</span>
          <span class="menu-arrow">›</span>
        </div>
        <div class="menu-item" @click="$router.push('/personal/memory')">
          <span class="menu-icon">🌸</span>
          <span class="menu-label">记忆花园</span>
          <span class="menu-arrow">›</span>
        </div>
        <div class="menu-item" @click="$router.push('/me/settings')">
          <span class="menu-icon">⚙️</span>
          <span class="menu-label">设置</span>
          <span class="menu-arrow">›</span>
        </div>
        <div class="menu-item" @click="$router.push('/me/security')">
          <span class="menu-icon">🔐</span>
          <span class="menu-label">安全中心</span>
          <span class="menu-arrow">›</span>
        </div>
      </div>
    </el-card>
    <!-- 底部 -->
    <div class="me-footer">
      <el-button text style="color:#b0a89a" @click="handleLogout">退出登录</el-button>
      <p class="version">暖忆录 v1.0.0 · 永恒版</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getProfile, logout as apiLogout } from '../../api'
import { ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const profile = ref({})
const stats = ref({})
const loginType = ref(localStorage.getItem('nuan_login_type') || '')
const avatar = computed(() => ({ email: '📧', guest: '👤', pinetwork: '🥧', wallet: '🔗' }[loginType.value] || '👤'))
const loginLabel = computed(() => ({ email: '邮箱', guest: '访客', pinetwork: 'Pi', wallet: '钱包' }[loginType.value] || ''))

async function loadProfile() {
  const r = await getProfile()
  if (r.success) {
    const u = r.user || r.data || r
    profile.value = u
    stats.value = {
      diary_count: u.diary_count || 0,
      continuous_days: u.continuous_days || 0,
      company_days: u.chat_count || 0,
      coins: u.coins || 0
    }
  }
}

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', { confirmButtonText: '退出', cancelButtonText: '取消', type: 'warning' })
    apiLogout()
    router.push('/home')
    window.location.reload()
  } catch {}
}

onMounted(loadProfile)
</script>

<style scoped>
.me-page { padding: 0 0 20px; }
.profile-card { border-radius: 16px; background: #fff; border: none; margin-bottom: 12px; }
.profile-row { display: flex; align-items: center; gap: 12px; }
.profile-avatar { width: 52px; height: 52px; border-radius: 50%; background: linear-gradient(135deg,#f5d6b8,#e8c4a0); display: flex; align-items: center; justify-content: center; font-size: 28px; }
.profile-info { flex: 1; }
.profile-name { font-size: 16px; font-weight: 600; color: #333; }
.profile-login { font-size: 12px; color: #b0a89a; margin-top: 2px; }
.stats-card { border-radius: 16px; background: #fff; border: none; margin-bottom: 12px; }
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; text-align: center; }
.stat-item { display: flex; flex-direction: column; align-items: center; }
.stat-num { font-size: 20px; font-weight: 700; color: #C17B4E; }
.stat-label { font-size: 11px; color: #b0a89a; margin-top: 4px; }
.menu-card { border-radius: 16px; background: #fff; border: none; margin-bottom: 12px; }
.menu-list { display: flex; flex-direction: column; }
.menu-item { display: flex; align-items: center; gap: 12px; padding: 14px 0; border-bottom: 1px solid #f5ede6; cursor: pointer; }
.menu-item:last-child { border-bottom: none; }
.menu-icon { font-size: 22px; }
.menu-label { flex: 1; font-size: 14px; color: #444; }
.menu-arrow { font-size: 18px; color: #b0a89a; }
.me-footer { text-align: center; padding: 20px 0; }
.version { font-size: 11px; color: #ccc; margin-top: 8px; }
</style>
