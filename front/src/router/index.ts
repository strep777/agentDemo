import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Agents from '../views/Agents.vue'
import AgentDetail from '../views/AgentDetail.vue'
import Chat from '../views/Chat.vue'
import Knowledge from '../views/Knowledge.vue'
import Workflows from '../views/Workflows.vue'
import Plugins from '../views/Plugins.vue'
import Models from '../views/Models.vue'
import Training from '../views/Training.vue'
import Settings from '../views/Settings.vue'
import Analytics from '../views/Analytics.vue'
import NotFound from '../views/NotFound.vue'
import Login from '../views/Login.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录' }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { title: '仪表盘' }
  },
  {
    path: '/agents',
    name: 'Agents',
    component: Agents,
    meta: { title: '智能体管理' }
  },
  {
    path: '/agents/:id',
    name: 'AgentDetail',
    component: AgentDetail,
    meta: { title: '智能体详情' }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: Chat,
    meta: { title: '聊天' }
  },
  {
    path: '/knowledge',
    name: 'Knowledge',
    component: Knowledge,
    meta: { title: '知识库' }
  },
  {
    path: '/workflows',
    name: 'Workflows',
    component: Workflows,
    meta: { title: '工作流' }
  },
  {
    path: '/plugins',
    name: 'Plugins',
    component: Plugins,
    meta: { title: '插件管理' }
  },
  {
    path: '/models',
    name: 'Models',
    component: Models,
    meta: { title: '模型管理' }
  },
  {
    path: '/training',
    name: 'Training',
    component: Training,
    meta: { title: '智能体训练' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { title: '设置' }
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: Analytics,
    meta: { title: '数据分析' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { title: '页面未找到' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - Agent Demo`
  }
  
  next()
})

export default router 