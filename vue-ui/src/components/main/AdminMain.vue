<template>
  <div>
    <div ref="adminChart" style="width: 1500px; height: 1000px;"></div>
  </div>
</template>

<script setup>
import {onMounted, ref} from 'vue';
import * as echarts from 'echarts';
const adminChart = ref(null);
const initCharts = async () => {
  try {

    const adminChartInstance = echarts.init(adminChart.value);
    adminChartInstance.setOption({

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
              name: '管理员端',
              description: '教学平台管理后台入口',
              children: [
                {
                  name: '个人中心',
                  description: '管理管理员账户信息',
                  children: [
                    {
                      name: '查看信息',
                      description: '浏览当前管理员的基本资料'
                    },
                    {
                      name: '更新信息',
                      description: '编辑并保存新的个人信息'
                    },
                    {
                      name: '修改密码',
                      description: '更改当前管理员登录密码'
                    }
                  ]
                },
                {
                  name: '课程管理',
                  description: '管理所有课程资源',
                  children: [
                    {
                      name: '查看课程',
                      description: '分页查询所有课程信息，支持按课程名、教师名过滤'
                    },
                    {
                      name: '删除课程',
                      description: '永久删除一门课程及其关联数据'
                    }
                  ]
                },
                {
                  name: '用户管理',
                  description: '管理平台用户账号',
                  children: [
                    {
                      name: '查看用户',
                      description: '分页查询所有用户信息，包括学生和教师'
                    },
                    {
                      name: '删除用户',
                      description: '删除一个用户账号，支持软删除机制'
                    },
                    {
                      name: '恢复用户',
                      description: '从回收站中恢复被删除的用户账号'
                    },
                    {
                      name: '查看已删用户',
                      description: '查看所有已被标记为删除状态的用户列表'
                    }
                  ]
                },
                {
                  name: 'AI助手',
                  description: 'AI辅助管理工具，提供智能操作建议',
                  children: [
                    {
                      name: '智能问答',
                      description: '向AI提问，获取系统操作、数据管理相关解答'
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
