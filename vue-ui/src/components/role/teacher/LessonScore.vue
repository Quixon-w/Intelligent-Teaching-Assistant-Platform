<template>
  <div class="dashboard">
    <el-button @click="goBack" type="primary" style="margin-bottom: 20px">返回</el-button>

    <!-- 顶部统计 -->
    <div class="summary-cards">
      <div class="card" v-for="item in summaryData" :key="item.label">
        <div class="icon">{{ item.icon }}</div>
        <div class="info">
          <div class="value">{{ item.value }}</div>
          <div class="label">{{ item.label }}</div>
        </div>
      </div>
    </div>

    <!-- 成绩分布 -->
    <div class="chart-row">
      <div ref="trendChart" class="chart-box"></div>
      <div ref="completionRateChart" class="chart-box"></div>
    </div>

    <!-- 成绩柱状图 -->
    <div ref="lessonScoreTable" class="chart-large"></div>

    <!-- 成绩详情表格 -->
    <el-table :data="scoreDetailList" style="width: 100%; margin-top: 30px" border>
      <el-table-column prop="id" label="学号" />
      <el-table-column prop="name" label="姓名" />
      <el-table-column prop="score" label="成绩" />
      <el-table-column prop="rank" label="排名" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import * as echarts from 'echarts';
import { getLessonScores } from '@/api/course/lesson.js';
import { getAllStudents} from "@/api/course/coures.js";

const route = useRoute();
const router = useRouter();
const lessonId = route.query.lessonId;
const courseId = route.query.courseId;
const trendChart = ref(null);
const lessonScoreTable = ref(null);
const completionRateChart = ref(null);

const scoreList = ref([]);
const scoreMapList = ref([]);
const scoreDetailList = ref([]);

const scoreRanges = ['0-60', '60-70', '70-80', '80-90', '90-100'];

const summaryData = ref([
  { label: '总学生数', value: 0, icon: '🤓' },
  { label: '平均分', value: 0, icon: '🧐' },
  { label: '及格率', value: '0%', icon: '🙂' },
  { label: '优秀率', value: '0%', icon: '🥳' },
]);

const initCharts = async () => {
  try {
    const res = await getLessonScores(lessonId);
    const data = res.data;

    scoreList.value = data.map(d => d.score);
    scoreMapList.value = data.map(d => ({
      studentName: d.student.username,
      score: d.score,
    }));

    const students= await getAllStudents(courseId);
    const studentNum = students.length;

    const total = data.length;
    const average = (scoreList.value.reduce((a, b) => a + b, 0) / total).toFixed(1);
    const passRate = (data.filter(d => d.score >= 60).length / total * 100).toFixed(1) + '%';
    const excellentRate = (data.filter(d => d.score >= 90).length / total * 100).toFixed(1) + '%';
    const completionRate = (total / studentNum * 100).toFixed(1);

    summaryData.value[0].value = studentNum;
    summaryData.value[1].value = average;
    summaryData.value[2].value = passRate;
    summaryData.value[3].value = excellentRate;

    const counts = [0, 0, 0, 0, 0];
    scoreList.value.forEach(score => {
      if (score < 60) counts[0]++;
      else if (score < 70) counts[1]++;
      else if (score < 80) counts[2]++;
      else if (score < 90) counts[3]++;
      else counts[4]++;
    });

    const trendChartInstance = echarts.init(trendChart.value);
    trendChartInstance.setOption({
      title: { text: '成绩分布' },
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      xAxis: { type: 'category', data: scoreRanges },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: counts, barWidth: '60%', name: '人数' }]
    });

    const completionRateChartInstance = echarts.init(completionRateChart.value);
    completionRateChartInstance.setOption({
      title: { text: '完成度' },
      tooltip: {
        trigger: 'item',
        formatter: (params) => {
          let result = `人数：`;
          if (params.name === '完成率') {
            result += `${total}人<br/>`;
          } else {
            result += `${studentNum - total}人<br/>`;
          }
          return result;
        }
      },
      series: [{
        type: 'pie',
        radius: '70%',
        data: [
          { value: parseFloat(completionRate), name: '完成率' },
          { value: 100 - parseFloat(completionRate), name: '未完成率' }
        ],
        label: {
          formatter: '{b}: {d}%'
        }
      }]
    });

    const lessonScoreTableInstance = echarts.init(lessonScoreTable.value);
    lessonScoreTableInstance.setOption({
      title: { text: '学生成绩一览' },
      tooltip: { trigger: 'item', formatter: '{b}：{c} 分' },
      xAxis: { type: 'value', min: 0, max: 100 },
      yAxis: { type: 'category', data: scoreMapList.value.map(i => i.studentName) },
      series: [{
        type: 'bar',
        data: scoreMapList.value.map(i => i.score),
        label: { show: true, position: 'right' }
      }],
      dataZoom: [{ type: 'slider', yAxisIndex: 0, start: 0, end: 50 }]
    });

    scoreDetailList.value = data.map((d, index) => ({
      id: d.student.id ,
      name: d.student.username,
      score: d.score,
      rank: index + 1,
    }));

    window.addEventListener('resize', () => {
      trendChartInstance.resize();
      lessonScoreTableInstance.resize();
      completionRateChartInstance.resize();
    });
  } catch (error) {
    console.error('初始化失败:', error);
  }
};

const goBack = () => router.back();
onMounted(initCharts);
</script>

<style scoped>
.dashboard {
  padding: 20px;
}
.summary-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}
.card {
  flex: 1;
  background: #f6f8fa;
  border-radius: 10px;
  padding: 20px;
  display: flex;
  align-items: center;
}
.card .icon {
  font-size: 32px;
  margin-right: 15px;
}
.card .value {
  font-size: 24px;
  font-weight: bold;
}
.card .label {
  color: #666;
}
.chart-row {
  display: flex;
  margin-bottom: 30px;
}
.chart-box {
  width: 100%;
  height: 300px;
}
.chart-large {
  width: 100%;
  height: 400px;
}
.chart-row {
  display: flex;
  margin-bottom: 30px;
}
.chart-box {
  width: 50%;
  height: 300px;
}

</style>
