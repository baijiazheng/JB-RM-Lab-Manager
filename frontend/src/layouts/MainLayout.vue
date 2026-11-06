<template>
  <el-container class="layout">
    <!-- ★ 侧边导航栏 -->
    <el-aside width="220px" class="aside">
      <div class="logo">RM 实验室</div>
      <el-menu :default-active="route.path" router class="menu">
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon><span>我的工作台</span>
        </el-menu-item>

        <template v-if="store.isAdmin">
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon><span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/tasks">
            <el-icon><List /></el-icon><span>任务管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/submissions">
            <el-icon><Document /></el-icon><span>提交记录</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶栏 -->
      <el-header class="header">
        <span class="title">{{ route.meta.title || '' }}</span>
        <div class="right">
          <el-tag v-if="store.user" size="small" type="info">
            {{ store.user.name }}（{{ store.user.group_name || '未分组' }}）
          </el-tag>
          <el-tag size="small" :type="store.isAdmin ? 'danger' : 'success'">
            {{ store.isAdmin ? '管理员' : '队员' }}
          </el-tag>
          <el-button size="small" @click="onLogout">退出</el-button>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const store = useUserStore()

function onLogout() {
  store.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout { height: 100vh; }
.aside { background: #2c3e50; }
.logo {
  height: 60px; line-height: 60px; text-align: center;
  color: #fff; font-size: 18px; font-weight: 600;
  border-bottom: 1px solid #3d5166;
}
.menu { border: none; background: transparent; }
.menu :deep(.el-menu-item) { color: #bfcbd9; }
.menu :deep(.el-menu-item.is-active) { background: #1f2d3d; color: #409eff; }
.menu :deep(.el-menu-item:hover) { background: #34495e; }

.header {
  background: #fff; display: flex; align-items: center;
  justify-content: space-between; border-bottom: 1px solid #e4e7ed;
}
.title { font-size: 16px; font-weight: 600; }
.right { display: flex; gap: 10px; align-items: center; }
.main { background: #f5f7fa; padding: 20px; }
</style>
