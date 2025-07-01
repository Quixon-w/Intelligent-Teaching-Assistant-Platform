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
                  description: '查看，更新个人信息，修改密码',
                  children: [
                    {
                      name: '添加学生',
                      description: '添加学生',
                      children: [
                        {
                          name: '添加学生',
                          description: '添加学生',

                        },
                        {
                          name: '删除学生',
                          description: '删除学生'
                        }
                      ]
                    },
                    {
                      name: '删除学生',
                      description: '删除学生' ,
                      children: [
                        {
                          name: '添加学生',
                          description: '添加学生',

                        },
                        {
                          name: '删除学生',
                          description: '删除学生'
                        }
                      ]
                    }
                  ]
                },
                {
                  name: '课程管理',
                  description: '创建课程内容、教学大纲等教学资源',
                  children: [
                    {
                      name: '添加学生',
                      description: '添加学生'
                    },
                    {
                      name: '删除学生',
                      description: '删除学生'
                    }
                  ]
                },
                {
                  name: '课时管理',
                  description: '发布习题，给学生分配作业任务',
                  children: [
                    {
                      name: '添加学生',
                      description: '添加学生'
                    },
                    {
                      name: '删除学生',
                      description: '删除学生'
                    }
                  ]
                },
                {
                  name: '成绩分析',
                  description: '统计学生成绩、生成图表报告',
                  children: [
                    {
                      name: '添加学生',
                      description: '添加学生'
                    },
                    {
                      name: '删除学生',
                      description: '删除学生'
                    }
                  ]
                },
                {
                  name: '学生管理',
                  description: '查看和管理所教班级的学生信息',
                  children: [
                    {
                      name: '添加学生',
                      description: '添加学生'
                    },
                    {
                      name: '删除学生',
                      description: '删除学生'
                    }
                  ]
                },
                {
                  name: 'AI助手',
                  description: 'ai教学助手',
                  children: [
                    {
                      name: '添加学生',
                      description: '添加学生'
                    },
                    {
                      name: '删除学生',
                      description: '删除学生'
                    }
                  ]
                }
              ]
            }
          ],
          expandAndCollapse: true,
          initialTreeDepth: 2,
          animationDuration: 750,
          nodePadding: 30,
        }
      ]
    })
  } catch (error) {
    console.error('图表加载失败:', error);
  }
};

onMounted(initCharts);
</script>
