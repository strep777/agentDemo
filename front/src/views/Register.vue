<template>
  <div class="register-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">用户注册</h1>
        <p class="page-description">创建新的AI智能体管理系统账户</p>
      </div>
    </div>

    <!-- 注册卡片 -->
    <div class="register-container">
      <n-card class="register-card" hoverable>
        <div class="register-header">
          <div class="logo-container">
            <n-icon size="48" color="#18a058">
              <ServerOutline />
            </n-icon>
          </div>
          <h2 class="register-title">Agent Demo</h2>
          <p class="register-subtitle">智能体管理系统</p>
        </div>
        
        <n-form
          ref="formRef"
          :model="formData"
          :rules="rules"
          @submit.prevent="handleRegister"
          class="register-form"
          label-placement="left"
          label-width="auto"
        >
          <n-form-item path="username" label="用户名">
            <n-input
              v-model:value="formData.username"
              placeholder="请输入用户名"
              size="large"
              class="register-input"
            >
              <template #prefix>
                <n-icon>
                  <PersonOutline />
                </n-icon>
              </template>
            </n-input>
          </n-form-item>
          
          <n-form-item path="email" label="邮箱">
            <n-input
              v-model:value="formData.email"
              placeholder="请输入邮箱"
              size="large"
              class="register-input"
            >
              <template #prefix>
                <n-icon>
                  <MailOutline />
                </n-icon>
              </template>
            </n-input>
          </n-form-item>
          
          <n-form-item path="password" label="密码">
            <n-input
              v-model:value="formData.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              show-password-on="click"
              class="register-input"
            >
              <template #prefix>
                <n-icon>
                  <LockClosedOutline />
                </n-icon>
              </template>
            </n-input>
          </n-form-item>
          
          <n-form-item path="confirmPassword" label="确认密码">
            <n-input
              v-model:value="formData.confirmPassword"
              type="password"
              placeholder="请再次输入密码"
              size="large"
              show-password-on="click"
              class="register-input"
            >
              <template #prefix>
                <n-icon>
                  <LockClosedOutline />
                </n-icon>
              </template>
            </n-input>
          </n-form-item>
          
          <n-form-item>
            <n-button
              type="primary"
              size="large"
              block
              :loading="loading"
              @click="handleRegister"
              class="register-button"
            >
              <template #icon>
                <n-icon>
                  <PersonAddOutline />
                </n-icon>
              </template>
              注册
            </n-button>
          </n-form-item>
          
          <!-- 开发环境：跳过注册按钮 -->
          <n-form-item v-if="isDev">
            <n-button
              type="info"
              size="large"
              block
              @click="skipRegister"
              class="skip-register-button"
            >
              <template #icon>
                <n-icon>
                  <RocketOutline />
                </n-icon>
              </template>
              跳过注册（开发环境）
            </n-button>
          </n-form-item>
        </n-form>
        
        <div class="register-footer">
          <n-alert type="info" :show-icon="false">
            <template #header>
              <div class="alert-header">
                <n-icon>
                  <InformationCircleOutline />
                </n-icon>
                <span>注册说明</span>
              </div>
            </template>
            <div class="alert-content">
              <p>• 用户名和邮箱必须唯一</p>
              <p>• 密码长度至少6位</p>
              <p>• 注册成功后自动登录</p>
              <p>• 开发环境可跳过注册直接登录</p>
            </div>
          </n-alert>
          
          <div class="login-link">
            <span>已有账户？</span>
            <n-button text type="primary" @click="goToLogin">
              立即登录
            </n-button>
          </div>
        </div>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { 
  ServerOutline, 
  PersonOutline, 
  LockClosedOutline, 
  PersonAddOutline,
  InformationCircleOutline,
  MailOutline,
  RocketOutline
} from '@vicons/ionicons5'
import api from '@/api'

const router = useRouter()
const message = useMessage()
const loading = ref(false)
const formRef = ref()

// 开发环境检测
const isDev = import.meta.env.DEV

const formData = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string) => {
        if (value !== formData.password) {
          return new Error('两次输入的密码不一致')
        }
        return true
      },
      trigger: 'blur'
    }
  ]
}

// 统一的错误处理函数
const handleError = (error: any, operation: string = '操作') => {
  if (error.code === 'ECONNABORTED') {
    return '请求超时，请检查后端服务是否正常运行'
  } else if (error.code === 'ERR_NETWORK') {
    return '网络连接失败，请检查网络连接'
  } else if (error.response?.status === 500) {
    return '服务器内部错误，请稍后重试'
  } else if (error.response?.status === 404) {
    return 'API端点不存在，请检查后端配置'
  } else if (error.response?.status === 401) {
    return '认证失败，请重新登录'
  } else if (error.response?.status === 403) {
    return '权限不足，无法访问此资源'
  } else if (error.response?.status === 422) {
    return '请求参数错误，请检查输入数据'
  } else {
    return `${operation}失败: ${error.message || '未知错误'}`
  }
}

const handleRegister = async () => {
  try {
    // 验证表单
    await formRef.value?.validate()
    
    loading.value = true
    
    // 执行注册
    const response = await api.auth.register({
      username: formData.username,
      email: formData.email,
      password: formData.password
    })
    
    if (response.data.success) {
      // 保存token和用户信息
      localStorage.setItem('token', response.data.data.token)
      localStorage.setItem('user', JSON.stringify(response.data.data.user))
      
      message.success('注册成功')
      router.push('/')
    } else {
      throw new Error('注册失败')
    }
  } catch (error: any) {
    console.error('注册错误:', error)
    message.error(handleError(error, '注册'))
  } finally {
    loading.value = false
  }
}

const skipRegister = () => {
  // 开发环境跳过注册，直接跳转到登录页面
  if (isDev) {
    message.info('开发环境跳过注册，直接跳转到登录页面')
    router.push('/login')
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
/* 页面布局 */
.register-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-height: 100vh;
  background: var(--n-color);
  padding: 24px;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 8px 0;
  color: var(--n-text-color);
}

.page-description {
  margin: 0;
  color: var(--n-text-color-3);
}

/* 注册容器 */
.register-container {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  min-height: calc(100vh - 200px);
}

.register-card {
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
  border-radius: 8px;
  width: 100%;
  max-width: 480px;
  transition: all 0.3s ease;
}

.register-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 注册头部 */
.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-container {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  background: var(--n-primary-color);
  border-radius: 16px;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(24, 160, 88, 0.2);
}

.register-title {
  margin: 0 0 8px 0;
  color: var(--n-text-color);
  font-size: 24px;
  font-weight: 600;
}

.register-subtitle {
  margin: 0;
  color: var(--n-text-color-3);
  font-size: 14px;
}

/* 注册表单 */
.register-form {
  margin-bottom: 24px;
}

.register-input :deep(.n-input__input) {
  background: var(--n-color-2);
  border: 1px solid var(--n-border-color);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.register-input :deep(.n-input__input:focus) {
  border-color: var(--n-primary-color);
  box-shadow: 0 0 0 3px rgba(24, 160, 88, 0.1);
}

.register-button {
  background: var(--n-primary-color) !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  font-size: 16px !important;
  height: 48px !important;
  transition: all 0.2s ease !important;
}

.register-button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(24, 160, 88, 0.3) !important;
}

.skip-register-button {
  background: var(--n-info-color) !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  font-size: 16px !important;
  height: 48px !important;
  transition: all 0.2s ease !important;
}

.skip-register-button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(13, 110, 253, 0.3) !important;
}

/* 注册底部 */
.register-footer {
  margin-top: 24px;
}

.alert-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--n-text-color);
}

.alert-content {
  margin-top: 8px;
}

.alert-content p {
  margin: 4px 0;
  color: var(--n-text-color-2);
  font-size: 14px;
}

.login-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--n-border-color);
  color: var(--n-text-color-2);
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .register-page {
    padding: 16px;
  }
  
  .register-container {
    min-height: calc(100vh - 150px);
  }
  
  .register-card {
    margin: 0;
  }
  
  .page-title {
    font-size: 20px;
  }
  
  .register-title {
    font-size: 20px;
  }
  
  .logo-container {
    width: 64px;
    height: 64px;
  }
}

@media (max-width: 480px) {
  .register-page {
    padding: 12px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .register-card {
    padding: 20px;
  }
}
</style> 