<script setup>
import {onMounted, ref, watch} from "vue";
import {ElMessage} from "element-plus";
import {useRoute} from "vue-router";
import {chat, clearChat, getSession} from "@/api/ai/ai.js";

const route = useRoute();
const messages = ref([]);
const input = ref('');
const isLoading = ref(false);
const messagesEndRef = ref(null);
const userId=sessionStorage.getItem('userId');
const sessionID = ref(route.params.sessionID);
const role=sessionStorage.getItem('role');

const scrollToBottom = () => {
  messagesEndRef.value?.scrollIntoView({ behavior: "smooth" });
};

watch(messages, () => {
  localStorage.setItem('chatMessages', JSON.stringify(messages.value));
  scrollToBottom();
});

const handleSubmit = async () => {
  if (!input.value.trim()) return;

  const userMessage = {
    id: Date.now(),
    content: input.value.trim(),
    isAI: false,
  };

  messages.value.push(userMessage);
  const userInput = input.value.trim();
  input.value = '';
  isLoading.value = true;

  try {
    const response=await chat(sessionID.value,[{ role: "user", content: userInput, raw: false }]);
    // 直接使用fetch调用后端API
    /*const response = await fetch('/ai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: [{ role: "user", content: userInput, raw: false }],
        user_id: userId,
        session_id: sessionID.value,
        is_teacher: role=='teacher',
        stream: false
      })
    });*/

    console.log(response);
    if (!response.ok) {
      console.log( new Error(`HTTP error! status: ${response.status}`));
    }
    // 获取响应文本
    const responseText = await response.text();
    console.log("+++++++++++++++++++++++")

    console.log(responseText);

    // 解析JSON字符串
    let aiResponse;
    try {
      aiResponse = JSON.parse(responseText);
    } catch (e) {
      console.error('解析响应失败:', e);
    }

    // 提取AI回复内容
    const aiContent = JSON.parse(aiResponse).choices?.[0]?.message?.content || "抱歉，我没有得到有效的回复";
    console.log(aiContent)

    const aiMessage = {
      id: Date.now() + 1,
      content: aiContent,
      isAI: true,
    };

    messages.value.push(aiMessage);

  } catch (error) {
    console.error("API请求失败:", error);
    messages.value.push({
      id: Date.now() + 1,
      content: "请求失败，请稍后重试",
      isAI: true,
    });
  } finally {
    isLoading.value = false;
  }
};

const handleKeyDown = (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleSubmit();
  }
};

const clearChatHistory = () => {
  clearChat(sessionID).then(res => {messages.value = [];ElMessage.success('清除成功')}).catch(err => {ElMessage.error('清除失败')});
};
const getSessionHistory=async (sessionId) => {
  let temp = await getSession(sessionId);
  let amessages=[];
  for (let message of temp){
    amessages.push({
      id: Date.now() + 1,
      content: message.content,
      isAI: message.role!=='user',
    })
  }
  messages.value=amessages;
  console.log(messages.value);
  scrollToBottom();
}
onMounted(()=>{
  sessionID.value=route.params.sessionId;
  getSessionHistory(sessionID.value);
})
</script>

<template>
  <div style="display: flex; flex-direction: column; height: 100%; width: 100% ">
    <div style="overflow-y: auto; padding: 1rem 1rem 8rem;margin-top: 1rem; flex: 1 1 0; ">
      <div v-for="message in messages" :key="message.id" class="flex items-start" :class="message.isAI ? 'justify-start' : 'justify-end'">
        <div v-if="message.isAI" style="display: flex; gap: 0.75rem; align-items: flex-start; width: 100%;">
          <div style="margin-top: 0.5rem;width: 3rem;height: 3rem;">
            <img src="../../assets/logo.svg" alt="StreamAI" style="object-fit: cover; border-radius: 9999px; width: 100%; height: 100%;" />
          </div>
          <div class="message-box">
            <div style="display: flex; padding: 1rem; flex: 1 1 0; align-items: center; border-radius: 0.5rem; border-width: 1px; border-color: #E5E7EB; background-color: #ffffff; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); " v-html="message.content"></div>
          </div>
        </div>
        <div v-else style="display: flex;gap: 0.75rem;justify-content: flex-end;align-items: flex-start;width: 100%;">
          <div style="padding: 1rem;flex: 1 1 0;border-radius: 0.5rem;color: #ffffff;background-color: #2563EB;">
            <div style="line-height: 1.625;white-space: pre-wrap;">
              {{ message.content }}
            </div>
          </div>
          <div style="margin-top: 0.5rem;width: 3rem;height: 3rem;">
            <img src="../../assets/logo.svg" alt="User" style="object-fit: cover;border-radius: 9999px;width: 100%;height: 100%;" />
          </div>
        </div>
      </div>

      <div v-if="isLoading" style="display: flex;gap: 0.75rem;align-items: flex-start;width: 100%;">
        <div style="margin-top: 0.5rem;width: 3rem;height: 3rem;">
          <img src="../../assets/logo.svg" alt="StreamAI" style="object-fit: cover;border-radius: 9999px;width: 100%;height: 100%;"/>
        </div>
        <div class="message-box">
          <div style="display: flex;padding: 1rem;flex: 1 1 0;align-items: center;border-radius: 0.5rem;border-width: 1px;border-color: #E5E7EB;background-color: #ffffff;box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);">
            <div class="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <div ref="messagesEnd" />
    </div>

    <div style="position: relative;right: 0;bottom: 0;left: 0;border-top-width: 1px;border-color: #E5E7EB;">
      <div style="width: 100%;height: 17%;gap: 5px">
        <el-button type="danger" @click="clearChatHistory" style="width: 6%;height: 100%">清空会话</el-button>
        <el-button type="primary" @click="" style="width: 6%;height: 100%">上传文件</el-button>
        <el-button type="primary" @click="" style="width: 6%;height: 100%">下载文件</el-button>
        <el-text>已加载的文件</el-text>
      </div>
      <div style="padding: 1rem;">
        <div style="display: flex;gap: 0.5rem;align-items: center;width: 100%;height: 100%">

          <form @submit.prevent="handleSubmit" style="display: flex;flex: 1 1 0;gap: 0.5rem; width: 91%;height: 100%">
            <textarea
                v-model="input"
                @keydown="handleKeyDown"
                placeholder="输入你的问题..."
                style="overflow-y: auto;padding: 1rem 3rem 1rem 1rem;border-radius: 0.5rem;border-width: 1px;border-color: #D1D5DB;width: 100%;max-height: 3.5rem;font-size: 1rem;line-height: 1.5rem;background-color: #ffffff;resize: none;"
                :disabled="isLoading"
            />
            <button type="submit" :disabled="isLoading" style="padding: 0.625rem 1.25rem;margin-bottom: 0.5rem;border-radius: 0.5rem;width: 6rem;height: 5.5rem;font-size: 0.875rem;line-height: 1.25rem;font-weight: 500;color: #ffffff;background-color: #1D4ED8;:hover {background-color: #1E40AF;}">
              发送
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.loading-dots {
  position: absolute;
  display: inline-flex;
  align-items: center;
  height: 100%;
  min-height: 25px;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
}
.loading-dots span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #000;
  animation: loading-dots 1.4s infinite;
  margin: 0 5px;
}
.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}
.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}
@keyframes loading-dots {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}
.message-box {
  position: relative;
  width: 100%;
  transition: width 0.2s ease-in-out;
}
</style>
