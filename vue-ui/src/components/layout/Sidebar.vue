<template>
  <el-aside class="sidebar" width="250px">
    <div class="sidebar-header">
      <h2 class="platform-title">智能教学辅助平台</h2>
    </div>
    
    <el-scrollbar class="sidebar-content">
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        @select="handleMenuSelect"
      >
        <!-- 管理员菜单 -->
        <template v-if="userRole === 'admin'">
          <el-menu-item index="/dashboard/home">
            <el-icon><Monitor /></el-icon>
            <span>系统概览</span>
          </el-menu-item>
          <el-sub-menu index="users">
            <template #title>
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </template>
            <el-menu-item index="/dashboard/admin/users">用户列表</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="courses">
            <template #title>
              <el-icon><Reading /></el-icon>
              <span>课程监控</span>
            </template>
            <el-menu-item index="/dashboard/admin/courses">课程列表</el-menu-item>
          </el-sub-menu>
        </template>
        
        <!-- 教师菜单 -->
        <template v-if="userRole === 'teacher'">
          <el-menu-item index="/dashboard/home">
            <el-icon><Monitor /></el-icon>
            <span>教学中心</span>
          </el-menu-item>
          <el-sub-menu index="courses">
            <template #title>
              <el-icon><Reading /></el-icon>
              <span>课程管理</span>
            </template>
            <el-menu-item index="/dashboard/teacher/home">所有课程</el-menu-item>
            <el-menu-item index="/dashboard/teacher/courses">我的课程</el-menu-item>
          </el-sub-menu>
          <el-menu-item index="/dashboard/teacher/questions">
            <el-icon><EditPen /></el-icon>
            <span>我的题库</span>
          </el-menu-item>
        </template>
        
        <!-- 学生菜单 -->
        <template v-if="userRole === 'student'">
          <el-menu-item index="/dashboard/home">
            <el-icon><Monitor /></el-icon>
            <span>学习中心</span>
          </el-menu-item>
          <el-sub-menu index="courses">
            <template #title>
              <el-icon><Reading /></el-icon>
              <span>课程学习</span>
            </template>
            <el-menu-item index="/dashboard/student/courses">课程选择</el-menu-item>
            <el-menu-item index="/dashboard/student/my-courses">我的课程</el-menu-item>
          </el-sub-menu>
        </template>
        
        <!-- 通用菜单 -->
        <el-sub-menu index="ai">
          <template #title>
            <el-icon><ChatDotRound /></el-icon>
            <span>智能助手</span>
          </template>
          <el-menu-item index="/dashboard/ai-assistant">智能助手</el-menu-item>
          
        </el-sub-menu>
        
        <el-menu-item index="/dashboard/profile">
          <el-icon><UserFilled /></el-icon>
          <span>个人信息</span>
        </el-menu-item>
      </el-menu>
    </el-scrollbar>
    
    <!-- 用户信息区域 -->
    <div class="sidebar-footer">
      <el-dropdown @command="handleUserCommand" placement="top">
        <div class="user-info">
          <el-avatar :size="40" :src="userAvatar" class="user-avatar">
            {{ userAvatar ? '' : userInitials }}
          </el-avatar>
          <div class="user-details">
            <div class="username">{{ username }}</div>
            <div class="user-role">{{ userRoleText }}</div>
          </div>
          <el-icon class="dropdown-icon"><ArrowUp /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><UserFilled /></el-icon>
              个人信息
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>
              设置
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </el-aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { mapRoleToText } from '@/utils/roleMapper'
import { ElMessageBox } from 'element-plus'
import {
  Monitor,
  User,
  Reading,
  Document,
  EditPen,
  ChatDotRound,
  UserFilled,
  ArrowUp,
  Setting,
  SwitchButton
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 计算属性
const userRole = computed(() => {
  const role = authStore.userRole
  return mapRoleToText(role)
})
const activeMenu = computed(() => route.path)

// 用户信息相关计算属性
const username = computed(() => authStore.user?.username || '用户')
const userInitials = computed(() => {
  const name = username.value
  return name.charAt(0).toUpperCase()
})
const userAvatar = computed(() => {
  return authStore.user?.avatar || ''
})
console.log('Sidebar authStore.user:', authStore.user)
console.log('Sidebar userAvatar:', userAvatar.value)
const userRoleText = computed(() => {
  const role = userRole.value
  const roleMap = {
    'admin': '管理员',
    'teacher': '教师',
    'student': '学生'
  }
  return roleMap[role] || role
})

// 方法
const handleMenuSelect = (index) => {
  console.log('Sidebar 菜单点击:', index)
  router.push(index)
}

const handleUserCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/dashboard/profile')
      break
    case 'settings':
      // TODO: 实现设置页面
      break
    case 'logout':
      try {
        await ElMessageBox.confirm(
          '确定要退出登录吗？',
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        await authStore.logout()
        router.push('/login')
      } catch {
        // 用户取消
      }
      break
  }
}


</script>

<style scoped>
.sidebar {
  background-color: #304156;
  height: 100vh;
  border-right: 1px solid #e6e6e6;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #4a5568;
  flex-shrink: 0;
}

.platform-title {
  color: #ffffff;
  font-size: 18px;
  font-weight: bold;
  margin: 0;
  text-align: center;
}

.sidebar-content {
  flex: 1;
  overflow: hidden;
}

.sidebar-menu {
  border: none;
  background-color: transparent;
}

.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) {
  color: #b0c4de;
  background-color: transparent;
}

.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background-color: #263445;
  color: #ffffff;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: #409eff;
  color: #ffffff;
}

.sidebar-menu :deep(.el-icon) {
  margin-right: 8px;
}

/* 用户信息区域样式 */
.sidebar-footer {
  border-top: 1px solid #4a5568;
  padding: 16px;
  background-color: #263445;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.3s;
  color: #b0c4de;
}

.user-info:hover {
  background-color: #1f2d3d;
  color: #ffffff;
}

.user-avatar {
  margin-right: 12px;
  border: 2px solid #4a5568;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.username {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 12px;
  opacity: 0.8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-icon {
  margin-left: 8px;
  font-size: 12px;
  transition: transform 0.3s;
}

.user-info:hover .dropdown-icon {
  transform: rotate(180deg);
}

/* 下拉菜单样式 */
:deep(.el-dropdown-menu) {
  min-width: 140px;
}

:deep(.el-dropdown-menu .el-icon) {
  margin-right: 8px;
}
</style> 