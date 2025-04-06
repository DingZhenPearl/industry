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
    
    <div class="content">
      <!-- 设备基本信息卡片 -->
      <div class="info-card">
        <div class="info-row">
          <div class="info-item">
            <span class="label">设备名称</span>
            <span class="value">{{ equipment.name }}</span>
          </div>
          <div class="info-item">
            <span class="label">设备位置</span>
            <span class="value">{{ equipment.location }}</span>
          </div>
        </div>
        <div class="info-row">
          <div class="info-item">
            <span class="label">设备状态</span>
            <span class="value" :class="equipment.status">{{ equipment.statusText }}</span>
          </div>
          <div class="info-item">
            <span class="label">传感器ID</span>
            <span class="value">{{ equipment.sensorId }}</span>
          </div>
        </div>
        <div class="info-row">
          <div class="info-item">
            <span class="label">设备详情</span>
            <span class="value">{{ equipment.description }}</span>
          </div>
        </div>
      </div>

      <!-- 传感器数据展示区 -->
      <div class="sensor-data">
        <h3>传感器数据</h3>
        <div class="sensor-type">{{ currentSensor.name }}传感器</div>
        <div class="sensor-value">{{ currentSensor.value }}<span class="unit">{{ currentSensor.unit }}</span></div>
      </div>

      <!-- 时间范围选择器 -->
      <div class="time-range">
        <h3>选择时间范围：</h3>
        <div class="date-inputs">
          <div class="date-input">
            <span>日期</span>
            <input type="date" v-model="dateRange.date">
          </div>
          <div class="time-input">
            <span>开始时间</span>
            <input type="time" v-model="dateRange.startTime">
          </div>
          <div class="time-input">
            <span>结束时间</span>
            <input type="time" v-model="dateRange.endTime">
          </div>
        </div>
        <button class="generate-btn" @click="generateChart">绘制图像</button>
      </div>

      <!-- 图表展示区域 -->
      <div class="chart-container">
        <h3>{{ equipment.name }} - {{ currentSensor.name }}传感器数据</h3>
        <div class="chart">
          <!-- 这里将放置图表组件 -->
        </div>
      </div>
    </div>

    <SupervisorNav />
  </div>
</template>

<script>
import SupervisorNav from '@/components/SupervisorNav.vue'
import * as echarts from 'echarts';

export default {
  name: 'EquipmentDetail',
  components: {
    SupervisorNav
  },
  data() {
    return {
      equipment: {
        id: '',
        name: '花都新工厂-机加线M3内喷电机',
        location: '花都',
        status: 'normal',
        statusText: '正常',
        sensorId: '1000004700060003',
        description: '该设备提供传感器共有2个，当前传感器提供属性：温度'
      },
      sensors: [
        { name: '接触式温度', value: '24.8', unit: '°C' }
      ],
      currentSensor: { name: '温度', value: '24.8', unit: '°C' },
      dateRange: {
        date: '2023-04-13',
        startTime: '08:00',
        endTime: '08:05'
      },
      chartData: [
        { time: '08:00', value: 24.8 },
        { time: '08:01', value: 24.6 },
        { time: '08:02', value: 24.8 },
        { time: '08:03', value: 24.7 },
        { time: '08:04', value: 24.9 },
        { time: '08:05', value: 24.7 }
      ]
    }
  },
  created() {
    // 获取路由参数中的设备ID
    const equipmentId = this.$route.params.id
    this.equipment.id = equipmentId
    
    // 这里应该根据ID从API获取设备详情
    this.fetchEquipmentDetail(equipmentId)
  },
  methods: {
    fetchEquipmentDetail(id) {
      // 模拟API调用获取设备详情
      console.log('获取设备ID:', id, '的详情')
      // 实际项目中应该调用API获取数据
    },
    initChart() {
      const chartDom = document.querySelector('.chart');
      const myChart = echarts.init(chartDom);
      
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        xAxis: {
          type: 'category',
          data: this.chartData.map(item => item.time)
        },
        yAxis: {
          type: 'value',
          min: 24.5,
          max: 25.5
        },
        series: [{
          data: this.chartData.map(item => item.value),
          type: 'line',
          smooth: true,
          lineStyle: {
            color: '#FFD700',
            width: 3
          },
          itemStyle: {
            color: '#FF4500'
          }
        }]
      };
      
      myChart.setOption(option);
    },
    generateChart() {
      // 模拟数据生成
      this.chartData = this.generateRandomData();
      this.initChart();
    },
    generateRandomData() {
      // ...existing data generation code...
    },
    goBack() {
      // 返回到监控中心页面
      this.$router.push('/supervisor/monitor')
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.initChart();
    });
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
</style>