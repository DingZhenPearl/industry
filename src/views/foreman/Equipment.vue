<template>
  <div class="equipment">
    <header class="header">
      <h1>设备监控</h1>
    </header>
    
    <div class="content">
      <div class="equipment-content">
        <!-- 设备监控内容 -->
        <p>设备监控页面开发中...</p>
      </div>
    </div>

    <ForemanNav />
  </div>
</template>

<script>
import ForemanNav from '@/components/ForemanNav.vue'

export default {
  name: 'ForemanEquipment',
  components: {
    ForemanNav
  }
}
</script>

<style scoped>
.equipment {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding-bottom: 60px;
}

.header {
  background-color: #2196F3;
  color: white;
  padding: 15px;
  text-align: center;
}

.content {
  flex: 1;
  padding: 15px;
}
</style>
