<template>
  <el-card shadow="never">
    <template #header>
      <div class="head">
        <span>用户管理（{{ total }}）</span>
        <div style="display:flex;gap:8px">
          <el-input v-model="keyword" size="small" placeholder="工号/姓名"
                    style="width:150px" clearable @keyup.enter="load" />
          <el-button size="small" @click="load">搜索</el-button>
          <el-button type="success" size="small" @click="csvDialog = true">批量导入 CSV</el-button>
          <el-button type="primary" size="small" @click="openCreate">新增队员</el-button>
        </div>
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

    <!-- ★ CSV 批量导入 -->
    <el-dialog v-model="csvDialog" title="批量导入 CSV" width="520px">
      <el-alert type="info" :closable="false" style="margin-bottom:12px">
        <div style="font-size:13px;line-height:1.8">
          CSV 格式（第一行表头）：<br>
          <code>工号,姓名,组别,密码,角色</code><br>
          示例：<code>2024001,张三,视觉,123456,member</code><br>
          · 角色可填 member / admin，默认 member<br>
          · 密码留空默认 123456<br>
          · 已存在的工号会跳过
        </div>
      </el-alert>
      <el-upload :auto-upload="false" :show-file-list="true"
                 accept=".csv" :on-change="onCsvChange" :limit="1">
        <el-button>选择 CSV 文件</el-button>
      </el-upload>
      <template #footer>
        <el-button @click="csvDialog = false">取消</el-button>
        <el-button type="primary" :loading="importing" @click="onImport">开始导入</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listUsers, createUser, updateUser, resetPassword, deleteUser, importUsers } from '../../api/users'

const users = ref([])
const loading = ref(false)
const saving = ref(false)
const dialog = ref(false)
const editing = ref(false)
const editId = ref(null)
const groups = ['视觉', '机械', '电控', '运营', '管理']
const csvDialog = ref(false)
const importing = ref(false)
const csvFile = ref(null)

function onCsvChange(file) { csvFile.value = file.raw }

async function onImport() {
  if (!csvFile.value) { ElMessage.warning('请先选文件'); return }
  importing.value = true
  try {
    const res = await importUsers(csvFile.value)
    ElMessage.success(`导入完成：新增 ${res.created}，跳过 ${res.skipped}` +
                      (res.errors.length ? `，错误 ${res.errors.length}` : ''))
    if (res.errors.length) console.warn('导入错误:', res.errors)
    csvDialog.value = false
    csvFile.value = null
    load()
  } finally { importing.value = false }
}

const form = reactive({
  emp_no: '', name: '', group_name: '视觉', password: '', role: 'member',
})

function fmt(d) { return d ? d.replace('T', ' ').slice(0, 16) : '—' }

const total = ref(0)
const keyword = ref('')

async function load() {
  loading.value = true
  try {
    const res = await listUsers({ page: 1, size: 500, q: keyword.value })
    users.value = res.items
    total.value = res.total
  } finally { loading.value = false }
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
