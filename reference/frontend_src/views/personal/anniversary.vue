<template>
  <div class="anniversary-page">
    <el-card shadow="never" style="border-radius:16px;border:none;margin-bottom:12px">
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <el-input v-model="newName" placeholder="纪念日名称" size="small" style="flex:1;min-width:120px" />
        <el-input v-model="newDate" type="date" size="small" style="width:160px" />
        <el-select v-model="newType" size="small" style="width:100px">
          <el-option label="生日" value="birthday" />
          <el-option label="纪念日" value="anniversary" />
          <el-option label="其他" value="other" />
        </el-select>
        <el-button type="primary" size="small" @click="addAnniv">➕ 添加</el-button>
      </div>
    </el-card>
    <el-card shadow="never" class="list-card">
      <h4 style="margin-bottom:12px">🎂 纪念日</h4>
      <div v-if="list.length===0" style="text-align:center;color:#999;padding:20px">还没有纪念日</div>
      <div v-for="item in list" :key="item.id" class="anniv-item">
        <span class="anniv-icon">{{ item.type==='birthday'?'🎂':'💝' }}</span>
        <div style="flex:1">
          <span style="font-weight:500">{{ item.name }}</span>
          <span style="font-size:12px;color:#b0a89a;margin-left:8px">{{ item.date }}</span>
        </div>
        <el-button text size="small" type="danger" @click="delAnniv(item.id)">🗑️</el-button>
      </div>
    </el-card>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { anniversaryList, anniversaryCreate, anniversaryDelete } from '../../api'

const list = ref([])
const newName = ref(''); const newDate = ref(''); const newType = ref('birthday')

async function load() { const r = await anniversaryList(); if (r.success) list.value = r.anniversaries || [] }
async function addAnniv() {
  if (!newName.value || !newDate.value) return
  await anniversaryCreate(newName.value, newDate.value, newType.value)
  newName.value = ''; newDate.value = ''
  load()
}
async function delAnniv(id) { await anniversaryDelete(id); load() }
onMounted(load)
</script>
<style scoped>
.anniversary-page { padding: 0 0 20px; }
.list-card { border-radius: 16px; border: none; }
.anniv-item { display: flex; align-items: center; gap: 10px; padding: 12px 0; border-bottom: 1px solid #f5ede6; }
.anniv-icon { font-size: 24px; }
</style>
