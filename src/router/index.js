import Vue from 'vue'
import VueRouter from 'vue-router'
import Login from '../views/Login.vue'

Vue.use(VueRouter)

const foremanRoutes = [
  {
    path: '/foreman/workorder',
    name: 'WorkOrder',
    component: () => import('../views/foreman/WorkOrder.vue')
  },
  {
    path: '/foreman/equipment',
    name: 'Equipment',
    component: () => import('../views/foreman/Equipment.vue')
  },
  {
    path: '/foreman/statistics',
    name: 'Statistics',
    component: () => import('../views/foreman/Statistics.vue')
  },
  {
    path: '/foreman/team',
    name: 'Team',
    component: () => import('../views/foreman/Team.vue')
  },
  {
    path: '/foreman/profile',
    name: 'ForemanProfile',
    component: () => import('../views/foreman/Account.vue')
  }
]

const workerRoutes = [
  {
    path: '/worker/tasks',
    name: 'MyTasks',
    component: () => import('../views/worker/MyTasks.vue')
  },
  {
    path: '/worker/issues',
    name: 'Issues',
    component: () => import('../views/worker/Issues.vue')
  },
  {
    path: '/worker/equipment-status',
    name: 'EquipmentStatus',
    component: () => import('../views/worker/EquipmentStatus.vue')
  },
  {
    path: '/worker/knowledge',
    name: 'Knowledge',
    component: () => import('../views/worker/Knowledge.vue')
  },
  {
    path: '/worker/profile',
    name: 'WorkerProfile', 
    component: () => import('../views/worker/Account.vue')
  }
]

const supervisorRoutes = [
  {
    path: '/supervisor/monitor',
    name: 'MonitorCenter',
    component: () => import('../views/supervisor/MonitorCenter.vue')
  },
  {
    path: '/supervisor/efficiency',
    name: 'EfficiencyAnalysis',
    component: () => import('../views/supervisor/EfficiencyAnalysis.vue')
  },
  {
    path: '/supervisor/team',
    name: 'TeamManagement',
    component: () => import('../views/supervisor/TeamManagement.vue')
  },
  {
    path: '/supervisor/workorders',
    name: 'WorkOrders',
    component: () => import('../views/supervisor/WorkOrders.vue')
  },
  {
    path: '/supervisor/profile',
    name: 'SupervisorProfile',
    component: () => import('../views/supervisor/SystemSettings.vue')
  }
]

const safetyRoutes = [
  {
    path: '/safety/monitor',
    name: 'SafetyMonitor',
    component: () => import('../views/safety/Monitor.vue')
  },
  {
    path: '/safety/warning',
    name: 'SafetyWarning',
    component: () => import('../views/safety/Warning.vue')
  },
  {
    path: '/safety/inspection',
    name: 'SafetyInspection',
    component: () => import('../views/safety/Inspection.vue')
  },
  {
    path: '/safety/statistics',
    name: 'SafetyStatistics',
    component: () => import('../views/safety/Statistics.vue')
  },
  {
    path: '/safety/profile',
    name: 'SafetyProfile',
    component: () => import('../views/safety/Account.vue')
  }
]

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/',
    redirect: '/login'
  },
  ...foremanRoutes,
  ...workerRoutes,
  ...supervisorRoutes,
  ...safetyRoutes
]

const router = new VueRouter({
  routes
})

// 修改导航守卫
router.beforeEach((to, from, next) => {
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  
  if (to.path === '/login') {
    next()
    return
  }

  if (!userInfo.role) {
    next('/login')
    return
  }

  // 新增厂长路由权限判断
  if (userInfo.role === 'supervisor' && !to.path.startsWith('/supervisor')) {
    next('/supervisor/monitor')
    return
  }

  // 添加安全员路由判断
  if (userInfo.role === 'safety_officer' && !to.path.startsWith('/safety')) {
    next('/safety/monitor')
    return
  }

  // 保持原有的工长和工人的路由权限判断
  if (userInfo.role === 'foreman' && to.path.startsWith('/worker')) {
    next('/foreman/workorder')
    return
  }

  if (userInfo.role === 'member' && to.path.startsWith('/foreman')) {
    next('/worker/tasks')
    return
  }

  next()
})

export default router