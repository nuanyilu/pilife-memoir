<template>
  <div class="chat-page">
    <div class="chat-header">
      <span class="chat-title">👨‍👩‍👧‍👦 {{ familyName }}</span>
    </div>
    <div class="msg-list" ref="msgRef">
      <div v-for="(m, i) in messages" :key="i" class="msg-row" :class="m.role">
        <div class="msg-bubble">{{ m.content }}</div>
        <div class="msg-time">{{ m.time }}</div>
      </div>
      <el-empty v-if="!messages.length" description="开始家庭聊天 💛" />
    </div>
    <div class="chat-input-bar">
      <el-input v-model="inputText" placeholder="说点什么..." :rows="2" type="textarea" resize="none" @keydown.enter.ctrl="sendMessage" />
      <el-button type="primary" :loading="sending" @click="sendMessage" round>发送</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { familyChat, chatHistory } from '../../api'
import { ElMessage } from 'element-plus'

const messages = ref([])
const inputText = ref('')
const sending = ref(false)
const msgRef = ref(null)
const familyName = ref(localStorage.getItem('nuan_family_name') || '家庭聊天')

async function loadHistory() {
  const r = await chatHistory()
  if (r.success) {
    messages.value = (r.data || []).map(item => ({
      role: item.role || 'user',
      content: item.content,
      time: item.created_at ? new Date(item.created_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) : ''
    }))
  }
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text) return
  inputText.value = ''
  messages.value.push({ role: 'user', content: text, time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) })
  sending.value = true
  const r = await familyChat(text)
  sending.value = false
  if (r.success) {
    messages.value.push({ role: 'assistant', content: r.content || r.reply, time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) })
  } else {
    ElMessage.error('发送失败')
  }
  await nextTick()
  if (msgRef.value) msgRef.value.scrollTop = msgRef.value.scrollHeight
}

onMounted(loadHistory)
</script>

<style scoped>
.chat-page { display: flex; flex-direction: column; height: calc(100vh - 170px); background: #f8f2ec; border-radius: 16px; overflow: hidden; }
.chat-header { background: linear-gradient(135deg,#b8c4a0,#a0b88a); color: #fff; padding: 12px 16px; text-align: center; font-size: 16px; font-weight: 600; }
.msg-list { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.msg-row { max-width: 80%; display: flex; flex-direction: column; gap: 2px; }
.msg-row.user { align-self: flex-end; align-items: flex-end; }
.msg-row.assistant { align-self: flex-start; align-items: flex-start; }
.msg-bubble { padding: 10px 14px; border-radius: 16px; font-size: 14px; line-height: 1.5; word-break: break-word; }
.msg-row.user .msg-bubble { background: #a0b88a; color: #fff; border-bottom-right-radius: 4px; }
.msg-row.assistant .msg-bubble { background: #fff; color: #333; border-bottom-left-radius: 4px; box-shadow: 0 1px 4px rgba(0,0,0,.06); }
.msg-time { font-size: 10px; color: #b0a89a; }
.chat-input-bar { padding: 10px 12px; background: #fff; display: flex; gap: 8px; align-items: flex-end; border-top: 1px solid #e8ddd5; }
.chat-input-bar .el-button { flex-shrink: 0; }
</style>
