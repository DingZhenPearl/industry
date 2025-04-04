<template>
  <nav class="bottom-nav">
    <div class="nav-item" :class="{ active: $route.path === '/safety/monitor' }" @click="$router.push('/safety/monitor')">
      <i class="nav-icon monitor-icon"></i>
      <span>安全监控</span>
    </div>
    <div class="nav-item" :class="{ active: $route.path === '/safety/warning' }" @click="$router.push('/safety/warning')">
      <i class="nav-icon warning-icon"></i>
      <span>预警处理</span>
    </div>
    <div class="nav-item" :class="{ active: $route.path === '/safety/inspection' }" @click="$router.push('/safety/inspection')">
      <i class="nav-icon inspection-icon"></i>
      <span>安全巡检</span>
    </div>
    <div class="nav-item" :class="{ active: $route.path === '/safety/statistics' }" @click="$router.push('/safety/statistics')">
      <i class="nav-icon statistics-icon"></i>
      <span>安全统计</span>
    </div>
    <div class="nav-item" :class="{ active: $route.path === '/safety/profile' }" @click="$router.push('/safety/profile')">
      <i class="nav-icon profile-icon"></i>
      <span>我的</span>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'SafetyNav'
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
  padding: 8px 0;
  border-top: 1px solid #e0e0e0;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 12px;
}

.nav-icon {
  width: 24px;
  height: 24px;
  margin-bottom: 4px;
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
