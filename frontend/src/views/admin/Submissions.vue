<template>
  <el-card shadow="never">
    <template #header>
      <div class="head">
        <span>全部提交记录（{{ list.length }}）</span>
        <el-button size="small" @click="load">刷新</el-button>
      </div>
    </template>

    <el-table :data="list" v-loading="loading" empty-text="暂无提交">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column label="任务" min-width="160">
        <template #default="{ row }">{{ row.task_title || `#${row.task_id}` }}</template>
      </el-table-column>
      <el-table-column prop="user_name" label="提交人" width="110" />
      <el-table-column label="内容" min-width="240">
        <template #default="{ row }">
          <div class="ellipsis">{{ row.content || '（无文字）' }}</div>
        </template>
      </el-table-column>
      <el-table-column label="附件" width="160">
        <template #default="{ row }">
          <el-link v-for="f in row.files" :key="f.id" type="primary"
                   :href="downloadUrl(f.id)" target="_blank" class="file-link">
            📎 {{ f.original_name }}
          </el-link>
          <span v-if="!row.files?.length" class="dim">—</span>
        </template>
      </el-table-column>
      <el-table-column label="时间" width="160">
        <template #default="{ row }">{{ fmt(row.created_at) }}</template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { allSubmissions, downloadUrl } from '../../api/tasks'

const list = ref([])
const loading = ref(false)

function fmt(d) { return d ? d.replace('T', ' ').slice(0, 16) : '—' }

async function load() {
  loading.value = true
  try { list.value = await allSubmissions() } finally { loading.value = false }
}

onMounted(load)
</script>

<style scoped>
.head { display: flex; justify-content: space-between; align-items: center; }
.dim { color: #909399; }
.ellipsis { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.file-link { display: block; }
</style>
