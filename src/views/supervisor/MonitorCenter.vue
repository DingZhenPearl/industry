<template>
  <div class="monitor-center">
    <header class="header">
      <h1>监控中心</h1>
    </header>
    
    <div class="content">
      <!-- 增加实时监控卡片 -->
      <div class="status-cards">
        <div class="status-card running">
          <h3>运行产线</h3>
          <div class="count">8</div>
          <div class="status-detail">正常运行中</div>
        </div>
        <div class="status-card warning">
          <h3>预警设备</h3>
          <div class="count">2</div>
          <div class="status-detail">需要维护</div>
        </div>
        <div class="status-card stopped">
          <h3>停机产线</h3>
          <div class="count">1</div>
          <div class="status-detail">故障处理中</div>
        </div>
      </div>

      <div class="monitor-stats">
        <div class="stat-item">
          <span class="stat-label">设备运行率</span>
          <span class="stat-value">95%</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">生产完成率</span>
          <span class="stat-value">87%</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">任务达成率</span>
          <span class="stat-value">92%</span>
        </div>
      </div>

      <!-- 增加产线状态列表 -->
      <div class="production-lines">
        <h3 class="section-title">产线运行状态</h3>
        <div class="line-list">
          <div class="line-item" v-for="line in productionLines" :key="line.id">
            <div class="line-header">
              <span class="line-name">{{ line.name }}</span>
              <span class="line-status" :class="line.status">{{ line.statusText }}</span>
            </div>
            <div class="line-details">
              <div class="detail-item">
                <span class="label">产能利用率</span>
                <span class="value">{{ line.utilization }}%</span>
              </div>
              <div class="detail-item">
                <span class="label">当前产量</span>
                <span class="value">{{ line.output }}/{{ line.target }}</span>
              </div>
              <div class="detail-item">
                <span class="label">运行时长</span>
                <span class="value">{{ line.runtime }}h</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <SupervisorNav />
  </div>
</template>

<script>
import SupervisorNav from '@/components/SupervisorNav.vue'

export default {
  name: 'MonitorCenter',
  components: {
    SupervisorNav
  },
  data() {
    return {
      productionLines: [
        {
          id: 1,
          name: '一号生产线',
          status: 'running',
          statusText: '运行中',
          utilization: 95,
          output: 850,
          target: 1000,
          runtime: 18.5
        },
        {
          id: 2,
          name: '二号生产线',
          status: 'warning',
          statusText: '预警',
          utilization: 75,
          output: 620,
          target: 1000,
          runtime: 16.8
        },
        {
          id: 3,
          name: '三号生产线',
          status: 'stopped',
          statusText: '已停机',
          utilization: 0,
          output: 420,
          target: 1000,
          runtime: 8.2
        }
      ]
    }
  }
}
</script>

<style scoped>
.monitor-center {
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

.monitor-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.stat-item {
  background: white;
  padding: 15px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #2196F3;
}

.monitor-chart {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.status-card {
  padding: 20px;
  border-radius: 8px;
  color: white;
  text-align: center;
}

.status-card.running {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
}

.status-card.warning {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
}

.status-card.stopped {
  background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
}

.status-card .count {
  font-size: 36px;
  font-weight: bold;
  margin: 10px 0;
}

.section-title {
  margin: 20px 0;
  font-size: 18px;
  color: #333;
}

.line-list {
  display: grid;
  gap: 15px;
}

.line-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.line-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.line-name {
  font-weight: bold;
  font-size: 16px;
}

.line-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
}

.line-status.running {
  background: #e8f5e9;
  color: #4CAF50;
}

.line-status.warning {
  background: #fff3e0;
  color: #ff9800;
}

.line-status.stopped {
  background: #ffebee;
  color: #f44336;
}

.line-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.detail-item {
  text-align: center;
}

.detail-item .label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.detail-item .value {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}
</style>
