<script lang="ts" setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadProps, UploadUserFile } from 'element-plus'
const userId = ref(sessionStorage.getItem('userId'));
const role = ref(sessionStorage.getItem('role'));
const props = defineProps({
  courseId: {
    required: true
  },
  lessonId: {
    required: true
  }
})

const fileList = ref<UploadUserFile[]>([
])

const handleRemove: UploadProps['onRemove'] = (file, uploadFiles) => {
  console.log(file, uploadFiles)
}

const handlePreview: UploadProps['onPreview'] = (uploadFile) => {
  console.log(uploadFile)
}

const handleExceed: UploadProps['onExceed'] = (files, uploadFiles) => {
  ElMessage.warning(
      `The limit is 3, you selected ${files.length} files this time, add up to ${
          files.length + uploadFiles.length
      } totally`
  )
}

const beforeRemove: UploadProps['beforeRemove'] = (uploadFile, uploadFiles) => {
  return ElMessageBox.confirm(
      `Cancel the transfer of ${uploadFile.name} ?`
  ).then(
      () => true,
      () => false
  )
}

const handleSuccess: UploadProps['onSuccess'] = (response, uploadFile, uploadFiles) => {
  console.log(response, uploadFile, uploadFiles)
}

const handleError: UploadProps['onError'] = (error, uploadFile, uploadFiles) => {
  console.log(error, uploadFile, uploadFiles)
}
</script>

<template>
  <el-upload
      v-model:file-list="fileList"
      class="upload-demo"
      action="http://192.168.240.200:9001/v1/upload"
      method="post"
      :data="{ session_id: 'test', user_id: userId, role: role ,course_id: props.courseId, lesson_num: props.lessonId , is_teacher:true}"
      multiple
      :on-preview="handlePreview"
      :on-remove="handleRemove"
      :before-remove="beforeRemove"
      :on-success="handleSuccess"
      :on-error="handleError"
      :limit="3"
      :on-exceed="handleExceed"
  >
    <el-button type="primary">点击上传</el-button>
    <template #tip>
      <div class="el-upload__tip">
        jpg/png files with a size less than 500KB.
      </div>
    </template>
  </el-upload>
</template>

<style scoped>

</style>
