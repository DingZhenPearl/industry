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
        id: 0,
        name: '加载中...',
        status: '',
        statusText: '加载中',
        utilization: 0,
        output: 0,
        target: 0,
        runtime: 0,
        manager: ''
      },
      devices: [],
      loading: {
        productionLine: false,
        devices: false
      },
      error: {
        productionLine: null,
        devices: null
      },

      startDate: new Date().toISOString().split('T')[0],
      endDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      zoomLevel: 'day'
    }
  },
  created() {
    // 获取产线ID并加载数据
    const lineId = this.$route.params.id;
    if (lineId) {
      this.fetchProductionLineDetail(lineId);
    }
  },
  mounted() {
    this.initGantt()
  },
  methods: {
    async fetchProductionLineDetail(lineId) {
      this.loading.productionLine = true;
      this.error.productionLine = null;

      try {
        const response = await fetch(`/api/production_line/detail?line_id=${lineId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取产线详情失败: ${response.status}`);
        }

        const result = await response.json();

        if (result.success && result.data) {
          // 处理产线数据
          const lineData = result.data.line;

          // 根据状态设置状态文本
          let statusText = '未知';
          let status = '';

          if (lineData.status === '正常') {
            statusText = '运行中';
            status = 'running';
          } else if (lineData.status === '异常') {
            statusText = '异常';
            status = 'warning';
          } else if (lineData.status === '停机') {
            statusText = '已停机';
            status = 'stopped';
          }

          // 计算产能利用率
          const utilization = lineData.real_time_capacity && lineData.theoretical_capacity ?
            Math.round((lineData.real_time_capacity / lineData.theoretical_capacity) * 100) : 0;

          this.productionLine = {
            id: lineData.id,
            name: lineData.line_name,
            status: status,
            statusText: statusText,
            utilization: utilization,
            output: lineData.real_time_capacity || 0,
            target: lineData.theoretical_capacity || 0,
            runtime: lineData.runtime_hours || 0,
            manager: lineData.foreman_name || '未分配'
          };

          // 处理设备数据
          if (result.data.equipment && result.data.equipment.length > 0) {
            this.devices = result.data.equipment.map(device => {
              // 根据设备状态设置状态文本
              let deviceStatus = 'running';
              let deviceTypeText = '生产设备';

              if (device.status === '异常') {
                deviceStatus = 'warning';
              } else if (device.status === '停机') {
                deviceStatus = 'stopped';
              }

              if (device.type === 'inspection') {
                deviceTypeText = '检测设备';
              }

              return {
                id: device.id,
                name: device.equipment_name,
                type: device.type || 'production',
                typeText: deviceTypeText,
                status: deviceStatus,
                runtime: device.runtime_hours || 0,
                manager: device.worker_name || '未分配'
              };
            });
          }
        } else {
          throw new Error(result.error || '获取产线详情失败');
        }
      } catch (error) {
        this.error.productionLine = error.message || '获取产线详情出错';
        console.error('获取产线详情出错:', error);
      } finally {
        this.loading.productionLine = false;
      }
    },
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


</style>