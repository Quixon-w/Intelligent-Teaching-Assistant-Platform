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
          <el-form-item label="用户账号">
            <el-input
              v-model="tableSetting.userAccount"
              placeholder="请输入用户账号"
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
          <el-button type="warning" @click="getBannedUser">
            <el-icon><Lock /></el-icon>
            查看已封禁用户
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 用户表格 -->
    <el-card class="table-card">
      <div class="table-header">
        <div class="table-title">
          <h3>用户列表</h3>
          <div class="table-info">
            <el-tag type="info">共 {{ tableSetting.total }} 条记录</el-tag>
            <el-tag v-if="bannedCount > 0" type="warning" style="margin-left: 8px">
              封禁用户: {{ bannedCount }} 个
            </el-tag>
            <el-tag v-if="tableSetting.username" type="success" style="margin-left: 8px">
              用户名: {{ tableSetting.username }}
            </el-tag>
            <el-tag v-if="tableSetting.userAccount" type="success" style="margin-left: 8px">
              用户账号: {{ tableSetting.userAccount }}
            </el-tag>
          </div>
        </div>
      </div>
      
      <el-table 
        :data="tableData" 
        border 
        style="width: 100%"
        v-loading="loading"
        empty-text="暂无数据"
        :header-cell-style="{ backgroundColor: '#f5f7fa' }"
        :row-style="getRowStyle"
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
               type="warning" 
               @click="handleResetPassword(row)"
               v-if="row.userRole !== 2"
               :loading="actionLoading[`reset_${row.id}`]"
             >
               重置密码
             </el-button>
             <el-button 
               size="small" 
               :type="getToggleButtonType(row.isDelete)"
               @click="handleToggleStatus(row)"
               v-if="row.userRole !== 2"
               :loading="actionLoading[`toggle_${row.id}`]"
             >
               <el-icon v-if="!actionLoading[`toggle_${row.id}`]"><Switch /></el-icon>
               {{ getToggleButtonText(row.isDelete) }}
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

    <!-- 已封禁用户对话框 -->
    <el-dialog 
      v-model="dialogDeletedUserVisible" 
      title="已封禁的用户" 
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
               @click="handleUnban(row)"
               :loading="recoverLoading"
             >
               <el-icon><RefreshRight /></el-icon>
               解封
             </el-button>
           </template>
         </el-table-column>
      </el-table>
    </el-dialog>

    
  </div>
</template>

<script setup>
import { onMounted, ref, reactive, computed } from 'vue'
import { getUsersList, resetUserPassword, deleteUser as banUser, recoverUser, getDeletedUsers } from "@/api/admin.js"
import UserRoleMap from "@/utils/userrole.js"
import { ElMessage, ElMessageBox } from "element-plus"
import { 
  Search, 
  Refresh, 
  Lock, 
  Switch, 
  RefreshRight 
} from '@element-plus/icons-vue'

// 响应式数据
const tableData = ref([])
const loading = ref(false)
const recoverLoading = ref(false)
const actionLoading = ref({})

const tableSetting = ref({
  username: '', // 用户名搜索
  userAccount: '', // 用户账号搜索
  total: 0,
  pageSize: 10,
  currentPage: 1,
})

const deletedUserList = ref([])
const dialogDeletedUserVisible = ref(false)

// 计算属性
const bannedCount = computed(() => {
  return tableData.value.filter(user => Number(user.isDelete) === 1).length
})

// 方法
const getUserList = async () => {
  loading.value = true
  try {
    console.log('开始获取用户列表，参数:', {
      currentPage: tableSetting.value.currentPage,
      pageSize: tableSetting.value.pageSize,
      username: tableSetting.value.username,
      userAccount: tableSetting.value.userAccount
    })
    
    const res = await getUsersList(
      tableSetting.value.currentPage,
      tableSetting.value.pageSize,
      tableSetting.value.username,
      tableSetting.value.userAccount
    )
    
    console.log('API响应:', res)
    
    if (res && res.code === 0) {
      tableData.value = res.data.records || []
      tableSetting.value.total = res.data.total || 0
      console.log('用户列表加载成功:', {
        records: res.data.records,
        total: res.data.total
      })
      ElMessage.success(`成功加载 ${res.data.records?.length || 0} 条用户数据`)
    } else {
      const errorMsg = res?.message || res?.description || '获取用户列表失败'
      console.error('API返回错误:', errorMsg)
      ElMessage.error(errorMsg)
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('网络请求失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  tableSetting.value.username = ''
  tableSetting.value.userAccount = ''
  tableSetting.value.currentPage = 1
  getUserList()
}

const handleSizeChange = (size) => {
  tableSetting.value.pageSize = size
  getUserList()
}

const handleCurrentChange = (page) => {
  tableSetting.value.currentPage = page
  getUserList()
}

const getBannedUser = async () => {
  try {
    loading.value = true
    console.log('开始获取已封禁用户列表...')
    
    const res = await getDeletedUsers()
    console.log('已封禁用户API响应:', res)
    
    // 处理不同的数据结构
    let bannedUsers = []
    if (res && res.code === 0) {
      // 标准响应格式
      bannedUsers = res.data || []
    } else if (Array.isArray(res)) {
      // 直接返回数组格式
      bannedUsers = res
    } else if (res && res.data && Array.isArray(res.data)) {
      // 嵌套data格式
      bannedUsers = res.data
    }
    
    console.log('已封禁用户数据:', bannedUsers)
    
    deletedUserList.value = bannedUsers
    dialogDeletedUserVisible.value = true
    
    if (bannedUsers.length > 0) {
      ElMessage.success(`找到 ${bannedUsers.length} 个已封禁用户`)
    } else {
      ElMessage.info('当前没有已封禁的用户')
    }
  } catch (error) {
    console.error('获取已封禁用户失败:', error)
    ElMessage.error('获取已封禁用户失败')
  } finally {
    loading.value = false
  }
}

const handleUnban = async (row) => {
  recoverLoading.value = true
  try {
    const res = await recoverUser(row.id)
    if (res && res.code === 0) {
      ElMessage.success('解封成功')
      // 刷新已封禁用户列表
      await getBannedUser()
      // 刷新主用户列表
      await getUserList()
    } else {
      ElMessage.error(res?.message || '解封失败')
    }
  } catch (error) {
    console.error('解封请求失败:', error)
    ElMessage.error('解封请求失败')
  } finally {
    recoverLoading.value = false
  }
}



const handleResetPassword = async (row) => {
  ElMessageBox.confirm(
    `确定要重置用户 "${row.username}" 的密码吗？密码将被重置为：12345678`,
    '重置密码确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    const loadingKey = `reset_${row.id}`
    actionLoading.value[loadingKey] = true
    
    try {
      const res = await resetUserPassword(row.id)
      if (res.code === 0) {
        ElMessage.success('密码重置成功，已将密码重置为 12345678')
      } else {
        ElMessage.error(res.message || '密码重置失败')
      }
    } catch (error) {
      console.error('密码重置请求失败:', error)
      ElMessage.error('密码重置请求失败')
    } finally {
      actionLoading.value[loadingKey] = false
    }
  }).catch(() => {
    ElMessage.info('已取消重置密码')
  })
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
    const loadingKey = `toggle_${row.id}`
    actionLoading.value[loadingKey] = true
    
    try {
      let res
      if (numStatus === 0) {
        // 当前是正常状态，执行封禁
        res = await banUser(row.id)
      } else {
        // 当前是封禁状态，执行解封
        res = await recoverUser(row.id)
      }
      
      if (res && res.code === 0) {
        ElMessage.success(`${action}成功`)
        // 刷新用户列表以更新状态
        await getUserList()
      } else {
        ElMessage.error(res?.message || `${action}失败`)
      }
    } catch (error) {
      console.error(`${action}请求失败:`, error)
      ElMessage.error(`${action}请求失败`)
    } finally {
      actionLoading.value[loadingKey] = false
    }
  }).catch(() => {
    ElMessage.info(`已取消${action}`)
  })
}

const handleCloseDeletedDialog = () => {
  dialogDeletedUserVisible.value = false
}

const getRoleTagType = (role) => {
  switch (role) {
    case 0: return 'primary' // 学生
    case 1: return 'success' // 教师
    case 2: return 'danger'  // 管理员
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

const getRowStyle = ({ row }) => {
  // 为封禁用户设置不同的行样式
  if (Number(row.isDelete) === 1) {
    return {
      backgroundColor: '#fef0f0',
      color: '#909399'
    }
  }
  return {}
}

onMounted(() => {
  getUserList()
})
</script>

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
  justify-content: space-between;
  width: 100%;
}

.table-title h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
}

.table-info {
  display: flex;
  align-items: center;
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

/* 封禁用户行样式 */
:deep(.el-table__row.banned-user) {
  background-color: #fef0f0 !important;
}

:deep(.el-table__row.banned-user:hover) {
  background-color: #fde2e2 !important;
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