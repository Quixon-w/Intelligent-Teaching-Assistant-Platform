<template>
  <div>
    <el-button @click="goBack" type="primary">返回</el-button>
    <h2>学生成绩分布</h2>
    <div ref="trendChart" style="width: 600px; height: 400px;"></div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import * as echarts from 'echarts';
import { getLessonScores} from '@/api/course/lesson.js'
import {useRoute, useRouter} from "vue-router";
const route = useRoute()
const router = useRouter()
const lessonId = route.query.lessonId
const trendChart = ref(null);
const scoreList = ref([]);
const scoreRanges = ['0-60', '60-70', '70-80', '80-90', '90-100'];

const initCharts = async () => {
  try {
    const res = await getLessonScores(lessonId);
    scoreList.value = res.data.map(item => item.score);

    const counts = Array(scoreRanges.length).fill(0);
    scoreList.value.forEach(score => {
      if (score >= 0 && score < 60) counts[0]++;
      else if (score < 70) counts[1]++;
      else if (score < 80) counts[2]++;
      else if (score < 90) counts[3]++;
      else if (score <= 100) counts[4]++;
    });

    const trendChartInstance = echarts.init(trendChart.value);

    trendChartInstance.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: [
        {
          type: 'category',
          data: scoreRanges,
          axisTick: {
            alignWithLabel: true
          }
        }
      ],
      yAxis: [
        {
          type: 'value'
        }
      ],
      series: [
        {
          name: '人数',
          type: 'bar',
          barWidth: '60%',
          data: counts
        }
      ]
    });

    window.addEventListener('resize', () => {
      trendChartInstance.resize();
    });
  } catch (error) {
    console.error('初始化图表失败:', error);
  }
};

const goBack = () => {
  router.back()
}
onMounted(initCharts);
</script>