<template>
  <div>
    <div ref="teacherChart" style="width: 1500px; height: 1000px;"></div>
  </div>
</template>

<script setup>
import {onMounted, ref} from 'vue';
import * as echarts from 'echarts';
const teacherChart = ref(null);
const initCharts = async () => {
  try {

    const teacherChartInstance = echarts.init(teacherChart.value);
    teacherChartInstance.setOption({

      tooltip: {
        trigger: 'item',
        triggerOn: 'mousemove',
        formatter: function (params) {
          return params.data.description || params.name;
        }
      },
      series: [
        {
          type: 'tree',
          top: '5%',
          left: '10%',
          bottom: '5%',
          right: '20%',
          symbol: 'circle',
          symbolSize: 60,
          label: {
            show: true,
            position: 'inside',
            color: '#fff',
            fontSize: 12,
            fontWeight: 'bold'
          },
          itemStyle: {
            color: '#5470C6',
            borderColor: '#333',
            borderWidth: 1
          },
          lineStyle: {
            color: '#aaa',
            width: 2
          },
          data: [
            {
              name: '教师端',
              description: '教师操作系统的入口',
              children: [
                {
                  name: '个人中心',
                  description: '查看、更新个人信息，修改密码等操作',
                  children: [
                    {
                      name: '查看信息',
                      description: '浏览当前教师的基本信息'
                    },
                    {
                      name: '更新信息',
                      description: '编辑并保存新的个人信息'
                    },
                    {
                      name: '修改密码',
                      description: '更改当前账户的登录密码'
                    }
                  ]
                },
                {
                  name: '课程管理',
                  description: '创建、删除、结课及管理课程资源',
                  children: [
                    {
                      name: '新建课程',
                      description: '创建一门新课程，填写课程名称与简介'
                    },
                    {
                      name: '删除课程',
                      description: '删除一门课程'
                    },
                    {
                      name: '结课',
                      description: '结束课程教学周期'
                    },
                    {
                      name: '查看课程信息',
                      description: '查看课程名称、简介、教师等基本信息'
                    },
                    {
                      name: '修改课程简介',
                      description: '更新课程介绍信息'
                    }
                  ]
                },
                {
                  name: '课时管理',
                  description: '管理课程课时、大纲、文件上传与测试题生成',
                  children: [
                    {
                      name: '添加课时',
                      description: '为课程添加新的教学课时'
                    },
                    {
                      name: '创建课程大纲',
                      description: '基于AI自动生成课程教学大纲'
                    },
                    {
                      name: '上传文件',
                      description: '上传该课时相关的教学资料'
                    },
                    {
                      name: '下载大纲',
                      description: '下载已生成的课程大纲文档'
                    },
                    {
                      name: '预览大纲',
                      description: '在线查看课程大纲内容'
                    },
                    {
                      name: '创建测试',
                      description: '为课时生成随堂测验题目'
                    },
                    {
                      name: '查看测试',
                      description: '查看学生完成测验的情况'
                    },
                    {
                      name: '查看成绩',
                      description: '查看学生答题得分情况'
                    }
                  ]
                },
                {
                  name: '成绩分析',
                  description: '统计学生成绩、生成图表报告',
                  children: [
                    {
                      name: '查看学生成绩',
                      description: '查看每位学生的课程总成绩'
                    },
                    {
                      name: '查看测试完成情况',
                      description: '查看每个测验的学生答题详情及得分'
                    },
                    {
                      name: '生成图表报告',
                      description: '通过图表展示成绩分布、平均分等数据'
                    }
                  ]
                },
                {
                  name: '学生管理',
                  description: '查看和管理所教班级的学生信息',
                  children: [
                    {
                      name: '添加学生',
                      description: '将学生加入当前课程'
                    },
                    {
                      name: '删除学生',
                      description: '从课程中移除某个学生'
                    },
                    {
                      name: '退课处理',
                      description: '处理学生主动或被动退课请求'
                    }
                  ]
                },
                {
                  name: 'AI助手',
                  description: 'AI辅助教学工具，提供智能化支持',
                  children: [
                    {
                      name: '生成课程大纲',
                      description: '调用AI接口自动创建结构化教学大纲'
                    },
                    {
                      name: '生成测验题',
                      description: '使用AI自动生成随堂练习或作业题目'
                    }
                  ]
                }
              ]
            }
          ],
          expandAndCollapse: true,
          initialTreeDepth: 2,
          animationDuration: 750,
          nodePadding: 30
        }
      ]


    })
  } catch (error) {
    console.error('图表加载失败:', error);
  }
};

onMounted(initCharts);
</script>
