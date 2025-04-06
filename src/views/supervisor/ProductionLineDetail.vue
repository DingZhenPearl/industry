<template>
  <div class="production-line-detail">
    <header class="header">
      <div class="header-left">
        <button class="back-btn" @click="$router.go(-1)">&larr; 返回</button>
        <h1>{{ productionLine.name }} - 详细信息</h1>
      </div>
      <div class="header-right">
        <span :class="['status-tag', productionLine.status]">{{ productionLine.statusText }}</span>
      </div>
    </header>

    <div class="content">
      <!-- 基本信息卡片 -->
      <div class="info-card">
        <div class="info-item">
          <span class="label">产能利用率</span>
          <span class="value">{{ productionLine.utilization }}%</span>
        </div>
        <div class="info-item">
          <span class="label">当前产量</span>
          <span class="value">{{ productionLine.output }}/{{ productionLine.target }}</span>
        </div>
        <div class="info-item">
          <span class="label">运行时长</span>
          <span class="value">{{ productionLine.runtime }}h</span>
        </div>
        <div class="info-item">
          <span class="label">负责工长</span>
          <span class="value">{{ productionLine.manager }}</span>
        </div>
      </div>

      <!-- 甘特图区域 -->
      <div class="gantt-section">
        <div class="section-header">
          <h2>生产计划甘特图</h2>
          <div class="gantt-controls">
            <div class="date-range">
              <input type="date" v-model="startDate" @change="updateGantt">
              <span>至</span>
              <input type="date" v-model="endDate" @change="updateGantt">
            </div>
            <div class="zoom-controls">
              <button @click="zoomLevel = 'day'">日</button>
              <button @click="zoomLevel = 'week'">周</button>
              <button @click="zoomLevel = 'month'">月</button>
            </div>
          </div>
        </div>
        <div class="gantt-container" ref="ganttContainer"></div>
      </div>

      <!-- 设备状态列表 -->
      <div class="equipment-section">
        <h2>设备状态</h2>
        <div class="equipment-list">
          <div v-for="device in devices" :key="device.id" class="equipment-card">
            <div class="equipment-header">
              <span class="equipment-name">{{ device.name }}</span>
              <span :class="['status-indicator', device.status]"></span>
            </div>
            <div class="equipment-body">
              <div class="equipment-info">
                <div class="info-row">
                  <span class="label">类型：</span>
                  <span>{{ device.typeText }}</span>
                </div>
                <div class="info-row">
                  <span class="label">运行时长：</span>
                  <span>{{ device.runtime }}h</span>
                </div>
                <div class="info-row">
                  <span class="label">负责人：</span>
                  <span>{{ device.manager }}</span>
                </div>
              </div>
              <div class="equipment-actions">
                <button class="action-btn" @click="viewDeviceDetail(device)">详情</button>
                <button v-if="device.status === 'warning'" class="action-btn warning" @click="assignMaintenance(device)">维护</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 人员排班信息 -->
      <div class="staff-section">
        <h2>人员排班</h2>
        <div class="shift-schedule">
          <table>
            <thead>
              <tr>
                <th>班次</th>
                <th>时间</th>
                <th>工长</th>
                <th>操作员</th>
                <th>质检员</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="shift in shifts" :key="shift.id">
                <td>{{ shift.name }}</td>
                <td>{{ shift.time }}</td>
                <td>{{ shift.foreman }}</td>
                <td>{{ shift.operators.join(', ') }}</td>
                <td>{{ shift.inspector }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import 'dhtmlx-gantt/codebase/dhtmlxgantt.css'

export default {
  name: 'ProductionLineDetail',
  data() {
    return {
      productionLine: {
        id: 1,
        name: '一号生产线',
        status: 'running',
        statusText: '运行中',
        utilization: 95,
        output: 850,
        target: 1000,
        runtime: 18.5,
        manager: '张工长'
      },
      devices: [
        {
          id: 1,
          name: '注塑机A-01',
          type: 'production',
          typeText: '生产设备',
          status: 'running',
          runtime: 126.5,
          manager: '张工'
        },
        {
          id: 2,
          name: '检测仪B-01',
          type: 'inspection',
          typeText: '检测设备',
          status: 'warning',
          runtime: 85.2,
          manager: '李工'
        }
      ],
      shifts: [
        {
          id: 1,
          name: '早班',
          time: '06:00-14:00',
          foreman: '张工长',
          operators: ['王操作员', '李操作员'],
          inspector: '赵质检'
        },
        {
          id: 2,
          name: '中班',
          time: '14:00-22:00',
          foreman: '李工长',
          operators: ['刘操作员', '陈操作员'],
          inspector: '钱质检'
        }
      ],
      startDate: new Date().toISOString().split('T')[0],
      endDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      zoomLevel: 'day'
    }
  },
  mounted() {
    this.initGantt()
  },
  methods: {
    initGantt() {
      // 使用window.gantt访问甘特图对象
      const gantt = window.gantt
      gantt.init(this.$refs.ganttContainer)
      
      // 配置甘特图
      gantt.config.date_format = '%Y-%m-%d %H:%i'
      gantt.config.scale_height = 60
      
      // 示例数据
      const tasks = {
        data: [
          { id: 1, text: '产品A生产', start_date: '2023-07-10 08:00', end_date: '2023-07-12 18:00', progress: 0.6 },
          { id: 2, text: '产品B生产', start_date: '2023-07-13 08:00', end_date: '2023-07-15 18:00', progress: 0.3 }
        ],
        links: [
          { id: 1, source: 1, target: 2, type: '0' }
        ]
      }
      
      gantt.parse(tasks)
    },
    updateGantt() {
      // 更新甘特图时间范围
      const gantt = window.gantt
      gantt.config.start_date = new Date(this.startDate)
      gantt.config.end_date = new Date(this.endDate)
      gantt.render()
    },
    viewDeviceDetail(device) {
      this.$router.push(`/supervisor/equipment-detail/${device.id}`)
    },
    assignMaintenance(device) {
      // 实现设备维护分配逻辑
      console.log('分配设备维护:', device)
    }
  }
}
</script>

<style scoped>
.production-line-detail {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.back-btn {
  padding: 8px 15px;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.status-tag {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
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

.info-card {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.info-item {
  text-align: center;
}

.info-item .label {
  display: block;
  color: #666;
  margin-bottom: 5px;
}

.info-item .value {
  font-size: 24px;
  font-weight: bold;
  color: #2196F3;
}

.gantt-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.gantt-controls {
  display: flex;
  gap: 20px;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 10px;
}

.zoom-controls button {
  padding: 6px 12px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.gantt-container {
  height: 400px;
  width: 100%;
}

.equipment-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.equipment-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.equipment-card {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
}

.equipment-header {
  padding: 15px;
  background: #f5f5f5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-indicator.running {
  background: #4CAF50;
}

.status-indicator.warning {
  background: #ff9800;
}

.status-indicator.stopped {
  background: #f44336;
}

.equipment-body {
  padding: 15px;
}

.equipment-info {
  margin-bottom: 15px;
}

.info-row {
  display: flex;
  margin-bottom: 5px;
}

.info-row .label {
  color: #666;
  width: 80px;
}

.equipment-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background: #e3f2fd;
  color: #2196F3;
}

.action-btn.warning {
  background: #fff3e0;
  color: #ff9800;
}

.staff-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
}

.shift-schedule table {
  width: 100%;
  border-collapse: collapse;
}

.shift-schedule th,
.shift-schedule td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.shift-schedule th {
  background: #f5f5f5;
  font-weight: bold;
}
</style>