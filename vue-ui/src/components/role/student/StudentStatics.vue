<template>
  <div>
    <el-button @click="goBack" type="primary">返回</el-button>
    <h2>练习正确率趋势</h2>
    <div ref="trendChart" style="width: 600px; height: 400px;"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import {scoreTrend} from "@/api/course/coures.js";
import * as echarts from 'echarts';
import {useRoute, useRouter} from "vue-router";
import {getCurrentUser} from "@/api/user/userinfo.js";
const route = useRoute()
const router = useRouter()

const courseId = route.query.courseId
const trendChart = ref(null);
const scoreList = ref([]);
const lessonId = ref([]);

const userInfo = ref({
  id: 0,
});


const initCharts = async () => {
  try {

    const user = await getCurrentUser();
    userInfo.value = user.data;

    const res = await scoreTrend(courseId,userInfo.value.id);

    scoreList.value = res.data.map(item => item.score);
    lessonId.value = res.data.map(item => item.lessonId);
    const trendChartInstance = echarts.init(trendChart.value);
    trendChartInstance.setOption({

      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: lessonId.value,
      },
      yAxis: {
        min: 0,
        max: 100,
        type: 'value'
      },
      series: [
        {
          data: scoreList.value,
          type: 'line',
          areaStyle: {}
        }
      ]
    });
  } catch (error) {
    console.error('图表加载失败:', error);
  }
};
const goBack = () => {
  router.back()
}


onMounted(initCharts);
</script>