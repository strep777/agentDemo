<template>
  <div class="login-container">
    <div class="login-background">
      <div class="gradient-circle circle-1"></div>
      <div class="gradient-circle circle-2"></div>
      <div class="gradient-circle circle-3"></div>
    </div>
    
    <div class="login-card">
      <div class="login-header">
        <div class="logo-container">
          <n-icon size="48" color="#6366f1">
            <ServerOutline />
          </n-icon>
        </div>
        <h1>Agent Demo</h1>
        <p>智能体管理系统</p>
      </div>
      
      <n-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        @submit.prevent="handleLogin"
        class="login-form"
      >
        <n-form-item path="username" label="用户名">
          <n-input
            v-model:value="formData.username"
            placeholder="请输入用户名"
            size="large"
            class="login-input"
          />
        </n-form-item>
        
        <n-form-item path="password" label="密码">
          <n-input
            v-model:value="formData.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password-on="click"
            class="login-input"
          />
        </n-form-item>
        
        <n-form-item>
          <n-button
            type="primary"
            size="large"
            block
            :loading="loading"
            @click="handleLogin"
            class="login-button"
          >
            登录
          </n-button>
        </n-form-item>
      </n-form>
      
      <div class="login-footer">
        <p>开发环境：使用任意用户名密码登录</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ServerOutline } from '@vicons/ionicons5'

const router = useRouter()
const loading = ref(false)

const formData = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  try {
    loading.value = true
    const response = await api.auth.login({
      username: formData.username,
      password: formData.password
    })
    
    if (response.data.success) {
      localStorage.setItem('token', response.data.data.token)
      message.success('登录成功')
      router.push('/')
    } else {
      message.error(response.data.message || '登录失败')
    }
  } catch (error) {
    message.error('登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  position: relative;
  overflow: hidden;
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
}

.gradient-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(40px);
  opacity: 0.6;
}

.circle-1 {
  width: 300px;
  height: 300px;
  background: linear-gradient(45deg, #6366f1, #8b5cf6);
  top: -150px;
  right: -150px;
  animation: float 6s ease-in-out infinite;
}

.circle-2 {
  width: 200px;
  height: 200px;
  background: linear-gradient(45deg, #06b6d4, #3b82f6);
  bottom: -100px;
  left: -100px;
  animation: float 8s ease-in-out infinite reverse;
}

.circle-3 {
  width: 150px;
  height: 150px;
  background: linear-gradient(45deg, #f59e0b, #ef4444);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: float 10s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 48px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 1;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-container {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 20px;
  margin-bottom: 24px;
  box-shadow: 0 10px 25px rgba(99, 102, 241, 0.3);
}

.login-header h1 {
  margin: 0 0 8px 0;
  color: #1e293b;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.login-header p {
  margin: 0;
  color: #64748b;
  font-size: 16px;
  font-weight: 500;
}

.login-form {
  margin-bottom: 24px;
}

.login-input :deep(.n-input__input) {
  background: rgba(248, 250, 252, 0.8);
  border: 2px solid rgba(226, 232, 240, 0.8);
  border-radius: 12px;
  transition: all 0.2s ease;
}

.login-input :deep(.n-input__input:focus) {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.login-button {
  background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
  border: none !important;
  border-radius: 12px !important;
  font-weight: 600 !important;
  font-size: 16px !important;
  height: 48px !important;
  transition: all 0.2s ease !important;
}

.login-button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 10px 25px rgba(99, 102, 241, 0.3) !important;
}

.login-footer {
  text-align: center;
  padding-top: 24px;
  border-top: 1px solid rgba(226, 232, 240, 0.5);
}

.login-footer p {
  margin: 0;
  color: #94a3b8;
  font-size: 14px;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .login-card {
    margin: 20px;
    padding: 32px;
  }
  
  .login-header h1 {
    font-size: 24px;
  }
  
  .logo-container {
    width: 64px;
    height: 64px;
  }
}
</style>