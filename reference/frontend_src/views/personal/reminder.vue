<template>
  <div class="reminder-page">
    <el-card shadow="never" style="border-radius:16px;border:none;margin-bottom:12px">
      <div style="display:flex;gap:8px;align-items:center">
        <el-input v-model="newName" placeholder="提醒内容" size="small" style="flex:1" />
        <el-input v-model="newDate" type="date" size="small" style="width:160px" />
        <el-button type="primary" size="small" @click="addReminder">➕ 添加</el-button>
      </div>
    </el-card>
    <el-card shadow="never" class="list-card">
      <h4 style="margin-bottom:12px">⏰ 提醒列表</h4>
      <div v-if="list.length===0" style="text-align:center;color:#999;padding:20px">还没有提醒</div>
      <div v-for="item in list" :key="item.id" class="reminder-item">
        <span :class="{ done: item.status==='done' }">{{ item.name }}</span>
        <span style="font-size:12px;color:#b0a89a">{{ item.due_date }}</span>
        <div style="margin-left:auto;display:flex;gap:4px">
          <el-button text size="small" @click="markDone(item.id)" v-if="item.status==='pending'">✅</el-button>
          <el-button text size="small" type="danger" @click="delReminder(item.id)">🗑️</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { reminderList, reminderDone, reminderDelete, createReminder } from '../../api'

const list = ref([])
const newName = ref(''); const newDate = ref('')
const today = new Date().toISOString().slice(0,10)

async function load() { const r = await reminderList(); if (r.success) list.value = r.reminders || [] }
async function addReminder() {
  if (!newName.value || !newDate.value) return
  await createReminder(newName.value, newDate.value, 'general')
  newName.value = ''; newDate.value = ''
  load()
}
async function markDone(id) { await reminderDone(id); load() }
async function delReminder(id) { await reminderDelete(id); load() }
onMounted(load)
</script>
<style scoped>
.reminder-page { padding: 0 0 20px; }
.list-card { border-radius: 16px; border: none; }
.reminder-item { display: flex; align-items: center; gap: 8px; padding: 10px 0; border-bottom: 1px solid #f5ede6; }
.done { text-decoration: line-through; color: #b0a89a; }
</style>
