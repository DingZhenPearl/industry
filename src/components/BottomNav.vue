<template>
  <nav class="bottom-nav">
    <div class="nav-item" :class="{ active: $route.path === '/home' }" @click="$router.push('/home')">
      <i class="nav-icon home-icon"></i>
      <span>首页</span>
    </div>
    <div class="nav-item" :class="{ active: $route.path === '/task' }" @click="$router.push('/task')">
      <i class="nav-icon task-icon"></i>
      <span>任务</span>
    </div>
    <div class="nav-item" :class="{ active: $route.path === '/notification' }" @click="$router.push('/notification')">
      <i class="nav-icon notification-icon"></i>
      <span>通知</span>
    </div>
    <div class="nav-item" :class="{ active: $route.path === '/profile' }" @click="$router.push('/profile')">
      <i class="nav-icon profile-icon"></i>
      <span>我的</span>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'BottomNav'
}
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-around;
  background-color: #f8f8f8;
  padding: 10px 0;
  border-top: 1px solid #e0e0e0;
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}

.nav-icon {
  width: 24px;
  height: 24px;
  margin-bottom: 5px;
  background-color: #666;
  border-radius: 50%;
}

.nav-item.active {
  color: #2196F3;
}

.nav-item.active .nav-icon {
  background-color: #2196F3;
}
</style>