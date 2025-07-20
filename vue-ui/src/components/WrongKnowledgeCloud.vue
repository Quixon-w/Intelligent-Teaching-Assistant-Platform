<template>
  <div class="wrong-knowledge-cloud">
    <div class="header">
      <h3>{{ title }}</h3>
      <el-button 
        v-if="showRefresh" 
        type="primary" 
        size="small" 
        @click="loadData"
        :loading="loading"
      >
        刷新数据
      </el-button>
    </div>
    
    <div v-if="loading" class="loading">
      <el-skeleton :rows="5" animated />
    </div>
    
    <div v-else-if="knowledgeStats.length === 0" class="empty">
      <el-empty description="暂无错题数据" />
    </div>
    
    <div v-else class="content">
      <!-- 知识点云图 -->
      <div class="cloud-container">
        <div 
          v-for="(item, index) in knowledgeStats" 
          :key="index"
          class="knowledge-tag"
          :style="getTagStyle(item.wrongCount)"
          @click="handleTagClick(item)"
        >
          {{ item.knowledge }}
          <span class="count">({{ item.wrongCount }})</span>
          <el-button 
            v-if="showPracticeButton"
            size="small" 
            type="primary" 
            class="practice-btn"
            @click.stop="startInstantPractice(item)"
          >
            练习
          </el-button>
        </div>
      </div>
      
      <!-- 统计信息 -->
      <div class="stats-info">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card shadow="hover">
              <div class="stat-item">
                <div class="stat-number">{{ totalWrongCount }}</div>
                <div class="stat-label">总错题数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover">
              <div class="stat-item">
                <div class="stat-number">{{ knowledgeStats.length }}</div>
                <div class="stat-label">涉及知识点</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover">
              <div class="stat-item">
                <div class="stat-number">{{ maxWrongCount }}</div>
                <div class="stat-label">最高错误次数</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <!-- 错题详情列表 -->
      <div v-if="showDetails && wrongQuestions.length > 0" class="wrong-questions">
        <h4>错题详情</h4>
        <el-table :data="wrongQuestions" stripe>
          <el-table-column prop="knowledge" label="知识点" width="150" />
          <el-table-column prop="question" label="题目" show-overflow-tooltip />
          <el-table-column prop="selectedOption" label="你的答案" width="100" />
          <el-table-column prop="explanation" label="解析" show-overflow-tooltip />
          <el-table-column prop="submitTime" label="提交时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.submitTime) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getWrongKnowledgeStatsByLesson, getWrongKnowledgeStatsByCourse, getWrongQuestionsByLesson } from '@/api/questionRecords'

export default {
  name: 'WrongKnowledgeCloud',
  props: {
    type: {
      type: String,
      required: true,
      validator: (value) => ['lesson', 'course'].includes(value)
    },
    lessonId: {
      type: [String, Number],
      default: null
    },
    courseId: {
      type: [String, Number],
      default: null
    },
    studentId: {
      type: [String, Number],
      required: true
    },
    title: {
      type: String,
      default: '错题知识点统计'
    },
    showRefresh: {
      type: Boolean,
      default: true
    },
    showDetails: {
      type: Boolean,
      default: false
    },
    showPracticeButton: {
      type: Boolean,
      default: false
    }
  },
  emits: ['tag-click', 'start-practice'],
  setup(props, { emit }) {
    const loading = ref(false)
    const knowledgeStats = ref([])
    const wrongQuestions = ref([])

    // 计算属性
    const totalWrongCount = computed(() => {
      return knowledgeStats.value.reduce((sum, item) => sum + item.wrongCount, 0)
    })

    const maxWrongCount = computed(() => {
      if (knowledgeStats.value.length === 0) return 0
      return Math.max(...knowledgeStats.value.map(item => item.wrongCount))
    })

    // 获取标签样式
    const getTagStyle = (wrongCount) => {
      const maxCount = maxWrongCount.value
      const ratio = maxCount > 0 ? wrongCount / maxCount : 0
      const fontSize = 14 + ratio * 10 // 14-24px
      const opacity = 0.6 + ratio * 0.4 // 0.6-1.0
      const color = ratio > 0.7 ? '#f56c6c' : ratio > 0.4 ? '#e6a23c' : '#409eff'
      
      return {
        fontSize: `${fontSize}px`,
        opacity: opacity,
        color: color,
        fontWeight: ratio > 0.7 ? 'bold' : 'normal'
      }
    }

    // 加载数据
    const loadData = async () => {
      loading.value = true
      try {
        let statsResponse, questionsResponse
        
        if (props.type === 'lesson') {
          statsResponse = await getWrongKnowledgeStatsByLesson(props.lessonId, props.studentId)
          if (props.showDetails) {
            questionsResponse = await getWrongQuestionsByLesson(props.lessonId, props.studentId)
          }
        } else {
          statsResponse = await getWrongKnowledgeStatsByCourse(props.courseId, props.studentId)
        }
        
        if (statsResponse.code === 0) {
          knowledgeStats.value = statsResponse.data || []
        } else {
          ElMessage.error(statsResponse.message || '获取错题统计失败')
        }
        
        if (props.showDetails && questionsResponse) {
          if (questionsResponse.code === 0) {
            wrongQuestions.value = questionsResponse.data || []
          } else {
            ElMessage.error(questionsResponse.message || '获取错题详情失败')
          }
        }
      } catch (error) {
        console.error('加载错题数据失败:', error)
        ElMessage.error('加载错题数据失败')
      } finally {
        loading.value = false
      }
    }

    // 处理标签点击
    const handleTagClick = (item) => {
      emit('tag-click', item)
    }
    
    // 开始即时练习
    const startInstantPractice = (item) => {
      emit('start-practice', item)
    }

    // 格式化日期
    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleString('zh-CN')
    }

    // 组件挂载时加载数据
    onMounted(() => {
      loadData()
    })

    return {
      loading,
      knowledgeStats,
      wrongQuestions,
      totalWrongCount,
      maxWrongCount,
      getTagStyle,
      loadData,
      handleTagClick,
      startInstantPractice,
      formatDate
    }
  }
}
</script>

<style scoped>
.wrong-knowledge-cloud {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h3 {
  margin: 0;
  color: #303133;
}

.loading {
  padding: 20px;
}

.empty {
  padding: 40px;
  text-align: center;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.cloud-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  min-height: 100px;
  align-items: center;
  justify-content: center;
}

.knowledge-tag {
  padding: 8px 16px;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.knowledge-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.knowledge-tag .count {
  font-size: 0.8em;
  opacity: 0.7;
  margin-left: 4px;
}

.knowledge-tag .practice-btn {
  margin-left: 8px;
  font-size: 12px;
  padding: 2px 8px;
}

.stats-info {
  margin-top: 20px;
}

.stat-item {
  text-align: center;
  padding: 10px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.wrong-questions {
  margin-top: 20px;
}

.wrong-questions h4 {
  margin-bottom: 15px;
  color: #303133;
}
</style> 