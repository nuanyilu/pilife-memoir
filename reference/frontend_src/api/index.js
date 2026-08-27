import axios from 'axios'

const api = axios.create({ baseURL: '/api/v1', timeout: 30000 })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('nuan_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res.data,
  err => Promise.reject(err.response?.data || err)
)

// ── 认证 ──
export async function login(type) {
  const r = await api.post('/auth/login', { login_type: type })
  if (r.success) {
    localStorage.setItem('nuan_token', r.token)
    localStorage.setItem('nuan_login_type', r.user.login_type)
    localStorage.setItem('nuan_user_id', r.user.id)
  }
  return r
}

export function loginEmail(email, password) {
  return api.post('/auth/login', { email, password })
}

export function register(email, password, nickname) {
  return api.post('/auth/register', { email, password, nickname })
}

export function loginGuest() {
  return api.post('/auth/guest')
}

export function logout() {
  localStorage.removeItem('nuan_token')
  localStorage.removeItem('nuan_login_type')
  localStorage.removeItem('nuan_user_id')
}

// ── 聊天 ──
export function chat(message) { return api.post('/chat', { message }) }
export function chatHistory() { return api.get('/chat/history') }

// ── 日记 ──
export function diaryGenerate() { return api.post('/diary/generate') }
export function diaryToday() { return api.get('/diary/today') }
export function diaryList(page) { return api.get('/diary/list', { params: { page } }) }

// ── 记忆 ──
export function memoryRecall(query) { return api.post('/memory/recall', { query }) }
export function getFacts() { return api.get('/memory/facts') }
export function setFact(type, value) { return api.post('/facts/set', { type, value }) }

// ── 意图 & 情感 ──
export function matchIntent(text) { return api.post('/intent/match', { text }) }
export function matchEmotion(text) { return api.post('/emotion/match', { text }) }
export function emotionOverview(days) { return api.get('/emotion/overview', { params: { days } }) }
export function emotionTimeline(days) { return api.get('/emotion/timeline', { params: { days } }) }

// ── 情感互动（新增） ──
export function emotionSign() { return api.post('/emotion/sign') }
export function heartFortune() { return api.get('/emotion/fortune') }
export function heartAdvice() { return api.get('/emotion/advice') }
export function heartHealing() { return api.get('/emotion/healing') }
export function dreamAnalyze(dream) { return api.post('/emotion/dream', { dream }) }

// ── 回顾 ──
export function monthlyReview(month) { return api.post('/review/monthly', { month }) }
export function weeklyReview() { return api.get('/review/weekly') }

// ── 提醒 ──
export function parseReminder(text) { return api.post('/reminder/parse', { text }) }
export function createReminder(name, date, type) { return api.post('/reminder/create', { name, date, type }) }
export function reminderList() { return api.get('/reminder/list') }
export function reminderDone(id) { return api.post(`/reminder/${id}/done`) }
export function reminderDelete(id) { return api.delete(`/reminder/${id}`) }

// ── 纪念日 ──
export function getAnniversaries() { return api.get('/anniversary') }
export function createAnniversary(name, date, type) { return api.post('/anniversary', { name, date, type }) }
export function deleteAnniversary(id) { return api.delete(`/anniversary/${id}`) }
export function anniversaryList() { return api.get('/anniversary/list') }
export function anniversaryCreate(name, date, type) { return api.post('/anniversary', { name, date, type }) }
export function anniversaryDelete(id) { return api.delete(`/anniversary/${id}`) }

// ── 人生时间线 ──
export function lifeTimeline() { return api.get('/life/timeline') }
export function lifeEventCreate(year, title, desc, type) { return api.post('/life/event', { year, title, description: desc, event_type: type }) }
export function lifeEventDelete(id) { return api.delete(`/life/event/${id}`) }
export function lifeArchive() { return api.get('/life/archive') }
export function thisDay() { return api.get('/memory/thisday') }

// ── 广场 ──
export function squarePosts(page, topic) { return api.get('/square/posts', { params: { page, topic, per_page: 20 } }) }
export function squareCreate(content, emotion_tag, topic) { return api.post('/square/posts', { content, emotion_tag, topic }) }
export function squareToggleLike(postId) { return api.post(`/square/posts/${postId}/like`) }
export function squareComment(postId, content) { return api.post(`/square/posts/${postId}/comments`, { content }) }
export function squareTopics() { return api.get('/square/topics') }
export function squareFeed(page) { return api.get('/square/feed', { params: { page } }) }

// ── 家庭 ──
export function familyCreate(name) { return api.post('/family', { name }) }
export function familyList() { return api.get('/family') }
export function familyDiary(family_id) { return api.post('/family/diary', { family_id }) }
export function familyChat(message) { return api.post('/family/chat', { message }) }

// ── 用户 ──
export function getProfile() { return api.get('/user/profile') }
export function clearUser() { return api.post('/user/clear') }
export function userUpdate(nickname) { return api.put('/user/profile', { nickname }) }

// ── 积分 ──
export function getPoints() { return api.get('/user/points') }
export function addPoints(amount, reason) { return api.post('/user/points', { amount, reason }) }

// ── 许愿 ──
export function blessing(context) { return api.post('/blessing', { context }) }

// ── 知识库 ──
export function factsSearch(keyword) { return api.get('/memory/facts/search', { params: { keyword } }) }
export function factsDelete(id) { return api.delete(`/memory/facts/${id}`) }

export default api
