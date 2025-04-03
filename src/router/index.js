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
    path: '/foreman/account',
    name: 'ForemanAccount',
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
    path: '/worker/account',
    name: 'WorkerAccount',
    component: () => import('../views/worker/Account.vue')
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
  ...workerRoutes
]

const router = new VueRouter({
  routes
})

// 导航守卫
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