/*
 Navicat Premium Data Transfer

 Source Server         : local
 Source Server Type    : MySQL
 Source Server Version : 80037
 Source Host           : localhost:3306
 Source Schema         : itap

 Target Server Type    : MySQL
 Target Server Version : 80037
 File Encoding         : 65001

 Date: 05/07/2025 22:21:57
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for courses
-- ----------------------------
DROP TABLE IF EXISTS `courses`;
CREATE TABLE `courses`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '课程ID',
  `name` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '课程名称',
  `teacher_id` bigint NULL DEFAULT NULL COMMENT '教师ID',
  `teacher_name` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '教师名字',
  `is_over` tinyint(1) NULL DEFAULT 0 COMMENT '是否已经结课',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `comment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '课程简介',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id_in_courses`(`teacher_id` ASC) USING BTREE,
  CONSTRAINT `user_id_in_courses` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 39 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '课程表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for enroll
-- ----------------------------
DROP TABLE IF EXISTS `enroll`;
CREATE TABLE `enroll`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'id',
  `courses_id` bigint NULL DEFAULT NULL COMMENT '课程ID',
  `student_id` bigint NULL DEFAULT NULL COMMENT '学生ID',
  `final_score` float NULL DEFAULT NULL COMMENT '最终成绩',
  `start_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '选课时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `course_id_in_enroll`(`courses_id` ASC) USING BTREE,
  INDEX `student_id_in_enroll`(`student_id` ASC) USING BTREE,
  CONSTRAINT `course_id_in_enroll` FOREIGN KEY (`courses_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `student_id_in_enroll` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 105 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '选课表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for lesson_question_map
-- ----------------------------
DROP TABLE IF EXISTS `lesson_question_map`;
CREATE TABLE `lesson_question_map`  (
  `lesson_id` bigint NOT NULL COMMENT '课时ID',
  `question_id` bigint NOT NULL COMMENT '习题ID',
  PRIMARY KEY (`lesson_id`, `question_id`) USING BTREE,
  INDEX `question_id_in_lesson_question_map`(`question_id` ASC) USING BTREE,
  CONSTRAINT `lessons_id_in_lesson_question_map` FOREIGN KEY (`lesson_id`) REFERENCES `lessons` (`lesson_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `question_id_in_lesson_question_map` FOREIGN KEY (`question_id`) REFERENCES `questions` (`question_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '课时习题对应表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for lessons
-- ----------------------------
DROP TABLE IF EXISTS `lessons`;
CREATE TABLE `lessons`  (
  `lesson_id` bigint NOT NULL AUTO_INCREMENT COMMENT '课时ID',
  `course_id` bigint NULL DEFAULT NULL COMMENT '所属课程ID',
  `lesson_name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '课时名称',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '课时生成时间',
  `has_question` tinyint NULL DEFAULT 0,
  PRIMARY KEY (`lesson_id`) USING BTREE,
  INDEX `course_id_in_lessons`(`course_id` ASC) USING BTREE,
  CONSTRAINT `course_id_in_lessons` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 31 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '课时表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for question_records
-- ----------------------------
DROP TABLE IF EXISTS `question_records`;
CREATE TABLE `question_records`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `student_id` bigint NULL DEFAULT NULL COMMENT '学生ID',
  `lesson_id` bigint NULL DEFAULT NULL COMMENT '课时id',
  `question_id` bigint NULL DEFAULT NULL COMMENT '习题ID',
  `selected_option` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '选择的选项',
  `is_correct` tinyint(1) NULL DEFAULT NULL COMMENT '是否正确',
  `submit_time` timestamp NULL DEFAULT 'now()' COMMENT '提交时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `lesson_id_in_question_records`(`lesson_id` ASC) USING BTREE,
  INDEX `calculate_student_lesson_score`(`student_id` ASC, `lesson_id` ASC) USING BTREE COMMENT 'lessonId联合索引动态计算学生在某课时的成绩',
  INDEX `exercise_id_in_question_records`(`question_id` ASC) USING BTREE,
  CONSTRAINT `exercise_id_in_question_records` FOREIGN KEY (`question_id`) REFERENCES `questions` (`question_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `lesson_id_in_question_records` FOREIGN KEY (`lesson_id`) REFERENCES `lessons` (`lesson_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `student_id_in_question_records` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 69 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '做题记录' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for questions
-- ----------------------------
DROP TABLE IF EXISTS `questions`;
CREATE TABLE `questions`  (
  `question_id` bigint NOT NULL AUTO_INCREMENT COMMENT '习题ID',
  `teacher_id` bigint NULL DEFAULT NULL COMMENT '教师ID',
  `knowledge` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '知识点',
  `question` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '题目',
  `options` json NULL COMMENT '选项',
  `answer` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '答案',
  `explanation` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '解析',
  PRIMARY KEY (`question_id`) USING BTREE,
  INDEX `teacher_id_in_questions`(`teacher_id` ASC) USING BTREE,
  CONSTRAINT `teacher_id_in_questions` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 262 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '习题集' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for scores
-- ----------------------------
DROP TABLE IF EXISTS `scores`;
CREATE TABLE `scores`  (
  `student_id` bigint NOT NULL COMMENT '学生ID',
  `lesson_id` bigint NOT NULL COMMENT '测试ID',
  `score` float NULL DEFAULT NULL COMMENT '测试得分',
  `commen_errors` json NULL COMMENT '高频错误知识点',
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`student_id`, `lesson_id`) USING BTREE,
  INDEX `lessons_id_in_scores`(`lesson_id` ASC) USING BTREE,
  CONSTRAINT `lessons_id_in_scores` FOREIGN KEY (`lesson_id`) REFERENCES `lessons` (`lesson_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `user_id_in_scores` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '课时成绩表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'id',
  `username` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '用户昵称',
  `user_account` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '账号',
  `avatar_url` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '用户头像',
  `gender` tinyint NULL DEFAULT 0 COMMENT '性别 0-未知 1-男 2-女',
  `user_password` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '密码',
  `phone` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '电话',
  `email` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '邮箱',
  `is_delete` tinyint NOT NULL DEFAULT 0 COMMENT '是否删除',
  `user_role` tinyint NOT NULL DEFAULT 0 COMMENT '用户角色 0-学生 1-老师 2-管理员',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `userAccount`(`user_account` ASC) USING BTREE COMMENT '用户账号',
  INDEX `user_name`(`username` ASC) USING BTREE COMMENT '用户昵称'
) ENGINE = InnoDB AUTO_INCREMENT = 34 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户表' ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
