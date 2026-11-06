<template>
  <div>
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="6" v-for="s in stats" :key="s.label">
        <el-card shadow="never">
          <div class="stat-label">{{ s.label }}</div>
          <div class="stat-num" :style="{ color: s.color }">{{ s.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never">
      <template #header>
        <div class="card-head">
          <span>我的任务</span>
          <el-button size="small" @click="load">刷新</el-button>
        </div>
      </template>

      <el-table :data="tasks" v-loading="loading" empty-text="暂无任务">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">
              {{ statusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="截止时间" width="170">
          <template #default="{ row }">{{ fmt(row.deadline) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" type="primary" link
                       @click="$router.push(`/task/${row.id}`)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { myTasks } from '../api/tasks'
import { useUserStore } from '../stores/user'

const store = useUserStore()
const tasks = ref([])
const loading = ref(false)

const stats = computed(() => {
  const c = (s) => tasks.value.filter(t => t.status === s).length
  return [
    { label: '未开始', value: c('pending'), color: '#909399' },
    { label: '进行中', value: c('doing'), color: '#409eff' },
    { label: '待审核', value: c('submitted'), color: '#e6a23c' },
    { label: '已完成', value: c('done'), color: '#67c23a' },
  ]
})

function statusType(s) {
  return { pending: 'info', doing: 'primary', submitted: 'warning',
           rejected: 'danger', done: 'success' }[s] || 'info'
}
function statusText(s) {
  return { pending: '未开始', doing: '进行中', submitted: '已提交',
           rejected: '已驳回', done: '已完成' }[s] || s
}
function fmt(d) { return d ? d.replace('T', ' ').slice(0, 16) : '—' }

async function load() {
  loading.value = true
  try { tasks.value = await myTasks() } finally { loading.value = false }
}

onMounted(async () => {
  if (!store.user) await store.fetchMe()
  load()
})
</script>

<style scoped>
.stat-label { color: #909399; font-size: 13px; }
.stat-num { font-size: 28px; font-weight: 600; margin-top: 6px; }
.card-head { display: flex; justify-content: space-between; align-items: center; }
</style>
