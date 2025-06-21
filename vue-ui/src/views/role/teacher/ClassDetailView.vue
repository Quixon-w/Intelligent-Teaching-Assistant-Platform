<script setup>
import { useRoute, useRouter } from 'vue-router'
const router = useRouter();
const route=useRoute();
</script>

<template>
<span>Class {{route.params.id}}</span>
</template>

<style scoped>

</style>
