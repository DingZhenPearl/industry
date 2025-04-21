<template>
  <nav class="bottom-nav">
    <div class="nav-item" :class="{ active: $route.path === '/supervisor/monitor' }" @click="navigateTo('/supervisor/monitor')">
      <i class="nav-icon monitor-icon"></i>
      <span>监控中心</span>
    </div>
    <div class="nav-item" :class="{ active: $route.path === '/supervisor/team' }" @click="navigateTo('/supervisor/team')">
      <i class="nav-icon team-icon"></i>
      <span>团队管理</span>
    </div>

    <div class="nav-item" :class="{ active: $route.path === '/supervisor/workorders' }" @click="navigateTo('/supervisor/workorders')">
      <i class="nav-icon workorder-icon"></i>
      <span>工单管理</span>
    </div>
    <div class="nav-item" :class="{ active: $route.path === '/supervisor/profile' }" @click="navigateTo('/supervisor/profile')">
      <i class="nav-icon profile-icon"></i>
      <span>我的</span>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'SupervisorNav',
  methods: {
    navigateTo(path) {
      // 如果不是当前路径才进行跳转
      if (this.$route.path !== path) {
        // 获取当前的uid参数或从本地存储中获取
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
        const currentUid = this.$route.query.uid || userInfo.uid

        // 构建带有uid参数的路由
        if (currentUid) {
          this.$router.push({ path, query: { uid: currentUid } })
        } else {
          this.$router.push(path)
        }
      }
    }
  }
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
