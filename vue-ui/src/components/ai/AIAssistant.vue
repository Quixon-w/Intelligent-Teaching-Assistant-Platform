<template>
  <div class="ai-assistant-container">
    <div class="ai-header">
      <h2>智能助手</h2>
      <p>与AI助手进行智能对话或上传文件进行问答</p>
    </div>
    
    <el-tabs v-model="activeTab" class="ai-tabs">
      <el-tab-pane label="AI对话" name="chat">
        <AIChat />
      </el-tab-pane>
      <el-tab-pane label="文件提问" name="file-qa">
        <FileQA />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AIChat from './AIChat.vue'
import FileQA from './FileQA.vue'

// 响应式数据
const activeTab = ref('chat')
</script>

<style scoped>
.ai-assistant-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.ai-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.ai-header h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
  font-weight: 600;
}

.ai-header p {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}

.ai-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ai-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
}

.ai-tabs :deep(.el-tab-pane) {
  height: 100%;
  overflow: hidden;
}

.ai-tabs :deep(.el-tabs__header) {
  margin: 0;
  background: white;
  border-bottom: 1px solid #e4e7ed;
}

.ai-tabs :deep(.el-tabs__nav-wrap) {
  padding: 0 20px;
}

.ai-tabs :deep(.el-tabs__item) {
  padding: 15px 20px;
  font-size: 16px;
  font-weight: 500;
}

.ai-tabs :deep(.el-tabs__item.is-active) {
  color: #667eea;
}

.ai-tabs :deep(.el-tabs__active-bar) {
  background-color: #667eea;
}
</style> 