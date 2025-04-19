<template>
  <nav class="bottom-nav">
    <div class="nav-item" :class="{ active: $route.path === '/worker/workorders' }" @click="$router.push('/worker/workorders')">
      <i class="nav-icon tasks-icon"></i>
      <span>我的工单</span>
    </div>
    <div class="nav-item" :class="{ active: $route.path === '/worker/issues' }" @click="$router.push('/worker/issues')">
      <i class="nav-icon issues-icon"></i>
      <span>故障上报</span>
    </div>
    <div class="nav-item" :class="{ active: $route.path === '/worker/equipment-status' }" @click="$router.push('/worker/equipment-status')">
      <i class="nav-icon equipment-icon"></i>
      <span>设备状态</span>
    </div>

    <div class="nav-item" :class="{ active: $route.path === '/worker/profile' }" @click="$router.push('/worker/profile')">
      <i class="nav-icon profile-icon"></i>
      <span>我的</span>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'WorkerNav'
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
