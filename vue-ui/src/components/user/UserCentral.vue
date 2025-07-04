<template>
  <div class="user-central-container">
    <el-tabs v-model="activeTab" class="user-tabs">
      <!-- 基本信息编辑 -->
      <el-tab-pane label="基本信息" name="info">
        <div class="user-edit">
          <div class="avatar-section">
            <img :src="userInfo.avatarUrl" alt="头像" class="avatar" />
          </div>
          <div class="edit-form">
            <h3>编辑个人信息</h3>
            <div class="user-info-container">
              <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" class="user-info-form">
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="form.username" />
                </el-form-item>
                <el-form-item label="账号" prop="userAccount">
                  <el-input v-model="form.userAccount" disabled />
                </el-form-item>
                <el-form-item label="电话" prop="phone">
                  <el-input v-model="form.phone" />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="form.email" />
                </el-form-item>
                <el-form-item label="性别" prop="gender">
                  <el-select v-model="form.gender" placeholder="请选择">
                    <el-option label="未知" :value="0" />
                    <el-option label="男" :value="1" />
                    <el-option label="女" :value="2" />
                  </el-select>
                </el-form-item>
                <el-form-item label="身份" prop="userRole">
                  <el-select v-model="form.userRole" placeholder="请选择">
                    <el-option label="学生" :value="0" />
                    <el-option label="教师" :value="1" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="onSubmit">保存</el-button>
                </el-form-item>
              </el-form>
            </div>
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
import { ref, onMounted, reactive } from 'vue';
import { getCurrentUser, updateUserInfo, changePassword } from '@/api/user/userinfo';
import { ElMessage } from 'element-plus';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();

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

const formRef = ref();
const form = reactive({ ...userInfo.value });

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  phone: [{ required: false }],
  email: [{ required: false, type: 'email', message: '请输入正确的邮箱', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  userRole: [{ required: true, message: '请选择身份', trigger: 'change' }]
};

const fetchCurrentUser = async () => {
  try {
    const res = await getCurrentUser();
    if (res.code === 0) {
      Object.assign(userInfo.value, res.data);
      form.username = res.data.username;
      form.userAccount = res.data.userAccount;
      form.phone = res.data.phone;
      form.email = res.data.email;
      form.gender = res.data.gender;
      form.userRole = res.data.userRole;
      
      // 同步更新authStore和localStorage中的用户信息
      if (authStore.user) {
        authStore.user.username = res.data.username;
        authStore.user.avatar = res.data.avatarUrl || '';
      }
      localStorage.setItem('username', res.data.username);
      localStorage.setItem('userAvatar', res.data.avatarUrl || '');
    } else {
      ElMessage.error(res.message || '无法加载当前用户信息');
    }
  } catch (error) {
    ElMessage.error('请求失败，请重试');
  }
};

const onSubmit = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      const res = await updateUserInfo(form);
      if (res.code === 0) {
        ElMessage.success('信息更新成功');
        userInfo.value = { ...form };
        
        // 同步更新authStore和localStorage中的用户信息
        if (authStore.user) {
          authStore.user.username = form.username;
          authStore.user.avatar = userInfo.value.avatarUrl || '';
        }
        localStorage.setItem('username', form.username);
        localStorage.setItem('userAvatar', userInfo.value.avatarUrl || '');
      } else {
        ElMessage.error(res.message || '更新失败');
      }
    }
  });
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
      ElMessage.success('密码修改成功，请重新登录');
      
      // 清空密码表单
      oldPassword.value = '';
      newPassword.value = '';
      checkPassword.value = '';
      
      // 延迟一下让用户看到成功消息，然后登出并跳转到登录页
      setTimeout(async () => {
        try {
          await authStore.logout()
          // 跳转到登录页
          window.location.href = '/login'
        } catch (error) {
          console.error('登出失败:', error)
          // 如果登出失败，直接跳转到登录页
          window.location.href = '/login'
        }
      }, 1500)
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

.user-info-container {
  max-width: 500px;
  margin: 40px auto;
  background: #fff;
  padding: 32px 24px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}
</style>



