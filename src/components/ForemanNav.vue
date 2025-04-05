<template>
  <nav class="bottom-nav">
    <div class="nav-item" :class="{ active: $route.path === '/foreman/workorder' }" @click="$router.push('/foreman/workorder')">
      <i class="nav-icon workorder-icon"></i>
      <span>工单排班</span>
    </div>
    <div class="nav-item" :class="{ active: $route.path === '/foreman/equipment' }" @click="$router.push('/foreman/equipment')">
      <i class="nav-icon equipment-icon"></i>
      <span>设备与产线</span>
    </div>
    <div class="nav-item" :class="{ active: $route.path === '/foreman/statistics' }" @click="$router.push('/foreman/statistics')">
      <i class="nav-icon statistics-icon"></i>
      <span>统计分析</span>
    </div>
    <div class="nav-item" :class="{ active: $route.path === '/foreman/team' }" @click="$router.push('/foreman/team')">
      <i class="nav-icon team-icon"></i>
      <span>团队管理</span>
    </div>
    <div class="nav-item" :class="{ active: $route.path === '/foreman/profile' }" @click="$router.push('/foreman/profile')">
      <i class="nav-icon profile-icon"></i>
      <span>我的</span>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'ForemanNav'
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
