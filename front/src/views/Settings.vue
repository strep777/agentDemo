<template>
  <div class="settings-page">
    <n-card title="系统设置" class="mb-6">
      <n-tabs v-model:value="activeTab" type="line">
        <!-- 个人信息设置 -->
        <n-tab-pane name="profile" tab="个人信息">
          <n-form
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileRules"
            label-placement="left"
            label-width="120"
            require-mark-placement="right-hanging"
          >
            <n-form-item label="用户名" path="username">
              <n-input v-model:value="profileForm.username" placeholder="请输入用户名" />
            </n-form-item>
            
            <n-form-item label="邮箱" path="email">
              <n-input v-model:value="profileForm.email" placeholder="请输入邮箱" />
            </n-form-item>
            
            <n-form-item label="个人简介" path="bio">
              <n-input
                v-model:value="profileForm.bio"
                type="textarea"
                placeholder="请输入个人简介"
                :rows="3"
              />
            </n-form-item>
            
            <n-form-item>
              <n-button type="primary" @click="updateProfile" :loading="loading">
                保存修改
              </n-button>
            </n-form-item>
          </n-form>
        </n-tab-pane>

        <!-- 密码修改 -->
        <n-tab-pane name="password" tab="密码修改">
          <n-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-placement="left"
            label-width="120"
            require-mark-placement="right-hanging"
          >
            <n-form-item label="当前密码" path="oldPassword">
              <n-input
                v-model:value="passwordForm.oldPassword"
                type="password"
                placeholder="请输入当前密码"
                show-password-on="click"
              />
            </n-form-item>
            
            <n-form-item label="新密码" path="newPassword">
              <n-input
                v-model:value="passwordForm.newPassword"
                type="password"
                placeholder="请输入新密码"
                show-password-on="click"
              />
            </n-form-item>
            
            <n-form-item label="确认新密码" path="confirmPassword">
              <n-input
                v-model:value="passwordForm.confirmPassword"
                type="password"
                placeholder="请再次输入新密码"
                show-password-on="click"
              />
            </n-form-item>
            
            <n-form-item>
              <n-button type="primary" @click="changePassword" :loading="loading">
                修改密码
              </n-button>
            </n-form-item>
          </n-form>
        </n-tab-pane>

        <!-- 系统配置 -->
        <n-tab-pane name="system" tab="系统配置">
          <n-form
            ref="systemFormRef"
            :model="systemForm"
            label-placement="left"
            label-width="120"
          >
            <n-form-item label="API基础URL">
              <n-input
                v-model:value="systemForm.apiBaseUrl"
                placeholder="http://localhost:5000/api"
              />
            </n-form-item>
            
            <n-form-item label="Ollama服务地址">
              <n-input
                v-model:value="systemForm.ollamaUrl"
                placeholder="http://localhost:11434"
              />
            </n-form-item>
            
            <n-form-item label="默认模型">
              <n-select
                v-model:value="systemForm.defaultModel"
                :options="modelOptions"
                placeholder="选择默认模型"
              />
            </n-form-item>
            
            <n-form-item label="主题设置">
              <n-select
                v-model:value="systemForm.theme"
                :options="themeOptions"
                placeholder="选择主题"
              />
            </n-form-item>
            
            <n-form-item label="语言设置">
              <n-select
                v-model:value="systemForm.language"
                :options="languageOptions"
                placeholder="选择语言"
              />
            </n-form-item>
            
            <n-form-item>
              <n-button type="primary" @click="saveSystemConfig" :loading="loading">
                保存配置
              </n-button>
            </n-form-item>
          </n-form>
        </n-tab-pane>

        <!-- 通知设置 -->
        <n-tab-pane name="notifications" tab="通知设置">
          <n-space vertical>
            <n-card title="邮件通知" size="small">
              <n-space vertical>
                <n-checkbox v-model:checked="notificationSettings.emailEnabled">
                  启用邮件通知
                </n-checkbox>
                <n-input
                  v-model:value="notificationSettings.emailAddress"
                  placeholder="通知邮箱地址"
                  :disabled="!notificationSettings.emailEnabled"
                />
              </n-space>
            </n-card>
            
            <n-card title="系统通知" size="small">
              <n-space vertical>
                <n-checkbox v-model:checked="notificationSettings.systemNotifications">
                  启用系统通知
                </n-checkbox>
                <n-checkbox v-model:checked="notificationSettings.trainingComplete">
                  训练完成通知
                </n-checkbox>
                <n-checkbox v-model:checked="notificationSettings.workflowComplete">
                  工作流完成通知
                </n-checkbox>
              </n-space>
            </n-card>
            
            <n-button type="primary" @click="saveNotificationSettings" :loading="loading">
              保存通知设置
            </n-button>
          </n-space>
        </n-tab-pane>

        <!-- 数据管理 -->
        <n-tab-pane name="data" tab="数据管理">
          <n-space vertical>
            <n-card title="数据导出" size="small">
              <n-space vertical>
                <n-button @click="exportData('conversations')">
                  导出对话数据
                </n-button>
                <n-button @click="exportData('agents')">
                  导出智能体数据
                </n-button>
                <n-button @click="exportData('workflows')">
                  导出工作流数据
                </n-button>
              </n-space>
            </n-card>
            
            <n-card title="数据清理" size="small">
              <n-space vertical>
                <n-button type="warning" @click="clearData('conversations')">
                  清理对话数据
                </n-button>
                <n-button type="warning" @click="clearData('messages')">
                  清理消息数据
                </n-button>
                <n-button type="error" @click="clearAllData">
                  清理所有数据
                </n-button>
              </n-space>
            </n-card>
          </n-space>
        </n-tab-pane>
      </n-tabs>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import {
  Save,
  Refresh,
  Settings,
  Notifications,
  ShieldCheckmark,
  Server,
  Cloud,
  Globe
} from '@vicons/ionicons5'
import {
  NCard, NTabs, NTabPane, NForm, NFormItem, NInput, NButton, 
  NSelect, NCheckbox, NSpace 
} from 'naive-ui'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { useMessage, useDialog } from 'naive-ui'
import { api } from '@/api'

const authStore = useAuthStore()
const chatStore = useChatStore()
const message = useMessage()
const dialog = useDialog()

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

// 响应式数据
const activeTab = ref('profile')
const loading = ref(false)

// 表单引用
const profileFormRef = ref()
const passwordFormRef = ref()
const systemFormRef = ref()

// 个人信息表单
const profileForm = reactive({
  username: '',
  email: '',
  bio: ''
})

// 密码修改表单
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 系统配置表单
const systemForm = reactive({
  apiBaseUrl: 'http://localhost:5000/api',
  ollamaUrl: 'http://localhost:11434',
  defaultModel: '',
  theme: 'light',
  language: 'zh-CN'
})

// 通知设置
const notificationSettings = reactive({
  emailEnabled: false,
  emailAddress: '',
  systemNotifications: true,
  trainingComplete: true,
  workflowComplete: true
})

// 表单验证规则
const profileRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度在2-20个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email' as const, message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string) => {
        if (value !== passwordForm.newPassword) {
          return new Error('两次输入的密码不一致')
        }
        return true
      },
      trigger: 'blur'
    }
  ]
}

// 选项数据
const modelOptions = [
  { label: 'llama2', value: 'llama2' },
  { label: 'llama2:7b', value: 'llama2:7b' },
  { label: 'llama2:13b', value: 'llama2:13b' },
  { label: 'codellama', value: 'codellama' },
  { label: 'mistral', value: 'mistral' }
]

const themeOptions = [
  { label: '浅色主题', value: 'light' },
  { label: '深色主题', value: 'dark' },
  { label: '跟随系统', value: 'auto' }
]

const languageOptions = [
  { label: '简体中文', value: 'zh-CN' },
  { label: 'English', value: 'en-US' }
]

// 更新个人信息
const updateProfile = async () => {
  try {
    await profileFormRef.value?.validate()
    loading.value = true
    
    // 使用生产环境数据更新个人信息
    console.log('📊 使用生产环境数据更新个人信息')
    
    const response = await api.auth.updateProfile({
      username: profileForm.username,
      email: profileForm.email,
      bio: profileForm.bio
    })
    
    if (response.data && response.data.success) {
      message.success('个人信息更新成功')
    } else {
      throw new Error('更新失败')
    }
    } catch (error: any) {
    console.error('更新个人信息失败:', error)
    message.error(handleError(error, '更新个人信息'))
  } finally {
    loading.value = false
  }
}

// 修改密码
const changePassword = async () => {
  try {
    await passwordFormRef.value?.validate()
    loading.value = true
    
    const response = await api.auth.changePassword({
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    })
    
    if (response.data.success) {
      message.success('密码修改成功')
      // 清空表单
      passwordForm.oldPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
    } else {
      throw new Error('密码修改失败')
    }
  } catch (error: any) {
    console.error('密码修改失败:', error)
    message.error(handleError(error, '密码修改'))
  } finally {
    loading.value = false
  }
}

// 保存系统配置
const saveSystemConfig = async () => {
  try {
    loading.value = true
    
    const response = await api.settings.system.update(systemForm)
    
    if (response.data.success) {
      message.success('系统配置保存成功')
    }
  } catch (error: any) {
    console.error('保存系统配置失败:', error)
    message.error(handleError(error, '保存系统配置'))
  } finally {
    loading.value = false
  }
}

// 保存通知设置
const saveNotificationSettings = async () => {
  try {
    loading.value = true
    
    const response = await api.settings.notifications.update(notificationSettings)
    
    if (response.data.success) {
      message.success('通知设置保存成功')
    }
  } catch (error: any) {
    console.error('保存通知设置失败:', error)
    message.error(handleError(error, '保存通知设置'))
  } finally {
    loading.value = false
  }
}

// 导出数据
const exportData = async (type: string) => {
  try {
    loading.value = true
    
    const response = await api.settings.export(type)
    
    // 创建下载链接
    const blob = new Blob([response.data], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${type}_export_${new Date().toISOString().split('T')[0]}.json`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    message.success('数据导出成功')
  } catch (error: any) {
    console.error('数据导出失败:', error)
    message.error(handleError(error, '数据导出'))
  } finally {
    loading.value = false
  }
}

// 清理数据
const clearData = async (type: string) => {
  dialog.warning({
    title: '确认清理',
    content: `确定要清理所有${type === 'conversations' ? '对话' : '消息'}数据吗？此操作不可恢复！`,
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        loading.value = true
        
        // 清理对话数据
        if (type === 'conversations') {
          await chatStore.clearAllConversations()
        } else {
          // 使用API清理其他类型数据
          await api.settings.clear(type)
        }
        
        message.success('数据清理成功')
      } catch (error: any) {
        console.error('数据清理失败:', error)
        message.error(handleError(error, '数据清理'))
      } finally {
        loading.value = false
      }
    }
  })
}

// 清理所有数据
const clearAllData = async () => {
  dialog.error({
    title: '危险操作',
    content: '确定要清理所有数据吗？此操作不可恢复！',
    positiveText: '确定清理',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        loading.value = true
        
        // 清理所有相关数据
        await chatStore.clearAllConversations()
        await api.settings.clearAll()
        
        message.success('所有数据清理成功')
      } catch (error: any) {
        console.error('清理所有数据失败:', error)
        message.error(handleError(error, '清理所有数据'))
      } finally {
        loading.value = false
      }
    }
  })
}

// 加载用户信息
const loadUserInfo = async () => {
  try {
    const response = await api.auth.profile()
    if (response.data.success) {
      profileForm.username = response.data.data.username || ''
      profileForm.email = response.data.data.email || ''
      profileForm.bio = response.data.data.bio || ''
    }
  } catch (error: any) {
    console.error('加载用户信息失败:', error)
    message.error(handleError(error, '加载用户信息'))
  }
}

// 加载系统配置
const loadSystemConfig = async () => {
  try {
    const response = await api.settings.system.get()
    if (response.data.success) {
      const config = response.data.data
      systemForm.apiBaseUrl = config.apiBaseUrl || 'http://localhost:5000/api'
      systemForm.ollamaUrl = config.ollamaUrl || 'http://localhost:11434'
      systemForm.defaultModel = config.defaultModel || ''
      systemForm.theme = config.theme || 'light'
      systemForm.language = config.language || 'zh-CN'
    }
  } catch (error: any) {
    console.error('加载系统配置失败:', error)
    message.error(handleError(error, '加载系统配置'))
  }
}

// 加载通知设置
const loadNotificationSettings = async () => {
  try {
    const response = await api.settings.notifications.get()
    if (response.data.success) {
      const config = response.data.data
      notificationSettings.emailEnabled = config.emailEnabled || false
      notificationSettings.emailAddress = config.emailAddress || ''
      notificationSettings.systemNotifications = config.systemNotifications || true
      notificationSettings.trainingComplete = config.trainingComplete || true
      notificationSettings.workflowComplete = config.workflowComplete || true
    }
  } catch (error: any) {
    console.error('加载通知设置失败:', error)
    message.error(handleError(error, '加载通知设置'))
  }
}

onMounted(() => {
  loadUserInfo()
  loadSystemConfig()
  loadNotificationSettings()
})
</script>

<style scoped>
.settings-page {
  padding: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-page {
    padding: 16px;
  }
  
  :deep(.n-form-item-label) {
    min-width: 80px;
  }
}

@media (max-width: 480px) {
  .settings-page {
    padding: 12px;
  }
  
  :deep(.n-form-item-label) {
    min-width: 60px;
    font-size: 14px;
  }
}
</style> 