<template>
  <div class="production-line-detail-component">
    <!-- 加载中状态 -->
    <div class="loading-container" v-if="loading">
      <div class="loading-spinner"></div>
      <div class="loading-text">正在加载产线数据...</div>
    </div>

    <!-- 错误状态 -->
    <div class="error-container" v-else-if="error">
      <div class="error-message">{{ error }}</div>
      <button class="retry-btn" @click="$emit('retry')">重试</button>
    </div>

    <!-- 空数据状态 -->
    <div class="empty-container" v-else-if="!productionLine">
      <div class="empty-icon">📊</div>
      <div class="empty-text">暂无产线数据</div>
    </div>

    <!-- 产线数据展示 -->
    <template v-else>
      <!-- 产线基本信息卡片 -->
      <div class="info-card">
        <div class="device-header">
          <h3>{{ productionLine.name }}</h3>
          <span :class="['status-tag', productionLine.status]">{{ productionLine.statusText }}</span>
        </div>

        <div class="info-rows">
          <div class="info-row">
            <span class="label">产线编号:</span>
            <span class="value">{{ productionLine.id }}</span>
          </div>
          <div class="info-row">
            <span class="label">负责工长:</span>
            <span class="value">{{ productionLine.manager || '未分配' }}</span>
          </div>
          <div class="info-row">
            <span class="label">运行时长:</span>
            <span class="value">{{ productionLine.runtime || 0 }}小时</span>
          </div>
        </div>

        <div class="parameter-list">
          <div class="parameter-item">
            <span class="label">理论产能</span>
            <span class="value">{{ productionLine.target || 0 }}件/小时</span>
          </div>
          <div class="parameter-item">
            <span class="label">实际产能</span>
            <span class="value" :class="{ 'warning': productionLine.output < productionLine.target * 0.8 }">
              {{ productionLine.output || 0 }}件/小时
            </span>
          </div>
          <div class="parameter-item">
            <span class="label">产能利用率</span>
            <span class="value" :class="{ 'warning': productionLine.utilization < 80 }">
              {{ productionLine.utilization || 0 }}%
            </span>
          </div>
        </div>

        <!-- 自定义操作按钮插槽 -->
        <div class="action-group" v-if="showActions">
          <slot name="actions"></slot>
        </div>
      </div>

      <!-- 产线历史数据图表 -->
      <div class="parameter-chart">
        <div class="chart-header">
          <h3>产线历史数据</h3>
          <div class="chart-controls">
            <select v-model="selectedParameter" class="parameter-select" @change="updateChart">
              <option value="real_time_capacity">实际产能</option>
              <option value="utilization">产能利用率</option>
            </select>
            <select v-model="historyLimit" class="limit-select" @change="fetchLineHistory">
              <option value="5">最近5条</option>
              <option value="10">最近10条</option>
              <option value="20">最近20条</option>
              <option value="50">最近50条</option>
            </select>
            <button
              :class="['auto-refresh-btn', { active: autoRefresh }]"
              @click="toggleAutoRefresh"
            >
              {{ autoRefresh ? '自动刷新中' : '自动刷新' }}
            </button>
          </div>
        </div>

        <!-- 图表容器 -->
        <div ref="chartContainer" class="chart-container"></div>
      </div>

      <!-- 额外内容插槽 -->
      <slot name="extra-content"></slot>
    </template>
  </div>
</template>

<script>
import * as echarts from 'echarts/core';
import { LineChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DataZoomComponent,
  ToolboxComponent,
  LegendComponent
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

// 注册必要的组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DataZoomComponent,
  ToolboxComponent,
  LegendComponent,
  LineChart,
  CanvasRenderer
]);

export default {
  name: 'ProductionLineDetailComponent',
  props: {
    // 产线数据
    productionLine: {
      type: Object,
      default: null
    },
    // 产线历史数据
    lineHistory: {
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
      selectedParameter: 'real_time_capacity',
      historyLimit: '10',
      chartInstance: null,
      autoRefresh: this.autoRefreshEnabled, // 初始化时使用传入的值
      refreshInterval: null,
      parameterLabels: {
        'real_time_capacity': '实际产能',
        'utilization': '产能利用率'
      }
    }
  },
  watch: {
    productionLine(newValue) {
      if (newValue) {
        this.$emit('production-line-changed', newValue);
      }
    },
    lineHistory() {
      console.log('检测到 lineHistory 变化，新数据长度:', this.lineHistory.length);
      if (this.lineHistory.length > 0) {
        console.log('最新数据时间:', new Date(this.lineHistory[this.lineHistory.length - 1].collection_time).toLocaleString());
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

    // 获取产线历史数据
    fetchLineHistory() {
      console.log('组件请求获取历史数据，条数:', this.historyLimit);
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
      console.log('开始更新产线图表');
      if (!this.chartInstance) {
        console.log('图表实例不存在，初始化图表');
        this.initChart();
        return;
      }

      if (!this.lineHistory || !this.lineHistory.length) {
        console.log('产线历史数据为空，不更新图表');
        return;
      }

      console.log('开始处理图表数据，数据长度:', this.lineHistory.length);

      const xAxisData = [];
      const seriesData = [];

      // 准备图表数据
      this.lineHistory.forEach(item => {
        // 格式化时间
        const date = new Date(item.collection_time);
        const timeStr = `${date.getMonth()+1}-${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
        xAxisData.push(timeStr);

        // 获取数据值
        if (this.selectedParameter === 'utilization') {
          // 如果是产能利用率，直接使用预处理的利用率数据
          if (item.utilization !== null && item.utilization !== undefined && !isNaN(item.utilization)) {
            console.log(`使用预处理的产能利用率数据:`, item.utilization, '%');
            seriesData.push(parseFloat(item.utilization));
          } else {
            // 如果没有预处理的利用率数据，尝试计算
            const realCapacity = parseFloat(item.real_time_capacity);
            const theoreticalCapacity = parseFloat(item.theoretical_capacity);

            // 检查数据有效性
            if (!isNaN(realCapacity) && !isNaN(theoreticalCapacity) && theoreticalCapacity > 0) {
              // 计算产能利用率
              const utilization = (realCapacity / theoreticalCapacity * 100).toFixed(2);
              console.log(`实时计算产能利用率:`, realCapacity, '/', theoreticalCapacity, '=', utilization, '%');
              seriesData.push(parseFloat(utilization));
            } else {
              // 数据无效，使用 null
              console.warn(`数据无效，无法计算产能利用率，使用 null`);
              if (isNaN(realCapacity)) console.warn(`  实际产量无效: ${item.real_time_capacity}`);
              if (isNaN(theoreticalCapacity)) console.warn(`  理论产量无效: ${item.theoretical_capacity}`);
              if (theoreticalCapacity <= 0) console.warn(`  理论产量小于等于 0: ${theoreticalCapacity}`);
              seriesData.push(null);
            }
          }
        } else if (item[this.selectedParameter] !== undefined) {
          // 如果是其他数据，直接使用
          seriesData.push(parseFloat(item[this.selectedParameter]) || 0);
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
      this.chartInstance.setOption(option, true); // 添加 true 参数，强制刷新
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
      return this.parameterLabels[this.selectedParameter] || this.selectedParameter;
    },

    // 获取参数单位
    getParameterUnit() {
      const unitMap = {
        'real_time_capacity': '件/小时',
        'utilization': '%'
      };

      return unitMap[this.selectedParameter] || '';
    },

    // 获取参数颜色
    getParameterColor(alpha = 1) {
      const colorMap = {
        'real_time_capacity': `rgba(30, 144, 255, ${alpha})`,  // 蓝色
        'utilization': `rgba(50, 205, 50, ${alpha})`           // 绿色
      };

      return colorMap[this.selectedParameter] || `rgba(65, 105, 225, ${alpha})`;
    }
  }
}
</script>

<style scoped>
.production-line-detail-component {
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

.info-rows {
  margin-bottom: 15px;
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
  margin-top: 15px;
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
