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
  box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
  z-index: 100;
  /* 安全区域适配 */
  padding-bottom: calc(8px + var(--safe-area-inset-bottom));
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  padding: 8px 0;
  flex: 1;
  position: relative;
  transition: all 0.2s ease;
}

.nav-item:active {
  opacity: 0.7;
  transform: scale(0.95);
}

.nav-icon {
  width: 24px;
  height: 24px;
  margin-bottom: 4px;
  background-color: #666;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.nav-item.active {
  color: #2196F3;
}

.nav-item.active .nav-icon {
  background-color: #2196F3;
}

/* 安卓特定样式 */
.android-device .bottom-nav {
  padding-bottom: calc(12px + var(--safe-area-inset-bottom));
}

.android-device .nav-item {
  font-size: 13px;
  font-weight: 500;
}

.android-device .nav-icon {
  width: 28px;
  height: 28px;
}

/* 添加触摸反馈效果 */
@media (max-width: 768px) {
  .nav-item {
    min-height: 56px;
  }

  .nav-item span {
    margin-top: 4px;
  }
}
</style>
