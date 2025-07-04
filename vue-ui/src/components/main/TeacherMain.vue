<template>
  <div class="teacher-layout">
    <TeacherAside />
    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import TeacherAside from '@/components/asides/TeacherAside.vue'
</script>

<style scoped>
.teacher-layout {
  display: flex;
  height: 100vh;
}
.main-content {
  flex: 1;
  padding: 24px;
  background: #f5f6fa;
  overflow: auto;
}
</style>
