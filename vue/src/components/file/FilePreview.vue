<script setup lang='ts'>
import VueOfficeDocx from '@vue-office/docx'
import '@vue-office/docx/lib/index.css'
import {ref} from "vue";

const props = defineProps({
  courseId: {
    required: true
  },
  lessonId: {
    required: true
  }
})
const filesrc=ref("");
let loading = ref(false)

const renderedHandler = () => {
  loading.value = false;
  console.log("渲染完成")
}
const errorHandler = () => {
  loading.value = false;
  console.log("渲染失败")
}
</script>

<template>
    <vue-office-docx
        :src=filesrc
        style="width: 100%;height: 100%"
        @rendered="renderedHandler"
        @error="errorHandler"
    />
</template>

<style scoped >
.box {
  width: 100%;
  height: 75vh;
  height: 100%;
  background-color: #fff;
  box-sizing: border-box;
  overflow: auto;

}
.con{
  display: flex;
  justify-content: center;
  align-items: center;
  img{
    max-width: 100%;
    max-height: 100%;
  }
}
</style>
