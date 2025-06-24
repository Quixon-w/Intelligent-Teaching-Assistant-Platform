<script setup>
import {onMounted, ref} from 'vue'
import {getUsersList} from "@/api/admin/admin.js";
import UserRoleMap from "@/utils/userrole.js";

const tableData = ref([]);
const tableSetting=ref({
  username:'',
  total:0,
  pageSize:10,
  currentPage:1,
})
const getUserList=()=>{
  getUsersList(tableSetting.value.currentPage,tableSetting.value.pageSize,tableSetting.value.username).then(res=>{
    tableData.value=res.data.data.records;
    tableSetting.value.total=res.data.data.total;
    console.log(res);
  }).catch(err => {
    console.log(err);
  })
}
const handleSizeChange=(number)=>{
  getUserList()
  console.log(number);
}
const handleCurrentChange=(number)=>{
  getUserList()
  console.log(number);
}
onMounted(()=>{
  getUserList();
})
</script>

<template>
  <div style="display: flex;flex-direction: column">
    <div>
      <el-form :model="tableSetting" label-width="auto" style="max-width: 600px">
        <el-form-item label="身份">
          <el-input v-model="tableSetting.username"></el-input>
        </el-form-item>
      </el-form>
    </div>
    <div>
      <el-button type="primary" @click="getUserList">查询</el-button>
      <el-table :data="tableData" border style="width: 100%">
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
  </div>
</template>

<style scoped>

</style>
