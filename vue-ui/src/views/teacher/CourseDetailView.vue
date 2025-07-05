<template>
  <div class="course-detail-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>{{ courseInfo ? `${courseInfo.name || courseInfo.courseName} - 课程管理` : '课程详情' }}</h3>
          <div>
          <el-button @click="$router.back()">返回</el-button>
            <el-button 
              v-if="isCurrentUserTeacher && courseInfo?.isOver === 0" 
              type="danger" 
              @click="endCourse"
            >
              结束课程
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 课程状态提示（仅课程教师可见） -->
      <div v-if="courseInfo && isCurrentUserTeacher" class="course-status">
        <el-alert
          :title="courseInfo.isOver === 0 ? '课程进行中' : '课程已结束'"
          :type="courseInfo.isOver === 0 ? 'success' : 'info'"
          :description="courseInfo.isOver === 0 ? '可以进行编辑和管理操作' : '课程已结束，仅可查看信息和成绩'"
          show-icon
          :closable="false"
        />
      </div>
      
      <!-- 非课程教师的提示信息 -->
      <div v-if="courseInfo && !isCurrentUserTeacher" class="visitor-info">
        <el-alert
          title="浏览模式"
          description="您正在以访客身份查看此课程信息"
          type="info"
          :closable="false"
          show-icon
        />
      </div>
      
      <!-- 主要内容区域 -->
      <div v-if="courseInfo && isCurrentUserTeacher" class="course-content">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- 课程信息 -->
          <el-tab-pane label="课程信息" name="info">
            <div class="course-info-section">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="课程ID">{{ courseInfo.id }}</el-descriptions-item>
                <el-descriptions-item label="课程名称">{{ courseInfo.name || courseInfo.courseName }}</el-descriptions-item>
                <el-descriptions-item label="教师姓名">{{ courseInfo.teacherName }}</el-descriptions-item>
          <el-descriptions-item label="课程状态">
                  <el-tag :type="courseInfo.isOver === 0 ? 'success' : 'danger'">
                    {{ courseInfo.isOver === 0 ? '进行中' : '已结束' }}
            </el-tag>
          </el-descriptions-item>
                <el-descriptions-item label="创建时间" :span="2">{{ courseInfo.createTime }}</el-descriptions-item>
        </el-descriptions>
              
              <!-- 课程简介编辑 -->
              <div class="course-description">
                <h4>课程简介</h4>
                <div v-if="!editingDescription">
                  <p>{{ courseInfo.comment || '暂无课程简介' }}</p>
                  <el-button 
                    v-if="courseInfo.isOver === 0" 
                    type="primary" 
                    size="small" 
                    @click="startEditDescription"
                  >
                    编辑简介
                  </el-button>
                </div>
                <div v-else>
                  <el-input
                    v-model="descriptionForm.comment"
                    type="textarea"
                    :rows="4"
                    placeholder="请输入课程简介"
                  />
                  <div class="edit-actions">
                    <el-button type="primary" size="small" @click="saveDescription">保存</el-button>
                    <el-button size="small" @click="cancelEditDescription">取消</el-button>
                  </div>
                </div>
      </div>
      
              <!-- 课程资料上传 -->
              <div class="course-materials">
                <h4>课程资料</h4>
                <el-upload
                  v-if="courseInfo.isOver === 0"
                  class="upload-demo"
                  action="/ai/v1/upload"
                  :data="courseUploadData"
                  :on-success="handleCourseUploadSuccess"
                  :on-error="handleCourseUploadError"
                  :on-progress="handleCourseUploadProgress"
                  :before-upload="beforeCourseUpload"
                  :file-list="courseMaterialsList"
                  multiple
                  accept=".pdf,.doc,.docx,.txt,.md"
                >
                  <el-button type="primary" :loading="courseUploading">
                    {{ courseUploading ? '上传中...' : '上传课程资料' }}
                  </el-button>
                  <template #tip>
                    <div class="el-upload__tip">
                      支持 PDF、Word、TXT、MD 格式文件，学生可以下载学习
                    </div>
                  </template>
                </el-upload>
                
                <!-- 已上传的资料列表 -->
                <div v-if="courseMaterialsList.length > 0" class="materials-list">
                  <el-table :data="courseMaterialsList" v-loading="courseMaterialsLoading" style="width: 100%">
                    <el-table-column prop="filename" label="文件名" />
                    <el-table-column prop="size" label="文件大小" width="120">
                      <template #default="scope">
                        {{ formatFileSize(scope.row.size) }}
                      </template>
                    </el-table-column>
                    <el-table-column label="操作" width="120">
                      <template #default="scope">
                        <el-button 
                          type="primary" 
                          size="small" 
                          @click="downloadCourseMaterial(scope.row)"
                        >
                          下载
                        </el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
                
                <!-- 空状态 -->
                <div v-else-if="!courseMaterialsLoading" class="empty-materials">
                  <el-empty description="暂无课程资料" />
                </div>
              </div>
            </div>
          </el-tab-pane>
          
          <!-- 课时管理 -->
          <el-tab-pane label="课时管理" name="lessons">
            <div class="lessons-section">
              <div class="section-header">
                <h4>课时列表</h4>
                <el-button 
                  v-if="courseInfo.isOver === 0" 
                  type="primary" 
                  @click="showAddLessonDialog = true"
                >
                  新增课时
                </el-button>
              </div>
              
              <el-table :data="lessonsList" v-loading="lessonsLoading" style="width: 100%">
                <el-table-column prop="lessonId" label="课时ID" width="80" />
                <el-table-column prop="lessonName" label="课时名称" />
                <el-table-column prop="createTime" label="创建时间" width="180" />
                <el-table-column label="测试状态" width="120">
                  <template #default="scope">
                    <el-tag :type="getTestStatusType(scope.row)">
                      {{ getTestStatusText(scope.row) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="完成测试人数" width="120">
                  <template #default="scope">
                    <span v-if="scope.row.hasQuestion === 1">
                      {{ scope.row.completedCount || 0 }} / {{ studentsList.length }}
                    </span>
                    <span v-else>-</span>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="350">
                  <template #default="scope">
                    <el-button size="small" @click="manageLessonFiles(scope.row)">文件管理</el-button>
                    
                    <!-- 状态1：没有创建测试的课时 -->
                    <el-button 
                      v-if="scope.row.hasQuestion === 0"
                      size="small" 
                      type="success" 
                      @click="createTest(scope.row)"
                    >
                      创建测试
                    </el-button>
                    
                    <!-- 状态2：创建了测试但未发布（草稿状态，hasQuestion=2） -->
                    <el-button 
                      v-else-if="scope.row.hasQuestion === 2"
                      size="small" 
                      type="warning" 
                      @click="editTest(scope.row)"
                    >
                      编辑测试
                    </el-button>
                    
                    <!-- 状态3：已发布的测试（hasQuestion=1，只能查看） -->
                    <el-button 
                      v-else-if="scope.row.hasQuestion === 1"
                      size="small" 
                      type="info" 
                      @click="viewTest(scope.row)"
                    >
                      查看测试
                    </el-button>
                    
                    <!-- 已发布测试的课时可以查看学生做题统计 -->
                    <el-button 
                      v-if="scope.row.hasQuestion === 1"
                      size="small" 
                      type="success" 
                      @click="viewTestStatistics(scope.row)"
                    >
                      查看统计
                    </el-button>
                    
                    <el-button 
                      v-if="courseInfo.isOver === 0 && scope.row.hasQuestion !== 1" 
                      size="small" 
                      type="danger" 
                      @click="deleteLesson(scope.row)"
                    >
                      删除课时
                    </el-button>
                    <el-tooltip 
                      v-if="courseInfo.isOver === 0 && scope.row.hasQuestion === 1"
                      content="已发布测试的课时无法删除"
                      placement="top"
                    >
                      <el-button 
                        size="small" 
                        type="danger" 
                        disabled
                      >
                        删除课时
                      </el-button>
                    </el-tooltip>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
          
          <!-- 学生管理 -->
          <el-tab-pane label="学生管理" name="students">
            <div class="students-section">
              <div class="section-header">
                <h4>选课学生列表</h4>
                <el-button @click="loadStudents">刷新</el-button>
              </div>
              
              <el-table :data="studentsList" v-loading="studentsLoading" style="width: 100%">
                <el-table-column prop="id" label="学生ID" width="80" />
                <el-table-column prop="username" label="学生姓名" />
                <el-table-column prop="email" label="邮箱" />
                <el-table-column prop="phone" label="联系电话" width="120" />
                <el-table-column label="操作" width="150">
                  <template #default="scope">
                    <el-button size="small" @click="viewStudentScore(scope.row)">查看成绩</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
          
          <!-- 成绩管理 -->
          <el-tab-pane label="成绩管理" name="scores">
            <div class="scores-section">
              <div class="section-header">
                <h4>成绩管理</h4>
                <div class="action-buttons">
                  <el-button @click="loadAllScores">刷新成绩</el-button>
                </div>
              </div>
              
              <!-- 学生成绩趋势图 -->
              <div class="score-trend-section">
                <h5>学生成绩趋势</h5>
                <div class="student-selector">
                  <el-select 
                    v-model="selectedStudentId" 
                    placeholder="选择学生查看成绩趋势" 
                    @change="loadStudentScoreTrend"
                    style="width: 300px;"
                  >
                    <el-option
                      v-for="student in studentsList"
                      :key="student.id"
                      :label="student.username"
                      :value="student.id"
                    />
                  </el-select>
                </div>
                
                <!-- 折线图 -->
                <div v-if="selectedStudentId && scoreTrendData.length > 0" class="chart-container">
                  <div ref="scoreChartRef" style="width: 100%; height: 400px;"></div>
                </div>
                
                <div v-else-if="selectedStudentId && !scoreTrendLoading" class="no-data">
                  <el-empty description="该学生暂无成绩数据" />
                </div>
              </div>
              
              <!-- 课程总成绩统计 -->
              <div class="course-score-section">
                <h5>课程总成绩统计</h5>
              
              <!-- 仅显示结课后的总成绩 -->
              <div v-if="courseInfo.isOver === 0" class="course-ongoing-notice">
                <el-alert
                  title="课程进行中"
                  description="课程结束后将显示学生的总成绩统计"
                  type="info"
                  :closable="false"
                  show-icon
                />
              </div>
              
              <div v-else>
                <!-- 成绩概览 -->
                <div class="score-overview">
                  <el-row :gutter="20">
                    <el-col :span="6">
                      <el-statistic title="选课学生数" :value="studentsList.length" />
                    </el-col>
                    <el-col :span="6">
                      <el-statistic title="平均分" :value="averageScore" :precision="2" />
                    </el-col>
                    <el-col :span="6">
                      <el-statistic title="及格率" :value="passRate" suffix="%" :precision="1" />
                    </el-col>
                    <el-col :span="6">
                      <el-statistic title="最高分" :value="maxScore" :precision="2" />
                    </el-col>
                  </el-row>
                </div>
                
                <!-- 详细成绩表 -->
                  <el-table :data="scoresList" v-loading="scoresLoading" style="width: 100%; margin-top: 20px;">
                  <el-table-column prop="studentName" label="学生姓名" />
                  <el-table-column prop="finalScore" label="总成绩" width="120">
                    <template #default="scope">
                      <el-tag :type="scope.row.finalScore >= 60 ? 'success' : 'danger'">
                        {{ scope.row.finalScore || '0' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="grade" label="等级" width="100">
                    <template #default="scope">
                      <el-tag :type="getGradeType(scope.row.finalScore)">
                        {{ getGrade(scope.row.finalScore) }}
                      </el-tag>
                    </template>
                  </el-table-column>
                    <el-table-column label="操作" width="120">
                      <template #default="scope">
                        <el-button size="small" @click="viewStudentDetailScore(scope.row)">
                          查看详情
                        </el-button>
                    </template>
                  </el-table-column>
                </el-table>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <!-- 访客查看界面 -->
      <div v-else-if="courseInfo && !isCurrentUserTeacher" class="visitor-view">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="课程ID">{{ courseInfo.id }}</el-descriptions-item>
          <el-descriptions-item label="课程名称">{{ courseInfo.name || courseInfo.courseName }}</el-descriptions-item>
          <el-descriptions-item label="教师姓名">{{ courseInfo.teacherName }}</el-descriptions-item>
          <el-descriptions-item label="课程描述" :span="2">{{ courseInfo.comment || '暂无描述' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">{{ courseInfo.createTime }}</el-descriptions-item>
        </el-descriptions>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="5" animated />
      </div>
    </el-card>
    
    <!-- 新增课时对话框 -->
    <el-dialog v-model="showAddLessonDialog" title="新增课时" width="500px">
      <el-form :model="lessonForm" :rules="lessonRules" ref="lessonFormRef" label-width="100px">
        <el-form-item label="课时名称" prop="lessonName">
          <el-input v-model="lessonForm.lessonName" placeholder="请输入课时名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddLessonDialog = false">取消</el-button>
        <el-button type="primary" @click="addLesson">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 文件管理对话框 -->
    <el-dialog v-model="showFileDialog" title="课时文件管理" width="1000px">
      <div v-if="currentLesson">
        <h4>{{ currentLesson.lessonName }} - 文件管理</h4>
        
        <!-- 文件上传 -->
        <div class="file-upload-section">
          <h5>上传课时文件</h5>
          <el-upload
            class="upload-demo"
            action="/ai/v1/upload"
            :data="getLessonUploadData(currentLesson.lessonId)"
            :on-success="handleLessonFileUploadSuccess"
            :on-error="handleLessonFileUploadError"
            :on-progress="handleLessonFileUploadProgress"
            :before-upload="beforeLessonFileUpload"
            :file-list="lessonFilesList"
            multiple
            accept=".pdf,.doc,.docx,.txt,.md"
          >
            <el-button type="primary" :loading="lessonFileUploading">
              {{ lessonFileUploading ? '上传中...' : '上传文件' }}
            </el-button>
            <template #tip>
              <div class="el-upload__tip">
                上传后可生成教学大纲和习题，支持PDF、Word、TXT、MD格式
              </div>
            </template>
          </el-upload>
        </div>
        
        <!-- AI功能 -->
        <div class="ai-functions">
          <h5>AI智能生成</h5>
          <div class="ai-buttons">
            <el-button 
              type="success" 
              @click="generateOutline(currentLesson)"
              :loading="outlineGenerating"
              :disabled="!hasLessonFiles"
            >
              {{ outlineGenerating ? '生成中...' : '生成教学大纲' }}
            </el-button>
            <el-button 
              type="warning" 
              @click="generateExercises(currentLesson)"
              :loading="exercisesGenerating"
              :disabled="!hasLessonFiles"
            >
              {{ exercisesGenerating ? '生成中...' : '生成习题' }}
            </el-button>
          </div>
          
          <!-- 生成状态提示 -->
          <div v-if="outlineGenerating || exercisesGenerating" class="generation-status">
            <el-alert
              :title="getGenerationStatusTitle()"
              :description="getGenerationStatusDescription()"
              type="info"
              :closable="false"
              show-icon
            />
          </div>
        </div>
        
        <!-- 文件下载 -->
        <div class="file-downloads">
          <h5>文件下载</h5>
          <div class="download-buttons">
            <el-button 
              @click="downloadOutline(currentLesson)"
              :disabled="!hasOutline"
            >
              下载教学大纲
            </el-button>
            <el-button 
              @click="downloadExercises(currentLesson)"
              :disabled="!hasExercises"
            >
              下载习题
            </el-button>
          </div>
          
          <!-- 文件状态显示 -->
          <div class="file-status">
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="教学大纲">
                <el-tag :type="hasOutline ? 'success' : 'info'">
                  {{ hasOutline ? '已生成' : '未生成' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="习题">
                <el-tag :type="hasExercises ? 'success' : 'info'">
                  {{ hasExercises ? '已生成' : '未生成' }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>
          
          <!-- 教学大纲文件列表 -->
          <div v-if="hasOutline" class="outline-files">
            <h6>教学大纲文件</h6>
            <el-table :data="lessonOutlineStatus.files" style="width: 100%" size="small">
              <el-table-column prop="filename" label="文件名" />
              <el-table-column prop="size" label="文件大小" width="120">
                <template #default="scope">
                  {{ formatFileSize(scope.row.size) }}
                </template>
              </el-table-column>
              <el-table-column prop="created_time" label="创建时间" width="180" />
              <el-table-column label="操作" width="120">
                <template #default="scope">
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="downloadOutlineFile(scope.row)"
                  >
                    下载
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          

          
          <!-- 习题文件列表 -->
          <div v-if="hasExercises" class="exercise-files">
            <h6>习题文件</h6>
            <el-table :data="lessonExercisesStatus.files" style="width: 100%" size="small">
              <el-table-column prop="filename" label="文件名" />
              <el-table-column prop="size" label="文件大小" width="120">
                <template #default="scope">
                  {{ formatFileSize(scope.row.size) }}
                </template>
              </el-table-column>
              <el-table-column prop="created_time" label="创建时间" width="180" />
              <el-table-column label="操作" width="120">
                <template #default="scope">
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="downloadExerciseFile(scope.row)"
                  >
                    下载
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
    </el-dialog>
    
    <!-- 题目管理对话框 -->
    <el-dialog v-model="showQuestionDialog" :title="dialogTitle" width="1200px">
      <div v-if="currentLesson">
        <h4>{{ currentLesson.lessonName }} - {{ dialogSubTitle }}</h4>
        
        <!-- 状态提示 -->
        <el-alert
          :title="getStatusAlertTitle()"
          :description="getStatusAlertDescription()"
          :type="getStatusAlertType()"
          :closable="false"
          style="margin-bottom: 20px;"
          show-icon
        />
        
        <!-- 题目列表 -->
        <div class="questions-list">
          <div class="section-header">
            <h5>{{ getQuestionListTitle() }}</h5>
            <div class="action-buttons">
              <!-- 状态1和2：可以编辑测试 -->
              <template v-if="canEditTest()">
                <el-button type="primary" @click="addNewQuestion">新增题目</el-button>
                <el-button type="success" @click="importFromQuestionBank">从题库导入</el-button>
                <el-button 
                  v-if="questionsList.length > 0"
                  type="warning" 
                  @click="saveDraft"
                >
                  保存草稿
                </el-button>
                <el-button 
                  v-if="questionsList.length > 0"
                  type="danger" 
                  @click="publishTest"
                  :loading="publishing"
                >
                  发布测试
                </el-button>
              </template>
              
              <!-- 状态3：只能查看 -->
              <template v-else>
                <el-button type="primary" @click="showQuestionDialog = false">关闭</el-button>
              </template>
            </div>
          </div>
          
          <!-- 功能说明 -->
          <el-alert
            v-if="questionsList.length === 0 && canEditTest()"
            title="开始创建测试"
            type="info"
            :closable="false"
            style="margin: 20px 0;"
          >
            <template #default>
              <p>您可以通过以下方式添加测试题目：</p>
              <ul style="margin: 5px 0 0 20px; padding: 0;">
                <li>手动新增单选题（包含题目、4个选项、正确答案、解析）</li>
                <li>从个人题库中导入已有的题目</li>
                <li>保存为草稿或直接发布给学生</li>
              </ul>
            </template>
          </el-alert>
          
          <el-alert
            v-if="questionsList.length === 0 && !canEditTest()"
            title="暂无测试题目"
            type="info"
            :closable="false"
            style="margin: 20px 0;"
            description="此课时暂未发布测试题目"
          />
          
          <el-table :data="questionsList" style="width: 100%">
            <el-table-column type="expand" width="50">
              <template #default="props">
                <div class="question-detail">
                  <h6>题目解析</h6>
                  <p v-if="props.row.questionExplanation" class="explanation-text">
                    {{ props.row.questionExplanation }}
                  </p>
                  <p v-else class="no-explanation">暂无解析</p>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="questionContent" label="题目内容" min-width="200" />
            <el-table-column prop="questionKnowledge" label="知识点" width="120" />
            <el-table-column label="选项" width="300">
              <template #default="scope">
                <div class="options">
                  <div v-for="(option, index) in scope.row.questionAnswer.slice(1)" :key="index">
                    {{ String.fromCharCode(65 + index) }}. {{ option }}
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="questionAnswer[0]" label="答案" width="60" />
            
            <!-- 编辑状态下显示操作列 -->
            <el-table-column v-if="canEditTest()" label="操作" width="150">
              <template #default="scope">
                <el-button size="small" @click="editQuestion(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteQuestion(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>
    
    <!-- 题目编辑对话框 -->
    <el-dialog 
      v-model="showQuestionEditDialog" 
      :title="questionForm.questionId ? '编辑题目' : '新增题目'" 
      width="600px"
    >
      <el-form 
        ref="questionFormRef"
        :model="questionForm" 
        :rules="questionRules"
        label-width="100px"
      >
        <el-form-item label="父知识点" prop="parentKnowledge">
          <el-input 
            v-model="questionForm.parentKnowledge" 
            placeholder="请输入父级知识点，如：数学、物理等"
          />
        </el-form-item>
        <el-form-item label="子知识点" prop="childKnowledge">
          <el-input 
            v-model="questionForm.childKnowledge" 
            placeholder="请输入具体知识点，如：线性代数、力学等"
          />
        </el-form-item>
        <el-form-item label="题目内容" prop="questionContent">
          <el-input 
            v-model="questionForm.questionContent" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入题目内容"
          />
        </el-form-item>
        <el-form-item label="选项A" prop="optionA">
          <el-input 
            v-model="questionForm.questionAnswer[1]" 
            placeholder="请输入选项A内容"
          />
        </el-form-item>
        <el-form-item label="选项B" prop="optionB">
          <el-input 
            v-model="questionForm.questionAnswer[2]" 
            placeholder="请输入选项B内容"
          />
        </el-form-item>
        <el-form-item label="选项C" prop="optionC">
          <el-input 
            v-model="questionForm.questionAnswer[3]" 
            placeholder="请输入选项C内容"
          />
        </el-form-item>
        <el-form-item label="选项D" prop="optionD">
          <el-input 
            v-model="questionForm.questionAnswer[4]" 
            placeholder="请输入选项D内容"
          />
        </el-form-item>
        <el-form-item label="正确答案" prop="correctAnswer">
          <el-select 
            v-model="questionForm.questionAnswer[0]" 
            placeholder="请选择正确答案"
            style="width: 100%"
          >
            <el-option label="A" value="A" />
            <el-option label="B" value="B" />
            <el-option label="C" value="C" />
            <el-option label="D" value="D" />
          </el-select>
        </el-form-item>
        <el-form-item label="题目解析">
          <el-input 
            v-model="questionForm.questionExplanation" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入题目解析（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelEditQuestion">取消</el-button>
        <el-button type="primary" @click="saveQuestion" :loading="saving">
          {{ questionForm.questionId ? '保存修改' : '添加题目' }}
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 题库导入对话框 -->
    <el-dialog v-model="showQuestionBankDialog" title="从个人题库导入题目" width="1200px">
      <div class="question-bank">
        <el-alert
          title="从个人题库导入"
          description="选择要导入到当前课时的题目，导入后会自动关联到这个课时的测试中"
          type="info"
          :closable="false"
          style="margin-bottom: 20px;"
          show-icon
        />
        
        <div class="search-section">
          <el-row :gutter="20">
            <el-col :span="16">
              <el-input
                v-model="questionBankSearch"
                placeholder="搜索题目内容或知识点"
                clearable
                @keyup.enter="searchQuestionBank"
                @clear="searchQuestionBank"
              >
                <template #prepend>搜索</template>
                <template #append>
                  <el-button @click="searchQuestionBank">查找</el-button>
                </template>
              </el-input>
            </el-col>
            <el-col :span="8">
              <div class="stats-info">
                <span>共 {{ questionBankList.length }} 道题目</span>
                <span v-if="selectedQuestionBankItems.length > 0" style="margin-left: 20px;">
                  已选择 {{ selectedQuestionBankItems.length }} 道
                </span>
              </div>
            </el-col>
          </el-row>
        </div>
        
        <el-table 
          :data="questionBankList" 
          @selection-change="handleQuestionBankSelection"
          style="width: 100%; margin-top: 20px;"
          v-loading="questionBankLoading"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="questionContent" label="题目内容" min-width="200" show-overflow-tooltip />
          <el-table-column prop="questionKnowledge" label="知识点" width="120" />
          <el-table-column label="选项" width="300">
            <template #default="scope">
              <div class="options-display">
                <div v-for="(option, index) in scope.row.questionAnswer.slice(1)" :key="index" style="font-size: 12px; line-height: 1.4;">
                  {{ String.fromCharCode(65 + index) }}. {{ option }}
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="questionAnswer[0]" label="答案" width="60" align="center">
            <template #default="scope">
              <el-tag size="small" type="success">{{ scope.row.questionAnswer[0] }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 空状态 -->
        <div v-if="questionBankList.length === 0 && !questionBankLoading" class="empty-state">
          <el-empty description="暂无题目">
            <template #description>
              <span>您的个人题库为空</span>
            </template>
            <el-button type="primary" @click="showQuestionBankDialog = false">
              去题库管理添加题目
            </el-button>
          </el-empty>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showQuestionBankDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="importSelectedQuestions" 
            :disabled="selectedQuestionBankItems.length === 0"
            :loading="importing"
          >
            导入选中题目 ({{ selectedQuestionBankItems.length }})
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 学生成绩查看对话框 -->
    <el-dialog v-model="showStudentScoreDialog" title="学生成绩详情" width="600px">
      <div v-if="currentStudent" class="student-score-dialog">
        <div class="student-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="学生姓名">{{ currentStudent.username }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ currentStudent.email }}</el-descriptions-item>
            <el-descriptions-item label="联系电话">{{ currentStudent.phone }}</el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="score-info" style="margin-top: 20px;">
          <el-card>
            <template #header>
              <div class="score-header">
                <span>课程成绩</span>
                <el-tag 
                  v-if="studentScore !== null" 
                  :type="studentScore >= 60 ? 'success' : 'danger'"
                  size="large"
                >
                  {{ studentScore }} 分
                </el-tag>
              </div>
            </template>
            
            <div v-if="studentScoreLoading" class="loading-score">
              <el-skeleton :rows="3" animated />
            </div>
            
            <div v-else-if="studentScore !== null" class="score-details">
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="score-item">
                    <div class="score-label">成绩等级</div>
                    <div class="score-value">
                      <el-tag :type="getGradeType(studentScore)">
                        {{ getGrade(studentScore) }}
                      </el-tag>
                    </div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="score-item">
                    <div class="score-label">是否及格</div>
                    <div class="score-value">
                      <el-tag :type="studentScore >= 60 ? 'success' : 'danger'">
                        {{ studentScore >= 60 ? '及格' : '不及格' }}
                      </el-tag>
                    </div>
                  </div>
                </el-col>
              </el-row>
              
              <div class="score-description" style="margin-top: 20px;">
                <el-alert
                  :title="getScoreDescription(studentScore)"
                  :type="studentScore >= 60 ? 'success' : 'warning'"
                  :closable="false"
                  show-icon
                />
              </div>
            </div>
            
            <div v-else class="no-score">
              <el-empty description="暂无成绩数据">
                <template #description>
                  <span>该学生在此课程中暂无成绩记录</span>
                </template>
              </el-empty>
            </div>
          </el-card>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showStudentScoreDialog = false">关闭</el-button>
      </template>
    </el-dialog>
    
    <!-- 测试统计对话框 -->
    <el-dialog 
      v-model="showStatisticsDialog" 
      title="测试统计" 
      width="90%"
      :before-close="() => showStatisticsDialog = false"
    >
      <div v-if="currentStatisticsLesson" class="statistics-container">
        <div class="statistics-header">
          <h4>{{ currentStatisticsLesson.lessonName }} - 测试统计</h4>
          <el-button @click="loadTestStatistics(currentStatisticsLesson.lessonId)" :loading="testStatisticsLoading">
            刷新统计
          </el-button>
        </div>
        
        <div v-loading="testStatisticsLoading" class="statistics-content">
          <div v-if="testStatisticsData.length === 0" class="no-statistics">
            <el-empty description="暂无统计数据">
              <template #description>
                <span>该课时暂无学生完成测试</span>
              </template>
            </el-empty>
          </div>
          
          <div v-else class="statistics-list">
            <div v-for="(item, index) in testStatisticsData" :key="item.questionId" class="statistics-item">
              <div class="question-header">
                <h5>第{{ index + 1 }}题：{{ item.question }}</h5>
                <div class="question-meta">
                  <el-tag size="small" type="info">{{ item.knowledge }}</el-tag>
                  <el-tag size="small" type="success">正确答案：{{ item.answer }}</el-tag>
                  <el-tag size="small" :type="item.correctRate >= 80 ? 'success' : item.correctRate >= 60 ? 'warning' : 'danger'">
                    正确率：{{ item.correctRate.toFixed(1) }}%
                  </el-tag>
                </div>
              </div>
              
              <div class="statistics-details">
                <div class="overview-stats">
                  <el-row :gutter="20">
                    <el-col :span="6">
                      <el-statistic title="答题人数" :value="item.totalAnswers" />
                    </el-col>
                    <el-col :span="6">
                      <el-statistic title="正确人数" :value="item.correctCount" />
                    </el-col>
                    <el-col :span="6">
                      <el-statistic title="正确率" :value="item.correctRate" suffix="%" :precision="1" />
                    </el-col>
                    <el-col :span="6">
                      <el-statistic title="错误人数" :value="item.totalAnswers - item.correctCount" />
                    </el-col>
                  </el-row>
                </div>
                
                <div class="options-chart">
                  <h6>选项分布</h6>
                  <div class="chart-container">
                    <div class="option-bars">
                      <div v-for="option in ['A', 'B', 'C', 'D']" :key="option" class="option-bar-item">
                        <div class="option-label">
                          <span class="option-letter">{{ option }}</span>
                          <span class="option-text">{{ item.options[option] }}</span>
                          <el-tag v-if="item.optionStats[option].isCorrect" size="small" type="success">正确答案</el-tag>
                        </div>
                        <div class="bar-container">
                          <div 
                            class="bar-fill" 
                            :style="{ 
                              width: item.optionStats[option].percentage + '%',
                              backgroundColor: item.optionStats[option].isCorrect ? '#67c23a' : '#f56c6c'
                            }"
                          ></div>
                          <span class="bar-text">
                            {{ item.optionStats[option].count }}人 ({{ item.optionStats[option].percentage.toFixed(1) }}%)
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div v-if="item.explanation" class="question-explanation">
                  <h6>题目解析</h6>
                  <p>{{ item.explanation }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import axios from 'axios'
import { addLesson as addLessonApi, commitQuestion } from '@/api/course/lesson'
import { getCourseScore } from '@/api/course'
import { showError, showDetailedError, showSuccess, showWarning, handleApiResponse, handleException } from '@/utils/errorHandler'
import * as echarts from 'echarts'

const route = useRoute()
const authStore = useAuthStore()

// 响应式数据
const courseInfo = ref(null)
const loading = ref(false)
const activeTab = ref('info')

// 课程信息编辑
const editingDescription = ref(false)
const descriptionForm = reactive({
  comment: ''
})

// 文件上传
const materialsList = ref([])
const uploadData = computed(() => ({
  session_id: Date.now().toString(),
  user_id: authStore.user?.id || '',
  is_teacher: true,
  course_id: route.params.id,
  is_resource: true,
  is_ask: false
}))

// 课程资料管理
const courseMaterialsList = ref([])
const courseMaterialsLoading = ref(false)
const courseUploading = ref(false)
const courseUploadData = computed(() => ({
  session_id: Date.now().toString(),
  user_id: authStore.user?.id || '',
  is_teacher: true,
  course_id: route.params.id,
  lesson_num: 'course', // 课程资料使用course标识
  file_encoding: 'utf-8',
  is_resource: true,
  is_ask: false
}))

// 课时文件管理
const lessonFilesList = ref([]) // 用于el-upload组件的文件列表
const lessonUploadedFiles = ref([]) // 用于跟踪实际上传的文件
const lessonFileUploading = ref(false)
const outlineGenerating = ref(false)
const exercisesGenerating = ref(false)
const lessonOutlineStatus = ref(null)
const lessonExercisesStatus = ref(null)

// 课时管理
const lessonsList = ref([])
const lessonsLoading = ref(false)
const showAddLessonDialog = ref(false)
const showFileDialog = ref(false)
const showQuestionDialog = ref(false)
const currentLesson = ref(null)
const lessonForm = reactive({
  lessonName: ''
})
const lessonRules = {
  lessonName: [
    { required: true, message: '请输入课时名称', trigger: 'blur' }
  ]
}
const lessonFormRef = ref()

// 题目管理
const questionsList = ref([])
const showQuestionEditDialog = ref(false)
const showQuestionBankDialog = ref(false)
const currentTestStatus = ref(0) // 0: 无测试, 1: 有测试未发布, 2: 已发布

// 题目编辑表单
const questionForm = ref({
  questionId: null,
  questionContent: '',
  questionKnowledge: '',
  questionAnswer: ['', '', '', '', ''], // [答案, 选项A, 选项B, 选项C, 选项D]
  questionExplanation: ''
})

const questionFormRef = ref()
const saving = ref(false)

const questionRules = {
  parentKnowledge: [
    { required: true, message: '请输入父知识点', trigger: 'blur' }
  ],
  childKnowledge: [
    { required: true, message: '请输入子知识点', trigger: 'blur' }
  ],
  questionContent: [
    { required: true, message: '请输入题目内容', trigger: 'blur' }
  ],
  optionA: [
    { 
      validator: (rule, value, callback) => {
        if (!questionForm.value.questionAnswer[1]) {
          callback(new Error('请输入选项A内容'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ],
  optionB: [
    { 
      validator: (rule, value, callback) => {
        if (!questionForm.value.questionAnswer[2]) {
          callback(new Error('请输入选项B内容'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ],
  optionC: [
    { 
      validator: (rule, value, callback) => {
        if (!questionForm.value.questionAnswer[3]) {
          callback(new Error('请输入选项C内容'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ],
  optionD: [
    { 
      validator: (rule, value, callback) => {
        if (!questionForm.value.questionAnswer[4]) {
          callback(new Error('请输入选项D内容'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ],
  correctAnswer: [
    { 
      validator: (rule, value, callback) => {
        if (!questionForm.value.questionAnswer[0]) {
          callback(new Error('请选择正确答案'))
        } else {
          callback()
        }
      }, 
      trigger: 'change' 
    }
  ]
}

// 题库相关
const questionBankList = ref([])
const questionBankSearch = ref('')
const selectedQuestionBankItems = ref([])
const questionBankLoading = ref(false)
const importing = ref(false)
const publishing = ref(false)

// 测试统计相关
const showStatisticsDialog = ref(false)
const currentStatisticsLesson = ref(null)
const testStatisticsData = ref([])
const testStatisticsLoading = ref(false)

// 学生管理
const studentsList = ref([])
const studentsLoading = ref(false)

// 成绩管理
const scoresList = ref([])
const scoresLoading = ref(false)
const averageScore = ref(0)
const passRate = ref(0)
const maxScore = ref(0)

// 学生成绩趋势图相关
const selectedStudentId = ref(null)
const scoreTrendData = ref([])
const scoreTrendLoading = ref(false)
const scoreChartRef = ref(null)

// 计算属性：判断当前用户是否为课程教师
const isCurrentUserTeacher = computed(() => {
  if (!courseInfo.value || !authStore.user?.id) {
    return false
  }
  return courseInfo.value.teacherId === parseInt(authStore.user.id)
})

// 计算属性：动态显示对话框标题
const dialogTitle = computed(() => {
  if (!currentLesson.value) return '题目管理'
  return currentLesson.value.hasQuestion === 1 ? '题目管理' : '创建测试'
})

const dialogSubTitle = computed(() => {
  if (!currentLesson.value) return '题目管理'
  return currentLesson.value.hasQuestion === 1 ? '题目管理' : '创建测试'
})

// 课时文件管理计算属性
const hasLessonFiles = computed(() => {
  return lessonUploadedFiles.value.length > 0
})

const hasOutline = computed(() => {
  return lessonOutlineStatus.value !== null && lessonOutlineStatus.value.files && lessonOutlineStatus.value.files.length > 0
})

const hasExercises = computed(() => {
  return lessonExercisesStatus.value !== null && lessonExercisesStatus.value.files && lessonExercisesStatus.value.files.length > 0
})

// 测试状态判断方法
const getTestStatusType = (lesson) => {
  console.log('getTestStatusType:', {
    lessonId: lesson.lessonId,
    lessonName: lesson.lessonName,
    hasQuestion: lesson.hasQuestion
  })
  
  if (lesson.hasQuestion === 0) {
    return 'info' // 无测试
  } else if (lesson.hasQuestion === 1) {
    return 'success' // 已发布
  } else if (lesson.hasQuestion === 2) {
    return 'warning' // 草稿状态
  } else {
    return 'info' // 其他未知状态
  }
}

const getTestStatusText = (lesson) => {
  console.log('getTestStatusText:', {
    lessonId: lesson.lessonId,
    lessonName: lesson.lessonName,
    hasQuestion: lesson.hasQuestion
  })
  
  if (lesson.hasQuestion === 0) {
    return '无测试'
  } else if (lesson.hasQuestion === 1) {
    return '已发布'
  } else if (lesson.hasQuestion === 2) {
    return '草稿中'
  } else {
    return '未知状态'
  }
}

// 题目管理状态方法
const canEditTest = () => {
  // 状态0：创建新测试 或 状态1：待发布状态 - 可以编辑
  // 状态2：已发布状态 - 不可编辑
  return currentTestStatus.value === 0 || currentTestStatus.value === 1
}

const getStatusAlertTitle = () => {
  switch (currentTestStatus.value) {
    case 0:
      return '创建新测试'
    case 1:
      return '编辑测试（待发布状态）'
    case 2:
      return '查看已发布测试'
    default:
      return '测试管理'
  }
}

const getStatusAlertDescription = () => {
  switch (currentTestStatus.value) {
    case 0:
      return '这个课时还没有创建测试，您可以添加题目并保存为草稿或直接发布'
    case 1:
      return '测试正在编辑中（待发布状态），您可以继续添加、修改题目，或者发布给学生'
    case 2:
      return '测试已经发布给学生，无法再进行修改，只能查看内容'
    default:
      return '正在加载测试状态...'
  }
}

const getStatusAlertType = () => {
  switch (currentTestStatus.value) {
    case 0:
      return 'success'
    case 1:
      return 'warning'
    case 2:
      return 'info'
    default:
      return 'info'
  }
}

const getQuestionListTitle = () => {
  if (!currentLesson.value) return '题目列表'
  if (questionsList.value.length === 0) {
    return canEditTest() ? '开始添加题目' : '暂无题目'
  } else {
    return `题目列表 (${questionsList.value.length}题)`
  }
}

// API方法
const getCourseById = (courseId) => {
  return request.get('/api/course/findOne', {
    params: { courseId }
  })
}

const endCourseById = (courseId) => {
  return request.post('/api/course/over', null, {
    params: { courseId }
  })
}

const updateCourseComment = (courseId, comment) => {
  return request.post('/api/course/edit', null, {
    params: { courseId, comment }
  })
}

const getStudentsByCourseId = (courseId) => {
  return request.get('/api/enroll/list/course', {
    params: { courseId }
  })
}

const dismissStudent = (studentId, courseId) => {
  return request.post('/api/enroll/dismiss', null, {
    params: { studentId, courseId }
  })
}

// 主要功能方法
const loadCourseInfo = async () => {
  try {
    loading.value = true
    const courseId = route.params.id
    const result = await getCourseById(courseId)
    
    if (result.code === 0) {
      courseInfo.value = result.data
    } else {
      showDetailedError(result, '获取课程信息失败')
    }
  } catch (error) {
    handleException(error, '加载课程信息')
  } finally {
    loading.value = false
  }
}

const loadLessons = async () => {
  try {
    lessonsLoading.value = true
    
    // 直接调用 /api/lesson/list 接口
    const result = await request.get('/api/lesson/list', {
      params: {
        courseId: route.params.id
      }
    })
    
    if (result.code === 0) {
      lessonsList.value = result.data || []
      
      console.log('loadLessons: 加载到的课时数据:', lessonsList.value.map(l => ({
        lessonId: l.lessonId,
        lessonName: l.lessonName,
        hasQuestion: l.hasQuestion
      })))
      
      // 检测每个课时的实际题目状态
      await updateAllLessonsQuestionStatus()
      
      // 为每个有测试的课时加载完成人数
      for (const lesson of lessonsList.value) {
        if (lesson.hasQuestion === 1) {
          try {
            // 调用 /api/lesson/getListScores 接口获取该课时的所有学生成绩
            const scoresResult = await request.get('/api/lesson/getListScores', {
              params: {
                lessonId: lesson.lessonId
              }
            })
            
            if (scoresResult.code === 0 && scoresResult.data) {
              // 统计有成绩的学生数量（score不为null的学生）
              const completedCount = scoresResult.data.filter(item => item.score !== null).length
              lesson.completedCount = completedCount
              console.log(`课时 ${lesson.lessonName} 完成测试人数: ${completedCount}`)
            } else {
              lesson.completedCount = 0
              console.warn(`获取课时 ${lesson.lessonName} 成绩列表失败:`, scoresResult.message)
            }
          } catch (error) {
            console.error(`获取课时 ${lesson.lessonName} 完成人数失败:`, error)
            lesson.completedCount = 0
          }
        } else {
          lesson.completedCount = 0
        }
      }
    } else {
      ElMessage.error(result.message || '获取课时列表失败')
    }
  } catch (error) {
    console.error('加载课时失败:', error)
    ElMessage.error('加载课时失败')
  } finally {
    lessonsLoading.value = false
  }
}

const loadStudents = async () => {
  try {
    studentsLoading.value = true
    const result = await getStudentsByCourseId(route.params.id)
    
    if (result.code === 0) {
      studentsList.value = result.data || []
    } else {
      ElMessage.error(result.message || '获取学生列表失败')
    }
  } catch (error) {
    console.error('加载学生失败:', error)
    ElMessage.error('加载学生失败')
  } finally {
    studentsLoading.value = false
  }
}

const loadScores = async () => {
  try {
    scoresLoading.value = true
    
    if (courseInfo.value.isOver === 1) {
      // 只有结课后才加载成绩
      // TODO: 调用获取总成绩的API
      // 这里应该调用类似 /api/course/finalScores?courseId=${courseId} 的接口
      ElMessage.info('成绩管理功能开发中...')
      
      // 模拟数据计算
      if (scoresList.value.length > 0) {
        const scores = scoresList.value.map(item => item.finalScore || 0)
        averageScore.value = scores.reduce((sum, score) => sum + score, 0) / scores.length
        passRate.value = (scores.filter(score => score >= 60).length / scores.length) * 100
        maxScore.value = Math.max(...scores)
      }
    }
  } catch (error) {
    console.error('加载成绩失败:', error)
    ElMessage.error('加载成绩失败')
  } finally {
    scoresLoading.value = false
  }
}

// 课程信息编辑
const startEditDescription = () => {
  editingDescription.value = true
  descriptionForm.comment = courseInfo.value.comment || ''
}

const cancelEditDescription = () => {
  editingDescription.value = false
  descriptionForm.comment = ''
}

const saveDescription = async () => {
  try {
    const result = await updateCourseComment(courseInfo.value.id, descriptionForm.comment)
    
    if (result.code === 0) {
      courseInfo.value.comment = descriptionForm.comment
      editingDescription.value = false
      ElMessage.success('课程简介更新成功')
    } else {
      ElMessage.error(result.message || '更新失败')
    }
  } catch (error) {
    console.error('更新课程简介失败:', error)
    ElMessage.error('更新失败')
  }
}

// 文件上传处理
const handleUploadSuccess = (response) => {
  console.log('上传成功:', response)
  ElMessage.success('文件上传成功')
  // TODO: 更新文件列表
}

const handleUploadError = (error) => {
  console.error('上传失败:', error)
  ElMessage.error('文件上传失败')
}

const handleFileUploadSuccess = (response) => {
  console.log('课时文件上传成功:', response)
  ElMessage.success('课时文件上传成功')
}

// 课程资料上传相关方法
const beforeCourseUpload = (file) => {
  // 检查文件大小（限制为50MB）
  const isLt50M = file.size / 1024 / 1024 < 50
  if (!isLt50M) {
    ElMessage.error('文件大小不能超过50MB!')
    return false
  }
  
  // 检查文件类型
  const allowedTypes = ['.pdf', '.doc', '.docx', '.txt', '.md']
  const fileName = file.name.toLowerCase()
  const isValidType = allowedTypes.some(type => fileName.endsWith(type))
  
  if (!isValidType) {
    ElMessage.error('只支持PDF、Word、TXT、MD格式文件!')
    return false
  }
  
  return true
}

const handleCourseUploadProgress = (event, file, fileList) => {
  courseUploading.value = true
  console.log('课程资料上传进度:', event.percent)
}

const handleCourseUploadSuccess = (response, file, fileList) => {
  courseUploading.value = false
  console.log('课程资料上传成功:', response)
  
  // AI端API直接返回数据，response就是响应数据
  if (response.message) {
    ElMessage.success(response.message)
  } else {
    ElMessage.success('课程资料上传成功')
  }
  
  // 重新加载课程资料列表
  loadCourseMaterials()
}

const handleCourseUploadError = (error, file, fileList) => {
  courseUploading.value = false
  console.error('课程资料上传失败:', error)
  ElMessage.error('课程资料上传失败，请重试')
}

// 加载课程资料列表
const loadCourseMaterials = async () => {
  try {
    courseMaterialsLoading.value = true
    
    const userId = authStore.user?.id
    const courseId = route.params.id
    
    console.log('loadCourseMaterials 参数:', {
      userId,
      courseId,
      userIdType: typeof userId,
      courseIdType: typeof courseId,
      authStoreUser: authStore.user
    })
    
    // 检查参数是否有效
    if (!userId) {
      console.error('用户ID为空')
      ElMessage.error('用户信息获取失败')
      return
    }
    
    if (!courseId) {
      console.error('课程ID为空')
      ElMessage.error('课程信息获取失败')
      return
    }
    
    // AI端API直接返回数据，不使用request拦截器
    const response = await axios.get(`/ai/v1/list/resources/${userId}/${courseId}`)
    
    console.log('loadCourseMaterials API响应:', response.data)
    
    const result = response.data
    
    if (result.files) {
      courseMaterialsList.value = result.files
      console.log('课程资料列表加载成功:', result.files)
    } else {
      courseMaterialsList.value = []
      console.warn('课程资料列表为空')
    }
  } catch (error) {
    console.error('加载课程资料列表失败:', error)
    courseMaterialsList.value = []
    ElMessage.error('加载课程资料列表失败')
  } finally {
    courseMaterialsLoading.value = false
  }
}

// 下载课程资料
const downloadCourseMaterial = async (file) => {
  try {
    const downloadUrl = `/ai/v1/download/resource/${authStore.user?.id}/${route.params.id}/${file.filename}`
    
    // 创建一个隐藏的a标签来下载文件
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = file.filename
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('开始下载文件')
  } catch (error) {
    console.error('下载课程资料失败:', error)
    ElMessage.error('下载失败，请重试')
  }
}



// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const downloadMaterial = (file) => {
  // TODO: 实现文件下载
  ElMessage.info('文件下载功能开发中...')
}

const deleteMaterial = (file) => {
  // TODO: 实现文件删除
  ElMessage.info('文件删除功能开发中...')
}

// 课时管理
const addLesson = async () => {
  try {
    await lessonFormRef.value.validate()
    
    const result = await addLessonApi(route.params.id, lessonForm.lessonName)
    
    if (result.code === 0) {
      ElMessage.success('课时添加成功')
      showAddLessonDialog.value = false
      lessonForm.lessonName = ''
      loadLessons()
    } else {
      ElMessage.error(result.message || '添加失败')
    }
  } catch (error) {
    console.error('添加课时失败:', error)
    ElMessage.error('添加失败')
  }
}

const deleteLesson = async (lesson) => {
  try {
    // 检查是否已发布测试
    if (lesson.hasQuestion === 1) {
      showError('该课时已发布测试，无法删除')
      return
    }
    
    await ElMessageBox.confirm(
      `确定要删除课时 "${lesson.lessonName}" 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 调用删除课时API
    const result = await request.post('/api/lesson/delete', null, {
      params: {
        lessonId: lesson.lessonId
      }
    })
    
    if (result.code === 0) {
      showSuccess('课时删除成功')
      loadLessons()
    } else {
      showDetailedError(result, '删除课时失败')
    }
  } catch (error) {
    if (error === 'cancel') {
      // 用户取消
      return
    }
    handleException(error, '删除课时')
  }
}

const manageLessonFiles = (lesson) => {
  console.log('manageLessonFiles 被调用，课时数据:', lesson)
  currentLesson.value = lesson
  showFileDialog.value = true
  
  // 重置文件列表
  lessonFilesList.value = []
  lessonUploadedFiles.value = []
  
  // 加载课时文件列表和状态
  loadLessonFiles()
  loadLessonOutlineStatus()
  loadLessonExercisesStatus()
}

// 课时文件管理相关方法
const getLessonUploadData = (lessonId) => ({
  session_id: Date.now().toString(),
  user_id: authStore.user?.id || '',
  is_teacher: true,
  course_id: route.params.id,
  lesson_num: `lesson${lessonId}`,
  file_encoding: 'utf-8',
  is_resource: true,
  is_ask: false
})

const beforeLessonFileUpload = (file) => {
  // 检查文件大小（限制为50MB）
  const isLt50M = file.size / 1024 / 1024 < 50
  if (!isLt50M) {
    ElMessage.error('文件大小不能超过50MB!')
    return false
  }
  
  // 检查文件类型
  const allowedTypes = ['.pdf', '.doc', '.docx', '.txt', '.md']
  const fileName = file.name.toLowerCase()
  const isValidType = allowedTypes.some(type => fileName.endsWith(type))
  
  if (!isValidType) {
    ElMessage.error('只支持PDF、Word、TXT、MD格式文件!')
    return false
  }
  
  return true
}

const handleLessonFileUploadProgress = (event, file, fileList) => {
  lessonFileUploading.value = true
  console.log('课时文件上传进度:', event.percent)
}

const handleLessonFileUploadSuccess = (response, file, fileList) => {
  lessonFileUploading.value = false
  console.log('课时文件上传成功:', response)
  
  if (response.message) {
    ElMessage.success(response.message)
  } else {
    ElMessage.success('课时文件上传成功')
  }
  
  // 将上传成功的文件添加到实际上传文件列表
  lessonUploadedFiles.value.push({
    name: file.name,
    url: response.url || file.url,
    status: 'success'
  })
  
  console.log('实际上传文件列表:', lessonUploadedFiles.value)
  console.log('hasLessonFiles:', hasLessonFiles.value)
  
  // 延迟重新加载课时文件列表，确保服务器文件已保存
  setTimeout(() => {
    loadLessonFiles()
  }, 1000)
}

const handleLessonFileUploadError = (error, file, fileList) => {
  lessonFileUploading.value = false
  console.error('课时文件上传失败:', error)
  ElMessage.error('课时文件上传失败，请重试')
}

// 加载课时文件列表
const loadLessonFiles = async () => {
  if (!currentLesson.value) return
  
  try {
    const userId = authStore.user?.id
    const courseId = route.params.id
    const lessonNum = `lesson${currentLesson.value.lessonId}`
    
    console.log('loadLessonFiles 参数:', { userId, courseId, lessonNum })
    
    const response = await axios.get(`/ai/v1/list/resources/${userId}/${courseId}`)
    const result = response.data
    
    console.log('loadLessonFiles 原始文件列表:', result.files)
    
    if (result.files) {
      // 过滤出当前课时的文件 - 修改过滤逻辑
      const filteredFiles = result.files.filter(file => {
        // 检查文件名是否包含课时编号，或者检查文件是否属于当前课时
        const filename = file.filename.toLowerCase()
        const lessonNumLower = lessonNum.toLowerCase()
        
        // 如果文件名包含课时编号，或者文件属于当前课时的资源
        return filename.includes(lessonNumLower) || 
               filename.includes(`lesson${currentLesson.value.lessonId}`) ||
               // 如果是当前课时的资源文件，也包含在内
               (file.course_id === courseId && file.lesson_num === lessonNum)
      })
      
      lessonFilesList.value = filteredFiles
      
      // 同时更新实际上传文件列表，但保留已上传的文件
      const serverFiles = filteredFiles.map(file => ({
        name: file.filename,
        url: file.url || file.download_url,
        status: 'success'
      }))
      
      // 合并服务器文件和已上传文件，避免重复
      const existingFiles = lessonUploadedFiles.value || []
      const mergedFiles = [...existingFiles]
      
      serverFiles.forEach(serverFile => {
        const exists = mergedFiles.find(f => f.name === serverFile.name)
        if (!exists) {
          mergedFiles.push(serverFile)
        }
      })
      
      lessonUploadedFiles.value = mergedFiles
      
      console.log('loadLessonFiles 过滤后文件列表:', filteredFiles)
      console.log('实际上传文件列表:', lessonUploadedFiles.value)
    } else {
      lessonFilesList.value = []
      lessonUploadedFiles.value = []
      console.log('loadLessonFiles 没有文件')
    }
  } catch (error) {
    console.error('加载课时文件列表失败:', error)
    lessonFilesList.value = []
    lessonUploadedFiles.value = []
  }
}

// 生成教学大纲
const generateOutline = async (lesson) => {
  try {
    outlineGenerating.value = true
    
    const requestData = {
      user_id: authStore.user?.id,
      session_id: Date.now().toString(),
      course_id: route.params.id,
      lesson_num: `lesson${lesson.lessonId}`,
      is_teacher: true,
      max_words: 1000
    }
    
    console.log('生成教学大纲请求:', requestData)
    
    const response = await axios.post('/ai/v1/create/outline', requestData)
    const result = response.data
    
    console.log('教学大纲生成响应:', result)
    
    if (result.success) {
      ElMessage.success(result.message || '教学大纲生成成功')
      // 延迟加载状态，确保文件已生成
      setTimeout(() => {
        loadLessonOutlineStatus()
      }, 2000)
    } else {
      ElMessage.error(result.message || '教学大纲生成失败')
    }
  } catch (error) {
    console.error('生成教学大纲失败:', error)
    ElMessage.error('生成教学大纲失败，请重试')
  } finally {
    outlineGenerating.value = false
  }
}

// 生成习题
const generateExercises = async (lesson) => {
  try {
    exercisesGenerating.value = true
    
    const requestData = {
      user_id: authStore.user?.id,
      session_id: Date.now().toString(),
      course_id: route.params.id,
      lesson_num: `lesson${lesson.lessonId}`,
      is_teacher: true,
      question_count: 5,
      difficulty: 'medium',
      max_tokens: 2000,
      temperature: 0.7,
      generation_mode: 'block'
    }
    
    console.log('生成习题请求:', requestData)
    
    const response = await axios.post('/ai/v1/exercise/generate', requestData)
    const result = response.data
    
    console.log('习题生成响应:', result)
    
    if (result.success) {
      ElMessage.success(result.message || '习题生成成功')
      // 延迟加载状态，确保文件已生成
      setTimeout(() => {
        loadLessonExercisesStatus()
      }, 2000)
    } else {
      ElMessage.error(result.message || '习题生成失败')
    }
  } catch (error) {
    console.error('生成习题失败:', error)
    ElMessage.error('生成习题失败，请重试')
  } finally {
    exercisesGenerating.value = false
  }
}

// 加载教学大纲状态
const loadLessonOutlineStatus = async () => {
  if (!currentLesson.value) return
  
  try {
    const userId = authStore.user?.id
    const courseId = route.params.id
    const lessonNum = `lesson${currentLesson.value.lessonId}`
    
    const response = await axios.get(`/ai/v1/list/outlines/${userId}/${courseId}/${lessonNum}`)
    console.log('教学大纲列表响应:', response.data)
    
    if (response.data && response.data.files && response.data.files.length > 0) {
      lessonOutlineStatus.value = response.data
    } else {
      lessonOutlineStatus.value = null
    }
  } catch (error) {
    console.error('加载教学大纲状态失败:', error)
    lessonOutlineStatus.value = null
  }
}

// 加载习题状态
const loadLessonExercisesStatus = async () => {
  if (!currentLesson.value) return
  
  try {
    const userId = authStore.user?.id
    const courseId = route.params.id
    const lessonNum = `lesson${currentLesson.value.lessonId}`
    
    console.log('loadLessonExercisesStatus 参数:', { userId, courseId, lessonNum })
    
    // 使用正确的习题列表API路径
    const response = await axios.get(`/ai/v1/exercise/list/${userId}/${courseId}/${lessonNum}?is_teacher=true`)
    console.log('习题列表响应:', response.data)
    
    // 检查响应格式并处理 - 习题API返回格式：{ success: true, data: [...], total: 2, message: "..." }
    if (response.data && response.data.success && response.data.data && response.data.data.length > 0) {
      console.log('原始习题文件数据:', response.data.data)
      
      // 转换为前端期望的格式，与教学大纲保持一致
      lessonExercisesStatus.value = {
        files: response.data.data.map(file => {
          console.log('处理文件:', file)
          console.log('文件大小:', file.file_size, '类型:', typeof file.file_size)
          
          return {
            filename: file.filename,
            size: file.file_size || 0, // 使用后端返回的实际文件大小
            created_time: file.created_time || file.metadata?.generated_at || '',
            download_url: `/ai/v1/exercise/download/${userId}/${courseId}/${lessonNum}/${file.filename}?is_teacher=true`
          }
        }),
        total_files: response.data.total,
        course_id: courseId,
        lesson_num: lessonNum,
        user_id: userId,
        is_teacher: true
      }
      console.log('习题状态已更新:', lessonExercisesStatus.value)
    } else {
      lessonExercisesStatus.value = null
      console.log('没有找到习题文件')
    }
    
    console.log('hasExercises 计算属性值:', hasExercises.value)
  } catch (error) {
    console.error('加载习题状态失败:', error)
    lessonExercisesStatus.value = null
  }
}

// 下载教学大纲
const downloadOutline = async (lesson) => {
  try {
    if (!lessonOutlineStatus.value?.files || lessonOutlineStatus.value.files.length === 0) {
      ElMessage.warning('教学大纲尚未生成')
      return
    }
    
    const userId = authStore.user?.id
    const courseId = route.params.id
    const lessonNum = `lesson${lesson.lessonId}`
    const filename = lessonOutlineStatus.value.files[0].filename
    
    const downloadUrl = `/ai/v1/download/outline/${userId}/${courseId}/${lessonNum}/${filename}`
    
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('开始下载教学大纲')
  } catch (error) {
    console.error('下载教学大纲失败:', error)
    ElMessage.error('下载失败，请重试')
  }
}

// 下载习题
const downloadExercises = async (lesson) => {
  try {
    if (!lessonExercisesStatus.value?.files || lessonExercisesStatus.value.files.length === 0) {
      ElMessage.warning('习题尚未生成')
      return
    }
    
    const userId = authStore.user?.id
    const courseId = route.params.id
    const lessonNum = `lesson${lesson.lessonId}`
    const filename = lessonExercisesStatus.value.files[0].filename
    
    // 使用正确的习题下载接口
    const downloadUrl = `/ai/v1/exercise/${userId}/${courseId}/${lessonNum}/${filename}?is_teacher=true`
    
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('开始下载习题')
  } catch (error) {
    console.error('下载习题失败:', error)
    ElMessage.error('下载失败，请重试')
  }
}

// 下载单个教学大纲文件
const downloadOutlineFile = async (file) => {
  try {
    const userId = authStore.user?.id
    const courseId = route.params.id
    const lessonNum = `lesson${currentLesson.value.lessonId}`
    
    const downloadUrl = `/ai/v1/download/outline/${userId}/${courseId}/${lessonNum}/${file.filename}`
    
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = file.filename
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('开始下载教学大纲文件')
  } catch (error) {
    console.error('下载教学大纲文件失败:', error)
    ElMessage.error('下载失败，请重试')
  }
}

// 下载单个习题文件
const downloadExerciseFile = async (file) => {
  try {
    const userId = authStore.user?.id
    const courseId = route.params.id
    const lessonNum = `lesson${currentLesson.value.lessonId}`
    
    // 使用正确的习题下载接口
    const downloadUrl = `/ai/v1/exercise/download/${userId}/${courseId}/${lessonNum}/${file.filename}?is_teacher=true`
    
    console.log('下载习题文件:', {
      userId,
      courseId,
      lessonNum,
      filename: file.filename,
      downloadUrl
    })
    
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = file.filename
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('开始下载习题文件')
  } catch (error) {
    console.error('下载习题文件失败:', error)
    ElMessage.error('下载失败，请重试')
  }
}

// 生成状态相关方法
const getGenerationStatusTitle = () => {
  if (outlineGenerating.value) return '正在生成教学大纲'
  if (exercisesGenerating.value) return '正在生成习题'
  return '生成状态'
}

const getGenerationStatusDescription = () => {
  if (outlineGenerating.value) return 'AI正在分析课时文件并生成教学大纲，请稍候...'
  if (exercisesGenerating.value) return 'AI正在基于课时内容生成习题，请稍候...'
  return ''
}

// 更新课时的题目状态
const updateLessonQuestionStatus = (lessonId, hasQuestionStatus) => {
  const lesson = lessonsList.value.find(l => l.lessonId === lessonId)
  if (lesson) {
    lesson.hasQuestion = hasQuestionStatus
    console.log('updateLessonQuestionStatus: 更新课时状态', {
      lessonId,
      hasQuestion: lesson.hasQuestion,
      lessonName: lesson.lessonName,
      statusMeaning: hasQuestionStatus === 0 ? '无测试' : hasQuestionStatus === 1 ? '已发布' : '草稿'
    })
  }
}

// 检测所有课时的实际题目状态
const updateAllLessonsQuestionStatus = async () => {
  console.log('updateAllLessonsQuestionStatus: 开始检测所有课时的题目状态')
  
  // 并行检测所有课时的题目状态
  const promises = lessonsList.value.map(async (lesson) => {
    try {
      const result = await request.get('/api/map/list', {
        params: {
          lessonId: lesson.lessonId
        }
      })
      
      if (result.code === 0) {
        const questions = result.data || []
        const hasQuestions = questions.length > 0
        
        // 根据实际情况智能更新状态
        if (!hasQuestions && lesson.hasQuestion !== 0) {
          // 如果没有题目，但状态不是0，更新为0
          console.log('updateAllLessonsQuestionStatus: 没有题目，更新状态为0', {
            lessonId: lesson.lessonId,
            lessonName: lesson.lessonName,
            oldHasQuestion: lesson.hasQuestion,
            questionCount: questions.length
          })
          lesson.hasQuestion = 0
        } else if (hasQuestions && lesson.hasQuestion === 0) {
          // 如果有题目，但状态是0，说明可能是新添加的题目，设置为草稿状态
          console.log('updateAllLessonsQuestionStatus: 有题目但状态为0，更新为草稿状态', {
            lessonId: lesson.lessonId,
            lessonName: lesson.lessonName,
            oldHasQuestion: lesson.hasQuestion,
            questionCount: questions.length
          })
          lesson.hasQuestion = 2
        }
        // 如果状态是1（已发布），不做修改
      }
    } catch (error) {
      console.error(`检测课时 ${lesson.lessonId} 题目状态失败:`, error)
    }
  })
  
  await Promise.all(promises)
  console.log('updateAllLessonsQuestionStatus: 所有课时状态检测完成')
}

// 自动检测课时测试状态并打开对话框
const openTestDialog = async (lesson) => {
  currentLesson.value = lesson
  
  // 自动检测课时状态
  await detectTestStatus()
  
  await loadCurrentTestQuestions()
  showQuestionDialog.value = true
}

// 检测测试状态的方法
const detectTestStatus = async () => {
  if (!currentLesson.value) {
    console.log('detectTestStatus: 没有当前课时')
    return
  }
  
  console.log('detectTestStatus: 开始检测课时状态', {
    lessonId: currentLesson.value.lessonId,
    lessonName: currentLesson.value.lessonName,
    hasQuestion: currentLesson.value.hasQuestion
  })
  
  try {
    // 先检查是否有任何题目（包括未提交的）
    const allQuestionsResult = await request.get('/api/map/list', {
      params: {
        lessonId: currentLesson.value.lessonId
      }
    })
    
    console.log('detectTestStatus: /api/map/list 响应', allQuestionsResult)
    
    if (allQuestionsResult.code === 0) {
      const allQuestions = allQuestionsResult.data || []
      console.log('detectTestStatus: 所有题目数量', allQuestions.length)
      
      if (allQuestions.length === 0) {
        // 没有任何题目 -> 新测试状态
        currentTestStatus.value = 0
        console.log('detectTestStatus: 设置状态为0（新测试）')
        return
      }
      
      // 如果有题目，根据课时的hasQuestion字段判断状态
      if (currentLesson.value.hasQuestion === 1) {
        // 已发布状态
        currentTestStatus.value = 2
        console.log('detectTestStatus: 设置状态为2（已发布）')
      } else {
        // 草稿状态
        currentTestStatus.value = 1
        console.log('detectTestStatus: 设置状态为1（草稿）')
      }
    } else {
      console.error('detectTestStatus: /api/map/list 返回错误', allQuestionsResult)
      // 发生错误时，根据课时的hasQuestion字段来判断
      if (currentLesson.value.hasQuestion === 1) {
        currentTestStatus.value = 2 // 已发布
        console.log('detectTestStatus: API错误回退，设置状态为2（已发布）')
      } else if (currentLesson.value.hasQuestion === 2) {
        currentTestStatus.value = 1 // 草稿
        console.log('detectTestStatus: API错误回退，设置状态为1（草稿）')
      } else {
        currentTestStatus.value = 0 // 无测试
        console.log('detectTestStatus: API错误回退，设置状态为0（无测试）')
      }
    }
  } catch (error) {
    console.error('检测测试状态失败:', error)
    // 发生错误时，根据课时的hasQuestion字段来判断
    if (currentLesson.value.hasQuestion === 1) {
      currentTestStatus.value = 2 // 已发布
      console.log('detectTestStatus: 异常错误回退，设置状态为2（已发布）')
    } else if (currentLesson.value.hasQuestion === 2) {
      currentTestStatus.value = 1 // 草稿
      console.log('detectTestStatus: 异常错误回退，设置状态为1（草稿）')
    } else {
      currentTestStatus.value = 0 // 无测试
      console.log('detectTestStatus: 异常错误回退，设置状态为0（无测试）')
    }
  }
  
  console.log('detectTestStatus: 最终状态', currentTestStatus.value)
}

const createTest = async (lesson) => {
  await openTestDialog(lesson)
}

const editTest = async (lesson) => {
  await openTestDialog(lesson)
}

const viewTest = async (lesson) => {
  await openTestDialog(lesson)
}

// 查看测试统计
const viewTestStatistics = async (lesson) => {
  currentStatisticsLesson.value = lesson
  showStatisticsDialog.value = true
  await loadTestStatistics(lesson.lessonId)
}

const getUploadData = (lessonId) => ({
  session_id: Date.now().toString(),
  user_id: authStore.user?.id || '',
  is_teacher: true,
  course_id: route.params.id,
  lesson_num: lessonId,
  is_resource: false,
  is_ask: false
})



// 安全解析选项的函数
const parseOptions = (options) => {
  if (typeof options === 'string') {
    try {
      return JSON.parse(options)
    } catch (e) {
      console.error('解析选项JSON失败:', e)
      return { A: '', B: '', C: '', D: '' }
    }
  }
  return options || { A: '', B: '', C: '', D: '' }
}

// 加载测试统计
const loadTestStatistics = async (lessonId) => {
  try {
    testStatisticsLoading.value = true
    
    // 并行获取题目列表和做题记录
    const [questionsRes, recordsRes] = await Promise.all([
      request.get('/api/map/list', { params: { lessonId } }),
      request.get('/api/records/getLessonRecords', { params: { lessonId } })
    ])
    
    if (questionsRes.code === 0 && recordsRes.code === 0) {
      const questions = questionsRes.data || []
      const records = recordsRes.data || []
      
      // 为每个题目计算统计信息
      const statistics = questions.map(question => {
        const questionRecords = records.filter(record => record.questionId === question.questionId)
        const totalAnswers = questionRecords.length
        
        if (totalAnswers === 0) {
          return {
            questionId: question.questionId,
            question: question.question,
            knowledge: question.knowledge,
            answer: question.answer,
            explanation: question.explanation,
            options: parseOptions(question.options),
            totalAnswers: 0,
            correctCount: 0,
            correctRate: 0,
            optionStats: {
              A: { count: 0, percentage: 0, isCorrect: false },
              B: { count: 0, percentage: 0, isCorrect: false },
              C: { count: 0, percentage: 0, isCorrect: false },
              D: { count: 0, percentage: 0, isCorrect: false }
            }
          }
        }
        
        // 统计每个选项的选择次数
        const optionStats = { A: 0, B: 0, C: 0, D: 0 }
        let correctCount = 0
        
        questionRecords.forEach(record => {
          optionStats[record.selectedOption]++
          if (record.isCorrect === 1) {
            correctCount++
          }
        })
        
        // 计算百分比和正确率
        const correctRate = (correctCount / totalAnswers) * 100
        const optionStatsWithPercentage = {}
        
        Object.keys(optionStats).forEach(option => {
          const count = optionStats[option]
          const percentage = (count / totalAnswers) * 100
          optionStatsWithPercentage[option] = {
            count,
            percentage,
            isCorrect: option === question.answer
          }
        })
        
        return {
          questionId: question.questionId,
          question: question.question,
          knowledge: question.knowledge,
          answer: question.answer,
          explanation: question.explanation,
          options: parseOptions(question.options),
          totalAnswers,
          correctCount,
          correctRate,
          optionStats: optionStatsWithPercentage
        }
      })
      
      testStatisticsData.value = statistics
    } else {
      ElMessage.error('获取测试统计数据失败')
      testStatisticsData.value = []
    }
  } catch (error) {
    console.error('加载测试统计失败:', error)
    ElMessage.error('加载测试统计失败')
    testStatisticsData.value = []
  } finally {
    testStatisticsLoading.value = false
  }
}

// 加载当前测试的题目列表
const loadCurrentTestQuestions = async () => {
  if (!currentLesson.value) {
    console.log('loadCurrentTestQuestions: 没有当前课时')
    return
  }
  
  console.log('loadCurrentTestQuestions: 开始加载题目', {
    lessonId: currentLesson.value.lessonId,
    currentStatus: currentTestStatus.value
  })
  
  try {
    if (currentTestStatus.value === 0) {
      // 状态0：新测试，题目列表为空
      questionsList.value = []
      console.log('loadCurrentTestQuestions: 状态0，清空题目列表')
    } else if (currentTestStatus.value === 1) {
      // 状态1：草稿状态，获取所有题目（包括未提交的）
      console.log('loadCurrentTestQuestions: 状态1，调用 /api/map/list')
      const result = await request.get('/api/map/list', {
        params: {
          lessonId: currentLesson.value.lessonId
        }
      })
      
      console.log('loadCurrentTestQuestions: /api/map/list 响应', result)
      
      if (result.code === 0) {
        const questions = result.data || []
        console.log('loadCurrentTestQuestions: 获取到题目数量', questions.length)
        questionsList.value = questions.map(item => {
          const options = parseOptions(item.options)
          return {
            questionId: item.questionId,
            questionKnowledge: item.knowledge,
            questionContent: item.question,
            questionExplanation: item.explanation,
            questionAnswer: [
              item.answer,
              options.A || '',
              options.B || '',
              options.C || '',
              options.D || ''
            ]
          }
        })
        console.log('loadCurrentTestQuestions: 处理后的题目列表', questionsList.value)
      } else {
        console.error('loadCurrentTestQuestions: API返回错误', result)
        ElMessage.error(result.message || '获取题目列表失败')
      }
    } else if (currentTestStatus.value === 2) {
      // 状态2：已发布，暂时也使用 /api/map/list 获取所有题目
      // TODO: 等 /api/map/listCommitted 接口问题修复后再使用该接口
      console.log('loadCurrentTestQuestions: 状态2，暂时调用 /api/map/list')
      const result = await request.get('/api/map/list', {
        params: {
          lessonId: currentLesson.value.lessonId
        }
      })
      
      console.log('loadCurrentTestQuestions: /api/map/list 响应', result)
      
      if (result.code === 0) {
        const questions = result.data || []
        console.log('loadCurrentTestQuestions: 获取到题目数量', questions.length)
        questionsList.value = questions.map(item => {
          const options = parseOptions(item.options)
          return {
            questionId: item.questionId,
            questionKnowledge: item.knowledge,
            questionContent: item.question,
            questionExplanation: item.explanation,
            questionAnswer: [
              item.answer,
              options.A || '',
              options.B || '',
              options.C || '',
              options.D || ''
            ]
          }
        })
        console.log('loadCurrentTestQuestions: 处理后的题目列表', questionsList.value)
      } else {
        console.error('loadCurrentTestQuestions: API返回错误', result)
        ElMessage.error(result.message || '获取题目列表失败')
      }
    }
  } catch (error) {
    console.error('加载题目列表失败:', error)
    ElMessage.error('加载题目列表失败')
  }
  
  console.log('loadCurrentTestQuestions: 最终题目列表长度', questionsList.value.length)
}

// 题目编辑相关方法
const addNewQuestion = () => {
  questionForm.value = {
    questionId: null,
    questionContent: '',
    parentKnowledge: '',
    childKnowledge: '',
    questionAnswer: ['', '', '', '', ''],
    questionExplanation: ''
  }
  showQuestionEditDialog.value = true
  // 清除之前的验证状态
  nextTick(() => {
    questionFormRef.value?.clearValidate()
  })
}

const editQuestion = (question) => {
  // 处理知识点的拆分
  const knowledge = question.questionKnowledge || ''
  const knowledgeParts = knowledge.split('/')
  
  questionForm.value = {
    questionId: question.questionId,
    questionContent: question.questionContent,
    parentKnowledge: knowledgeParts[0] || '',
    childKnowledge: knowledgeParts[1] || '',
    questionAnswer: [...question.questionAnswer],
    questionExplanation: question.questionExplanation || ''
  }
  
  showQuestionEditDialog.value = true
  // 清除之前的验证状态
  nextTick(() => {
    questionFormRef.value?.clearValidate()
  })
}

const cancelEditQuestion = () => {
  showQuestionEditDialog.value = false
  questionFormRef.value?.resetFields()
}

const saveQuestion = async () => {
  try {
    // 表单验证
    const valid = await questionFormRef.value?.validate()
    if (!valid) return
    
    // 检查是否有当前课时
    if (!currentLesson.value?.lessonId) {
      showError('课时信息缺失，无法保存题目')
      return
    }
    
    saving.value = true

    console.log('保存题目 - 当前课时:', currentLesson.value)
    console.log('保存题目 - 表单数据:', questionForm.value)

    // 合并父子知识点
    const parentKnowledge = questionForm.value.parentKnowledge?.trim() || ''
    const childKnowledge = questionForm.value.childKnowledge?.trim() || ''
    const combinedKnowledge = parentKnowledge && childKnowledge 
      ? `${parentKnowledge}/${childKnowledge}`
      : parentKnowledge || childKnowledge
    
    // 构造请求数据
    const questionData = {
      questionId: questionForm.value.questionId || 0, // 新增时为0，编辑时为实际ID
      teacherId: parseInt(authStore.user?.id || 0),
      knowledge: combinedKnowledge,
      question: questionForm.value.questionContent.trim(),
      options: {
        A: questionForm.value.questionAnswer[1].trim(),
        B: questionForm.value.questionAnswer[2].trim(),
        C: questionForm.value.questionAnswer[3].trim(),
        D: questionForm.value.questionAnswer[4].trim()
      },
      answer: questionForm.value.questionAnswer[0],
      explanation: questionForm.value.questionExplanation?.trim() || ''
    }

    console.log('发送请求数据:', questionData)

    // 调用API保存题目到课时映射
    const result = await request.post(`/api/map/addByEntities?lessonId=${currentLesson.value.lessonId}`, [questionData])
    
    console.log('API响应:', result)
    
    if (result.code === 0) {
      showSuccess(questionForm.value.questionId ? '题目修改成功' : '题目添加成功')
      showQuestionEditDialog.value = false
      
      // 重新检测状态并加载题目列表
      await detectTestStatus()
      await loadCurrentTestQuestions()
      
      // 手动更新当前课时的hasQuestion字段为草稿状态（避免重新加载整个课时列表）
      updateLessonQuestionStatus(currentLesson.value.lessonId, 2)
    } else {
      showDetailedError(result, '保存题目失败')
    }
  } catch (error) {
    handleException(error, '保存题目')
  } finally {
    saving.value = false
  }
}

const deleteQuestion = async (question) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除题目"${question.questionContent}"吗？删除后不可恢复。`, 
      '确认删除', 
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消'
      }
    )
    
    console.log('删除题目:', {
      lessonId: currentLesson.value.lessonId,
      questionId: question.questionId,
      questionContent: question.questionContent
    })
    
    // 调用删除题目的API
    const result = await request.post('/api/map/delete', null, {
      params: {
        lessonId: currentLesson.value.lessonId,
        questionId: question.questionId
      }
    })
    
    console.log('删除题目API响应:', result)
    
    if (result.code === 0) {
      showSuccess('题目删除成功')
      
      // 重新检测状态并加载题目列表
      await detectTestStatus()
      await loadCurrentTestQuestions()
      
      // 如果删除后没有题目了，更新课时状态为无题目
      if (questionsList.value.length === 0) {
        updateLessonQuestionStatus(currentLesson.value.lessonId, 0)
      }
    } else {
      showDetailedError(result, '删除题目失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      handleException(error, '删除题目')
    }
  }
}

// 题库导入相关方法
const importFromQuestionBank = async () => {
  try {
    questionBankLoading.value = true
    console.log('开始加载个人题库, teacherId:', authStore.user?.id)
    
    // 调用获取个人题库的API
    const result = await request.get('/api/question/listByTeacherId', {
      params: {
        teacherId: authStore.user?.id
      }
    })
    
    console.log('个人题库API响应:', result)
    
    if (result.code === 0) {
      const questions = result.data || []
      console.log('获取到题库题目数量:', questions.length)
      
      // 转换数据格式以匹配前端显示
      questionBankList.value = questions.map(item => {
        const options = parseOptions(item.options)
        return {
          questionId: item.questionId,
          questionContent: item.question,
          questionKnowledge: item.knowledge,
          questionAnswer: [
            item.answer,
            options.A || '',
            options.B || '',
            options.C || '',
            options.D || ''
          ],
          questionExplanation: item.explanation || ''
        }
      })
      
      selectedQuestionBankItems.value = []
      showQuestionBankDialog.value = true
      
      if (questions.length === 0) {
        showWarning('您的个人题库为空，请先到题库管理中添加题目')
      }
    } else {
      showDetailedError(result, '获取个人题库失败')
    }
  } catch (error) {
    handleException(error, '获取题库')
  } finally {
    questionBankLoading.value = false
  }
}

const searchQuestionBank = async () => {
  try {
    questionBankLoading.value = true
    console.log('搜索题库, 关键词:', questionBankSearch.value)
    
    // 重新加载完整的题库数据
    const result = await request.get('/api/question/listByTeacherId', {
      params: {
        teacherId: authStore.user?.id
      }
    })
    
    if (result.code === 0) {
      let questions = result.data || []
      console.log('获取到完整题库数量:', questions.length)
      
      // 前端搜索过滤
      if (questionBankSearch.value.trim()) {
        const keyword = questionBankSearch.value.trim().toLowerCase()
        questions = questions.filter(q => 
          q.question.toLowerCase().includes(keyword) ||
          q.knowledge.toLowerCase().includes(keyword)
        )
        console.log('搜索后题目数量:', questions.length)
      }
      
      // 转换数据格式
      questionBankList.value = questions.map(item => {
        const options = parseOptions(item.options)
        return {
          questionId: item.questionId,
          questionContent: item.question,
          questionKnowledge: item.knowledge,
          questionAnswer: [
            item.answer,
            options.A || '',
            options.B || '',
            options.C || '',
            options.D || ''
          ],
          questionExplanation: item.explanation || ''
        }
      })
      
      if (questions.length === 0 && questionBankSearch.value.trim()) {
        showWarning('未找到匹配的题目')
      }
    } else {
      showDetailedError(result, '搜索题库失败')
    }
  } catch (error) {
    handleException(error, '搜索题库')
  } finally {
    questionBankLoading.value = false
  }
}

const handleQuestionBankSelection = (selection) => {
  selectedQuestionBankItems.value = selection
}

const importSelectedQuestions = async () => {
  try {
    if (selectedQuestionBankItems.value.length === 0) {
      showWarning('请选择要导入的题目')
      return
    }
    
    if (!currentLesson.value?.lessonId) {
      showError('课时信息缺失')
      return
    }
    
    importing.value = true
    console.log('开始导入题目:', {
      lessonId: currentLesson.value.lessonId,
      selectedCount: selectedQuestionBankItems.value.length,
      questionIds: selectedQuestionBankItems.value.map(q => q.questionId)
    })
    
    // 调用批量导入题目的API
    const questionIds = selectedQuestionBankItems.value.map(q => q.questionId)
    
    // 构建URL参数，数组参数需要特殊处理
    const params = new URLSearchParams()
    params.append('lessonId', currentLesson.value.lessonId)
    questionIds.forEach(id => {
      params.append('questionIds', id)
    })
    
    console.log('构建的URL参数:', params.toString())
    
    const result = await request.post(`/api/map/addByIds?${params.toString()}`)
    
    console.log('批量导入API响应:', result)
    
    if (result.code === 0) {
      showSuccess(`成功导入 ${selectedQuestionBankItems.value.length} 道题目`)
      showQuestionBankDialog.value = false
      
      // 重新检测测试状态
      await detectTestStatus()
      
      // 重新加载题目列表
      await loadCurrentTestQuestions()
      
      // 更新课时按钮状态为草稿状态
      updateLessonQuestionStatus(currentLesson.value.lessonId, 2)
      
      // 清空选择
      selectedQuestionBankItems.value = []
      questionBankSearch.value = ''
      
      console.log('题目导入完成，当前题目列表长度:', questionsList.value.length)
    } else {
      showDetailedError(result, '导入题目失败')
    }
  } catch (error) {
    handleException(error, '导入题目')
  } finally {
    importing.value = false
  }
}

// 测试操作方法
const saveDraft = async () => {
  try {
    if (!currentLesson.value?.lessonId) {
      ElMessage.error('课时信息缺失')
      return
    }

    if (questionsList.value.length === 0) {
      ElMessage.warning('请先添加一些题目再保存草稿')
      return
    }

    // 草稿保存实际上就是确保题目已经保存，并给用户一个明确的反馈
    // 因为每次添加题目时已经调用了 /api/map/addByEntities 保存到数据库
    // 所以这里主要是提供用户反馈和确认当前状态
    
    // 重新检测状态以确保数据一致性
    await detectTestStatus()
    
    // 重新加载题目列表以确保数据最新
    await loadCurrentTestQuestions()
    
    // 确保课时列表中的按钮状态正确（草稿状态）
    updateLessonQuestionStatus(currentLesson.value.lessonId, 2)
    
    ElMessage.success(`草稿保存成功！当前测试包含 ${questionsList.value.length} 道题目，您可以继续编辑或选择发布`)
    
    console.log('草稿保存完成:', {
      lessonId: currentLesson.value.lessonId,
      questionCount: questionsList.value.length,
      status: currentTestStatus.value
    })
    
  } catch (error) {
    console.error('保存草稿失败:', error)
    ElMessage.error('保存草稿失败')
  }
}

const publishTest = async () => {
  try {
    if (!currentLesson.value?.lessonId) {
      showError('课时信息缺失')
      return
    }

    if (questionsList.value.length === 0) {
      showWarning('请先添加题目再发布测试')
      return
    }

    await ElMessageBox.confirm(
      `确定要发布这个测试吗？发布后将无法修改题目，且该课时将无法删除。\n\n当前测试包含 ${questionsList.value.length} 道题目。`, 
      '确认发布', 
      {
        type: 'warning',
        confirmButtonText: '确认发布',
        cancelButtonText: '取消'
      }
    )
    
    publishing.value = true
    console.log('开始发布测试:', {
      lessonId: currentLesson.value.lessonId,
      questionCount: questionsList.value.length,
      questionIds: questionsList.value.map(q => q.questionId)
    })
    
    // 获取当前测试的所有题目ID
    const questionIds = questionsList.value.map(q => q.questionId)
    
    console.log('构建的发布参数:', {
      lessonId: currentLesson.value.lessonId,
      questionIds: questionIds
    })
    
    // 调用发布测试API
    const result = await commitQuestion(questionsList.value, currentLesson.value.lessonId)
    
    console.log('发布测试API响应:', result)
    
    if (result.code === 0) {
      showSuccess(`测试发布成功！包含 ${questionIds.length} 道题目，学生现在可以开始答题`)
      
      // 更新当前测试状态为已发布
      currentTestStatus.value = 2
      
      // 关闭题目管理对话框
      showQuestionDialog.value = false
      
      // 更新当前课时的发布状态：hasQuestion设置为1表示已发布
      currentLesson.value.hasQuestion = 1
      
      // 更新课时列表中对应课时的发布状态
      const lessonInList = lessonsList.value.find(l => l.lessonId === currentLesson.value.lessonId)
      if (lessonInList) {
        console.log('发布前的课时状态:', {
          lessonId: lessonInList.lessonId,
          lessonName: lessonInList.lessonName,
          hasQuestion: lessonInList.hasQuestion
        })
        
        lessonInList.hasQuestion = 1 // 设置为已发布状态
        
        console.log('发布后的课时状态:', {
          lessonId: lessonInList.lessonId,
          lessonName: lessonInList.lessonName,
          hasQuestion: lessonInList.hasQuestion
        })
        
        // 强制触发Vue响应式更新
        lessonsList.value = [...lessonsList.value]
        
        console.log('强制更新后的课时列表状态:', lessonsList.value.map(l => ({
          lessonId: l.lessonId,
          lessonName: l.lessonName,
          hasQuestion: l.hasQuestion
        })))
      } else {
        console.error('未找到对应的课时:', currentLesson.value.lessonId)
      }
      
      console.log('测试发布完成:', {
        lessonId: currentLesson.value.lessonId,
        questionCount: questionIds.length,
        newStatus: currentTestStatus.value
      })
    } else {
      showDetailedError(result, '发布测试失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      handleException(error, '发布测试')
    }
  } finally {
    publishing.value = false
  }
}

// 学生管理
const showStudentScoreDialog = ref(false)
const currentStudent = ref(null)
const studentScore = ref(null)
const studentScoreLoading = ref(false)

const viewStudentScore = async (student) => {
  currentStudent.value = student
  studentScore.value = null
  showStudentScoreDialog.value = true
  studentScoreLoading.value = true
  
  try {
    console.log('查看学生成绩，参数:', {
      courseId: route.params.id,
      studentId: student.id,
      courseIdType: typeof route.params.id,
      studentIdType: typeof student.id
    })
    
    // 确保参数类型正确
    const courseId = parseInt(route.params.id)
    const studentId = parseInt(student.id)
    
    const score = await getCourseScore(courseId, studentId)
    console.log('获取到的成绩:', score)
    studentScore.value = score
  } catch (error) {
    console.error('获取学生成绩失败:', error)
    ElMessage.error('获取学生成绩失败')
  } finally {
    studentScoreLoading.value = false
  }
}



// 成绩管理
const loadAllScores = async () => {
  try {
    scoresLoading.value = true
    
    if (courseInfo.value.isOver === 1) {
      // 获取所有学生的总成绩
      const promises = studentsList.value.map(async (student) => {
        try {
          const score = await getCourseScore(courseInfo.value.id, student.id)
          return {
            studentId: student.id,
            studentName: student.username,
            finalScore: score || 0
          }
        } catch (error) {
          console.error(`获取学生 ${student.username} 成绩失败:`, error)
          return {
            studentId: student.id,
            studentName: student.username,
            finalScore: 0
          }
        }
      })
      
      const results = await Promise.all(promises)
      scoresList.value = results
      
      // 计算统计数据
      if (scoresList.value.length > 0) {
        const scores = scoresList.value.map(item => item.finalScore || 0)
        averageScore.value = scores.reduce((sum, score) => sum + score, 0) / scores.length
        passRate.value = (scores.filter(score => score >= 60).length / scores.length) * 100
        maxScore.value = Math.max(...scores)
      }
      
      console.log('成绩统计完成:', {
        totalStudents: scoresList.value.length,
        averageScore: averageScore.value,
        passRate: passRate.value,
        maxScore: maxScore.value
      })
    }
  } catch (error) {
    console.error('加载成绩失败:', error)
    ElMessage.error('加载成绩失败')
  } finally {
    scoresLoading.value = false
  }
}

// 加载学生成绩趋势
const loadStudentScoreTrend = async () => {
  if (!selectedStudentId.value) {
    scoreTrendData.value = []
    return
  }
  
  try {
    scoreTrendLoading.value = true
    
    const result = await request.get('/api/course/scoreList', {
      params: {
        courseId: route.params.id,
        studentId: selectedStudentId.value
      }
    })
    
    if (result.code === 0 && result.data) {
      scoreTrendData.value = result.data
      console.log('学生成绩趋势数据:', scoreTrendData.value)
      
      // 渲染折线图
      nextTick(() => {
        renderScoreChart()
      })
    } else {
      scoreTrendData.value = []
      console.warn('获取学生成绩趋势失败:', result.message)
    }
  } catch (error) {
    console.error('获取学生成绩趋势失败:', error)
    scoreTrendData.value = []
  } finally {
    scoreTrendLoading.value = false
  }
}

// 渲染成绩趋势折线图
const renderScoreChart = () => {
  if (!scoreChartRef.value || scoreTrendData.value.length === 0) return
  
  // 准备图表数据
  const chartData = scoreTrendData.value.map(item => ({
    lessonId: item.lessonId,
    score: item.score || 0,
    updateTime: item.updateTime
  }))
  
  // 按课时ID排序
  chartData.sort((a, b) => a.lessonId - b.lessonId)
  
  // 获取课时名称映射
  const lessonNames = lessonsList.value.reduce((map, lesson) => {
    map[lesson.lessonId] = lesson.lessonName
    return map
  }, {})
  
  // 构建图表配置
  const option = {
    title: {
      text: '学生成绩趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const data = params[0]
        return `课时: ${lessonNames[data.dataIndex] || data.dataIndex}<br/>成绩: ${data.value}分`
      }
    },
    xAxis: {
      type: 'category',
      data: chartData.map(item => lessonNames[item.lessonId] || `课时${item.lessonId}`),
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      name: '成绩(分)'
    },
    series: [{
      name: '成绩',
      type: 'line',
      data: chartData.map(item => item.score),
      smooth: true,
      lineStyle: {
        color: '#409EFF'
      },
      itemStyle: {
        color: '#409EFF'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0, color: 'rgba(64, 158, 255, 0.3)'
          }, {
            offset: 1, color: 'rgba(64, 158, 255, 0.1)'
          }]
        }
      }
    }]
  }
  
  // 使用ECharts渲染图表
  const chart = echarts.init(scoreChartRef.value)
  chart.setOption(option)
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

// 查看学生详细成绩
const viewStudentDetailScore = async (student) => {
  try {
    // 设置选中的学生并加载趋势图
    selectedStudentId.value = student.studentId
    await loadStudentScoreTrend()
    
    // 切换到成绩管理标签页
    activeTab.value = 'scores'
    
    ElMessage.success(`已加载 ${student.studentName} 的成绩趋势图`)
  } catch (error) {
    console.error('查看学生详细成绩失败:', error)
    ElMessage.error('查看学生详细成绩失败')
  }
}



const getGrade = (score) => {
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 70) return '中等'
  if (score >= 60) return '及格'
  return '不及格'
}

const getGradeType = (score) => {
  if (score >= 90) return 'success'
  if (score >= 80) return 'success'
  if (score >= 70) return 'warning'
  if (score >= 60) return 'info'
  return 'danger'
}

const getScoreDescription = (score) => {
  if (score >= 90) return '优秀！学生表现非常出色，对课程内容掌握得很好。'
  if (score >= 80) return '良好！学生对课程内容有较好的理解和掌握。'
  if (score >= 70) return '中等！学生对课程内容有一定掌握，但还有提升空间。'
  if (score >= 60) return '及格！学生基本掌握了课程内容，建议加强薄弱环节。'
  return '不及格！学生需要重新学习课程内容，建议提供额外辅导。'
}

// 结束课程
const endCourse = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要结束课程 "${courseInfo.value.name || courseInfo.value.courseName}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const result = await endCourseById(courseInfo.value.id)
    if (result.code === 0) {
      showSuccess('课程已结束')
      loadCourseInfo()
    } else {
      showDetailedError(result, '结束课程失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      handleException(error, '结束课程')
    }
  }
}

// 生命周期
onMounted(async () => {
  await loadCourseInfo()
  await loadLessons()
  await loadStudents()
  
  // 加载课程资料列表
  await loadCourseMaterials()
  
  // 如果课程已结课，自动加载成绩数据
  if (courseInfo.value?.isOver === 1) {
    await loadAllScores()
  }
})
</script>

<style scoped>
.course-detail-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #303133;
}

.course-status {
  margin-bottom: 20px;
}

.visitor-info {
  margin-bottom: 20px;
}

.course-content {
  margin-top: 20px;
}

.course-info-section {
  padding: 20px;
}

.course-description {
  margin-top: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.course-description h4 {
  margin-bottom: 15px;
  color: #303133;
}

.edit-actions {
  margin-top: 10px;
}

.course-materials {
  margin-top: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h4,
.section-header h5 {
  margin: 0;
  color: #303133;
}

.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.lessons-section,
.students-section,
.scores-section {
  padding: 20px;
}

.questions-list {
  margin-top: 20px;
}

.options {
  line-height: 1.5;
}

.options div {
  margin: 2px 0;
}

.question-bank .search-section {
  margin-bottom: 20px;
}

.question-bank .stats-info {
  display: flex;
  align-items: center;
  height: 40px;
  font-size: 14px;
  color: #606266;
}

.question-bank .empty-state {
  padding: 40px;
  text-align: center;
}

.question-bank .options-display {
  font-size: 12px;
  line-height: 1.4;
}

.question-bank .dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.score-summary {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.summary-item {
  text-align: center;
  flex: 1;
}

.summary-item .label {
  color: #909399;
  font-size: 14px;
  margin-bottom: 5px;
}

.summary-item .value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.course-materials h4 {
  margin-bottom: 15px;
  color: #303133;
}

.materials-list {
  margin-top: 20px;
}

.lessons-section,
.students-section,
.scores-section {
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h4,
.section-header h5 {
  margin: 0;
  color: #303133;
}

.score-overview {
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.lesson-scores {
  display: flex;
  flex-wrap: wrap;
}

.visitor-view {
  padding: 20px;
}

.loading-state {
  padding: 20px;
}

.file-upload-section,
.ai-functions,
.file-downloads {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.file-upload-section h5,
.ai-functions h5,
.file-downloads h5 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
}

.questions-list {
  padding: 20px;
}

.options div {
  font-size: 12px;
  line-height: 1.4;
}

.course-ongoing-notice {
  margin-bottom: 20px;
}

/* 学生成绩对话框样式 */
.student-score-dialog {
  padding: 10px;
}

.student-info {
  margin-bottom: 20px;
}

.score-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-header span {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.score-details {
  padding: 10px 0;
}

.score-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.score-item:last-child {
  border-bottom: none;
}

.score-label {
  font-weight: 500;
  color: #606266;
}

.score-value {
  font-weight: bold;
}

.loading-score {
  padding: 20px;
  text-align: center;
}

.no-score {
  padding: 40px;
  text-align: center;
}

.score-description {
  margin-top: 20px;
}

/* 成绩管理页面样式 */
.score-trend-section {
  margin-bottom: 40px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.score-trend-section h5 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #303133;
  font-size: 16px;
}

.student-selector {
  margin-bottom: 20px;
}

.chart-container {
  margin-top: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  background: white;
}

.no-data {
  margin-top: 20px;
  padding: 40px;
  text-align: center;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.course-score-section {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.course-score-section h5 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #303133;
  font-size: 16px;
}

/* 课程资料样式 */
.course-materials {
  margin-top: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.course-materials h4 {
  margin-bottom: 15px;
  color: #303133;
}

.materials-list {
  margin-top: 20px;
}

.empty-materials {
  margin-top: 20px;
  padding: 40px;
  text-align: center;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.upload-demo {
  margin-bottom: 20px;
}

.el-upload__tip {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}

/* 课时文件管理样式 */
.file-upload-section,
.ai-functions,
.file-downloads {
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.file-upload-section h5,
.ai-functions h5,
.file-downloads h5 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
  font-size: 16px;
}

.ai-buttons {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.download-buttons {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.generation-status {
  margin-top: 15px;
}

.file-status {
  margin-top: 15px;
}

/* 测试统计样式 */
.statistics-container {
  padding: 20px;
}

.statistics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e4e7ed;
}

.statistics-header h4 {
  margin: 0;
  color: #303133;
}

.statistics-content {
  min-height: 400px;
}

.no-statistics {
  padding: 40px;
  text-align: center;
}

.statistics-list {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.statistics-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  background: #fafafa;
}

.question-header {
  margin-bottom: 20px;
}

.question-header h5 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 16px;
}

.question-meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.statistics-details {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.overview-stats {
  padding: 15px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.options-chart {
  padding: 15px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.options-chart h6 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 14px;
}

.option-bars {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.option-bar-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.option-label {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 200px;
  flex-shrink: 0;
}

.option-letter {
  font-weight: bold;
  color: #409eff;
  min-width: 20px;
}

.option-text {
  flex: 1;
  font-size: 14px;
  color: #606266;
}

.bar-container {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
  height: 30px;
  background: #f5f7fa;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  min-width: 20px;
  transition: width 0.3s ease;
  border-radius: 4px;
}

.bar-text {
  position: absolute;
  right: 10px;
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.question-explanation {
  padding: 15px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.question-explanation h6 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 14px;
}

.question-explanation p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.question-detail {
  padding: 15px;
}

.question-detail h6 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 14px;
}

.explanation-text {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.no-explanation {
  margin: 0;
  color: #909399;
  font-style: italic;
}
</style> 