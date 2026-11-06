// encoding: utf-8
import { createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  { path: '/login', component: () => import('../views/Login.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      // ---- 队员 ----
      { path: 'dashboard', component: () => import('../views/Dashboard.vue'),
        meta: { title: '我的工作台' } },
      { path: 'task/:id', component: () => import('../views/TaskDetail.vue'),
        meta: { title: '任务详情' } },
      // ---- 管理员 ----
      { path: 'admin/users', component: () => import('../views/admin/Users.vue'),
        meta: { title: '用户管理', adminOnly: true } },
      { path: 'admin/tasks', component: () => import('../views/admin/Tasks.vue'),
        meta: { title: '任务管理', adminOnly: true } },
      { path: 'admin/submissions', component: () => import('../views/admin/Submissions.vue'),
        meta: { title: '提交记录', adminOnly: true } },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHashHistory(),   // ★ hash 模式，内网部署不用配 nginx
  routes,
})

// ★ 全局守卫：未登录 → 登录页；非管理员访问 admin 页 → 首页
router.beforeEach(async (to) => {
  const store = useUserStore()
  if (to.meta.public) return true

  if (!store.isLoggedIn) return { path: '/login' }
  if (!store.user) {
    try { await store.fetchMe() } catch { return { path: '/login' } }
  }
  if (to.meta.adminOnly && !store.isAdmin) return { path: '/dashboard' }
  return true
})

export default router
