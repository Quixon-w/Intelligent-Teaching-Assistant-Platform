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
              name: '学生端',
              description: '学生操作系统的入口',
              children: [
                {
                  name: '个人中心',
                  description: '管理个人信息与账户设置',
                  children: [
                    {
                      name: '查看信息',
                      description: '浏览当前学生的个人信息'
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
                  name: '选课管理',
                  description: '查找、加入或退出课程',
                  children: [
                    {
                      name: '加入课程',
                      description: '选择感兴趣的课程并加入学习'
                    },
                    {
                      name: '退出课程',
                      description: '从已选课程中退课'
                    }
                  ]
                },
                {
                  name: '我的课程',
                  description: '根据所选课程进行学习和任务完成',
                  children: [
                    {
                      name: '查看课程信息',
                      description: '浏览课程名称、教师、简介等基本信息'
                    },
                    {
                      name: '课时学习',
                      description: '查看课时内容，下载或预览教学资料'
                    },
                    {
                      name: '完成测验',
                      description: '在线完成课后测试题目'
                    },
                    {
                      name: '查看测验结果',
                      description: '查看已完成测验的答题情况和得分'
                    },
                    {
                      name: '成绩统计',
                      description: '查看课程整体学习表现和成绩分析图表'
                    },
                    {
                      name: '下载大纲',
                      description: '下载课时对应的课程大纲文件'
                    }
                  ]
                },
                {
                  name: 'AI助手',
                  description: 'AI辅助学习工具，提供答疑与学习建议',
                  children: [
                    {
                      name: '智能问答',
                      description: '向AI提问，获取课程或习题相关解答'
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
