<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2>RM 战队实验室管理后台</h2>
      <el-form :model="form" @submit.prevent="onLogin" label-width="60px">
        <el-form-item label="工号">
          <el-input v-model="form.emp_no" placeholder="请输入工号" autofocus />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password
                    placeholder="请输入密码" @keyup.enter="onLogin" />
        </el-form-item>
        <el-button type="primary" :loading="loading" style="width:100%"
                   @click="onLogin">登录</el-button>
      </el-form>
      <p class="hint">默认管理员：admin / 123456（上线务必改密码）</p>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const router = useRouter()
const store = useUserStore()
const loading = ref(false)
const form = reactive({ emp_no: '', password: '' })

async function onLogin() {
  if (!form.emp_no || !form.password) {
    ElMessage.warning('请输入工号和密码')
    return
  }
  loading.value = true
  try {
    await store.login(form.emp_no, form.password)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch (e) {
    // 错误已由 axios 拦截器提示
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100vh; display: flex; align-items: center; justify-content: center;
  background: #2c3e50;
}
.login-card { width: 380px; }
.login-card h2 { text-align: center; font-size: 18px; margin: 0 0 24px; }
.hint { text-align: center; color: #909399; font-size: 12px; margin: 16px 0 0; }
</style>
