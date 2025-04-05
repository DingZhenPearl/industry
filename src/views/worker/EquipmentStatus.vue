<template>
  <div class="equipment-status">
    <header class="header">
      <h1>设备状态</h1>
    </header>
    
    <div class="content">
      <!-- 我负责的设备状态卡片 -->
      <div class="assigned-device">
        <div class="device-header">
          <h3>我负责的设备</h3>
          <span :class="['status-tag', myDevice.status]">{{ myDevice.statusText }}</span>
        </div>
        <div class="device-body">
          <div class="info-row">
            <span>设备名称：{{ myDevice.name }}</span>
            <span>设备编号：{{ myDevice.code }}</span>
          </div>
          <div class="info-row">
            <span>所属产线：{{ myDevice.productionLine }}</span>
            <span>运行时长：{{ myDevice.runtime }}h</span>
          </div>
          <div class="parameter-list">
            <div class="parameter-item">
              <span class="label">温度</span>
              <span class="value" :class="{ warning: myDevice.temperature > 80 }">
                {{ myDevice.temperature }}°C
              </span>
            </div>
            <div class="parameter-item">
              <span class="label">转速</span>
              <span class="value">{{ myDevice.speed }}rpm</span>
            </div>
            <div class="parameter-item">
              <span class="label">压力</span>
              <span class="value">{{ myDevice.pressure }}MPa</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作按钮组 -->
      <div class="action-group">
        <button 
          class="action-btn" 
          :class="{ disabled: myDevice.status === 'stopped' }"
          @click="checkParameters"
        >参数检查</button>
        <button 
          class="action-btn" 
          :class="{ disabled: myDevice.status === 'stopped' }"
          @click="reportIssue"
        >故障上报</button>
        <button 
          class="action-btn"
          @click="viewManual"
        >操作手册</button>
      </div>

      <!-- 运行日志 -->
      <div class="operation-log">
        <h3>运行日志</h3>
        <div class="log-list">
          <div class="log-item" v-for="log in operationLogs" :key="log.time">
            <span class="log-time">{{ log.time }}</span>
            <span class="log-content">{{ log.content }}</span>
          </div>
        </div>
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
  },
  data() {
    return {
      myDevice: {
        name: '注塑机A-01',
        code: 'JSJ-001',
        productionLine: '一号生产线',
        status: 'running',
        statusText: '运行中',
        runtime: 126.5,
        temperature: 75,
        speed: 1200,
        pressure: 2.5
      },
      operationLogs: [
        { time: '2023-07-10 10:30', content: '完成设备日常检查' },
        { time: '2023-07-10 09:15', content: '设备启动运行' },
        { time: '2023-07-10 09:00', content: '更换润滑油' }
      ]
    }
  },
  methods: {
    checkParameters() {
      if(this.myDevice.status === 'stopped') return;
      console.log('检查设备参数');
    },
    reportIssue() {
      if(this.myDevice.status === 'stopped') return;
      this.$router.push('/worker/issues');
    },
    viewManual() {
      console.log('查看设备操作手册');
    }
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

.assigned-device {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.device-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.status-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-tag.running {
  background: #e8f5e9;
  color: #4CAF50;
}

.status-tag.warning {
  background: #fff3e0;
  color: #ff9800;
}

.status-tag.stopped {
  background: #ffebee;
  color: #f44336;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  color: #666;
  font-size: 14px;
}

.parameter-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.parameter-item {
  text-align: center;
}

.parameter-item .label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.parameter-item .value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.parameter-item .value.warning {
  color: #ff9800;
}

.action-group {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 15px;
}

.action-btn {
  padding: 12px;
  border: none;
  border-radius: 8px;
  background: white;
  color: #2196F3;
  font-size: 14px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.action-btn.disabled {
  background: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}

.operation-log {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.operation-log h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
}

.log-list {
  max-height: 200px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
  font-size: 14px;
}

.log-item:last-child {
  border-bottom: none;
}

.log-time {
  color: #999;
  margin-right: 15px;
  flex-shrink: 0;
}

.log-content {
  color: #666;
}
</style>
