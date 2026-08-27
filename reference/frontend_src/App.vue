<template>
  <div class="app-container" :style="{ background: bgColor }">
    <!-- 登录弹窗 -->
    <el-dialog v-model="showLogin" title="登录暖忆录" width="360px" :close-on-click-modal="false" :close-on-press-escape="false">
      <div style="text-align:center;margin-bottom:16px">
        <div style="font-size:48px">🌙</div>
        <p style="color:#999;font-size:13px;margin-top:8px">登录后可享受完整功能，云端保存数据</p>
      </div>
      <el-tabs v-model="loginTab">
        <el-tab-pane label="登录" name="login">
          <el-input v-model="loginEmail" placeholder="邮箱" style="margin-bottom:12px" />
          <el-input v-model="loginPassword" type="password" placeholder="密码" show-password style="margin-bottom:12px" @keyup.enter="doEmailLogin" />
          <el-button type="primary" style="width:100%" :loading="loginLoading" @click="doEmailLogin">📧 登录</el-button>
        </el-tab-pane>
        <el-tab-pane label="注册" name="register">
          <el-input v-model="regEmail" placeholder="邮箱" style="margin-bottom:12px" />
          <el-input v-model="regPassword" type="password" placeholder="密码(至少6位)" show-password style="margin-bottom:12px" />
          <el-input v-model="regNickname" placeholder="昵称(可选)" style="margin-bottom:12px" />
          <el-button type="success" style="width:100%" :loading="regLoading" @click="doRegister">📝 注册</el-button>
        </el-tab-pane>
      </el-tabs>
      <div style="text-align:center;margin-top:12px">
        <el-button text size="small" @click="doGuestLogin">👤 先逛逛（访客模式）</el-button>
      </div>
    </el-dialog>

    <!-- 已登录：主界面 -->
    <div v-if="loggedIn" class="app-layout">
      <header class="app-header">
        <span class="header-logo">🌙 暖忆录</span>
        <div style="display:flex;align-items:center;gap:8px">
          <span style="font-size:12px;opacity:.8">{{ userNickname }}</span>
          <span class="header-badge">{{ loginLabel }}</span>
        </div>
      </header>
      <main class="app-main">
        <router-view />
      </main>
      <nav class="tab-bar">
        <div v-for="tab in tabs" :key="tab.path" class="tab-item" :class="{ active: currentTab === tab.path }" @click="switchTab(tab.path)">
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </div>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { loginEmail as apiLoginEmail, register, loginGuest, getProfile } from './api'

const router = useRouter()
const route = useRoute()

const loggedIn = ref(false)
const userNickname = ref('')
const showLogin = ref(false)
const loginTab = ref('login')

// 登录表单
const loginEmail = ref('admin@nuan.com')
const loginPassword = ref('nuan2026')
const loginLoading = ref(false)

// 注册表单
const regEmail = ref('')
const regPassword = ref('')
const regNickname = ref('')
const regLoading = ref(false)

const loginType = ref('')
const loginLabel = computed(() => ({ email: '📧', pinetwork: '🥧', guest: '👤' }[loginType.value] || '👤'))

const tabs = [
  { path: '/home', icon: '🏠', label: '首页' },
  { path: '/personal', icon: '💬', label: '个人' },
  { path: '/family', icon: '👨👩👧👦', label: '家和' },
  { path: '/square', icon: '🌊', label: '回响谷' },
  { path: '/me', icon: '👤', label: '我的' },
]
const currentTab = ref('home')
const bgColor = ref('#FFF5EB')

watch(() => route.path, p => { currentTab.value = p.split('/')[1] || 'home' })
function switchTab(path) { router.push(path) }

async function doEmailLogin() {
  if (!loginEmail.value || !loginPassword.value) return
  loginLoading.value = true
  try {
    const r = await apiLoginEmail(loginEmail.value, loginPassword.value)
    if (r.success) {
      loggedIn.value = true; loginType.value = 'email'
      userNickname.value = r.user?.nickname || '用户'
      localStorage.setItem('nuan_token', r.token)
      localStorage.setItem('nuan_login_type', 'email')
      showLogin.value = false
      router.push('/home')
    } else {
      alert(r.error || '登录失败')
    }
  } catch (e) { alert('登录失败: ' + (e.error || e.message)) }
  loginLoading.value = false
}

async function doRegister() {
  if (!regEmail.value || !regPassword.value) return
  if (regPassword.value.length < 6) { alert('密码至少6位'); return }
  regLoading.value = true
  try {
    const r = await register(regEmail.value, regPassword.value, regNickname.value)
    if (r.success) {
      loggedIn.value = true; loginType.value = 'email'
      userNickname.value = r.user?.nickname || '用户'
      localStorage.setItem('nuan_token', r.token)
      showLogin.value = false
      router.push('/home')
    } else {
      alert(r.error || '注册失败')
    }
  } catch (e) { alert('注册失败: ' + (e.error || e.message)) }
  regLoading.value = false
}

async function doGuestLogin() {
  try {
    const r = await loginGuest()
    if (r.success) {
      loggedIn.value = true; loginType.value = 'guest'
      userNickname.value = '访客'
      localStorage.setItem('nuan_token', r.token)
      localStorage.setItem('nuan_login_type', 'guest')
      showLogin.value = false
      router.push('/home')
    }
  } catch (e) { alert('访客模式失败') }
}

// 检查是否已登录
onMounted(async () => {
  const token = localStorage.getItem('nuan_token')
  if (token) {
    loggedIn.value = true
    loginType.value = localStorage.getItem('nuan_login_type') || 'email'
    try {
      const r = await getProfile()
      if (r.success) {
        userNickname.value = r.user?.nickname || '用户'
      }
    } catch (e) {
      // token过期，重新登录
      localStorage.removeItem('nuan_token')
      loggedIn.value = false
      showLogin.value = true
    }
  } else {
    showLogin.value = true
  }
})
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #FFF5EB; color: #2c2c2c; }
.app-container { min-height: 100vh; display: flex; flex-direction: column; }
.app-layout { display: flex; flex-direction: column; min-height: 100vh; }
.app-header { background: linear-gradient(135deg,#d4a574,#c4956a); color: #fff; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; }
.header-logo { font-size: 16px; font-weight: 600; letter-spacing: 1px; }
.header-badge { font-size: 14px; }
.tab-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #F9F7F3; border-top: 1px solid #e8ddd5; display: flex; justify-content: space-around; padding: 6px 0; padding-bottom: env(safe-area-inset-bottom, 6px); z-index: 100; }
.tab-item { display: flex; flex-direction: column; align-items: center; gap: 2px; cursor: pointer; padding: 4px 12px; }
.tab-icon { font-size: 22px; }
.tab-label { font-size: 10px; color: #B0A89A; }
.tab-item.active .tab-label { color: #C17B4E; font-weight: 600; }
.tab-item.active .tab-icon { transform: scale(1.1); }
.app-main { flex: 1; padding: 16px 16px 70px; overflow-y: auto; }
</style>
