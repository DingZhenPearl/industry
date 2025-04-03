<template>
  <div class="safety-warning">
    <header class="header">
      <h1>预警处理</h1>
    </header>
    
    <div class="content">
      <div class="warning-list">
        <div class="warning-item" v-for="(item, index) in warnings" :key="index">
          <div class="warning-header">
            <span class="warning-type">{{ item.type }}</span>
            <span class="warning-time">{{ item.time }}</span>
          </div>
          <div class="warning-content">
            <p>{{ item.description }}</p>
            <div class="warning-location">位置：{{ item.location }}</div>
          </div>
          <div class="warning-actions">
            <button class="action-btn primary" @click="handleWarning(item)">处理</button>
            <button class="action-btn" @click="ignoreWarning(item)">忽略</button>
          </div>
        </div>
      </div>
    </div>

    <SafetyNav />
  </div>
</template>

<script>
import SafetyNav from '@/components/SafetyNav.vue'

export default {
  name: 'SafetyWarning',
  components: {
    SafetyNav
  },
  data() {
    return {
      warnings: [
        {
          id: 1,
          type: '设备异常',
          time: '2023-07-10 10:30',
          description: '检测到设备温度异常升高',
          location: '一号生产线'
        },
        {
          id: 2,
          type: '环境预警',
          time: '2023-07-10 09:15',
          description: '空气质量超标',
          location: '生产车间A区'
        }
      ]
    }
  },
  methods: {
    handleWarning(warning) {
      console.log('处理预警:', warning)
    },
    ignoreWarning(warning) {
      console.log('忽略预警:', warning)
    }
  }
}
</script>

<style scoped>
.safety-warning {
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

.warning-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.warning-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.warning-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.warning-type {
  font-weight: bold;
  color: #f44336;
}

.warning-time {
  color: #666;
  font-size: 14px;
}

.warning-content {
  margin-bottom: 15px;
}

.warning-location {
  color: #666;
  font-size: 14px;
  margin-top: 5px;
}

.warning-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background: #f5f5f5;
  color: #666;
}

.action-btn.primary {
  background: #2196F3;
  color: white;
}
</style>
