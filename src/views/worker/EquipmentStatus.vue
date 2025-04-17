<template>
  <div class="equipment-status">
    <header class="header">
      <h1>设备状态</h1>
    </header>

    <div class="content">
      <!-- 加载中提示 -->
      <div class="loading-container" v-if="loading">
        <div class="loading-spinner"></div>
        <p>正在加载设备数据...</p>
      </div>

      <!-- 错误提示 -->
      <div class="error-container" v-if="error">
        <p class="error-message">{{ error }}</p>
        <button class="retry-btn" @click="fetchMyDevices">重试</button>
      </div>

      <!-- 无设备提示 -->
      <div class="empty-container" v-if="!loading && !error && myDevices.length === 0">
        <div class="empty-icon">🛠️</div>
        <p>您当前没有负责的设备</p>
      </div>

      <!-- 设备列表 -->
      <div v-if="!loading && !error && myDevices.length > 0">
        <!-- 设备选择器，当有多个设备时显示 -->
        <div class="device-selector" v-if="myDevices.length > 1">
          <label for="device-select">选择设备：</label>
          <select id="device-select" v-model="selectedDeviceId" @change="onDeviceChange" class="device-select">
            <option v-for="device in myDevices" :key="device.id" :value="device.id">
              {{ device.name }} ({{ device.code }})
            </option>
          </select>
        </div>

        <!-- 当前选中设备的状态卡片 -->
        <div class="assigned-device" v-if="currentDevice">
          <div class="device-header">
            <h3>设备状态</h3>
            <span :class="['status-tag', currentDevice.status]">{{ currentDevice.statusText }}</span>
          </div>
          <div class="device-body">
            <div class="info-row">
              <span>设备名称：{{ currentDevice.name }}</span>
              <span>设备编号：{{ currentDevice.code }}</span>
            </div>
            <div class="info-row">
              <span>所属产线：{{ currentDevice.productionLine }}</span>
              <span>运行时长：{{ currentDevice.runtime }}h</span>
            </div>
            <div class="parameter-list">
              <template v-if="currentDevice.sensorData && Object.keys(currentDevice.sensorData).length > 0">
                <div class="parameter-item" v-for="(value, key) in currentDevice.sensorData" :key="key">
                  <span class="label">{{ getSensorLabel(key) }}</span>
                  <span class="value" :class="{ warning: isSensorWarning(key, value) }">
                    {{ formatSensorValue(key, value) }}
                  </span>
                </div>
              </template>
              <div class="parameter-item" v-else>
                <span class="label">故障概率</span>
                <span class="value" :class="{ warning: currentDevice.faultProbability > 0.3 }">
                  {{ Math.round(currentDevice.faultProbability * 100) }}%
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮组 -->
        <div class="action-group" v-if="currentDevice">
          <button
            class="action-btn"
            :class="{ disabled: currentDevice.status === 'stopped' }"
            @click="checkParameters"
          >参数检查</button>
          <button
            class="action-btn"
            :class="{ disabled: currentDevice.status === 'stopped' }"
            @click="reportIssue"
          >故障上报</button>
          <button
            class="action-btn"
            @click="viewManual"
          >操作手册</button>
          <button
            class="action-btn refresh"
            @click="refreshDeviceData"
          >刷新数据</button>
        </div>

        <!-- 参数图表 -->
        <div class="parameter-chart" v-if="currentDevice">
          <div class="chart-header">
            <h3>参数变化图表</h3>
            <div class="chart-controls">
              <select v-model="selectedParameter" class="parameter-select" @change="updateChart">
                <option v-for="(label, key) in sensorLabels" :key="key" :value="key">
                  {{ label }}
                </option>
                <option value="fault_probability">故障概率</option>
              </select>
              <select v-model="historyLimit" class="limit-select" @change="fetchDeviceHistory">
                <option value="10">10条记录</option>
                <option value="20">20条记录</option>
                <option value="30">30条记录</option>
                <option value="50">50条记录</option>
              </select>
            </div>
          </div>
          <div class="chart-container" ref="chartContainer"></div>
        </div>

        <!-- 运行日志 -->
        <div class="operation-log" v-if="currentDevice">
          <h3>运行日志</h3>
          <div class="log-list">
            <div class="log-item" v-for="log in operationLogs" :key="log.time">
              <span class="log-time">{{ log.time }}</span>
              <span class="log-content">{{ log.content }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <WorkerNav />
  </div>
</template>

<script>
import WorkerNav from '@/components/WorkerNav.vue'
import * as echarts from 'echarts'

export default {
  name: 'EquipmentStatus',
  components: {
    WorkerNav
  },
  data() {
    return {
      loading: false,
      error: null,
      myDevices: [],
      selectedDeviceId: null,
      currentUserInfo: {},
      historyLimit: '10',
      selectedParameter: 'temperature',
      deviceHistory: [],
      chartInstance: null,
      sensorLabels: {
        'temperature': '温度',
        'pressure': '压力',
        'speed': '转速',
        'vibration': '振动',
        'noise': '噪音',
        'humidity': '湿度',
        'voltage': '电压',
        'current': '电流'
      },
      operationLogs: [
        { time: '2023-07-10 10:30', content: '完成设备检查' },
        { time: '2023-07-10 09:15', content: '设备启动运行' },
        { time: '2023-07-10 09:00', content: '设备维护' },
        { time: '2023-07-10 08:30', content: '参数调整' }
      ]
    }
  },
  computed: {
    // 当前选中的设备
    currentDevice() {
      if (!this.myDevices.length) return null;
      if (!this.selectedDeviceId) return this.myDevices[0];
      return this.myDevices.find(device => device.id === this.selectedDeviceId) || this.myDevices[0];
    }
  },
  created() {
    // 获取当前用户信息
    this.getCurrentUserInfo();
    // 获取工人负责的设备
    this.fetchMyDevices();
  },
  mounted() {
    window.addEventListener('resize', this.resizeChart);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.resizeChart);
    if (this.chartInstance) {
      this.chartInstance.dispose();
    }
  },
  watch: {
    currentDevice(newDevice) {
      if (newDevice) {
        this.fetchDeviceHistory();
      }
    }
  },
  methods: {
    // 获取当前用户信息
    getCurrentUserInfo() {
      const userInfoStr = localStorage.getItem('userInfo');
      if (userInfoStr) {
        try {
          this.currentUserInfo = JSON.parse(userInfoStr);
        } catch (error) {
          console.error('解析用户信息失败:', error);
          this.currentUserInfo = {};
        }
      }
    },

    // 获取工人负责的设备
    async fetchMyDevices() {
      this.loading = true;
      this.error = null;

      try {
        // 获取当前登录用户的工号
        const employeeId = this.currentUserInfo.employee_id;

        if (!employeeId) {
          this.error = '无法获取您的工号信息，请重新登录';
          return;
        }

        // 获取工人所在组的设备信息
        const groupId = this.currentUserInfo.group_id;
        const response = await fetch(`/api/equipment/with-status?group_id=${groupId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取设备信息失败: ${response.status}`);
        }

        const result = await response.json();
        console.log('设备信息:', result);

        if (result.success && result.data) {
          // 过滤出工人负责的设备
          this.myDevices = result.data
            .filter(device => device.worker_id === employeeId)
            .map(device => {
              // 获取设备状态
              let status = 'running';
              if (device.status === '故障') status = 'stopped';
              else if (device.fault_probability > 0.3) status = 'warning';

              // 获取设备状态文本
              let statusText = '运行中';
              if (status === 'warning') statusText = '预警';
              else if (status === 'stopped') statusText = '已停机';

              return {
                id: device.id,
                name: device.equipment_name,
                code: device.equipment_code,
                productionLine: device.line_name || '未知产线',
                status: status,
                statusText: statusText,
                runtime: device.runtime_hours || 0,
                faultProbability: device.fault_probability || 0,
                sensorData: device.sensor_data || {}
              };
            });

          // 如果有设备，选中第一个
          if (this.myDevices.length > 0) {
            this.selectedDeviceId = this.myDevices[0].id;
          }
        } else {
          this.error = result.error || '获取设备信息失败';
        }
      } catch (error) {
        console.error('获取设备信息出错:', error);
        this.error = error.message || '获取设备信息出错';
      } finally {
        this.loading = false;
      }
    },

    // 刷新设备数据
    refreshDeviceData() {
      this.fetchMyDevices();
    },

    // 设备选择变更
    onDeviceChange() {
      console.log('选中设备:', this.selectedDeviceId);
      this.fetchDeviceHistory();
    },

    // 获取设备历史数据
    async fetchDeviceHistory() {
      if (!this.currentDevice) return;

      try {
        const response = await fetch(`/api/equipment/status-history?equipment_id=${this.currentDevice.id}&limit=${this.historyLimit}`, {
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

          // 更新图表
          this.updateChart();
        } else {
          console.error('获取设备历史数据失败:', result.error || '未知错误');
        }
      } catch (error) {
        console.error('获取设备历史数据出错:', error);
      }
    },

    // 初始化图表
    initChart() {
      if (this.chartInstance) {
        this.chartInstance.dispose();
      }

      const chartDom = this.$refs.chartContainer;
      if (!chartDom) return;

      this.chartInstance = echarts.init(chartDom);
      this.updateChart();
    },

    // 更新图表
    updateChart() {
      if (!this.chartInstance) {
        this.initChart();
        return;
      }

      if (!this.deviceHistory.length) return;

      const xAxisData = [];
      const seriesData = [];

      // 准备图表数据
      this.deviceHistory.forEach(item => {
        // 格式化时间
        const date = new Date(item.collection_time);
        const timeStr = `${date.getMonth()+1}-${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
        xAxisData.push(timeStr);

        // 获取数据值
        if (this.selectedParameter === 'fault_probability') {
          // 如果是故障概率，直接使用
          seriesData.push((item.fault_probability * 100).toFixed(2));
        } else if (item.sensor_data && item.sensor_data[this.selectedParameter] !== undefined) {
          // 如果是传感器数据，从传感器数据中获取
          seriesData.push(item.sensor_data[this.selectedParameter]);
        } else {
          // 如果没有数据，使用null
          seriesData.push(null);
        }
      });

      // 设置图表选项
      const option = {
        title: {
          text: this.getParameterTitle(),
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const param = params[0];
            return `${param.name}<br/>${this.getParameterTitle()}: ${param.value}${this.getParameterUnit()}`;
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: xAxisData,
          axisLabel: {
            rotate: 30
          }
        },
        yAxis: {
          type: 'value',
          name: this.getParameterUnit(),
          nameLocation: 'end'
        },
        series: [{
          name: this.getParameterTitle(),
          type: 'line',
          data: seriesData,
          smooth: true,
          markPoint: {
            data: [
              { type: 'max', name: '最大值' },
              { type: 'min', name: '最小值' }
            ]
          },
          markLine: {
            data: [
              { type: 'average', name: '平均值' }
            ]
          },
          lineStyle: {
            width: 3
          },
          itemStyle: {
            color: this.getParameterColor()
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [{
                offset: 0, color: this.getParameterColor(0.6)
              }, {
                offset: 1, color: this.getParameterColor(0.1)
              }]
            }
          }
        }]
      };

      this.chartInstance.setOption(option);
    },

    // 调整图表大小
    resizeChart() {
      if (this.chartInstance) {
        this.chartInstance.resize();
      }
    },

    // 获取参数标题
    getParameterTitle() {
      if (this.selectedParameter === 'fault_probability') {
        return '故障概率';
      }
      return this.sensorLabels[this.selectedParameter] || this.selectedParameter;
    },

    // 获取参数单位
    getParameterUnit() {
      if (this.selectedParameter === 'fault_probability') {
        return '%';
      }

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

      return unitMap[this.selectedParameter] || '';
    },

    // 获取参数颜色
    getParameterColor(alpha = 1) {
      const colorMap = {
        'temperature': `rgba(255, 69, 0, ${alpha})`,  // 温度用红色
        'pressure': `rgba(30, 144, 255, ${alpha})`,   // 压力用蓝色
        'speed': `rgba(50, 205, 50, ${alpha})`,       // 转速用绿色
        'vibration': `rgba(255, 165, 0, ${alpha})`,   // 振动用橙色
        'noise': `rgba(128, 0, 128, ${alpha})`,       // 噪音用紫色
        'humidity': `rgba(0, 191, 255, ${alpha})`,    // 湿度用浅蓝色
        'voltage': `rgba(255, 215, 0, ${alpha})`,     // 电压用金色
        'current': `rgba(139, 69, 19, ${alpha})`,     // 电流用棕色
        'fault_probability': `rgba(220, 20, 60, ${alpha})` // 故障概率用深红色
      };

      return colorMap[this.selectedParameter] || `rgba(65, 105, 225, ${alpha})`;
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

    // 格式化传感器值
    formatSensorValue(key, value) {
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
      return `${value}${unitMap[key] || ''}`;
    },

    // 判断传感器值是否异常
    isSensorWarning(key, value) {
      const warningThresholds = {
        'temperature': 80,
        'pressure': 20,
        'vibration': 10,
        'noise': 90
      };
      return warningThresholds[key] && value > warningThresholds[key];
    },

    // 检查参数
    checkParameters() {
      if (!this.currentDevice || this.currentDevice.status === 'stopped') return;
      console.log('检查设备参数');
    },

    // 故障上报
    reportIssue() {
      if (!this.currentDevice || this.currentDevice.status === 'stopped') return;
      this.$router.push('/worker/issues');
    },

    // 查看操作手册
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
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 15px;
}

.action-btn.refresh {
  background: #e3f2fd;
  color: #2196F3;
}

.device-selector {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
}

.device-selector label {
  margin-right: 10px;
  font-weight: bold;
}

.device-select {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.loading-container, .error-container, .empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  background: white;
  border-radius: 8px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  color: #f44336;
  margin-bottom: 15px;
}

.retry-btn {
  background-color: #f44336;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
  color: #ddd;
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

.parameter-chart {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.chart-controls {
  display: flex;
  gap: 10px;
}

.parameter-select, .limit-select {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.chart-container {
  width: 100%;
  height: 300px;
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
