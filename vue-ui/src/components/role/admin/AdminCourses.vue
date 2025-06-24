<script setup>
import UserRoleMap from "@/utils/userrole.js";
import {ref} from "vue";

const tableSetting=ref({
  tableData:[],
  pageSize:5,
  currentPage:1,
  total:0,
  courseName:'',
});

const handleSizeChange=(number)=>{
  console.log(number);
}
const handleCurrentChange=(number)=>{
  console.log(number);
}
</script>

<template>
  <div>
    <el-form :model="tableSetting" label-width="auto" style="max-width: 600px">
      <el-form-item label="课程名">
        <el-input v-model="tableSetting.courseName"></el-input>
      </el-form-item>
      <el-form-item label="每页大小">
        <el-input v-model="tableSetting.pageSize"></el-input>
      </el-form-item>
      <el-form-item label="当前页">
        <el-input v-model="tableSetting.currentPage"></el-input>
      </el-form-item>
    </el-form>
  </div>
  <div>
    <el-table :data="tableSetting.tableData" border style="width: 100%">
      <el-table-column type="selection" width="55" />
      <el-table-column property="id" v-if="false" />
      <el-table-column property="userAccount" label="用户账户" width="120" />
      <el-table-column property="username" label="用户名称" width="120" />
      <el-table-column property="userRole" :formatter="(row, column, cellValue) => UserRoleMap[cellValue]" label="用户身份" width="120" />
      <el-table-column property="gender" label="用户性别" width="120" />
      <el-table-column property="phone" label="用户电话" width="120" />
      <el-table-column property="email" label="用户邮箱" width="120" />
      <el-table-column property="userStatus" label="用户状态" width="120" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.$index, scope.row)">删除</el-button>
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
