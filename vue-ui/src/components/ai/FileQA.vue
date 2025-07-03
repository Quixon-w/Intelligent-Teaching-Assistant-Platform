<template>
  <div class="file-qa-container">
    <div class="placeholder-content">
      <div class="placeholder-icon">
        <el-icon size="80" color="#c0c4cc">
          <DocumentAdd />
        </el-icon>
      </div>
      <h3>文件提问功能</h3>
      <p>该功能正在开发中，敬请期待...</p>
      <div class="feature-list">
        <div class="feature-item">
          <el-icon color="#67c23a"><Check /></el-icon>
          <span>上传文档文件（PDF、Word、TXT等）</span>
        </div>
        <div class="feature-item">
          <el-icon color="#67c23a"><Check /></el-icon>
          <span>智能文档解析和知识提取</span>
        </div>
        <div class="feature-item">
          <el-icon color="#67c23a"><Check /></el-icon>
          <span>基于文档内容的智能问答</span>
        </div>
        <div class="feature-item">
          <el-icon color="#67c23a"><Check /></el-icon>
          <span>多文档关联搜索</span>
        </div>
      </div>
      <el-button type="primary" disabled>
        <el-icon><Clock /></el-icon>
        即将推出
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { DocumentAdd, Check, Clock } from '@element-plus/icons-vue'
</script>

<style scoped>
.file-qa-container {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
}

.placeholder-content {
  text-align: center;
  max-width: 400px;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.placeholder-icon {
  margin-bottom: 24px;
}

h3 {
  margin: 0 0 16px 0;
  color: #1f2937;
  font-size: 20px;
  font-weight: 600;
}

p {
  margin: 0 0 32px 0;
  color: #6b7280;
  font-size: 16px;
}

.feature-list {
  text-align: left;
  margin-bottom: 32px;
}

.feature-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  padding: 8px 0;
}

.feature-item span {
  margin-left: 12px;
  color: #4b5563;
  font-size: 14px;
}

.el-button {
  font-size: 16px;
  padding: 12px 24px;
  border-radius: 8px;
}
</style> 