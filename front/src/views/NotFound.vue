<template>
  <div class="not-found-page">
    <div class="flex flex-col items-center justify-center min-h-screen">
      <n-icon size="120" class="text-gray-400 mb-8">
        <WarningOutline />
      </n-icon>
      
      <h1 class="text-6xl font-bold text-gray-600 mb-4">404</h1>
      
      <h2 class="text-2xl font-semibold text-gray-800 mb-4">
        页面未找到
      </h2>
      
      <p class="text-gray-600 mb-8 text-center max-w-md">
        抱歉，您访问的页面不存在或已被移动。
      </p>
      
      <n-space>
        <n-button type="primary" @click="goHome">
          返回首页
        </n-button>
        <n-button @click="goBack">
          返回上页
        </n-button>
      </n-space>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { NIcon, NButton, NSpace } from 'naive-ui'
import { WarningOutline } from '@vicons/ionicons5'

const router = useRouter()

const goHome = () => {
  router.push('/dashboard')
}

const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
.not-found-page {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style> 