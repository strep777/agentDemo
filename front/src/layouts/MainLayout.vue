<template>
  <n-layout has-sider>
    <!-- 侧边栏 -->
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="240"
      :collapsed="collapsed"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
    >
      <!-- Logo -->
      <div class="logo-container">
        <n-space align="center" justify="center" class="py-4">
          <n-icon size="24" color="#18a058">
            <ServerOutline />
          </n-icon>
          <n-text v-if="!collapsed" strong size="large">
            Agent Demo
          </n-text>
        </n-space>
      </div>

      <!-- 菜单 -->
      <n-menu
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="22"
        :options="menuOptions"
        :value="activeKey"
        @update:value="handleMenuClick"
      />
    </n-layout-sider>

    <!-- 主内容区 -->
    <n-layout>
      <!-- 顶部导航栏 -->
      <n-layout-header bordered class="header">
        <div class="header-content">
          <div class="header-left">
            <n-button
              quaternary
              circle
              @click="collapsed = !collapsed"
            >
              <template #icon>
                <n-icon>
                  <MenuOutline />
                </n-icon>
              </template>
            </n-button>
            <n-breadcrumb>
              <n-breadcrumb-item>
                {{ currentPageTitle }}
              </n-breadcrumb-item>
            </n-breadcrumb>
          </div>

          <div class="header-right">
            <!-- 通知 -->
            <n-badge :value="notificationCount" :max="99">
              <n-button quaternary circle>
                <template #icon>
                  <n-icon>
                    <NotificationsOutline />
                  </n-icon>
                </template>
              </n-button>
            </n-badge>

            <!-- 用户菜单 -->
            <n-dropdown
              :options="userMenuOptions"
              @select="handleUserMenuSelect"
            >
              <n-avatar round size="small">
                <template #icon>
                  <n-icon>
                    <PersonOutline />
                  </n-icon>
                </template>
              </n-avatar>
            </n-dropdown>
          </div>
        </div>
      </n-layout-header>

      <!-- 内容区 -->
      <n-layout-content class="content">
        <slot />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  NLayout,
  NLayoutSider,
  NLayoutHeader,
  NLayoutContent,
  NMenu,
  NButton,
  NIcon,
  NText,
  NSpace,
  NBreadcrumb,
  NBreadcrumbItem,
  NBadge,
  NAvatar,
  NDropdown
} from 'naive-ui'
import {
  ServerOutline,
  MenuOutline,
  NotificationsOutline,
  PersonOutline,
  HomeOutline,
  ChatbubblesOutline,
  GitNetworkOutline,
  BookOutline,
  SchoolOutline,
  SettingsOutline,
  LogOutOutline,
  ExtensionPuzzleOutline,
  SettingsSharp
} from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()

// 渲染图标函数
const renderIcon = (icon: any) => {
  return () => h(NIcon, null, { default: () => h(icon) })
}

// 响应式数据
const collapsed = ref(false)
const notificationCount = ref(3)

// 当前页面标题
const currentPageTitle = computed(() => {
  const routeMap: Record<string, string> = {
    Dashboard: '仪表盘',
    Chat: '聊天',
    Workflows: '工作流',
    Knowledge: '知识库',
    Agents: '智能体管理',
    Training: '智能体训练',
    Plugins: '插件管理',
    Models: '模型管理',
    Settings: '设置',
    Analytics: '数据分析'
  }
  return routeMap[route.name as string] || '首页'
})

// 菜单选项
const menuOptions = [
  {
    label: '仪表盘',
    key: 'dashboard',
    icon: renderIcon(HomeOutline),
    path: '/dashboard'
  },
  {
    label: '聊天',
    key: 'chat',
    icon: renderIcon(ChatbubblesOutline),
    path: '/chat'
  },
  {
    label: '工作流',
    key: 'workflows',
    icon: renderIcon(GitNetworkOutline),
    path: '/workflows'
  },
  {
    label: '知识库',
    key: 'knowledge',
    icon: renderIcon(BookOutline),
    path: '/knowledge'
  },
  {
    label: '智能体',
    key: 'agents',
    icon: renderIcon(ServerOutline),
    path: '/agents'
  },
  {
    label: '智能体训练',
    key: 'training',
    icon: renderIcon(SchoolOutline),
    path: '/training'
  },
  {
    label: '插件管理',
    key: 'plugins',
    icon: renderIcon(ExtensionPuzzleOutline),
    path: '/plugins'
  },
  {
    label: '模型管理',
    key: 'models',
    icon: renderIcon(SettingsSharp),
    path: '/models'
  }
]

// 用户菜单选项
const userMenuOptions = [
  {
    label: '个人设置',
    key: 'settings',
    icon: renderIcon(SettingsOutline)
  },
  {
    label: '退出登录',
    key: 'logout',
    icon: renderIcon(LogOutOutline)
  }
]

// 当前激活的菜单项
const activeKey = computed(() => {
  const path = route.path
  const menuItem = menuOptions.find(item => item.path === path)
  return menuItem?.key || 'dashboard'
})

// 菜单点击处理
const handleMenuClick = (key: string) => {
  const menuItem = menuOptions.find(item => item.key === key)
  if (menuItem) {
    // 使用router.push确保路由正确跳转
    router.push(menuItem.path).catch(err => {
      console.error('路由跳转失败:', err)
    })
  }
}

// 用户菜单选择处理
const handleUserMenuSelect = async (key: string) => {
  switch (key) {
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      // 处理退出登录
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
      break
  }
}
</script>

<style scoped>
.logo-container {
  border-bottom: 1px solid var(--n-border-color);
}

.header {
  height: 64px;
  padding: 0 24px;
  background: var(--n-color);
  border-bottom: 1px solid var(--n-border-color);
}

.header-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.content {
  padding: 24px;
  background: var(--n-color);
  height: calc(100vh - 64px);
  overflow-y: auto;
}

/* 确保布局占满整个视口 */
:deep(.n-layout) {
  height: 100vh;
}

:deep(.n-layout-sider) {
  height: 100vh;
}

:deep(.n-layout-content) {
  height: calc(100vh - 64px);
}
</style> 