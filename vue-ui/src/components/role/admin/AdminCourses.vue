<script setup>
import UserRoleMap from "@/utils/userrole.js";
import {onMounted, ref} from "vue";
import {getCourses} from "@/api/course/coures.js";
import {ElMessage, ElMessageBox} from "element-plus";
import { deleteCourse } from "@/api/course/coures.js";

const tableSetting=ref({
  tableData:[],
  pageSize:5,
  currentPage:1,
  total:0,
  courseName:'',
  teacherName:'',
});
const getData=()=>{
  getCourses(tableSetting.value.currentPage,tableSetting.value.pageSize,tableSetting.value.courseName, tableSetting.value.teacherName).then(res=>{
    tableSetting.value.tableData=res.data.data.records;
    tableSetting.value.total=res.data.data.total;
  }).catch(err=>{
    ElMessage(err);
  })
}
const handleSizeChange=(number)=>{
  getData();
}
const handleCurrentChange=(number)=>{
  getData();
}
const handleDelete = (row) => {
  ElMessageBox.confirm('此操作将永久删除该课程, 是否继续?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    deleteCourse(row.id).then(res => {
      if (res.data.code === 0) {
        ElMessage.success('删除成功');
        getData();
      } else {
        ElMessage.error(res.message);
      }
    }).catch(err => {
      ElMessage.error('删除请求失败'+err);
    });
  }).catch(() => {
    ElMessage.info('已取消删除');
  });
};

onMounted(()=>{
  getData();
})
</script>

<template>
  <div style="display: flex;justify-content: space-between;">
    <el-form :model="tableSetting" label-width="auto" style="max-width: 600px;display: flex;flex-direction: row">
      <el-form-item label="课程名">
        <el-input v-model="tableSetting.courseName"></el-input>
      </el-form-item>
      <el-form-item label="教师名">
        <el-input v-model="tableSetting.teacherName"></el-input>
      </el-form-item>
    </el-form>
    <el-button type="primary" @click="getData">查询</el-button>
  </div>
  <div>
    <el-table :data="tableSetting.tableData" border style="width: 100%">
      <el-table-column type="selection" width="55" />
      <el-table-column property="id" v-if="false" />
      <el-table-column property="name" label="课程名" width="120" />
      <el-table-column property="teacherName" label="任课教师" width="120" />
      <el-table-column property="comment" label="课程简介" width="120" />
      <el-table-column property="createTime" label="课程创建时间" width="120" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
  <div>
    <el-pagination
        v-model:current-page="tableSetting.currentPage"
        v-model:page-size="tableSetting.pageSize"
        v-model:total="tableSetting.total"
        :page-sizes="[5, 10, 20, 40]"
        :size="'default'"
        :disabled="false"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
    />
  </div>
</template>

<style scoped>

</style>
