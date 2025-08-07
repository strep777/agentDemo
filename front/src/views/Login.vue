<template>
  <div class="login-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">用户登录</h1>
        <p class="page-description">登录到AI智能体管理系统</p>
      </div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-container">
      <n-card class="login-card" hoverable>
        <div class="login-header">
          <div class="logo-container">
            <n-icon size="48" color="#18a058">
              <ServerOutline />
            </n-icon>
          </div>
          <h2 class="login-title">Agent Demo</h2>
          <p class="login-subtitle">智能体管理系统</p>
        </div>
        
        <n-form
          ref="formRef"
          :model="formData"
          :rules="rules"
          @submit.prevent="handleLogin"
          class="login-form"
          label-placement="left"
          label-width="auto"
        >
          <n-form-item path="username" label="用户名">
            <n-input
              v-model:value="formData.username"
              placeholder="请输入用户名"
              size="large"
              class="login-input"
            >
              <template #prefix>
                <n-icon>
                  <PersonOutline />
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
              class="login-input"
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
              @click="handleLogin"
              class="login-button"
            >
              <template #icon>
                <n-icon>
                  <LogInOutline />
                </n-icon>
              </template>
              登录
            </n-button>
          </n-form-item>
          
          <!-- 开发环境：跳过登录按钮 -->
          <n-form-item v-if="isDev">
            <n-button
              type="info"
              size="large"
              block
              @click="skipLogin"
              class="skip-login-button"
            >
              <template #icon>
                <n-icon>
                  <RocketOutline />
                </n-icon>
              </template>
              跳过登录（开发环境）
            </n-button>
          </n-form-item>
        </n-form>
        
        <div class="login-footer">
          <n-alert type="info" :show-icon="false">
            <template #header>
              <div class="alert-header">
                <n-icon>
                  <InformationCircleOutline />
                </n-icon>
                <span>开发环境提示</span>
              </div>
            </template>
            <div class="alert-content">
              <p>• 使用任意用户名密码登录</p>
              <p>• 系统会自动创建用户账户</p>
              <p>• 支持快速体验所有功能</p>
              <p>• 可点击"跳过登录"直接进入系统</p>
            </div>
          </n-alert>
          
          <div class="register-link">
            <span>还没有账户？</span>
            <n-button text type="primary" @click="goToRegister">
              立即注册
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
  LogInOutline,
  InformationCircleOutline,
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
    return '用户名或密码错误'
  } else if (error.response?.status === 403) {
    return '权限不足，无法访问此资源'
  } else if (error.response?.status === 422) {
    return '请求参数错误，请检查输入数据'
  } else {
    return `${operation}失败: ${error.message || '未知错误'}`
  }
}

const handleLogin = async () => {
  try {
    // 验证表单
    await formRef.value?.validate()
    
    loading.value = true
    
    // 开发环境：如果没有用户，先创建用户
    if (isDev) {
      try {
        // 尝试注册用户（如果用户不存在会自动创建）
        await api.auth.register({
          username: formData.username,
          email: `${formData.username}@example.com`,
          password: formData.password
        })
      } catch (error: any) {
        // 如果用户已存在，继续登录流程
        if (error.response?.status !== 400) {
          console.error('注册失败:', error)
        }
      }
    }
    
    // 执行登录
    const response = await api.auth.login({
      username: formData.username,
      password: formData.password
    })
    
    if (response.data.success) {
      // 保存token和用户信息
      localStorage.setItem('token', response.data.data.token)
      localStorage.setItem('user', JSON.stringify(response.data.data.user))
      
      message.success('登录成功')
      router.push('/')
    } else {
      throw new Error('登录失败')
    }
  } catch (error: any) {
    console.error('登录错误:', error)
    message.error(handleError(error, '登录'))
  } finally {
    loading.value = false
  }
}

const skipLogin = async () => {
  if (isDev) {
    try {
      loading.value = true
      
      // 使用生产环境API创建开发用户
      const response = await api.auth.register({
        username: 'dev_user',
        email: 'dev_user@example.com',
        password: 'dev_password_123'
      })
      
      if (response.data.success) {
        // 使用真实的token和用户信息
        localStorage.setItem('token', response.data.data.token)
        localStorage.setItem('user', JSON.stringify(response.data.data.user))
        message.success('开发环境跳过登录成功！')
        router.push('/')
      } else {
        throw new Error('开发用户创建失败')
      }
    } catch (error: any) {
      console.error('开发环境跳过登录失败:', error)
      message.error(handleError(error, '开发环境跳过登录'))
    } finally {
      loading.value = false
    }
  }
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
/* 页面布局 */
.login-page {
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

/* 登录容器 */
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  min-height: calc(100vh - 200px);
}

.login-card {
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
  border-radius: 8px;
  width: 100%;
  max-width: 480px;
  transition: all 0.3s ease;
}

.login-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 登录头部 */
.login-header {
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

.login-title {
  margin: 0 0 8px 0;
  color: var(--n-text-color);
  font-size: 24px;
  font-weight: 600;
}

.login-subtitle {
  margin: 0;
  color: var(--n-text-color-3);
  font-size: 14px;
}

/* 登录表单 */
.login-form {
  margin-bottom: 24px;
}

.login-input :deep(.n-input__input) {
  background: var(--n-color-2);
  border: 1px solid var(--n-border-color);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.login-input :deep(.n-input__input:focus) {
  border-color: var(--n-primary-color);
  box-shadow: 0 0 0 3px rgba(24, 160, 88, 0.1);
}

.login-button {
  background: var(--n-primary-color) !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  font-size: 16px !important;
  height: 48px !important;
  transition: all 0.2s ease !important;
}

.login-button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(24, 160, 88, 0.3) !important;
}

.skip-login-button {
  background: var(--n-info-color) !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  font-size: 16px !important;
  height: 48px !important;
  transition: all 0.2s ease !important;
}

.skip-login-button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(13, 110, 253, 0.3) !important;
}

/* 登录底部 */
.login-footer {
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

.register-link {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 24px;
  color: var(--n-text-color-3);
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-page {
    padding: 16px;
  }
  
  .login-container {
    min-height: calc(100vh - 150px);
  }
  
  .login-card {
    margin: 0;
  }
  
  .page-title {
    font-size: 20px;
  }
  
  .login-title {
    font-size: 20px;
  }
  
  .logo-container {
    width: 64px;
    height: 64px;
  }
}

@media (max-width: 480px) {
  .login-page {
    padding: 12px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .login-card {
    padding: 20px;
  }
}
</style>