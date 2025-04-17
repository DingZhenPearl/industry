<template>
  <div class="equipment-detail-component">
    <!-- 加载中提示 -->
    <div class="loading-container" v-if="loading">
      <div class="loading-spinner"></div>
      <p>正在加载设备数据...</p>
    </div>

    <!-- 错误提示 -->
    <div class="error-container" v-if="error">
      <p class="error-message">{{ error }}</p>
      <button class="retry-btn" @click="$emit('retry')">重试</button>
    </div>

    <!-- 无设备提示 -->
    <div class="empty-container" v-if="!loading && !error && !equipment">
      <div class="empty-icon">🛠️</div>
      <p>没有设备数据</p>
    </div>

    <!-- 设备详情内容 -->
    <div v-if="!loading && !error && equipment">
      <!-- 设备基本信息卡片 -->
      <div class="info-card">
        <div class="device-header">
          <h3>设备状态</h3>
          <span :class="['status-tag', equipment.status]">{{ equipment.statusText }}</span>
        </div>
        <div class="device-body">
          <div class="info-row">
            <span>设备名称：{{ equipment.name }}</span>
            <span>设备编号：{{ equipment.code }}</span>
          </div>
          <div class="info-row">
            <span>所属产线：{{ equipment.productionLine }}</span>
            <span>运行时长：{{ equipment.runtime }}h</span>
          </div>
          <div class="parameter-list">
            <template v-if="equipment.sensorData && Object.keys(equipment.sensorData).length > 0">
              <div class="parameter-item" v-for="(value, key) in equipment.sensorData" :key="key">
                <span class="label">{{ getSensorLabel(key) }}</span>
                <span class="value" :class="{ warning: isSensorWarning(key, value) }">
                  {{ formatSensorValue(key, value) }}
                </span>
              </div>
            </template>
            <div class="parameter-item" v-else>
              <span class="label">故障概率</span>
              <span class="value" :class="{ warning: equipment.faultProbability > 0.3 }">
                {{ Math.round(equipment.faultProbability * 100) }}%
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作按钮组 -->
      <div class="action-group" v-if="showActions">
        <slot name="actions"></slot>
      </div>

      <!-- 参数图表 -->
      <div class="parameter-chart">
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
            <button
              class="auto-refresh-btn"
              :class="{ active: autoRefresh }"
              @click="toggleAutoRefresh"
            >
              {{ autoRefresh ? '实时更新中' : '开启实时更新' }}
            </button>
          </div>
        </div>
        <div class="chart-container" ref="chartContainer"></div>
      </div>

      <!-- 额外内容插槽 -->
      <slot name="extra-content"></slot>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'EquipmentDetailComponent',
  props: {
    // 设备数据
    equipment: {
      type: Object,
      default: null
    },
    // 设备历史数据
    deviceHistory: {
      type: Array,
      default: () => []
    },
    // 是否显示加载状态
    loading: {
      type: Boolean,
      default: false
    },
    // 错误信息
    error: {
      type: String,
      default: null
    },
    // 是否显示操作按钮
    showActions: {
      type: Boolean,
      default: true
    },
    // 是否自动刷新
    autoRefreshEnabled: {
      type: Boolean,
      default: true
    },
    // 刷新间隔（毫秒）
    refreshRate: {
      type: Number,
      default: 10000
    }
  },
  data() {
    return {
      selectedParameter: 'temperature',
      historyLimit: '10',
      chartInstance: null,
      autoRefresh: this.autoRefreshEnabled, // 初始化时使用传入的值
      refreshInterval: null,
      sensorLabels: {
        'temperature': '温度',
        'pressure': '压力',
        'speed': '转速',
        'vibration': '振动',
        'noise': '噪音',
        'humidity': '湿度',
        'voltage': '电压',
        'current': '电流'
      }
    }
  },
  watch: {
    equipment(newEquipment) {
      if (newEquipment) {
        this.$emit('equipment-changed', newEquipment);
      }
    },
    deviceHistory(newHistory, oldHistory) {
      console.log('检测到 deviceHistory 变化，新数据长度:', newHistory.length, '旧数据长度:', oldHistory ? oldHistory.length : 0);
      if (newHistory.length > 0) {
        console.log('最新数据时间:', new Date(newHistory[newHistory.length - 1].collection_time).toLocaleString());
      }
      this.updateChart();
    },
    autoRefreshEnabled(newValue) {
      this.autoRefresh = newValue;
      if (newValue) {
        this.startAutoRefresh();
      } else {
        this.stopAutoRefresh();
      }
    }
  },
  mounted() {
    window.addEventListener('resize', this.resizeChart);
    this.initChart();

    // 如果启用了自动刷新，则启动
    if (this.autoRefreshEnabled) {
      this.autoRefresh = true;
      this.startAutoRefresh();
      console.log('自动刷新已启动，刷新间隔:', this.refreshRate, '毫秒');
    }
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.resizeChart);
    if (this.chartInstance) {
      this.chartInstance.dispose();
    }
    this.stopAutoRefresh();
  },
  methods: {
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

    // 开始自动刷新
    startAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
      }

      if (this.autoRefresh) {
        console.log('开始自动刷新，间隔:', this.refreshRate, '毫秒');
        this.refreshInterval = setInterval(() => {
          console.log('触发自动刷新事件');
          this.$emit('refresh-data');
        }, this.refreshRate);
      }
    },

    // 停止自动刷新
    stopAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
        this.refreshInterval = null;
      }
    },

    // 切换自动刷新状态
    toggleAutoRefresh() {
      this.autoRefresh = !this.autoRefresh;
      if (this.autoRefresh) {
        this.startAutoRefresh();
      } else {
        this.stopAutoRefresh();
      }
    },

    // 获取设备历史数据
    fetchDeviceHistory() {
      this.$emit('fetch-history', this.historyLimit);
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
      console.log('开始更新图表');
      if (!this.chartInstance) {
        console.log('图表实例不存在，初始化图表');
        this.initChart();
        return;
      }

      if (!this.deviceHistory || !this.deviceHistory.length) {
        console.log('设备历史数据为空，不更新图表');
        return;
      }

      console.log('开始处理图表数据，数据长度:', this.deviceHistory.length);

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

      console.log('设置图表选项，数据长度:', seriesData.length);
      this.chartInstance.setOption(option);
      console.log('图表更新完成');
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
    }
  }
}
</script>

<style scoped>
.equipment-detail-component {
  width: 100%;
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

.info-card {
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

.status-tag.normal {
  background: #e8f5e9;
  color: #4CAF50;
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

.auto-refresh-btn {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background-color: #f5f5f5;
  color: #333;
  cursor: pointer;
}

.auto-refresh-btn.active {
  background-color: #e3f2fd;
  color: #2196F3;
  border-color: #2196F3;
}

.chart-container {
  width: 100%;
  height: 300px;
}
</style>
