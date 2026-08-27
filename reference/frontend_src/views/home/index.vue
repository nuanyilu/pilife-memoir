<template>
  <div class="home-page" :style="{ backgroundImage: `url(${bgImage})` }">
    <div class="home-overlay"></div>
    <div class="home-content">
      <h1 class="home-title">暖忆录</h1>
      <p class="home-subtitle">让温暖的AI，陪你走过每段时光</p>

      <!-- 问候浮层 -->
      <div v-if="showGreeting" class="greeting-card">
        <div class="greeting-avatar">🌞</div>
        <p class="greeting-text">{{ greetingText }}</p>
        <el-button type="primary" round @click="goChat">跟我聊聊 ➜</el-button>
        <el-button text size="small" @click="showGreeting = false" style="color:#999;margin-top:8px">先看看</el-button>
      </div>

      <!-- 主按钮区 -->
      <div v-if="!showGreeting" class="action-buttons">
        <div class="glass-btn" @click="goChat">
          <span class="btn-icon">💬</span>
          <span class="btn-text">个人聊天</span>
        </div>
        <div class="glass-btn" @click="goFamily">
          <span class="btn-icon">👨‍👩‍👧‍👦</span>
          <span class="btn-text">家庭聊天</span>
        </div>
        <div class="glass-btn" @click="showSkills = true">
          <span class="btn-icon">✨</span>
          <span class="btn-text">十项精选技能</span>
        </div>
      </div>

      <!-- 技能面板 -->
      <el-drawer v-model="showSkills" title="✨ 十项精选技能" size="80%" direction="btt">
        <div class="skill-grid">
          <div v-for="s in skills" :key="s.name" class="skill-card" @click="executeSkill(s)">
            <span class="skill-icon">{{ s.icon }}</span>
            <span class="skill-name">{{ s.name }}</span>
            <span class="skill-desc">{{ s.desc }}</span>
          </div>
        </div>
        <div v-if="selectedSkill" class="skill-execute">
          <h4>{{ selectedSkill.icon }} {{ selectedSkill.name }}</h4>
          <el-input v-model="skillInput" type="textarea" :rows="4" placeholder="输入你想处理的内容..." />
          <el-button type="primary" :loading="skillLoading" @click="runSkill" style="margin-top:12px">✨ 生成</el-button>
          <div v-if="skillResult" class="skill-result">{{ skillResult }}</div>
        </div>
      </el-drawer>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { chat } from '../../api'

const router = useRouter()
const bgImage = 'https://636c-cloudbase-5gwk6xwt97aecd41-1405682343.tcb.qcloud.la/暖忆录小程序首页背景图.jpg'
const showGreeting = ref(true)
const showSkills = ref(false)
const selectedSkill = ref(null)
const skillInput = ref('')
const skillLoading = ref(false)
const skillResult = ref('')
const greetingText = '早安，今天是个好天气 ☀️ 想跟我聊聊吗？'

const skills = [
  { icon: '✍️', name: '润色文字', desc: '优化语句，提升表达' },
  { icon: '📝', name: '写日记', desc: '帮你生成今日日记' },
  { icon: '🎂', name: '生日祝福', desc: '生成温馨生日祝福' },
  { icon: '💌', name: '情书', desc: '代写情书/感谢信' },
  { icon: '🔮', name: '解梦', desc: '解析梦境含义' },
  { icon: '⭐', name: '星座运势', desc: '每日星座解读' },
  { icon: '💪', name: '鼓励的话', desc: '给你温暖鼓励' },
  { icon: '🎯', name: '目标规划', desc: '帮你制定计划' },
  { icon: '🧘', name: '冥想引导', desc: '引导放松冥想' },
  { icon: '📖', name: '故事创作', desc: '为你创作小故事' },
]

function goChat() { router.push('/personal/chat') }
function goFamily() { router.push('/family') }

function executeSkill(s) {
  selectedSkill.value = s
  skillInput.value = ''
  skillResult.value = ''
}

async function runSkill() {
  if (!skillInput.value) return
  skillLoading.value = true
  const r = await chat(`请帮我${selectedSkill.value.name}：${skillInput.value}`)
  if (r.success) skillResult.value = r.content
  else skillResult.value = '生成失败，请重试'
  skillLoading.value = false
}
</script>

<style scoped>
.home-page { min-height: calc(100vh - 100px); background-size: cover; background-position: center; position: relative; border-radius: 16px; overflow: hidden; }
.home-overlay { position: absolute; inset: 0; background: rgba(255,245,235,.75); }
.home-content { position: relative; z-index: 1; padding: 30px 16px; text-align: center; }
.home-title { font-size: 28px; color: #C17B4E; font-weight: 600; letter-spacing: 2px; }
.home-subtitle { color: #B0A89A; font-size: 14px; margin: 8px 0 24px; }
.greeting-card { background: #fff; border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,.08); max-width: 300px; margin: 0 auto; }
.greeting-avatar { font-size: 48px; margin-bottom: 12px; }
.greeting-text { font-size: 16px; color: #555; margin-bottom: 16px; line-height: 1.6; }
.action-buttons { display: flex; flex-direction: column; gap: 12px; max-width: 280px; margin: 0 auto; }
.glass-btn { background: rgba(255,255,255,.85); backdrop-filter: blur(10px); border-radius: 16px; padding: 16px 20px; display: flex; align-items: center; gap: 12px; cursor: pointer; transition: .2s; border: 1px solid rgba(255,255,255,.3); }
.glass-btn:hover { background: rgba(255,255,255,.95); transform: translateY(-1px); }
.btn-icon { font-size: 24px; }
.btn-text { font-size: 15px; font-weight: 500; color: #555; }
.skill-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; padding: 10px 0; }
.skill-card { background: #faf5f0; border-radius: 12px; padding: 14px; text-align: center; cursor: pointer; }
.skill-icon { font-size: 28px; display: block; margin-bottom: 6px; }
.skill-name { font-size: 13px; font-weight: 600; color: #555; display: block; }
.skill-desc { font-size: 11px; color: #999; margin-top: 4px; display: block; }
.skill-execute { margin-top: 16px; padding: 16px; background: #faf5f0; border-radius: 12px; }
.skill-execute h4 { font-size: 16px; margin-bottom: 12px; }
.skill-result { background: #fff; border-radius: 12px; padding: 16px; margin-top: 12px; font-size: 14px; line-height: 1.6; white-space: pre-wrap; }
</style>
