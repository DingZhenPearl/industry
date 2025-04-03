<template>
  <div class="equipment-status">
    <header class="header">
      <h1>设备状态</h1>
    </header>
    
    <div class="content">
      <div class="status-content">
        <!-- 设备状态内容 -->
        <p>设备状态页面开发中...</p>
      </div>
    </div>

    <WorkerNav />
  </div>
</template>

<script>
import WorkerNav from '@/components/WorkerNav.vue'

export default {
  name: 'EquipmentStatus',
  components: {
    WorkerNav
  }
}
</script>

<style scoped>
.equipment-status {
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
