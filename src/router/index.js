import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/task',
    name: 'Task',
    component: () => import('../views/Task.vue')
  },
  {
    path: '/notification',
    name: 'Notification',
    component: () => import('../views/Notification.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue')
  }
]

const router = new VueRouter({
  routes
})

export default router