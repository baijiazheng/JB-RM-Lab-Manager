<template>
  <el-card shadow="never">
    <template #header>
      <div class="head">
        <span>用户管理（{{ users.length }}）</span>
        <el-button type="primary" size="small" @click="openCreate">新增队员</el-button>
      </div>
    </template>

    <el-table :data="users" v-loading="loading" empty-text="暂无用户">
      <el-table-column prop="emp_no" label="工号" width="120" />
      <el-table-column prop="name" label="姓名" width="120" />
      <el-table-column prop="group_name" label="组别" width="100" />
      <el-table-column label="角色" width="100">
        <template #default="{ row }">
          <el-tag :type="row.role === 'admin' ? 'danger' : 'success'" size="small">
            {{ row.role === 'admin' ? '管理员' : '队员' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="加入时间" width="170">
        <template #default="{ row }">{{ fmt(row.joined_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" min-width="220">
        <template #default="{ row }">
          <el-button size="small" link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" link type="warning" @click="onReset(row)">重置密码</el-button>
          <el-button size="small" link type="danger" @click="onDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialog" :title="editing ? '编辑用户' : '新增队员'" width="460px">
      <el-form :model="form" label-width="70px">
        <el-form-item label="工号">
          <el-input v-model="form.emp_no" :disabled="editing" />
        </el-form-item>
        <el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="组别">
          <el-select v-model="form.group_name" style="width:100%" allow-create filterable>
            <el-option v-for="g in groups" :key="g" :label="g" :value="g" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!editing" label="密码">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="角色">
          <el-radio-group v-model="form.role">
            <el-radio value="member">队员</el-radio>
            <el-radio value="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listUsers, createUser, updateUser, resetPassword, deleteUser } from '../../api/users'

const users = ref([])
const loading = ref(false)
const saving = ref(false)
const dialog = ref(false)
const editing = ref(false)
const editId = ref(null)
const groups = ['视觉', '机械', '电控', '运营', '管理']

const form = reactive({
  emp_no: '', name: '', group_name: '视觉', password: '', role: 'member',
})

function fmt(d) { return d ? d.replace('T', ' ').slice(0, 16) : '—' }

async function load() {
  loading.value = true
  try { users.value = await listUsers() } finally { loading.value = false }
}

function openCreate() {
  editing.value = false
  Object.assign(form, { emp_no: '', name: '', group_name: '视觉', password: '', role: 'member' })
  dialog.value = true
}
function openEdit(row) {
  editing.value = true
  editId.value = row.id
  Object.assign(form, { emp_no: row.emp_no, name: row.name,
                         group_name: row.group_name, password: '', role: row.role })
  dialog.value = true
}

async function onSave() {
  saving.value = true
  try {
    if (editing.value) {
      await updateUser(editId.value, {
        name: form.name, group_name: form.group_name, role: form.role })
    } else {
      await createUser({ ...form })
    }
    ElMessage.success('已保存')
    dialog.value = false
    load()
  } finally { saving.value = false }
}

async function onReset(row) {
  const { value } = await ElMessageBox.prompt(
    `为 ${row.name} 设置新密码`, '重置密码',
    { inputPlaceholder: '至少 6 位', inputValidator: v => v?.length >= 6 || '至少 6 位' })
  await resetPassword(row.id, value)
  ElMessage.success('密码已重置')
}

async function onDelete(row) {
  await ElMessageBox.confirm(`确定删除 ${row.name}？`, '确认', { type: 'warning' })
  await deleteUser(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.head { display: flex; justify-content: space-between; align-items: center; }
</style>
