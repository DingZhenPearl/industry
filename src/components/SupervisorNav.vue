<template>
  <nav class="bottom-nav">
    <div class="nav-item" :class="{ active: $route.path === '/supervisor/monitor' }" @click="$router.push('/supervisor/monitor')">
      <i class="nav-icon monitor-icon"></i>
      <span>监控中心</span>
    </div>

    <div class="nav-item" :class="{ active: $route.path === '/supervisor/team' }" @click="$router.push('/supervisor/team')">
      <i class="nav-icon team-icon"></i>
      <span>团队管理</span>
    </div>
    <div class="nav-item" :class="{ active: $route.path === '/supervisor/workorders' }" @click="$router.push('/supervisor/workorders')">
      <i class="nav-icon workorder-icon"></i>
      <span>工单管理</span>
    </div>
    <div class="nav-item" :class="{ active: $route.path === '/supervisor/profile' }" @click="$router.push('/supervisor/profile')">
      <i class="nav-icon profile-icon"></i>
      <span>我的</span>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'SupervisorNav'
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
