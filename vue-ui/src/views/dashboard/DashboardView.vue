<script setup>
import {RouterView, useRoute} from 'vue-router'
import {useRouter} from 'vue-router'
import { ElMessage } from 'element-plus'
import CommonAside from '@/components/asides/AdminAside.vue'
import TeacherAside from '@/components/asides/TeacherAside.vue'
import { onExit } from '@/api/dashboard.js'
import StudentAside from '@/components/asides/StudentAside.vue'
import {ref, watch} from "vue";
import PathNameMap from "@/utils/pathname.js";
const router = useRouter();
const route = useRoute();
const role=sessionStorage.getItem('role');
const currentWeb=ref(PathNameMap[route.name]);
watch(() => router.currentRoute.value.path, (toPath) => {currentWeb.value=PathNameMap[toPath];},{immediate: true,deep: true});
const userImage = ref(sessionStorage.getItem('avatarUrl'));
const errorImage = ()=>{
  userImage.value='@/src/assets/logo.svg';
  console.log(userImage.value);
};
const handleCommand = (command) => {
  if (command === 'onExit') {
    onExit().then(res=>{
      sessionStorage.clear();
      router.push('/login');
    }).catch(err=>{
      ElMessage({
        message: '退出失败',
        type: 'error',
      });
    })
  } else if (command === 'toUserControl') {
    router.push('/dashboard/user/central');
  }
};
</script>

<template>
  <el-container class="main-container">
    <el-aside class="sidebar">
      <span v-if="role==='admin'"><CommonAside/></span>
      <span v-else-if="role==='teacher'"><TeacherAside/></span>
      <span v-else-if="role==='student'"><StudentAside/></span>
    </el-aside>
    <el-container>
      <el-header class="header">
        <el-text style="color: #B0C4DE;font-size: 30px">{{currentWeb}}</el-text>
        <div>
          <el-text style="color: #B0C4DE;font-size: 30px">{{role}}</el-text>
          <el-dropdown @command="handleCommand">
            <span>
              <el-avatar :size="50" :src=userImage :on-error="errorImage"></el-avatar>
<!--              <img alt="头像" class="logo" src="http://192.168.10.86:8080/{{sessionStorage.getItem('avatarUrl')}}" onerror="this.src='@/assent/logo.svg'" width="50" height="50"/>-->
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="toUserControl">用户中心</el-dropdown-item>
                <el-dropdown-item command="onExit">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main">
        <Router-view :key="route.path"/>
      </el-main>
    </el-container>
  </el-container>
</template>
<style src="@/assets/css/dashboard/dashboard.css"></style>
<style scoped>
</style>
