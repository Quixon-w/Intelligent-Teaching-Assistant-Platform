<template>
  <div class="user-central-container">
    <el-tabs v-model="activeTab" class="user-tabs">
      <!-- 基本信息编辑 -->
      <el-tab-pane label="基本信息" name="info">
        <div class="user-edit">
          <div class="avatar-section">
            <img :src="userInfo.avatarUrl" alt="上传头像" class="avatar" />
          </div>
          <div class="edit-form">
            <h3>编辑个人信息</h3>
            <form @submit.prevent="changeUserInfo" class="form-layout">
              <label>
                用户名：
                <input v-model="editInfo.username" type="text" />
              </label>
              <label>
                账号：
                <input v-model="editInfo.userAccount" type="text" />
              </label>
              <label>
                电话：
                <input v-model="editInfo.phone" type="text" />
              </label>
              <label>
                邮箱：
                <input v-model="editInfo.email" type="email" />
              </label>
              <label>
                性别：
                <select v-model="editInfo.gender">
                  <option :value="0">未知</option>
                  <option :value="1">男</option>
                  <option :value="2">女</option>
                </select>
              </label>
              <label>
                身份：
                <select v-model="editInfo.userRole">
                  <option :value="0">学生</option>
                  <option :value="1">老师</option>
                </select>
              </label>
              <button type="submit">保存信息</button>
            </form>
          </div>
        </div>
      </el-tab-pane>

      <!-- 修改密码 -->
      <el-tab-pane label="修改密码" name="password">
        <div class="password-form">
          <h3>修改密码</h3>
          <form @submit.prevent="updatePassword" class="form-layout">
            <label>
              旧密码：
              <input v-model="oldPassword" type="password" placeholder="请输入旧密码" />
            </label>
            <label>
              新密码：
              <input v-model="newPassword" type="password" placeholder="请输入新密码" />
            </label>
            <label>
              确认新密码：
              <input v-model="checkPassword" type="password" placeholder="请再次输入新密码" />
            </label>
            <button type="submit">修改密码</button>
          </form>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getCurrentUser, updateUserInfo, changePassword } from '@/api/user/userinfo';
import { ElMessage } from 'element-plus';

const activeTab = ref('info');

const oldPassword = ref('');
const newPassword = ref('');
const checkPassword = ref('');

const userInfo = ref({
  id: 0,
  username: '',
  userAccount: '',
  avatarUrl: '',
  gender: 0,
  phone: '',
  email: '',
  userRole: 0
});

const editInfo = ref({ ...userInfo.value });

const fetchCurrentUser = async () => {
  try {
    const res = await getCurrentUser();
    userInfo.value = res.data;
    editInfo.value = { ...res.data };
  } catch (error) {
    ElMessage.error('无法加载当前用户信息');
  }
};

const changeUserInfo = async () => {
  try {
    const res = await updateUserInfo(
        editInfo.value.id,
        editInfo.value.username,
        editInfo.value.userAccount,
        editInfo.value.avatarUrl,
        editInfo.value.gender,
        editInfo.value.phone,
        editInfo.value.email,
        editInfo.value.userRole
    );
    if (res.code === 0) {
      ElMessage.success('信息更新成功');
      userInfo.value = { ...editInfo.value };
    } else {
      ElMessage.error(res.message || '更新失败');
    }
  } catch (error) {
    ElMessage.error('请求失败，请重试');
  }
};

const updatePassword = async () => {
  try {
    const res = await changePassword(
        userInfo.value.id,
        oldPassword.value,
        newPassword.value,
        checkPassword.value
    );
    if (res.code === 0) {
      ElMessage.success('密码修改成功');
      oldPassword.value = '';
      newPassword.value = '';
      checkPassword.value = '';
    } else {
      ElMessage.error(res.message || '修改失败');
    }
  } catch (error) {
    ElMessage.error('请求失败，请重试');
  }
};

onMounted(fetchCurrentUser);
</script>

<style scoped>
.user-central-container {
  padding: 30px;
  background-color: #fff;
  max-width: 800px;
  margin: 0 auto;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.user-edit {
  display: flex;
  gap: 40px;
  margin-top: 20px;
}

.avatar-section {
  flex: 1;
  text-align: center;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
}

.avatar-tip {
  font-size: 12px;
  color: #999;
  margin-top: 10px;
}

.edit-form {
  flex: 2;
}

.password-form {
  margin-top: 20px;
  max-width: 500px;
}

.form-layout {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

label {
  font-size: 14px;
  color: #333;
  display: flex;
  flex-direction: column;
}

input,
select {
  padding: 8px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  margin-top: 5px;
  width: 100%;
}

button {
  margin-top: 10px;
  width: 120px;
  padding: 8px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  align-self: flex-start;
}
</style>



