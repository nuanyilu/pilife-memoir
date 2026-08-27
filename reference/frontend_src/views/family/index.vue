<template>
  <div class="family-page">
    <div class="page-header">
      <h2>👨‍👩‍👧‍👦 家和</h2>
      <p class="page-desc">与家人共享温暖时光</p>
    </div>
    <!-- 创建家庭 -->
    <el-card shadow="never" class="card-section">
      <template #header><span class="card-title">🏡 创建新家庭</span></template>
      <el-form :model="createForm" label-position="top">
        <el-form-item label="家庭名称">
          <el-input v-model="createForm.name" placeholder="给家取个名字..." />
        </el-form-item>
        <el-button type="primary" :loading="creating" @click="doCreate">创建家庭</el-button>
      </el-form>
    </el-card>
    <!-- 家庭列表 -->
    <el-card shadow="never" class="card-section">
      <template #header><span class="card-title">📋 我的家庭</span></template>
      <div v-if="families.length" class="family-list">
        <div v-for="f in families" :key="f.id" class="family-item" @click="enterFamily(f)">
          <div class="family-avatar">🏠</div>
          <div class="family-info">
            <span class="family-name">{{ f.name }}</span>
            <span class="family-meta">{{ f.member_count || '--' }} 位成员</span>
          </div>
          <span class="family-arrow">›</span>
        </div>
      </div>
      <el-empty v-else description="还没有加入任何家庭" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { familyList, familyCreate } from '../../api'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const families = ref([])
const createForm = ref({ name: '' })
const creating = ref(false)

async function loadFamilies() {
  const r = await familyList()
  if (r.success) families.value = r.data || []
}
async function doCreate() {
  if (!createForm.value.name) { ElMessage.warning('请输入家庭名称'); return }
  creating.value = true
  const r = await familyCreate(createForm.value.name)
  creating.value = false
  if (r.success) { ElMessage.success('家庭已创建 🎉'); createForm.value.name = ''; loadFamilies() }
  else ElMessage.error('创建失败')
}
function enterFamily(f) {
  localStorage.setItem('nuan_family_id', f.id)
  localStorage.setItem('nuan_family_name', f.name)
  router.push('/family/chat')
}
onMounted(loadFamilies)
</script>

<style scoped>
.family-page { padding: 0 0 20px; }
.page-header h2 { font-size: 18px; color: #C17B4E; margin-bottom: 4px; }
.page-desc { font-size: 13px; color: #b0a89a; margin-bottom: 16px; }
.card-section { border-radius: 16px; background: #fff; border: none; margin-bottom: 16px; }
.card-title { font-size: 14px; font-weight: 600; color: #555; }
.family-list { display: flex; flex-direction: column; gap: 4px; }
.family-item { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 12px; cursor: pointer; transition: .2s; }
.family-item:hover { background: #faf5f0; }
.family-avatar { font-size: 28px; }
.family-info { flex: 1; display: flex; flex-direction: column; }
.family-name { font-size: 15px; font-weight: 500; color: #333; }
.family-meta { font-size: 12px; color: #b0a89a; margin-top: 2px; }
.family-arrow { font-size: 20px; color: #b0a89a; }
</style>
