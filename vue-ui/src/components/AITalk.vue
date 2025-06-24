<script>
export default {
  name: "ChatBox",
  data() {
    return {
      messages: [
        { text: "你好！", align: "left" },
        { text: "你好！", align: "right" },
        { text: "如何才能帮助您？", align: "left" },
        { text: "我需要帮助进行Vue.js开发", align: "right" }
      ]
    }
  }
}
</script>

<template>
  <div class="chat-container">
    <div
        class="message"
        v-for="(message, index) in messages"
        :key="index"
        :class="message.align === 'left' ? 'message-left' : 'message-right'"
    >
      {{ message.text }}
    </div>
  </div>
  <el-input class="chat-input" placeholder="Please input" />
</template>

<style scoped>
.chat-container {
  width: 100%;
  height: 80%;
  margin: auto;
  padding: 20px;
  box-sizing: border-box;
  background-color: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.chat-input{
  width: 100%;
  height: 20%;
}
.message {
  width: 200px;
  padding: 10px;
  border-radius: 10px;
  margin-bottom: 15px;
  word-wrap: break-word;
}

.message-left {
  background-color: #42b983;
  align-self: flex-start;
}

.message-right {
  background-color: orange;
  align-self: flex-end;
}
</style>
