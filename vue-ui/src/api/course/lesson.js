import request from '@/utils/request.js'
import { lessonOutlineDownload, lessonOutlineStatus } from "@/api/ai.js";
import qs from "qs";
export function getLessons(courseId) {
  return request.get('/api/lesson/list', {
    params: {
      courseId: courseId
    },
  }).then(res => {
    let lessons = res.data.data;
    for (let lesson of lessons) {
      lessonOutlineStatus(courseId, lesson.lessonId).then(res => {
        lesson.outlineStatus = res;
      }).catch(err => {
        console.log(err);
      });
      lessonOutlineDownload(courseId, lesson.lessonId).then(res => {
        lesson.outlineDownload = res;
      }).catch(err => {
        console.log(err);
      });
      if (sessionStorage.getItem('role') === 'student') {
        lessonQuestionIsFinished(lesson.lessonId, sessionStorage.getItem('userId')).then(res => {
          lesson.isQuestionFinished = res.data.data !== null;
        }).catch(err => {
          console.log(err);
        })
      }
    }
    console.log(lessons);
    return lessons;
  }).catch(err => {
    return err;
  })
}
export function addLesson(courseId, lessonName) {
  return request.post('/api/lesson/add', null, {
    params: {
      courseId: courseId,
      lessonName: lessonName,
    }
  }).then(res => {
    console.log(res);
    return res;
  }).catch(err => {
    return err;
  })
}
export function getLessonQuestions(lessonId) {
  return request.get('/api/map/list', {
    params: {
      lessonId: lessonId
    }
  }).then(res => {
    console.log('getLessonQuestions API响应:', res);

    // 响应拦截器已经处理了错误情况，这里的res已经是成功的响应
    // 检查数据
    if (!res.data || !Array.isArray(res.data)) {
      console.warn('该课时暂无习题数据');
      return [];
    }

    let data = [];
    for (let adata of res.data) {
      try {
        let options = JSON.parse(adata.options);
        let aadata = {
          questionId: adata.questionId,
          questionKonwledge: adata.knowledge,
          questionContent: adata.question,
          questionExplanation: adata.explanation,
          questionAnswer: [adata.answer, options.A, options.B, options.C, options.D],
        }
        data.push(aadata);
      } catch (parseError) {
        console.error('解析题目数据失败:', adata, parseError);
        // 跳过有问题的数据，继续处理其他题目
      }
    }

    console.log('处理后的题目数据:', data);
    return data;
  }).catch(err => {
    console.error('getLessonQuestions API调用失败:', err);
    // 重新抛出错误，让调用方能够正确处理
    throw err;
  })
}
export function getLessonCommittedQuestions(lessonId) {
  return request.get('/api/map/listCommitted', {
    params: {
      lessonId: lessonId
    }
  }).then(res => {
    console.log(res);
    let data = [];
    for (let adata of res.data.data) {
      let options = JSON.parse(adata.options);
      let aadata = {
        questionId: adata.questionId,
        questionKonwledge: adata.knowledge,
        questionContent: adata.question,
        questionExplanation: adata.explanation,
        questionAnswer: [null, 'A、  ' + options.A, 'B、  ' + options.B, 'C、  ' + options.C, 'D、  ' + options.D],
      }
      data.push(aadata);
    }
    console.log(data);
    return data;
  }).catch(err => {
    return err;
  })
}
export function getLessonScores(lessonId) {
  return request.get('/api/lesson/getListScores', {
    params: {
      lessonId: lessonId
    },
  })
    .then(res => {
      return res.data;
    })
    .catch(err => {
      return err;
    })
}
export function saveQuestions(questions, lessonID) {
  // 由于API现在只接受单个Question，我们需要逐个保存
  const savePromises = questions.map(question => {
    const questionData = {
      "teacherId": sessionStorage.getItem("userId"),
      "knowledge": question.questionKonwledge,
      "question": question.questionContent,
      "options": {
        "A": question.questionAnswer[1],
        "B": question.questionAnswer[2],
        "C": question.questionAnswer[3],
        "D": question.questionAnswer[4]
      },
      "answer": question.questionAnswer[0],
      "explanation": question.questionExplanation,
    }
    return request.post('/api/map/addByEntity', questionData, {
      params: {
        lessonId: lessonID
      }
    })
  })

  return Promise.all(savePromises).then(results => {
    console.log('批量保存结果:', results);
    // 返回第一个结果作为代表，或者返回所有结果
    return results[0];
  }).catch(err => {
    return err;
  })
}
export function saveNewQuestion(question, lessonID) {
  const questionData = {
    "teacherId": sessionStorage.getItem("userId"),
    "knowledge": question.questionKonwledge,
    "question": question.questionContent,
    "options": {
      "A": question.questionAnswer[1],
      "B": question.questionAnswer[2],
      "C": question.questionAnswer[3],
      "D": question.questionAnswer[4]
    },
    "answer": question.questionAnswer[0],
    "explanation": question.questionExplanation,
  }
  return request.post('/api/map/addByEntity', questionData, {
    params: {
      lessonId: lessonID
    }
  }).then(res => {
    console.log(res);
    return res;
  }).catch(err => {
    return err;
  });
}
export function commitQuestion(questions, lessonID) {
  let ids = [];
  for (let question of questions) {
    ids.push(question.questionId);
  }
  console.log(ids)
  return request.post('/api/lesson/commit', null, {
    params: {
      lessonId: lessonID,
      questionIds: ids,
    },
    paramsSerializer: params => qs.stringify(params, { arrayFormat: 'repeat' })
  }).then(res => {
    return res;
  }).catch(err => {
    return err;
  })
}
export function deleteQuestion(lessonId, questionId) {
  return request.post('/api/map/delete', null, {
    params: {
      lessonId: lessonId,
      questionId: questionId
    }
  }).then(res => {
    return res;
  }).catch(err => {
    return err;
  })
}
export function getTeacherQuestions(teaccherId) {
  return request.get('/api/question/listByTeacherId', {
    params: {
      teacherId: teaccherId
    }
  }).then(res => {
    let data = [];
    for (let adata of res.data.data) {
      let options = JSON.parse(adata.options);
      let aadata = {
        questionId: adata.questionId,
        questionKonwledge: adata.knowledge,
        questionContent: adata.question,
        questionExplanation: adata.explanation,
        questionAnswer: [adata.answer, options.A, options.B, options.C, options.D],
      }
      data.push(aadata);
    }
    return data;
  }).catch(err => {
    return err;
  })
}
export function addOneQuestion(lessonId, questionId) {
  return request.post('/api/map/addByIds', null, {
    params: {
      lessonId: lessonId,
      questionIds: questionId
    }
  }).then(res => {
    return res;
  }).catch(err => {
    return err;
  })
}
export function saveChangedQuestion(question) {
  return request.post('/api/map/update', {
    questionId: question.questionId,
    teacherId: sessionStorage.getItem("userId"),
    knowledge: question.questionKonwledge,
    question: question.questionContent,
    options: {
      "A": question.questionAnswer[1],
      "B": question.questionAnswer[2],
      "C": question.questionAnswer[3],
      "D": question.questionAnswer[4]
    },
    answer: question.questionAnswer[0],
    explanation: question.questionExplanation
  }).then(res => {
    return res;
  }).catch(err => {
    return err;
  })
}
export function addTeachersQuestion(question) {
  return request.post('/api/question/addOne', {
    teacherId: sessionStorage.getItem("userId"),
    knowledge: question.questionKonwledge,
    question: question.questionContent,
    options: {
      "A": question.questionAnswer[1],
      "B": question.questionAnswer[2],
      "C": question.questionAnswer[3],
      "D": question.questionAnswer[4]
    },
    answer: question.questionAnswer[0],
    explanation: question.questionExplanation
  }).then(res => {
    return res;
  }).catch(err => {
    return err;
  })
}
export function searchFatherQuestion(questionKnowledge) {
  return request.get('/api/question/selectByFather', {
    params: {
      father: questionKnowledge,
      teacherId: sessionStorage.getItem("userId")
    }
  }).then(res => {
    let data = [];
    for (let adata of res.data.data) {
      let options = JSON.parse(adata.options);
      let aadata = {
        questionId: adata.questionId,
        questionKonwledge: adata.knowledge,
        questionContent: adata.question,
        questionExplanation: adata.explanation,
        questionAnswer: [adata.answer, options.A, options.B, options.C, options.D],
      }
      data.push(aadata);
    }
    return data;
  }).catch(err => {
    return err;
  })
}
export function commitQuestionHistory(questions, lessonId) {
  let questionAnswers = [];

  // 确保按顺序提取答案（学生做题时使用answer字段）
  for (let question of questions) {
    const answer = question.answer || '';
    questionAnswers.push(answer);
  }

  console.log('按顺序提交的答案数组:', questionAnswers);
  console.log('课时ID:', lessonId);
  console.log('提交的题目信息:', questions.map(q => ({
    questionId: q.questionId,
    answer: q.answer
  })));

  return request.post('/api/records/add', null, {
    params: {
      lessonId: lessonId,
      answers: questionAnswers,
    },
    paramsSerializer: params => qs.stringify(params, { arrayFormat: 'repeat' })
  }).then(res => {
    console.log('/api/records/add 响应:', res);
    return res;
  }).catch(err => {
    console.error('/api/records/add 错误:', err);
    // 重新抛出错误，让调用方能够正确处理
    throw err;
  })
}
export function getLessonRecords(lessonId, studentId) {
  return request.get('/api/records/getRecords', {
    params: { lessonId, studentId }
  }).then(res => {
    return res;
  }).catch(err => {
    return err;
  })
}

// 获取课时所有学生的做题记录（教师端使用）
export function getLessonAllRecords(lessonId) {
  return request.get('/api/records/getLessonRecords', {
    params: { lessonId }
  }).then(res => {
    return res;
  }).catch(err => {
    return err;
  })
}
export function getLessonQuestionsList(lessonId) {
  return request.get('/api/map/list', {
    params: { lessonId }
  }).then(res => {
    return res;
  }).catch(err => {
    return err;
  })
}
export function lessonQuestionIsFinished(lessonId, studentId) {
  return request.get('/api/records/getLessonRecords', {
    params: { lessonId }
  }).then(res => {
    return res;
  }).catch(err => {
    return err;
  })
}
