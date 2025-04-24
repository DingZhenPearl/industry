<template>
  <div class="equipment-detail">
    <header class="header">
      <div class="header-content">
        <button class="back-btn" @click="goBack">
          <i class="back-icon"></i>
          返回
        </button>
        <h1>设备详情</h1>
      </div>
    </header>

    <pull-to-refresh @refresh="onPullRefresh" class="pull-refresh-container">
      <div class="content">
        <!-- 使用设备详情组件 -->
        <equipment-detail-component
          :equipment="formattedEquipment"
          :device-history="deviceHistory"
          :loading="loading"
          :error="error"
          :auto-refresh-enabled="autoRefresh"
          :refresh-rate="refreshRate"
          :sensor-projects="sensorProjects"
          @retry="fetchEquipmentDetail"
          @refresh-data="fetchLatestDeviceData"
          @fetch-history="fetchDeviceHistory"
        >
          <!-- 自定义操作按钮 -->
          <template v-slot:actions>
            <button class="action-btn" @click="assignMaintenance" v-if="formattedEquipment && formattedEquipment.status === 'warning'">安排维护</button>
          </template>
        </equipment-detail-component>
      </div>
    </pull-to-refresh>

    <SupervisorNav />
  </div>
</template>

<script>
import SupervisorNav from '@/components/SupervisorNav.vue'
import EquipmentDetailComponent from '@/components/EquipmentDetailComponent.vue'
import PullToRefresh from '@/components/PullToRefresh.vue'

export default {
  name: 'EquipmentDetail',
  components: {
    SupervisorNav,
    EquipmentDetailComponent,
    PullToRefresh
  },
  data() {
    return {
      equipment: {
        id: '',
        name: '',
        location: '',
        status: 'normal',
        statusText: '正常',
        sensorId: '',
        description: ''
      },
      sensors: [],
      currentSensor: null,
      deviceHistory: [],
      loading: false,
      error: null,
      autoRefresh: true,
      refreshRate: 10000, // 10秒更新一次
      sensorProjects: {}
    }
  },
  computed: {
    // 格式化设备数据以适应组件
    formattedEquipment() {
      if (!this.equipment) return null;

      // 构建传感器数据对象
      const sensorData = {};
      if (this.sensors && this.sensors.length > 0) {
        this.sensors.forEach(sensor => {
          // 从传感器名称反向查找键名
          const key = this.getSensorKeyByLabel(sensor.name);
          if (key) {
            sensorData[key] = sensor.value;
          }
        });
      }

      return {
        id: this.equipment.id,
        name: this.equipment.name,
        code: this.equipment.sensorId,
        productionLine: this.equipment.lineName || this.equipment.location,
        status: this.equipment.status,
        statusText: this.equipment.statusText,
        runtime: this.equipment.runtime || 0, // 使用设备的运行时间
        sensorData: sensorData
      };
    }
  },
  created() {
    // 获取路由参数中的设备ID
    const equipmentId = this.$route.params.id
    this.equipment.id = equipmentId

    // 这里应该根据ID从API获取设备详情
    this.fetchEquipmentDetail(equipmentId)

    // 打印自动刷新设置
    console.log('厂长设备详情页面初始化，自动刷新:', this.autoRefresh, '刷新间隔:', this.refreshRate)
  },
  mounted() {
    // 测试自动刷新功能
    console.log('厂长设备详情页面挂载完成，测试自动刷新功能');

    // 手动触发一次数据刷新，测试是否正常工作
    setTimeout(() => {
      console.log('手动触发数据刷新');
      this.fetchLatestDeviceData();
    }, 2000);
  },
  methods: {
    async fetchEquipmentDetail(id) {
      this.loading = true;
      this.error = null;

      try {
        // 从后端获取设备详情
        console.log('获取设备ID:', id, '的详情')

        const response = await fetch(`/api/equipment/with-status?equipment_id=${id}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取设备详情失败: ${response.status}`);
        }

        const result = await response.json();
        console.log('设备详情数据:', result);

        if (result.success && result.data && result.data.length > 0) {
          // 获取设备数据
          const deviceData = result.data[0];

          // 处理sensor_data字段，确保是对象
          if (deviceData.sensor_data && typeof deviceData.sensor_data === 'string') {
            try {
              deviceData.sensor_data = JSON.parse(deviceData.sensor_data);
            } catch (e) {
              console.error('解析sensor_data失败:', e);
              deviceData.sensor_data = {};
            }
          }

          // 更新设备数据
          this.equipment = {
            id: deviceData.id,
            name: deviceData.equipment_name,
            line_id: deviceData.line_id,
            location: deviceData.line_name || '未知产线',
            lineName: deviceData.line_name || '未知产线',
            sensorId: deviceData.equipment_code,
            description: deviceData.description || '暂无详细信息',
            runtime: deviceData.runtime_hours || 0, // 从 API 返回的数据中获取运行时间
            status: deviceData.status === '故障' ? 'error' :
                   deviceData.status === '停机' ? 'stopped' :
                   deviceData.status === '维修中' ? 'warning' :
                   deviceData.fault_probability > 0.7 ? 'error' :
                   deviceData.fault_probability > 0.3 ? 'warning' : 'normal',
            statusText: deviceData.status === '故障' ? '故障' :
                       deviceData.status === '停机' ? '已停机' :
                       deviceData.status === '维修中' ? '维修中' :
                       deviceData.fault_probability > 0.7 ? '危险' :
                       deviceData.fault_probability > 0.3 ? '预警' : '正常'
          };

          console.log('设备产线名称:', deviceData.line_name);

          // 更新传感器数据
          if (deviceData.sensor_data) {
            this.sensors = [];
            for (const [key, value] of Object.entries(deviceData.sensor_data)) {
              const unit = this.getSensorUnit(key);
              this.sensors.push({
                name: this.getSensorLabel(key),
                value: value,
                unit: unit
              });
            }

            if (this.sensors.length > 0) {
              this.currentSensor = this.sensors[0];
            }
          }

          // 获取传感器项目数据
          if (deviceData.sensor_projects) {
            try {
              // 处理传感器项目数据，确保是对象
              if (typeof deviceData.sensor_projects === 'string') {
                this.sensorProjects = JSON.parse(deviceData.sensor_projects);
              } else {
                this.sensorProjects = deviceData.sensor_projects;
              }
            } catch (e) {
              console.error('解析传感器项目数据失败:', e);
              this.sensorProjects = {};
            }
          } else {
            // 如果没有传感器项目数据，尝试从专门的API获取
            this.fetchSensorProjects(deviceData.id);
          }

          // 获取设备历史数据
          this.fetchDeviceHistory();
        } else {
          this.error = result.error || '未找到设备数据';
        }
      } catch (error) {
        console.error('获取设备详情出错:', error);
        this.error = error.message || '获取设备详情出错';
      } finally {
        this.loading = false;
      }
    },

    // 获取设备历史数据
    async fetchDeviceHistory(limit = 10) {
      if (!this.equipment || !this.equipment.id) return;

      try {
        const response = await fetch(`/api/equipment/status-history?equipment_id=${this.equipment.id}&limit=${limit}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取设备历史数据失败: ${response.status}`);
        }

        const result = await response.json();
        console.log('设备历史数据:', result);

        if (result.success && result.data) {
          // 将数据按时间正序排列
          this.deviceHistory = result.data
            .sort((a, b) => new Date(a.collection_time) - new Date(b.collection_time))
            .map(item => {
              // 处理sensor_data字段，确保是对象
              if (item.sensor_data && typeof item.sensor_data === 'string') {
                try {
                  item.sensor_data = JSON.parse(item.sensor_data);
                } catch (e) {
                  console.error('解析sensor_data失败:', e);
                  item.sensor_data = {};
                }
              }
              return item;
            });
        } else {
          console.error('获取设备历史数据失败:', result.error || '未知错误');
        }
      } catch (error) {
        console.error('获取设备历史数据出错:', error);
      }
    },

    // 获取最新设备数据
    async fetchLatestDeviceData() {
      if (!this.equipment || !this.equipment.id) return;

      try {
        // 获取最新的一条记录
        const response = await fetch(`/api/equipment/status-history?equipment_id=${this.equipment.id}&limit=1`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取设备最新数据失败: ${response.status}`);
        }

        const result = await response.json();
        console.log('获取到最新设备数据:', result);

        if (result.success && result.data && result.data.length > 0) {
          const latestData = result.data[0];

          // 处理sensor_data字段，确保是对象
          if (latestData.sensor_data && typeof latestData.sensor_data === 'string') {
            try {
              latestData.sensor_data = JSON.parse(latestData.sensor_data);
            } catch (e) {
              console.error('解析sensor_data失败:', e);
              latestData.sensor_data = {};
            }
          }

          // 检查是否是新数据
          const isNewData = this.deviceHistory.length === 0 ||
                         new Date(latestData.collection_time) > new Date(this.deviceHistory[this.deviceHistory.length - 1].collection_time);

          if (isNewData) {
            console.log('检测到新数据，添加到历史数据中');
            // 添加新数据到历史数据中
            this.deviceHistory.push(latestData);

            // 如果历史数据超过限制，删除最早的数据
            if (this.deviceHistory.length > 10) {
              this.deviceHistory.shift();
            }

            // 对数据进行排序，确保按时间正序排列
            this.deviceHistory.sort((a, b) => new Date(a.collection_time) - new Date(b.collection_time));

            // 创建一个新数组，触发Vue的响应式更新
            this.deviceHistory = [...this.deviceHistory];
          }

          // 更新传感器数据
          if (latestData.sensor_data) {
            this.sensors = [];
            for (const [key, value] of Object.entries(latestData.sensor_data)) {
              const unit = this.getSensorUnit(key);
              this.sensors.push({
                name: this.getSensorLabel(key),
                value: value,
                unit: unit
              });
            }

            if (this.sensors.length > 0 && this.currentSensor) {
              // 更新当前选中的传感器数据
              const sensorName = this.currentSensor.name;
              const updatedSensor = this.sensors.find(s => s.name === sensorName);
              if (updatedSensor) {
                this.currentSensor = updatedSensor;
              } else {
                this.currentSensor = this.sensors[0];
              }
            }
          }

          // 更新设备状态
          this.equipment.status = latestData.status === '故障' ? 'error' :
                                 latestData.status === '停机' ? 'stopped' :
                                 latestData.status === '维修中' ? 'warning' :
                                 latestData.fault_probability > 0.7 ? 'error' :
                                 latestData.fault_probability > 0.3 ? 'warning' : 'normal';
          this.equipment.statusText = latestData.status === '故障' ? '故障' :
                                     latestData.status === '停机' ? '已停机' :
                                     latestData.status === '维修中' ? '维修中' :
                                     latestData.fault_probability > 0.7 ? '危险' :
                                     latestData.fault_probability > 0.3 ? '预警' : '正常';
        }
      } catch (error) {
        console.error('获取设备最新数据出错:', error);
      }
    },



    assignMaintenance() {
      // 安排维护的逻辑
      console.log('安排设备维护');
    },

    goBack() {
      // 使用导航辅助函数返回到监控中心页面
      import('@/utils/navigationHelper').then(({ navigateWithUid }) => {
        navigateWithUid(this.$router, '/supervisor/monitor');
      });
    },

    // 根据产线 ID 获取产线名称
    async fetchProductionLineName(lineId) {
      if (!lineId) return;

      try {
        console.log('获取产线信息, 产线ID:', lineId);
        const response = await fetch(`/api/production-line/detail?line_id=${lineId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取产线信息失败: ${response.status}`);
        }

        const result = await response.json();
        console.log('产线信息:', result);

        if (result.success && result.data && result.data.line) {
          const lineData = result.data.line;
          console.log('获取到产线名称:', lineData.line_name);

          // 更新设备的产线信息
          this.equipment.lineName = lineData.line_name;
          this.equipment.location = lineData.line_name;
        } else {
          console.error('获取产线信息失败: 没有找到产线数据');
        }
      } catch (error) {
        console.error('获取产线信息出错:', error);
      }
    },

    // 获取传感器标签
    getSensorLabel(key) {
      const labelMap = {
        'temperature': '温度',
        'pressure': '压力',
        'speed': '转速',
        'vibration': '振动',
        'noise': '噪音',
        'humidity': '湿度',
        'voltage': '电压',
        'current': '电流'
      };
      return labelMap[key] || key;
    },

    // 根据标签获取传感器键名
    getSensorKeyByLabel(label) {
      const keyMap = {
        '温度': 'temperature',
        '压力': 'pressure',
        '转速': 'speed',
        '振动': 'vibration',
        '噪音': 'noise',
        '湿度': 'humidity',
        '电压': 'voltage',
        '电流': 'current'
      };
      return keyMap[label] || null;
    },

    // 获取传感器单位
    getSensorUnit(key) {
      const unitMap = {
        'temperature': '°C',
        'pressure': 'MPa',
        'speed': 'rpm',
        'vibration': 'mm/s',
        'noise': 'dB',
        'humidity': '%',
        'voltage': 'V',
        'current': 'A'
      };
      return unitMap[key] || '';
    },

    // 获取设备的传感器项目列表
    async fetchSensorProjects(equipmentId) {
      if (!equipmentId) return;

      try {
        const response = await fetch(`/api/equipment/sensor-projects/${equipmentId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          console.error(`获取传感器项目列表失败: ${response.status}`);
          return;
        }

        const result = await response.json();

        if (result.success && result.data && result.data.sensor_projects) {
          // 处理传感器项目数据
          let sensorProjects = result.data.sensor_projects;
          if (typeof sensorProjects === 'string') {
            try {
              sensorProjects = JSON.parse(sensorProjects);
            } catch (e) {
              console.error('解析传感器项目数据失败:', e);
              sensorProjects = {};
            }
          }

          // 保存传感器项目数据
          this.sensorProjects = sensorProjects;
        }
      } catch (error) {
        console.error('获取传感器项目列表出错:', error);
      }
    },

    // 处理下拉刷新事件
    async onPullRefresh() {
      console.log('下拉刷新触发');

      try {
        // 重新获取设备详情
        await this.fetchEquipmentDetail(this.equipment.id);

        // 重新获取设备历史数据
        await this.fetchDeviceHistory();

        // 显示刷新成功提示
        this.$nextTick(() => {
          // 如果有需要，可以在这里添加刷新成功的提示
          console.log('下拉刷新完成');
        });
      } catch (error) {
        console.error('下拉刷新出错:', error);
      }
    }
  }
}
</script>

<style scoped>
.equipment-detail {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding-bottom: 60px; /* 为底部导航留出空间 */
}

.header {
  background-color: #2196F3;
  color: white;
  padding: 15px;
}

.header-content {
  display: flex;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
}

.header h1 {
  flex: 1;
  text-align: center;
}

.back-btn {
  display: flex;
  align-items: center;
  background: none;
  border: none;
  color: white;
  font-size: 16px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  position: absolute;
  left: 0;
}

.back-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.pull-refresh-container {
  min-height: calc(100vh - 60px - 60px); /* 减去头部和底部导航的高度 */
  display: flex;
  flex-direction: column;
}

/* 安卓特定样式 */
.android-device .back-btn {
  min-height: 48px;
  padding: 12px 16px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .header-content {
    padding: 0 10px;
  }

  .back-btn {
    padding: 10px;
  }

  .content {
    padding: 10px;
  }
}

.back-icon {
  display: inline-block;
  width: 20px;
  height: 20px;
  margin-right: 5px;
  background-color: white;
  mask-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>');
  mask-repeat: no-repeat;
  mask-position: center;
  mask-size: contain;
}

.content {
  flex: 1;
  padding: 15px;
}

/* 信息卡片样式 */
.info-card {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.info-row {
  display: flex;
  margin-bottom: 10px;
}

.info-item {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.label {
  color: #666;
  font-size: 14px;
  margin-bottom: 5px;
}

.value {
  font-size: 16px;
  font-weight: 500;
}

.value.normal {
  color: #4CAF50;
}

.value.warning {
  color: #FF9800;
}

.value.error {
  color: #F44336;
}

/* 传感器数据样式 */
.sensor-data {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.sensor-data h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
}

.sensor-type {
  font-size: 16px;
  color: #666;
  margin-bottom: 10px;
}

.sensor-value {
  font-size: 32px;
  font-weight: bold;
  color: #2196F3;
}

.unit {
  font-size: 18px;
  margin-left: 5px;
}

/* 时间范围选择器样式 */
.time-range {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.time-range h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
}

.date-inputs {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.date-input, .time-input {
  display: flex;
  flex-direction: column;
}

.date-input span, .time-input span {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.date-input input, .time-input input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.generate-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

/* 图表容器样式 */
.chart-container {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chart-container h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
}

.chart {
  width: 100%;
  height: 300px;
  position: relative;
}

.chart-placeholder {
  height: 100%;
  border: 1px solid #eee;
  border-radius: 4px;
  position: relative;
  padding: 20px;
}

.chart-legend {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-bottom: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  font-size: 12px;
}

.color-box {
  width: 12px;
  height: 12px;
  margin-right: 5px;
  border-radius: 2px;
}

.color-box.normal {
  background-color: #4CAF50;
}

.color-box.warning {
  background-color: #FFD700;
}

.color-box.danger {
  background-color: #F44336;
}

.chart-y-axis {
  position: absolute;
  left: 0;
  top: 40px;
  bottom: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
  padding-right: 5px;
}

.chart-line {
  position: absolute;
  left: 40px;
  right: 20px;
  top: 40px;
  bottom: 20px;
}

/* 模态框样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  font-size: 24px;
  cursor: pointer;
  color: #666;
  background: none;
  border: none;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #333;
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

textarea.form-input {
  resize: vertical;
  min-height: 80px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn.cancel {
  background-color: #f5f5f5;
  color: #333;
}

.btn.submit {
  background-color: #2196F3;
  color: white;
}

.action-btn {
  background-color: #2196F3;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  margin-right: 10px;
  cursor: pointer;
  font-size: 14px;
}

.action-btn:hover {
  background-color: #0b7dda;
}
</style>