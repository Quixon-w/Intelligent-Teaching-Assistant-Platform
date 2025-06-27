<script setup>
import {ref} from "vue";
import StudentMain from "@/components/main/StudentMain.vue";
import TeacherMain from "@/components/main/TeacherMain.vue";
import AdminMain from "@/components/main/AdminMain.vue";

const role=ref(sessionStorage.getItem('role'))
</script>

<template>
  <div v-if="role==='student'">
    <StudentMain/>
  </div>
  <div v-else-if="role==='teacher'">
    <TeacherMain/>
  </div>
  <div v-else-if="role==='admin'">
    <AdminMain/>
  </div>
</template>

<style scoped>

</style>
