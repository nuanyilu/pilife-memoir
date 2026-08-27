<template>
  <div class="album-page">
    <div class="page-header">
      <h2>👨‍👩‍👧‍👦 家庭相册</h2>
    </div>
    <el-card shadow="never" class="album-card">
      <el-empty description="家庭相册即将上线">
        <template #image>
          <div class="empty-icon">📸</div>
        </template>
        <p class="album-hint">正在建设中，敬请期待...</p>
        <el-button type="primary" round @click="$router.push('/family/chat')">先去聊聊天吧 💬</el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
</script>

<style scoped>
.album-page { padding: 0 0 20px; }
.page-header h2 { font-size: 18px; color: #C17B4E; margin-bottom: 16px; }
.album-card { border-radius: 16px; background: #fff; border: none; }
.empty-icon { font-size: 64px; margin-bottom: 12px; }
.album-hint { color: #b0a89a; font-size: 14px; margin-bottom: 16px; }
</style>
