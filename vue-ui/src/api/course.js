import request from '@/utils/request.js'

// 获取课程列表（分页）
export function getCourses(pageNum, pageSize, courseName, teacherName) {
  return request.get('/api/course/listPage', {
    params: {
      pageNum: pageNum,
      pageSize: pageSize,
      courseName: courseName,
      teacherName: teacherName
    }
  }).then(res => {
    console.log('课程列表:', res)
    return res
  }).catch(err => {
    console.log('获取课程列表失败:', err)
    return err
  })
}

// 获取学生的课程列表
export function getCoursesOfStudent(studentId) {
  return request.get('/api/enroll/list/student', {
    params: {
      studentId: studentId
    }
  }).then(res => {
    console.log('学生课程列表:', res)
    return res
  }).catch(err => {
    console.log('获取学生课程失败:', err)
    return err
  })
}

// 添加课程
export function addCourse(courseName, courseDescription) {
  return request.post('/api/course/add', null, {
    params: {
      courseName: courseName,
      comment: courseDescription
    }
  }).then(res => {
    console.log('添加课程:', res)
    return res
  }).catch(err => {
    console.log('添加课程失败:', err)
    return err
  })
}

// 删除课程
export function deleteCourse(courseId) {
  return request.post('/api/course/delete', null, {
    params: {
      courseId: courseId
    }
  }).then(res => {
    return res
  }).catch(err => {
    return err
  })
}

// 根据ID查找课程
export function findCourseByID(courseId) {
  return request.get('/api/course/findOne', {
    params: {
      courseId: courseId
    }
  }).then(res => {
    return res
  }).catch(err => {
    return err
  })
}

// 更新课程
export function updateCourse(courseId, comment) {
  return request.post('/api/course/edit', null, {
    params: {
      courseId: courseId,
      comment: comment
    }
  }).then(res => {
    return res
  }).catch(err => {
    return err
  })
}

// 获取课程的所有学生
export function getAllStudents(courseId) {
  return request.get('/api/enroll/list/course', {
    params: {
      courseId: courseId
    }
  }).then(res => {
    let data = []
    for (let student of res.data.data) {
      getCourseScore(courseId, student.id).then(scoreRes => {
        student.score = scoreRes
      }).catch(err => {
        console.log('获取学生成绩失败:', err)
      })
      data.push(student)
    }
    return data
  }).catch(err => {
    return err
  })
}

// 结课
export function endCourses(courseId) {
  return request.post('/api/course/over', null, {
    params: {
      courseId: courseId
    }
  }).then(res => {
    return res
  }).catch(err => {
    return err
  })
}

// 选课
export const enrollCourse = (courseId) => {
  return request.post('/api/enroll', null, {
    params: {
      courseId: courseId
    }
  }).then(res => {
    return res
  }).catch(err => {
    return err
  })
}

// 退课
export const dismissCourse = (studentId, courseId) => {
  console.log('退课API调用，参数:', { studentId, courseId })
  
  return request.post('/api/enroll/dismiss', null, {
    params: {
      studentId: studentId,
      courseId: courseId
    }
  }).then(res => {
    console.log('退课API原始响应:', res)
    return res
  }).catch(err => {
    console.error('退课API错误:', err)
    return err
  })
}

// 检查是否是我的课程
export const isMyCourse = (studentId, courseId) => {
  return request.get('/api/enroll/list/student', {
    params: {
      studentId: studentId
    }
  }).then(res => {
    if (res.code === 0 && res.data) {
      for (let i = 0; i < res.data.length; i++) {
        if (res.data[i].course.id == courseId) {
          return true
        }
      }
    }
    return false
  }).catch(err => {
    return err
  })
}

// 获取成绩趋势
export const scoreTrend = (courseId, studentId) => {
  return request.get('/api/course/scoreList', {
    params: {
      courseId: courseId,
      studentId: studentId
    }
  }).then(res => {
    return res.data
  }).catch(err => {
    return err
  })
}

// 获取课程成绩
export function getCourseScore(courseId, studentId) {
  return request.get('/api/course/score', {
    params: {
      courseId: courseId,
      studentId: studentId
    }
  }).then(res => {
    return res.data
  }).catch(err => {
    console.error('getCourseScore API错误:', err)
    return err
  })
}

// 获取热门课程
export function getHotCourses() {
  return request.get('/api/enroll/list/hot', null).then(res => {
    console.log('热门课程:', res)
    return res.data.data
  }).catch(err => {
    return err
  })
}

// 获取课程选课人数
export function getCourseEnrollmentCount(courseId) {
  return request.get('/api/enroll/list/course', {
    params: {
      courseId: courseId
    }
  }).then(res => {
    if (res.code === 0 && res.data) {
      return res.data.length || 0
    }
    return 0
  }).catch(err => {
    console.log('获取课程选课人数失败:', err)
    return 0
  })
} 