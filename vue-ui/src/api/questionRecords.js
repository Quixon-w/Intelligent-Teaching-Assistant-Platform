import request from '@/utils/request'

/**
 * 获取学生在某课时的错题知识点统计
 * @param {number} lessonId 课时ID
 * @param {number} studentId 学生ID
 * @returns {Promise}
 */
export function getWrongKnowledgeStatsByLesson(lessonId, studentId) {
  return request({
    url: `/api/records/wrongKnowledgeStats/lesson`,
    method: 'get',
    params: {
      lessonId,
      studentId
    }
  })
}

/**
 * 获取学生在某课程的错题知识点统计
 * @param {number} courseId 课程ID
 * @param {number} studentId 学生ID
 * @returns {Promise}
 */
export function getWrongKnowledgeStatsByCourse(courseId, studentId) {
  return request({
    url: `/records/wrongKnowledgeStats/course`,
    method: 'get',
    params: {
      courseId,
      studentId
    }
  })
}

/**
 * 获取学生在某课时的所有错题记录
 * @param {number} lessonId 课时ID
 * @param {number} studentId 学生ID
 * @returns {Promise}
 */
export function getWrongQuestionsByLesson(lessonId, studentId) {
  return request({
    url: `/records/wrongQuestions/lesson`,
    method: 'get',
    params: {
      lessonId,
      studentId
    }
  })
}

/**
 * 获取某学生某课时做题记录
 * @param {number} lessonId 课时ID
 * @param {number} studentId 学生ID
 * @returns {Promise}
 */
export function getStudentLessonRecords(lessonId, studentId) {
  return request({
    url: `/records/getRecords`,
    method: 'get',
    params: {
      lessonId,
      studentId
    }
  })
}

/**
 * 获取某课时所有做题记录
 * @param {number} lessonId 课时ID
 * @returns {Promise}
 */
export function getLessonRecords(lessonId) {
  return request({
    url: `/records/getLessonRecords`,
    method: 'get',
    params: {
      lessonId
    }
  })
}

/**
 * 获取某学生已完成测试数量
 * @param {number} studentId 学生ID
 * @returns {Promise}
 */
export function getFinishedTestNum(studentId) {
  return request({
    url: `/records/getFinishedTestNum`,
    method: 'get',
    params: {
      studentId
    }
  })
} 