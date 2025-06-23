<template>
  <div class="user-central">
    <div class="user-info">
      <img :src="userInfo.avatarUrl" alt="Avatar" class="avatar">
    </div>
    <div class="edit-form">
      <h3>编辑个人信息</h3>
      <form @submit.prevent="changeUserInfo">
        <label>
          用户名:
          <input v-model="editInfo.username" type="text">
        </label>
        <label>
          账号:
          <input v-model="editInfo.userAccount" type="text">
        </label>
        <label>
          电话:
          <input v-model="editInfo.phone" type="text">
        </label>
        <label>
          邮箱:
          <input v-model="editInfo.email" type="email">
        </label>
        <label>
          性别:
          <select v-model="editInfo.gender">
            <option :value="0">未知</option>
            <option :value="1">男</option>
            <option :value="2">女</option>
          </select>
        </label>
        <button type="submit">保存信息</button>
      </form>
    </div>
    <div class="password-form">
      <h3>修改密码</h3>
      <form @submit.prevent="updatePassword">
        <label>
          旧密码:
          <input v-model="oldPassword" type="password" placeholder="请输入旧密码">
        </label>
        <label>
          新密码:
          <input v-model="newPassword" type="password" placeholder="请输入新密码">
        </label>
        <label>
          确认新密码:
          <input v-model="checkPassword" type="password" placeholder="请再次输入新密码">
        </label>
        <button type="submit">修改密码</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import {getCurrentUserId, getUserInfoById,updateUserInfo,changePassword} from '@/api/user/userinfo';
import { ElMessage } from 'element-plus';
const oldPassword = ref('');
const newPassword = ref('');
const checkPassword = ref('');

const userInfo = ref({
  id: 0,
  username: '',
  userAccount: '',
  avatarUrl: '',
  gender: 0,
  userPassword: '',
  phone: '',
  email: '',
  userStatus: 0,
  isDelete: 0,
  userRole: 0
});

const editInfo = ref({ ...userInfo.value });

// 获取当前用户 ID
const fetchUserId = async () => {
  try {
    const res = await getCurrentUserId();
    return res.data.id;
  } catch (error) {
    ElMessage.error('无法获取用户信息，请重试');
    return null;
  }
};

// 根据用户 ID 获取详细信息
const fetchUserInfo = async (userId) => {
  try {
    const res = await getUserInfoById(userId);
    console.log('获取到的用户数据:', res.data);
    userInfo.value = res.data;
    editInfo.value = { ...userInfo.value };
  } catch (error) {
    ElMessage.error('加载用户信息失败');
  }
};

const changeUserInfo = async () => {
  try {
    const res = await updateUserInfo(editInfo.value);
    if (res.code === 200) {
      ElMessage.success('信息更新成功');
      userInfo.value = { ...editInfo.value };
    } else {
      ElMessage.error(res.message || '更新失败');
    }
  } catch (error) {
    ElMessage.error('请求失败，请重试');
    console.error('更新用户信息出错:', error);
  }
};

const updatePassword = async () => {
  if (newPassword.value !== checkPassword.value) {
    ElMessage.warning('两次输入的新密码不一致');
    return;
  }

  if (!oldPassword.value || !newPassword.value) {
    ElMessage.warning('请填写完整信息');
    return;
  }

  try {
    const res = await changePassword({
      userId: userInfo.value.id,
      oldPassword: oldPassword.value,
      newPassword: newPassword.value,
      checkPassword: checkPassword.value
    });

    if (res.code === 200) {
      ElMessage.success('密码修改成功');
      oldPassword.value = '';
      newPassword.value = '';
      checkPassword.value = '';
    } else {
      ElMessage.error(res.message || '修改失败');
    }
  } catch (error) {
    ElMessage.error('请求失败，请重试');
    console.error('修改密码出错:', error);
  }
};

// 组件挂载时获取用户信息
onMounted(async () => {
  const userId = await fetchUserId();
  if (userId) {
    await fetchUserInfo(userId);
  }
});

</script>

<style scoped>
.user-central {
  display: flex;
  justify-content: space-around;
  padding: 20px;
}

.user-info {
  flex: 1;
  text-align: center;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
}

.edit-form, .password-form {
  flex: 2;
  margin: 0 20px;
}

form {
  display: flex;
  flex-direction: column;
}

label {
  margin-bottom: 10px;
}

input, select {
  padding: 5px;
  margin-top: 5px;
  width: 100%;
  box-sizing: border-box;
}

button {
  width: 120px;
  padding: 8px;
  margin-top: 15px;
  cursor: pointer;
  align-self: flex-start;
}

h3 {
  margin-bottom: 10px;
}
</style>


