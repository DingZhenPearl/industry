<template>
  <div class="safety-monitor">
    <header class="header">
      <h1>安全监控</h1>
    </header>
    
    <div class="content">
      <div class="monitor-cards">
        <div class="monitor-card">
          <h3>今日安全状况</h3>
          <div class="status good">良好</div>
        </div>
        
        <div class="monitor-card">
          <h3>预警数量</h3>
          <div class="count">2</div>
        </div>
        
        <div class="monitor-card">
          <h3>待处理隐患</h3>
          <div class="count">1</div>
        </div>
      </div>

      <div class="monitor-list">
        <h3>实时监控</h3>
        <div class="list-item" v-for="(item, index) in monitorItems" :key="index">
          <div class="area-info">
            <div class="area-name">{{ item.area }}</div>
            <div class="area-status" :class="item.status">{{ item.statusText }}</div>
          </div>
          <div class="detail">{{ item.detail }}</div>
        </div>
      </div>
    </div>

    <SafetyNav />
  </div>
</template>

<script>
import SafetyNav from '@/components/SafetyNav.vue'

export default {
  name: 'SafetyMonitor',
  components: {
    SafetyNav
  },
  data() {
    return {
      monitorItems: [
        {
          area: '一号生产线',
          status: 'normal',
          statusText: '正常',
          detail: '设备运行正常，无安全隐患'
        },
        {
          area: '二号生产线',
          status: 'warning',
          statusText: '预警',
          detail: '检测到异常振动，建议检查'
        }
      ]
    }
  }
}
</script>

<style scoped>
.safety-monitor {
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

.monitor-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.monitor-card {
  background: white;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.monitor-card h3 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
}

.status {
  font-size: 18px;
  font-weight: bold;
}

.status.good {
  color: #4CAF50;
}

.count {
  font-size: 24px;
  font-weight: bold;
  color: #2196F3;
}

.monitor-list {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.list-item {
  border-bottom: 1px solid #eee;
  padding: 15px 0;
}

.list-item:last-child {
  border-bottom: none;
}

.area-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.area-name {
  font-weight: bold;
}

.area-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.area-status.normal {
  background: #e8f5e9;
  color: #4CAF50;
}

.area-status.warning {
  background: #fff3e0;
  color: #ff9800;
}

.detail {
  color: #666;
  font-size: 14px;
}
</style>
