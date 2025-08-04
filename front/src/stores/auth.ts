import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api'

export interface User {
  id: string
  username: string
  email: string
  role: string
  avatar?: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  // 登录
  const login = async (credentials: { username: string; password: string }) => {
    loading.value = true
    try {
      const response = await api.auth.login(credentials)
      token.value = response.token
      user.value = response.user
      localStorage.setItem('token', response.token)
      return response
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = async () => {
    loading.value = true
    try {
      await api.auth.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      loading.value = false
    }
  }

  // 获取用户信息
  const fetchProfile = async () => {
    if (!token.value) return
    
    loading.value = true
    try {
      const response = await api.auth.profile()
      user.value = response
    } catch (error) {
      console.error('Fetch profile error:', error)
      // 如果获取用户信息失败，可能是token过期，清除认证状态
      token.value = null
      user.value = null
      localStorage.removeItem('token')
    } finally {
      loading.value = false
    }
  }

  // 刷新token
  const refreshToken = async () => {
    if (!token.value) return
    
    try {
      const response = await api.auth.refresh()
      token.value = response.token
      localStorage.setItem('token', response.token)
    } catch (error) {
      console.error('Refresh token error:', error)
      // 刷新失败，清除认证状态
      token.value = null
      user.value = null
      localStorage.removeItem('token')
    }
  }

  // 初始化认证状态
  const initAuth = async () => {
    if (token.value) {
      await fetchProfile()
    }
  }

  return {
    user,
    token,
    loading,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    fetchProfile,
    refreshToken,
    initAuth
  }
}) 