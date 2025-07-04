<template>
  <div>
    <div ref="studentChart" style="width: 1500px; height: 1000px;"></div>
  </div>
</template>

<script setup>
import {onMounted, ref} from 'vue';
import * as echarts from 'echarts';
const studentChart = ref(null);
const initCharts = async () => {
  try {

    const studentChartInstance = echarts.init(studentChart.value);
    studentChartInstance.setOption({

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
              name: '学生端',
              description: '学生操作系统的入口',
              children: [
                {
                  name: '个人中心',
                  description: '管理个人信息',
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
                  description: '创建课程内容、试题等教学资源等',
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
                  description: '给学生分配作业任务',
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
                  description: 'ai助手',
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
