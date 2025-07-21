import request from '@/utils/request'

/**
 * 获取学生在某课时的所有错题记录
 * @param {number} lessonId 课时ID
 * @param {number} studentId 学生ID
 * @returns {Promise}
 */
export function getWrongQuestionsByLesson(lessonId, studentId) {
  return request({
    url: `/api/records/wrongQuestions/lesson`,
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
    url: `/api/records/getRecords`,
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
    url: `/api/records/getLessonRecords`,
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
    url: `/api/records/getFinishedTestNum`,
    method: 'get',
    params: {
      studentId
    }
  })
} 