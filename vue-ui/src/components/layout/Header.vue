<template>

</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const pageTitle = computed(() => route.meta?.title || '智能教学辅助平台')
</script>

<style scoped>
.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}
.header-title {
  font-size: 22px;
  font-weight: bold;
  color: #303133;
  text-align: center;
  width: 100%;
  letter-spacing: 2px;
}
</style> 