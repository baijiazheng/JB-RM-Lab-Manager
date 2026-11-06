<template>
  <div v-loading="loading">
    <el-page-header @back="$router.back()" :content="task.title || '任务详情'" />

    <el-card v-if="task.id" shadow="never" style="margin-top:16px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(task.status)" size="small">
            {{ statusText(task.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="截止时间">{{ fmt(task.deadline) }}</el-descriptions-item>
        <el-descriptions-item label="发布人">{{ task.creator_name }}</el-descriptions-item>
        <el-descriptions-item label="接收人">{{ task.assignee_name }}</el-descriptions-item>
        <el-descriptions-item label="任务描述" :span="2">
          <pre class="pre">{{ task.description || '—' }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="要求" :span="2">
          <pre class="pre">{{ task.requirement || '—' }}</pre>
        </el-descriptions-item>
        <el-descriptions-item v-if="task.reject_reason" label="驳回理由" :span="2">
          <span style="color:#f56c6c">{{ task.reject_reason }}</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- ★ 提交区（仅队员本人 + 未完成时） -->
    <el-card v-if="canSubmit" shadow="never" style="margin-top:16px">
      <template #header>提交任务</template>
      <el-input v-model="content" type="textarea" :rows="4"
                placeholder="填写你的提交内容..." />
      <div style="margin-top:12px">
        <el-upload :auto-upload="false" :on-change="onFileChange"
                   :file-list="fileList" multiple>
          <el-button size="small">选择附件</el-button>
          <template #tip>
            <span class="tip">支持图片/文档/压缩包，单个 ≤50MB</span>
          </template>
        </el-upload>
      </div>
      <el-button type="primary" style="margin-top:12px"
                 :loading="submitting" @click="onSubmit">提交</el-button>
    </el-card>

    <!-- 历史提交 -->
    <el-card shadow="never" style="margin-top:16px">
      <template #header>提交记录（{{ submissions.length }}）</template>
      <el-empty v-if="!submissions.length" description="还没有提交" />
      <div v-for="s in submissions" :key="s.id" class="sub-item">
        <div class="sub-head">
          <span>#{{ s.id }} · {{ s.user_name }} · {{ fmt(s.created_at) }}</span>
        </div>
        <pre class="pre">{{ s.content || '（无文字内容）' }}</pre>
        <div v-if="s.files?.length" class="files">
          <el-link v-for="f in s.files" :key="f.id" type="primary"
                   :href="downloadUrl(f.id)" target="_blank">
            📎 {{ f.original_name }}
          </el-link>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { taskDetail, submitTask, taskSubmissions, uploadFile, downloadUrl } from '../api/tasks'
import { useUserStore } from '../stores/user'

const route = useRoute()
const store = useUserStore()
const task = ref({})
const submissions = ref([])
const content = ref('')
const fileList = ref([])
const loading = ref(false)
const submitting = ref(false)

const canSubmit = computed(() =>
  task.value.id && task.value.assignee_id === store.user?.id &&
  !['done', 'submitted'].includes(task.value.status))

function statusType(s) {
  return { pending: 'info', doing: 'primary', submitted: 'warning',
           rejected: 'danger', done: 'success' }[s] || 'info'
}
function statusText(s) {
  return { pending: '未开始', doing: '进行中', submitted: '已提交',
           rejected: '已驳回', done: '已完成' }[s] || s
}
function fmt(d) { return d ? d.replace('T', ' ').slice(0, 16) : '—' }

function onFileChange(file, list) { fileList.value = list }

async function load() {
  loading.value = true
  try {
    task.value = await taskDetail(route.params.id)
    submissions.value = await taskSubmissions(route.params.id)
  } finally { loading.value = false }
}

async function onSubmit() {
  if (!content.value.trim() && !fileList.value.length) {
    ElMessage.warning('请填写内容或上传附件')
    return
  }
  submitting.value = true
  try {
    const { submission_id } = await submitTask(route.params.id, content.value)
    for (const f of fileList.value) {
      await uploadFile(submission_id, f.raw)
    }
    ElMessage.success('提交成功')
    content.value = ''
    fileList.value = []
    await load()
  } finally { submitting.value = false }
}

onMounted(load)
</script>

<style scoped>
.pre {
  margin: 0; white-space: pre-wrap; word-break: break-word;
  font-family: inherit; color: #606266;
}
.tip { color: #909399; font-size: 12px; margin-left: 8px; }
.sub-item { padding: 12px 0; border-bottom: 1px solid #ebeef5; }
.sub-item:last-child { border-bottom: none; }
.sub-head { color: #909399; font-size: 13px; margin-bottom: 6px; }
.files { margin-top: 8px; display: flex; gap: 16px; flex-wrap: wrap; }
</style>
