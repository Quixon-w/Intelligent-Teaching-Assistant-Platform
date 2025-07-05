<script setup>
import { onMounted, ref, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { commitQuestionHistory, getLessonQuestions } from "@/api/course/lesson.js";
import { ElMessage, ElMessageBox } from 'element-plus';
import { Check, Warning, InfoFilled } from '@element-plus/icons-vue';

const route = useRoute();
const router = useRouter();
const questions = ref([]);
const loading = ref(false);
const submitting = ref(false);

// 只读模式（用于查看测试题）
const isReadOnly = computed(() => {
  return route.query.readonly === 'true';
});

// 计算答题进度
const progress = computed(() => {
  const answered = questions.value.filter(q => q.selectedAnswer).length;
  return {
    answered,
    total: questions.value.length,
    percentage: questions.value.length > 0 ? Math.round((answered / questions.value.length) * 100) : 0
  };
});

// 获取习题列表
const getQuestions = async (lessonId) => {
  loading.value = true;
  
  console.log('开始获取习题列表, lessonId:', lessonId);
  console.log('lessonId 类型:', typeof lessonId);
  
  try {
    if (!lessonId) {
      throw new Error('lessonId 参数为空');
    }
    
    const res = await getLessonQuestions(lessonId);
    console.log('获取习题列表成功:', res);
    
    if (!Array.isArray(res)) {
      throw new Error('返回数据格式错误，期望数组类型');
    }
    
    // 为每个题目添加选中答案字段，并分离选项数据
    questions.value = res.map((question, index) => ({
      questionId: question.questionId,
      questionNumber: index + 1, // 题目序号
      questionKonwledge: question.questionKonwledge,
      questionContent: question.questionContent,
      // 分离选项，不包含正确答案信息
      optionA: question.questionAnswer[1],
      optionB: question.questionAnswer[2], 
      optionC: question.questionAnswer[3],
      optionD: question.questionAnswer[4],
      selectedAnswer: '', // 学生选择的答案
      // 在只读模式下显示正确答案和解析
      correctAnswer: isReadOnly.value ? question.questionAnswer[0] : null,
      questionExplanation: isReadOnly.value ? question.questionExplanation : null,
    }));
    
    if (questions.value.length === 0) {
      ElMessage.warning('该课时暂无测试题目');
    } else {
      ElMessage.success(`成功加载 ${questions.value.length} 道题目`);
    }
  } catch (err) {
    console.error('获取习题失败 - 详细错误信息:', err);
    
    let errorMessage = '获取习题失败';
    if (err.message) {
      errorMessage = err.message;
    } else if (err.response) {
      errorMessage = `服务器错误: ${err.response.status} ${err.response.statusText}`;
      console.error('错误响应数据:', err.response.data);
    } else if (err.request) {
      errorMessage = '网络请求失败，请检查网络连接';
      console.error('请求失败:', err.request);
    }
    
    ElMessage.error(errorMessage);
  } finally {
    loading.value = false;
  }
};

// 提交答案
const commit = async () => {
  // 检查是否所有题目都已答题
  const unanswered = questions.value.filter(q => !q.selectedAnswer);
  if (unanswered.length > 0) {
    const result = await ElMessageBox.confirm(
      `还有 ${unanswered.length} 道题目未答题，确定要提交吗？`,
      '提交确认',
      {
        confirmButtonText: '确定提交',
        cancelButtonText: '继续答题',
        type: 'warning',
      }
    ).catch(() => false);
    
    if (!result) return;
  } else {
    const result = await ElMessageBox.confirm(
      '确定要提交答案吗？提交后将无法修改。',
      '提交确认',
      {
        confirmButtonText: '确定提交',
        cancelButtonText: '取消',
        type: 'info',
      }
    ).catch(() => false);
    
    if (!result) return;
  }

  submitting.value = true;
  try {
    // 按题目顺序准备答案数组
    const orderedQuestions = [...questions.value].sort((a, b) => a.questionNumber - b.questionNumber);
    const answers = orderedQuestions.map(q => q.selectedAnswer || ''); // 未选择的题目用空字符串
    
    console.log('按顺序提交的答案:', answers);
    console.log('题目顺序:', orderedQuestions.map(q => ({ 
      questionNumber: q.questionNumber, 
      questionId: q.questionId, 
      selectedAnswer: q.selectedAnswer 
    })));
    
    // 构造提交所需的数据格式
    const submitData = orderedQuestions.map(q => ({
      selectedAnswer: q.selectedAnswer || '',
      questionId: q.questionId
    }));
    
    const res = await commitQuestionHistory(submitData, route.params.lessonId);
    console.log('提交结果:', res);
    
    if (res.code === 0) {
      ElMessage.success('答案提交成功！');
      // 跳转回课程详情页面
      const courseId = route.params.courseId;
      if (courseId) {
        router.push(`/dashboard/student/courses/${courseId}`);
      } else {
        router.push('/dashboard/student/my-courses');
      }
    } else {
      ElMessage.error(res.message || '提交失败，请重试');
    }
  } catch (err) {
    console.error('提交答案失败:', err);
    ElMessage.error('提交失败，请重试');
  } finally {
    submitting.value = false;
  }
};

onMounted(() => {
  console.log('路由参数:', route.params);
  const lessonId = route.params.lessonId;
  if (lessonId) {
    getQuestions(lessonId);
  } else {
    ElMessage.error('缺少课时ID参数');
  }
});
</script>

<template>
  <div class="student-questions">
    <!-- 答题进度 -->
    <el-card class="progress-card" shadow="never">
      <div class="progress-header">
        <h3>{{ isReadOnly ? '查看测试题与解析' : '课时测试' }}</h3>
        <div class="progress-info">
          <span v-if="!isReadOnly">进度: {{ progress.answered }}/{{ progress.total }}</span>
          <span v-else>题目数量: {{ progress.total }}</span>
          <el-progress 
            v-if="!isReadOnly"
            :percentage="progress.percentage" 
            :color="progress.percentage === 100 ? '#67c23a' : '#409eff'"
            style="margin-left: 16px; flex: 1;"
          />
        </div>
      </div>
    </el-card>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="3" animated />
    </div>

    <!-- 题目列表 -->
    <div v-else class="questions-list">
      <el-card 
        v-for="question in questions" 
        :key="question.questionId"
        class="question-card"
        shadow="hover"
      >
        <template #header>
          <div class="question-header">
            <div class="question-info">
              <el-tag type="primary" size="small">第{{ question.questionNumber }}题</el-tag>
              <el-tag v-if="question.questionKonwledge" type="info" size="small">
                {{ question.questionKonwledge }}
              </el-tag>
            </div>
            <div class="question-status">
              <el-icon v-if="question.selectedAnswer" color="#67c23a" size="18">
                <Check />
              </el-icon>
              <el-icon v-else color="#e6a23c" size="18">
                <Warning />
              </el-icon>
            </div>
          </div>
        </template>

        <div class="question-content">
          <!-- 题目内容 -->
          <div class="question-text-container">
            <p class="question-text">{{ question.questionContent }}</p>
          </div>
          
          <!-- 选项 -->
          <div class="question-options">
            <el-radio-group 
              v-model="question.selectedAnswer" 
              class="options-group"
              size="large"
              :disabled="isReadOnly"
            >
              <el-radio value="A" class="option-item">
                <span class="option-label">A</span>
                <span class="option-text">{{ question.optionA }}</span>
              </el-radio>
              <el-radio value="B" class="option-item">
                <span class="option-label">B</span>
                <span class="option-text">{{ question.optionB }}</span>
              </el-radio>
              <el-radio value="C" class="option-item">
                <span class="option-label">C</span>
                <span class="option-text">{{ question.optionC }}</span>
              </el-radio>
              <el-radio value="D" class="option-item">
                <span class="option-label">D</span>
                <span class="option-text">{{ question.optionD }}</span>
              </el-radio>
            </el-radio-group>
          </div>

          <!-- 只读模式下显示正确答案和解析 -->
          <div v-if="isReadOnly && question.correctAnswer" class="answer-section">
            <el-divider content-position="left">
              <el-tag type="success" size="small">正确答案</el-tag>
            </el-divider>
            <div class="correct-answer">
              <el-icon color="#67c23a"><Check /></el-icon>
              <span class="answer-text">正确答案：{{ question.correctAnswer }}</span>
            </div>
            <div v-if="question.questionExplanation" class="explanation">
              <el-divider content-position="left">
                <el-tag type="info" size="small">答案解析</el-tag>
              </el-divider>
              <div class="explanation-content">
                {{ question.questionExplanation }}
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 提交按钮 -->
    <div v-if="!isReadOnly" class="submit-section">
      <el-button 
        type="primary" 
        size="large"
        :loading="submitting"
        :disabled="questions.length === 0"
        @click="commit"
        class="submit-btn"
      >
        <el-icon v-if="!submitting"><Check /></el-icon>
        {{ submitting ? '提交中...' : '提交答案' }}
      </el-button>
      <p class="submit-tip">
        <el-icon><InfoFilled /></el-icon>
        答案提交后将无法修改，请仔细检查后再提交
      </p>
    </div>
    
    <!-- 只读模式提示 -->
    <div v-if="isReadOnly" class="readonly-section">
      <el-alert
        title="查看模式"
        type="info"
        description="课程已结课，您可以查看测试题目和答案解析，但无法提交答案。"
        show-icon
        :closable="false"
      />
    </div>
  </div>
</template>

<style scoped>
.student-questions {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.progress-card {
  margin-bottom: 24px;
}

.progress-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.progress-header h3 {
  margin: 0;
  color: #303133;
}

.progress-info {
  display: flex;
  align-items: center;
  flex: 1;
  margin-left: 20px;
}

.loading-container {
  padding: 20px;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.question-card {
  border-radius: 12px;
  transition: all 0.3s ease;
  /* 确保卡片不限制内容高度 */
  height: auto !important;
  max-height: none !important;
  overflow: visible !important;
}

.question-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.question-info {
  display: flex;
  gap: 8px;
  align-items: center;
}

.question-status {
  display: flex;
  align-items: center;
}

.question-content {
  padding: 0;
  /* 确保内容容器不截断 */
  height: auto !important;
  max-height: none !important;
  overflow: visible !important;
}

.question-text-container {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
  /* 确保容器不限制高度 */
  height: auto !important;
  max-height: none !important;
  overflow: visible !important;
}

.question-text {
  font-size: 16px;
  line-height: 1.8;
  color: #303133;
  margin: 0;
  font-weight: 500;
  /* 强制文本完整显示，不截断 */
  word-wrap: break-word !important;
  white-space: pre-wrap !important;
  max-width: 100% !important;
  overflow-wrap: break-word !important;
  text-overflow: initial !important;
  overflow: visible !important;
  height: auto !important;
  max-height: none !important;
  -webkit-line-clamp: none !important;
  -webkit-box-orient: initial !important;
  display: block !important;
}

.options-group {
  width: 100%;
}

.option-item {
  display: flex;
  align-items: flex-start;
  width: 100%;
  margin: 0 0 16px 0;
  padding: 12px;
  border: 2px solid #f0f0f0;
  border-radius: 8px;
  transition: all 0.3s ease;
  cursor: pointer;
  /* 确保选项容器不限制高度 */
}

.answer-section {
  margin-top: 20px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #67c23a;
}

.correct-answer {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.answer-text {
  font-weight: 500;
  color: #67c23a;
  font-size: 16px;
}

.explanation {
  margin-top: 16px;
}

.explanation-content {
  padding: 12px;
  background-color: #fff;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  line-height: 1.6;
  color: #606266;
  font-size: 14px;
}
  height: auto !important;
  max-height: none !important;
  overflow: visible !important;
}

.option-item:hover {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.option-item.is-checked {
  border-color: #409eff;
  background-color: #e1f3d8;
}

.option-label {
  font-weight: bold;
  color: #409eff;
  margin-right: 12px;
  min-width: 20px;
}

.option-text {
  flex: 1;
  line-height: 1.6;
  /* 确保选项文本也完整显示 */
  word-wrap: break-word !important;
  white-space: pre-wrap !important;
  overflow-wrap: break-word !important;
  text-overflow: initial !important;
  overflow: visible !important;
  height: auto !important;
  max-height: none !important;
  -webkit-line-clamp: none !important;
  -webkit-box-orient: initial !important;
  display: block !important;
}

.submit-section {
  margin-top: 40px;
  text-align: center;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 12px;
}

.submit-btn {
  padding: 12px 40px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
}

.submit-tip {
  margin: 12px 0 0 0;
  color: #909399;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

/* Element Plus 组件样式覆盖 - 确保内容完整显示 */
:deep(.el-card) {
  height: auto !important;
  max-height: none !important;
  overflow: visible !important;
}

:deep(.el-card__body) {
  height: auto !important;
  max-height: none !important;
  overflow: visible !important;
  padding: 20px !important;
}

:deep(.el-card__header) {
  height: auto !important;
  max-height: none !important;
  overflow: visible !important;
}

/* 确保所有文本内容都能完整显示 */
:deep(p), :deep(span), :deep(div) {
  text-overflow: initial !important;
  overflow: visible !important;
  -webkit-line-clamp: none !important;
  -webkit-box-orient: initial !important;
  white-space: pre-wrap !important;
  word-wrap: break-word !important;
  overflow-wrap: break-word !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .student-questions {
    padding: 12px;
  }
  
  .progress-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .progress-info {
    margin-left: 0;
  }
  
  .question-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .option-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .option-label {
    margin-right: 0;
  }
}
</style>
