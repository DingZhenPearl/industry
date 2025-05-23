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
    path: '/foreman/equipment-detail/:id',
    name: 'ForemanEquipmentDetail',
    component: () => import('../views/foreman/EquipmentDetail.vue')
  },
  {
    path: '/foreman/production-line-detail/:id',
    name: 'ForemanProductionLineDetail',
    component: () => import('../views/foreman/ProductionLineDetail.vue')
  },
  {
    path: '/foreman/team',
    name: 'Team',
    component: () => import('../views/foreman/TeamManagement.vue')
  },

  {
    path: '/foreman/profile',
    name: 'ForemanProfile',
    component: () => import('../views/foreman/Account.vue')
  }
]

const workerRoutes = [
  {
    path: '/worker/workorders',
    name: 'MyWorkorders',
    component: () => import('../views/worker/MyWorkorders.vue')
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
    path: '/supervisor/equipment-detail/:id',
    name: 'EquipmentDetail',
    component: () => import('../views/supervisor/EquipmentDetail.vue')
  },
  {
    path: '/supervisor/production-line-detail/:id',
    name: 'ProductionLineDetail',
    component: () => import('../views/supervisor/ProductionLineDetail.vue')
  },
  {
    path: '/supervisor/profile',
    name: 'SupervisorProfile',
    component: () => import('../views/supervisor/Account.vue')
  }
]

const safetyRoutes = [
  {
    path: '/safety-officer/monitoring',
    name: 'SafetyMonitoring',
    component: () => import('../views/safety/Monitor.vue')
  },
  {
    path: '/safety-officer/warnings',
    name: 'SafetyWarnings',
    component: () => import('../views/safety/Warning.vue')
  },
  {
    path: '/safety-officer/inspection',
    name: 'SafetyInspection',
    component: () => import('../views/safety/Inspection.vue')
  },
  {
    path: '/safety-officer/equipment-detail/:id',
    name: 'SafetyEquipmentDetail',
    component: () => import('../views/safety/EquipmentDetail.vue')
  },
  {
    path: '/safety-officer/production-line-detail/:id',
    name: 'SafetyProductionLineDetail',
    component: () => import('../views/safety/ProductionLineDetail.vue')
  },

  {
    path: '/safety-officer/profile',
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

  // 获取当前的uid参数，如果没有则使用本地存储中的uid
  const currentUid = to.query.uid || userInfo.uid
  const uidParam = currentUid ? { uid: currentUid } : {}

  // 新增厂长路由权限判断
  if (userInfo.role === 'supervisor' && !to.path.startsWith('/supervisor')) {
    next({ path: '/supervisor/monitor', query: uidParam })
    return
  }

  // 添加安全员路由判断
  if (userInfo.role === 'safety_officer' && !to.path.startsWith('/safety-officer')) {
    next({ path: '/safety-officer/monitoring', query: uidParam })
    return
  }

  // 保持原有的工长和工人的路由权限判断
  if (userInfo.role === 'foreman' && to.path.startsWith('/worker')) {
    next({ path: '/foreman/workorder', query: uidParam })
    return
  }

  if (userInfo.role === 'member' && to.path.startsWith('/foreman')) {
    next({ path: '/worker/workorders', query: uidParam })
    return
  }

  // 如果当前路由没有uid参数但用户有uid，添加uid参数
  if (userInfo.uid && !to.query.uid) {
    next({ path: to.path, query: { ...to.query, uid: userInfo.uid } })
    return
  }

  next()
})

export default router