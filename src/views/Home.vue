<template>
  <div class="home">
    <header class="header">
      <h1>首页</h1>
    </header>
    
    <div class="content">
      <div class="module" @click="navigateTo('device')">
        <img src="@/assets/device.png" alt="设备监控">
        <h2>设备监控</h2>
      </div>
      
      <div class="module" @click="navigateTo('production')">
        <img src="@/assets/production.png" alt="生产监控">
        <h2>生产监控</h2>
      </div>
      
      <div class="module" @click="navigateTo('workorder')">
        <img src="@/assets/workorder.png" alt="工单管理">
        <h2>工单管理</h2>
      </div>
    </div>
    
    <BottomNav />
  </div>
</template>

<script>
import BottomNav from '@/components/BottomNav.vue';

export default {
  name: 'HomePage',
  components: {
    BottomNav
  },
  methods: {
    navigateTo(module) {
      console.log(`导航到${module}模块`);
      // 这里可以添加导航逻辑
    }
  }
}
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.header {
  background-color: #2196F3;
  color: white;
  padding: 15px 0;
  text-align: center;
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-around;
  padding: 20px;
}

.module {
  width: 80%;
  max-width: 350px;
  background-color: #f5f5f5;
  border-radius: 10px;
  padding: 20px;
  margin: 10px 0;
  text-align: center;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.3s;
}

.module:hover {
  transform: scale(1.05);
}

.module img {
  max-width: 100%;
  height: auto;
  margin-bottom: 10px;
}

.bottom-nav {
  display: flex;
  justify-content: space-around;
  background-color: #f8f8f8;
  padding: 10px 0;
  border-top: 1px solid #e0e0e0;
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