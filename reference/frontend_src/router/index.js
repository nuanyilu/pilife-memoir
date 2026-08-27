import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/home' },
  // 首页
  { path: '/home', name: 'Home', component: () => import('../views/home/index.vue') },

  // 个人
  { path: '/personal', name: 'Personal', component: () => import('../views/personal/index.vue') },
  { path: '/personal/chat', name: 'PersonalChat', component: () => import('../views/personal/chat.vue') },
  { path: '/personal/diary', name: 'PersonalDiary', component: () => import('../views/personal/diary.vue') },
  { path: '/personal/memory', name: 'PersonalMemory', component: () => import('../views/personal/memory.vue') },
  { path: '/personal/emotion', name: 'PersonalEmotion', component: () => import('../views/personal/emotion.vue') },
  { path: '/personal/album', name: 'PersonalAlbum', component: () => import('../views/personal/album.vue') },

  // 个人 - 新增子页面
  { path: '/personal/emotion-sign', name: 'PersonalEmotionSign', component: () => import('../views/personal/emotion-sign.vue') },
  { path: '/personal/soul-shop', name: 'PersonalSoulShop', component: () => import('../views/personal/soul-shop.vue') },
  { path: '/personal/dream', name: 'PersonalDream', component: () => import('../views/personal/dream.vue') },
  { path: '/personal/reminder', name: 'PersonalReminder', component: () => import('../views/personal/reminder.vue') },
  { path: '/personal/anniversary', name: 'PersonalAnniversary', component: () => import('../views/personal/anniversary.vue') },
  { path: '/personal/life-archive', name: 'PersonalLifeArchive', component: () => import('../views/personal/life-archive.vue') },

  // 家和
  { path: '/family', name: 'Family', component: () => import('../views/family/index.vue') },
  { path: '/family/chat', name: 'FamilyChat', component: () => import('../views/family/chat.vue') },
  { path: '/family/diary', name: 'FamilyDiary', component: () => import('../views/family/diary.vue') },
  { path: '/family/album', name: 'FamilyAlbum', component: () => import('../views/family/album.vue') },

  // 回响谷
  { path: '/square', name: 'Square', component: () => import('../views/square/index.vue') },
  { path: '/square/post', name: 'SquarePost', component: () => import('../views/square/post.vue') },

  // 我的
  { path: '/me', name: 'Me', component: () => import('../views/me/index.vue') },
  { path: '/me/memory', name: 'MeMemory', component: () => import('../views/me/memory.vue') },
  { path: '/me/settings', name: 'MeSettings', component: () => import('../views/me/settings.vue') },
  { path: '/me/security', name: 'MeSecurity', component: () => import('../views/me/security.vue') },
]

export default createRouter({ history: createWebHistory(), routes })
