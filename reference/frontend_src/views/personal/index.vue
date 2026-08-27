<template>
  <div class="personal-page">
    <div class="privacy-badge"><span>🔐 端到端加密</span></div>
    <div class="welcome-section">
      <p class="welcome-text">欢迎回来</p>
      <p class="welcome-sub">暖暖一直在 💛</p>
    </div>
    <div class="avatar-section">
      <div class="avatar-circle">🌙</div>
      <p class="greeting">{{ greeting }}</p>
    </div>
    <div class="petal-grid">
      <div v-for="item in petals" :key="item.label" class="petal-card" @click="goTo(item.route)">
        <span class="petal-icon">{{ item.icon }}</span>
        <span class="petal-label">{{ item.label }}</span>
        <span v-if="item.desc" class="petal-desc">{{ item.desc }}</span>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
const greeting = ref('今天想和我聊点什么呢？☀️')
const petals = [
  { icon: '💬', label: '倾诉', route: '/personal/chat' },
  { icon: '📝', label: '日记', route: '/personal/diary' },
  { icon: '📷', label: '相册', route: '/personal/album' },
  { icon: '🌸', label: '情绪签', route: '/personal/emotion-sign' },
  { icon: '🎋', label: '心运小馆', route: '/personal/soul-shop' },
  { icon: '🌙', label: '梦境', route: '/personal/dream' },
]
const petals2 = [
  { icon: '⏰', label: '提醒', route: '/personal/reminder' },
  { icon: '🎂', label: '纪念日', route: '/personal/anniversary' },
  { icon: '📖', label: '生活档案', route: '/personal/life-archive' },
  { icon: '📊', label: '情绪回顾', route: '/personal/emotion' },
  { icon: '💝', label: '暖忆寄语', route: '/personal/chat' },
  { icon: '🎵', label: '音乐', route: '/personal/chat' },
]
function goTo(route) { router.push(route) }
</script>
<style scoped>
.personal-page { padding: 0 0 16px; }
.privacy-badge { text-align: center; padding: 6px 0; font-size: 11px; color: #b8a89a; }
.privacy-badge span { background: #f5ede6; padding: 2px 12px; border-radius: 20px; }
.welcome-section { text-align: center; padding: 16px 0 8px; }
.welcome-text { font-size: 20px; font-weight: 600; color: #C17B4E; }
.welcome-sub { font-size: 14px; color: #b0a89a; margin-top: 4px; }
.avatar-section { display: flex; flex-direction: column; align-items: center; padding: 12px 0 20px; }
.avatar-circle { width: 72px; height: 72px; border-radius: 50%; background: linear-gradient(135deg,#f5d6b8,#e8c4a0); display: flex; align-items: center; justify-content: center; font-size: 36px; box-shadow: 0 4px 16px rgba(193,123,78,.2); }
.greeting { font-size: 14px; color: #666; margin-top: 10px; }
.petal-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; padding: 0 16px; margin-bottom: 10px; }
.petal-card { background: #fff; border-radius: 16px; padding: 16px 10px; display: flex; flex-direction: column; align-items: center; gap: 6px; cursor: pointer; box-shadow: 0 2px 12px rgba(0,0,0,.04); transition: .2s; }
.petal-card:hover { transform: translateY(-2px); box-shadow: 0 4px 20px rgba(193,123,78,.12); }
.petal-icon { font-size: 28px; }
.petal-label { font-size: 12px; font-weight: 500; color: #555; }
.petal-desc { font-size: 10px; color: #b0a89a; }
</style>
