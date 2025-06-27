<template>
  <vue-office-pdf :src="iframeUrl.value"/>
</template>

<script setup lang='ts'>
import {onMounted, ref} from 'vue'
//引入VueOfficePdf组件
import VueOfficePdf from '@vue-office/pdf'
import {useRoute} from "vue-router";
import {previewFile} from "@/api/file"
const iframeUrl = ref('C:\\MY\\学习\\暑期实习\\项目\\工作日志_吴佳昊.pdf');
const props = defineProps({
  courseId: {
    required: true
  },
  lessonId: {
    required: true
  }
})
onMounted(async () => {
  console.log(iframeUrl.value);
  /*try {
    const response = await previewFile(props.courseId, props.lessonId);
    console.log(response);
    /!*const blob = await response.blob();
    iframeUrl.value = URL.createObjectURL(blob);
    console.log(iframeUrl.value);*!/
  } catch (error) {
    console.error('Error loading PDF:', error);
  }*/
});
</script>
<style scoped>
</style>
