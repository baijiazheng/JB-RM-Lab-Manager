<template>
  <el-card shadow="never">
    <template #header>
      <div class="head">
        <span>任务管理（{{ tasks.length }}）</span>
        <el-button type="primary" size="small" @click="openCreate">发布任务</el-button>
      </div>
    </template>

    <el-table :data="tasks" v-loading="loading" empty-text="暂无任务">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="title" label="标题" min-width="180" />
      <el-table-column label="接收人" width="120">
        <template #default="{ row }">
          {{ row.assignee_name }}<span class="dim">（{{ row.assignee_group }}）</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="截止" width="150">
        <template #default="{ row }">{{ fmt(row.deadline) }}</template>
      </el-table-column>
      <el-table-column label="提交" width="70">
        <template #default="{ row }">{{ row.submission_count }}</template>
      </el-table-column>
      <el-table-column label="操作" min-width="240">
        <template #default="{ row }">
          <el-button size="small" link type="primary" @click="$router.push(`/task/${row.id}`)">查看</el-button>
          <el-button v-if="row.status === 'submitted'" size="small" link type="success"
                     @click="onApprove(row)">通过</el-button>
          <el-button v-if="row.status === 'submitted'" size="small" link type="danger"
                     @click="onReject(row)">驳回</el-button>
          <el-button size="small" link @click="onSetStatus(row)">改状态</el-button>
          <el-button size="small" link type="danger" @click="onDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 发布任务弹窗 -->
    <el-dialog v-model="dialog" title="发布任务" width="560px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="接收人">
          <el-select v-model="form.assignee_id" style="width:100%" filterable>
            <el-option v-for="u in users" :key="u.id" :label="`${u.name}（${u.group_name || '未分组'}）`" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止时间">
          <el-date-picker v-model="form.deadline" type="datetime"
                          value-format="YYYY-MM-DDTHH:mm:ss" style="width:100%" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="要求">
          <el-input v-model="form.requirement" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">发布</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { allTasks, createTask, updateTaskStatus, deleteTask } from '../../api/tasks'
import { listUsers } from '../../api/users'

const tasks = ref([])
const users = ref([])
const loading = ref(false)
const saving = ref(false)
const dialog = ref(false)
const form = reactive({
  title: '', assignee_id: null, deadline: null, description: '', requirement: '',
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
  try {
    tasks.value = await allTasks()
    users.value = await listUsers()
  } finally { loading.value = false }
}

function openCreate() {
  Object.assign(form, { title: '', assignee_id: null, deadline: null,
                        description: '', requirement: '' })
  dialog.value = true
}

async function onSave() {
  if (!form.title || !form.assignee_id) {
    ElMessage.warning('标题和接收人必填'); return
  }
  saving.value = true
  try {
    await createTask({ ...form })
    ElMessage.success('已发布')
    dialog.value = false
    load()
  } finally { saving.value = false }
}

async function onApprove(row) {
  await updateTaskStatus(row.id, 'done')
  ElMessage.success('已通过'); load()
}

async function onReject(row) {
  const { value } = await ElMessageBox.prompt('驳回理由（必填）', '驳回',
    { inputValidator: v => !!v?.trim() || '必须填写理由' })
  await updateTaskStatus(row.id, 'rejected', value)
  ElMessage.success('已驳回'); load()
}

async function onSetStatus(row) {
  const { value } = await ElMessageBox.prompt(
    '状态：pending / doing / submitted / rejected / done', '修改状态',
    { inputValue: row.status })
  await updateTaskStatus(row.id, value)
  ElMessage.success('已更新'); load()
}

async function onDelete(row) {
  await ElMessageBox.confirm(`删除任务「${row.title}」？`, '确认', { type: 'warning' })
  await deleteTask(row.id)
  ElMessage.success('已删除'); load()
}

onMounted(load)
</script>

<style scoped>
.head { display: flex; justify-content: space-between; align-items: center; }
.dim { color: #909399; font-size: 12px; }
</style>
