<script lang="ts" setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadProps, UploadUserFile } from 'element-plus'
const userId = sessionStorage.getItem('userId');
const role = sessionStorage.getItem('role');
const isTeacher = sessionStorage.getItem('role')==='teacher';
const props = defineProps({
  courseId: {
  },
  lessonId: {
  },
  sessionId:{
  },
  isResource:{
    type: Boolean,
    default: false,
  },
  isAsk:{
    type: Boolean,
    default: false,
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
  console.log(response, uploadFile, uploadFiles);
  location.reload();
}

const handleError: UploadProps['onError'] = (error, uploadFile, uploadFiles) => {
  console.log(error, uploadFile, uploadFiles)
}
</script>

<template>
  <el-upload
      v-model:file-list="fileList"
      class="upload-demo"
      action="/api/user/setAvatar"
      method="post"
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
