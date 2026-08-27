<template>
  <div class="soul-shop-page">
    <el-card shadow="never" class="shop-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="🎋 每日上上签" name="fortune">
          <div style="text-align:center;padding:10px 0">
            <el-button type="primary" :loading="loading1" @click="getFortune" round>🎋 抽取今日上上签</el-button>
          </div>
          <div v-if="fortune" class="result-box">{{ fortune }}</div>
          <div v-else style="text-align:center;color:#999;padding:20px">点击获得今天的温暖签文</div>
        </el-tab-pane>
        <el-tab-pane label="💡 生活建议" name="advice">
          <div style="text-align:center;padding:10px 0">
            <el-button type="success" :loading="loading2" @click="getAdvice" round>💡 获取今日建议</el-button>
          </div>
          <div v-if="advice" class="result-box">{{ advice }}</div>
          <div v-else style="text-align:center;color:#999;padding:20px">让暖暖给你一个贴心建议</div>
        </el-tab-pane>
        <el-tab-pane label="🧘 情绪疗愈" name="healing">
          <div style="text-align:center;padding:10px 0">
            <el-button type="warning" :loading="loading3" @click="getHealing" round>🧘 开始疗愈引导</el-button>
          </div>
          <div v-if="healing" class="result-box">{{ healing }}</div>
          <div v-else style="text-align:center;color:#999;padding:20px">让暖暖引导你放松身心</div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { heartFortune, heartAdvice, heartHealing } from '../../api'

const activeTab = ref('fortune')
const fortune = ref(''); const loading1 = ref(false)
const advice = ref(''); const loading2 = ref(false)
const healing = ref(''); const loading3 = ref(false)

async function getFortune() { loading1.value = true; const r = await heartFortune(); if (r.success) fortune.value = r.content; loading1.value = false }
async function getAdvice() { loading2.value = true; const r = await heartAdvice(); if (r.success) advice.value = r.content; loading2.value = false }
async function getHealing() { loading3.value = true; const r = await heartHealing(); if (r.success) healing.value = r.content; loading3.value = false }
</script>
<style scoped>
.soul-shop-page { padding: 0 0 20px; }
.shop-card { border-radius: 16px; border: none; }
.result-box { background: #faf5f0; border-radius: 16px; padding: 20px; margin-top: 10px; font-size: 15px; line-height: 1.8; white-space: pre-wrap; color: #555; }
</style>
