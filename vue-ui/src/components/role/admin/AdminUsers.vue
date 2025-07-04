
<script setup>
import {onMounted, ref, reactive} from 'vue'
import {getDeletedUsers, getUsersList, recoverUser} from "@/api/admin/admin.js";
import UserRoleMap from "@/utils/userrole.js";
import { deleteUser } from "@/api/user/userinfo.js";
import {ElMessage, ElMessageBox} from "element-plus";
import { 
  Search, 
  Refresh, 
  Delete, 
  Edit, 
  Switch, 
  RefreshRight 
} from '@element-plus/icons-vue'

// 响应式数据
const tableData = ref([])
const loading = ref(false)
const recoverLoading = ref(false)
const editLoading = ref(false)

const tableSetting = ref({
  username: '',
  total: 0,
  pageSize: 10,
  currentPage: 1,
})

const deletedUserList = ref([])
const dialogDeletedUserVisible = ref(false)
const editDialogVisible = ref(false)
const editFormRef = ref()

// 编辑表单数据
const editForm = reactive({
  id: '',
  userAccount: '',
  username: '',
  userRole: 1,
  gender: 1,
  phone: '',
  email: ''
})

// 编辑表单验证规则
const editRules = {
  username: [
    { required: true, message: '请输入用户名称', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名称长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}



const handleEdit = (row) => {
  Object.assign(editForm, {
    id: row.id,
    userAccount: row.userAccount,
    username: row.username,
    userRole: row.userRole,
    gender: row.gender,
    phone: row.phone,
    email: row.email
  })
  editDialogVisible.value = true
}

const handleSaveEdit = async () => {
  if (!editFormRef.value) return
  
  try {
    await editFormRef.value.validate()
    editLoading.value = true
    
    // TODO: 实现编辑用户接口
    // const res = await updateUser(editForm)
    // if (res.data.code === 0) {
    //   ElMessage.success('编辑成功')
    //   editDialogVisible.value = false
    //   await getUserList()
    // } else {
    //   ElMessage.error(res.data.message || '编辑失败')
    // }
    
    // 临时模拟成功
    setTimeout(() => {
      ElMessage.success('编辑成功')
      editDialogVisible.value = false
      getUserList()
      editLoading.value = false
    }, 1000)
    
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

const handleToggleStatus = async (row) => {
  // 确保状态值为数字类型
  const numStatus = Number(row.isDelete)
  const action = numStatus === 0 ? '封禁' : '解封'
  
  ElMessageBox.confirm(
    `确定要${action}用户 "${row.username}" 吗?`,
    `${action}确认`,
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      // TODO: 实现切换用户状态接口
      // const res = await toggleUserStatus(row.id)
      // if (res.data.code === 0) {
      //   ElMessage.success(`${action}成功`)
      //   await getUserList()
      // } else {
      //   ElMessage.error(res.data.message || `${action}失败`)
      // }
      
      // 临时模拟成功
      ElMessage.success(`${action}成功`)
      await getUserList()
    } catch (error) {
      ElMessage.error(`${action}请求失败`)
    }
  }).catch(() => {
    ElMessage.info(`已取消${action}`)
  })
}

const handleCloseDeletedDialog = () => {
  dialogDeletedUserVisible.value = false
}

const handleCloseEditDialog = () => {
  editDialogVisible.value = false
  editFormRef.value?.clearValidate()
}

const getRoleTagType = (role) => {
  switch (role) {
    case 0: return 'danger'  // 管理员
    case 1: return 'primary' // 学生
    case 2: return 'success' // 教师
    default: return 'info'
  }
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  // 确保状态值为数字类型
  const numStatus = Number(status)
  // isDelete: 0=正常, 1=封禁
  return numStatus === 0 ? 'success' : 'danger'
}

// 获取状态文本
const getStatusText = (status) => {
  // 确保状态值为数字类型
  const numStatus = Number(status)
  // isDelete: 0=正常, 1=封禁
  return numStatus === 0 ? '正常' : '封禁'
}

// 获取切换按钮类型
const getToggleButtonType = (status) => {
  // 确保状态值为数字类型
  const numStatus = Number(status)
  // isDelete: 0=正常, 1=封禁
  return numStatus === 0 ? 'warning' : 'success'
}

// 获取切换按钮文本
const getToggleButtonText = (status) => {
  // 确保状态值为数字类型
  const numStatus = Number(status)
  // isDelete: 0=正常, 1=封禁
  return numStatus === 0 ? '封禁' : '解封'
}

onMounted(() => {
  getUserList()
})
</script>

<template>
  <div class="admin-users-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>用户管理</h2>
      <p>管理系统中的所有用户信息</p>
    </div>

    <!-- 搜索和操作区域 -->
    <el-card class="search-card">
      <div class="search-section">
        <el-form :model="tableSetting" label-width="80px" :inline="true">
          <el-form-item label="用户名">
            <el-input
              v-model="tableSetting.username"
              placeholder="请输入用户名"
              clearable
              style="width: 200px"
              @keyup.enter="getUserList"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="getUserList" :loading="loading">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="resetSearch">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="action-buttons">
          <el-button type="info" @click="getDeletedUser">
            <el-icon><Delete /></el-icon>
            查看已删除用户
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 用户表格 -->
    <el-card class="table-card">
      <div class="table-header">
        <div class="table-title">
          <h3>用户列表</h3>
          <el-tag type="info">共 {{ tableSetting.total }} 条记录</el-tag>
        </div>
      </div>
      
      <el-table 
        :data="tableData" 
        border 
        style="width: 100%"
        v-loading="loading"
        empty-text="暂无数据"
        :header-cell-style="{ backgroundColor: '#f5f7fa' }"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column property="id" label="ID" width="80" />
        <el-table-column property="userAccount" label="用户账户" width="120" />
        <el-table-column property="username" label="用户名称" width="120" />
        <el-table-column property="userRole" label="用户角色" width="100">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.userRole)">
              {{ UserRoleMap[row.userRole] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column property="gender" label="性别" width="80">
          <template #default="{ row }">
            <el-tag :type="row.gender === 1 ? 'primary' : 'success'">
              {{ row.gender === 1 ? '男' : '女' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column property="phone" label="手机号" width="120" />
        <el-table-column property="email" label="邮箱" width="180" />
        <el-table-column property="isDelete" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.isDelete)">
              {{ getStatusText(row.isDelete) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              size="small" 
              type="primary" 
              @click="handleEdit(row)"
              v-if="row.userRole !== 0"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button 
              size="small" 
              :type="getToggleButtonType(row.isDelete)"
              @click="handleToggleStatus(row)"
              v-if="row.userRole !== 0"
            >
              <el-icon><Switch /></el-icon>
              {{ getToggleButtonText(row.isDelete) }}
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="handleDelete(row)"
              v-if="row.userRole !== 0"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="tableSetting.currentPage"
          v-model:page-size="tableSetting.pageSize"
          :total="tableSetting.total"
          :page-sizes="[10, 20, 50, 100]"
          :size="'default'"
          :disabled="loading"
          :background="true"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 已删除用户对话框 -->
    <el-dialog 
      v-model="dialogDeletedUserVisible" 
      title="已删除的用户" 
      width="80%"
      :before-close="handleCloseDeletedDialog"
    >
      <el-table :data="deletedUserList" border style="width: 100%">
        <el-table-column type="selection" width="55" />
        <el-table-column property="id" label="ID" width="80" />
        <el-table-column property="userAccount" label="用户账户" width="120" />
        <el-table-column property="username" label="用户名称" width="120" />
        <el-table-column property="userRole" label="用户角色" width="100">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.userRole)">
              {{ UserRoleMap[row.userRole] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column property="gender" label="性别" width="80">
          <template #default="{ row }">
            <el-tag :type="row.gender === 1 ? 'primary' : 'success'">
              {{ row.gender === 1 ? '男' : '女' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column property="phone" label="手机号" width="120" />
        <el-table-column property="email" label="邮箱" width="180" />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button 
              size="small" 
              type="success" 
              @click="wakeUp(row.id)"
              :loading="recoverLoading"
            >
              <el-icon><RefreshRight /></el-icon>
              恢复
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 编辑用户对话框 -->
    <el-dialog 
      v-model="editDialogVisible" 
      title="编辑用户信息" 
      width="600px"
      :before-close="handleCloseEditDialog"
    >
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="100px">
        <el-form-item label="用户账户" prop="userAccount">
          <el-input v-model="editForm.userAccount" disabled />
        </el-form-item>
        <el-form-item label="用户名称" prop="username">
          <el-input v-model="editForm.username" />
        </el-form-item>
        <el-form-item label="用户角色" prop="userRole">
          <el-select v-model="editForm.userRole" placeholder="请选择角色">
            <el-option label="学生" :value="1" />
            <el-option label="教师" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="editForm.gender">
            <el-radio :value="1">男</el-radio>
            <el-radio :value="0">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="editForm.phone" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveEdit" :loading="editLoading">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.admin-users-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
}

.page-header p {
  margin: 8px 0 0 0;
  color: #909399;
  font-size: 14px;
}

.search-card {
  margin-bottom: 20px;
}

.search-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.table-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.table-title h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-users-container {
    padding: 10px;
  }
  
  .search-section {
    flex-direction: column;
    gap: 16px;
  }
  
  .action-buttons {
    width: 100%;
    justify-content: center;
  }
  
  .table-header {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
