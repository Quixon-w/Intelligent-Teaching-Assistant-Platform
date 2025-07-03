<template>
  <div class="error-demo">
    <h3>错误处理演示</h3>
    <p>这个组件演示了新的错误处理工具如何显示后端的详细错误信息</p>
    
    <el-row :gutter="20">
      <el-col :span="8">
        <el-button @click="showSimpleError" type="danger">简单错误消息</el-button>
      </el-col>
      <el-col :span="8">
        <el-button @click="showDetailedError" type="warning">详细错误消息</el-button>
      </el-col>
      <el-col :span="8">
        <el-button @click="showBackendError" type="info">模拟后端错误</el-button>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { showError, showDetailedError, showSuccess, handleApiResponse } from '@/utils/errorHandler'

// 演示简单错误
const showSimpleError = () => {
  showError('这是一个简单的错误消息')
}

// 演示详细错误（长文本会显示为通知）
const showDetailedErrorDemo = () => {
  const error = {
    message: '系统内部异常',
    description: '数据库连接超时：无法连接到数据库服务器 localhost:3306，请检查数据库服务是否正常运行，网络连接是否稳定，以及用户权限配置是否正确。'
  }
  showDetailedError(error, '操作失败')
}

// 演示模拟后端错误响应
const showBackendError = () => {
  const mockApiResponse = {
    code: 40000,
    message: '请求参数错误',
    description: '课时ID不能为空：在导入题目时必须指定有效的课时ID，请检查当前选择的课时是否正确，或重新选择课时后再试。',
    data: null
  }
  
  handleApiResponse(mockApiResponse, '操作成功', '导入题目失败')
}
</script>

<style scoped>
.error-demo {
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin: 20px 0;
}

.error-demo h3 {
  margin-bottom: 10px;
  color: #303133;
}

.error-demo p {
  margin-bottom: 20px;
  color: #606266;
}
</style> 