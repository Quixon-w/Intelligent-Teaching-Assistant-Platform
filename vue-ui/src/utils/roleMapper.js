// 角色映射工具
// 后端返回的数字角色 -> 前端使用的字符串角色

export const ROLE_MAP = {
  0: 'student',    // 学生
  1: 'teacher',    // 教师
  2: 'admin'       // 管理员
}

export const ROLE_REVERSE_MAP = {
  'student': 0,
  'teacher': 1,
  'admin': 2
}

// 数字角色转字符串角色
export const mapRoleToText = (role) => {
  if (typeof role === 'string') {
    // 如果已经是字符串，直接返回
    return role
  }
  
  const roleText = ROLE_MAP[role]
  if (roleText) {
    return roleText
  }
  
  console.warn(`未知的角色值: ${role}，默认返回 'student'`)
  return 'student'
}

// 字符串角色转数字角色
export const mapTextToRole = (roleText) => {
  if (typeof roleText === 'number') {
    // 如果已经是数字，直接返回
    return roleText
  }
  
  const role = ROLE_REVERSE_MAP[roleText]
  if (role !== undefined) {
    return role
  }
  
  console.warn(`未知的角色文本: ${roleText}，默认返回 0`)
  return 0
}

// 获取角色显示文本
export const getRoleDisplayText = (role) => {
  const roleText = mapRoleToText(role)
  const displayMap = {
    'student': '学生',
    'teacher': '教师',
    'admin': '管理员'
  }
  return displayMap[roleText] || '未知角色'
}

// 获取角色中心名称
export const getRoleCenterName = (role) => {
  const roleText = mapRoleToText(role)
  const centerMap = {
    'student': '学习中心',
    'teacher': '教师中心',
    'admin': '管理员中心'
  }
  return centerMap[roleText] || '平台'
} 