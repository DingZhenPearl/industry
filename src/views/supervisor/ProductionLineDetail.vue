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
        <div class="info-header">
          <h2>产线实时数据</h2>
          <div class="refresh-control">
            <span class="last-update" v-if="lastUpdateTime">上次更新: {{ lastUpdateTime }}</span>
            <button class="refresh-btn" :class="{ 'auto-refresh': autoRefresh }" @click="toggleAutoRefresh">
              {{ autoRefresh ? '自动刷新中' : '自动刷新' }}
            </button>
            <button class="refresh-btn" @click="fetchProductionLineDetail(productionLine.id)">
              <i class="refresh-icon"></i> 刷新
            </button>
          </div>
        </div>
        <div class="info-content">
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
      </div>

      <!-- 产线历史数据图表 -->
      <div class="parameter-chart">
        <div class="chart-header">
          <h3>产线历史数据</h3>
          <div class="chart-controls">
            <select v-model="selectedParameter" class="parameter-select" @change="handleParameterChange">
              <option value="real_time_capacity">实际产能</option>
              <option value="utilization">产能利用率</option>
            </select>
            <select v-model="historyLimit" class="limit-select" @change="handleLimitChange">
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
        <div ref="chartContainer" class="chart-container"></div>
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
])

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

      // 图表相关数据
      lineHistory: [],
      selectedParameter: 'utilization', // 默认显示产能利用率
      historyLimit: '10',
      chartInstance: null,

      // 自动刷新相关
      autoRefresh: true,
      refreshInterval: null,
      refreshRate: 10000, // 10秒更新一次
      lastUpdateTime: '',


    }
  },
  created() {
    // 获取产线ID并加载数据
    const lineId = this.$route.params.id;
    if (lineId) {
      // 先获取产线详情，然后获取历史数据
      this.fetchProductionLineDetail(lineId).then(() => {
        this.fetchLineHistory(this.historyLimit);
      });
    }
  },
  mounted() {
    this.initChart();

    // 如果启用了自动刷新，则启动
    if (this.autoRefresh) {
      this.startAutoRefresh();
    }
  },
  beforeDestroy() {
    // 清除定时器
    this.stopAutoRefresh();

    // 清除图表实例
    if (this.chartInstance) {
      this.chartInstance.dispose();
    }
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
        console.log('产线详情数据:', result);

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
          // 从动态表中获取实际产量，从静态表中获取理论产量
          let utilization = null;

          // 检查所有可能的字段名称
          console.log('产线基本信息中的字段名称:');
          for (const key in lineData) {
            console.log(`  ${key}: ${lineData[key]}`);
          }

          // 尝试从动态表中获取实际产量
          let realCapacity = null;
          if (lineData.output !== undefined) {
            realCapacity = parseFloat(lineData.output);
            console.log(`从 output 字段获取实际产量: ${realCapacity}`);
          } else if (lineData.real_time_capacity !== undefined) {
            realCapacity = parseFloat(lineData.real_time_capacity);
            console.log(`从 real_time_capacity 字段获取实际产量: ${realCapacity}`);
          } else if (lineData.realTimeCapacity !== undefined) {
            realCapacity = parseFloat(lineData.realTimeCapacity);
            console.log(`从 realTimeCapacity 字段获取实际产量: ${realCapacity}`);
          }

          // 尝试从静态表中获取理论产量
          let theoreticalCapacity = null;
          if (lineData.target !== undefined) {
            theoreticalCapacity = parseFloat(lineData.target);
            console.log(`从 target 字段获取理论产量: ${theoreticalCapacity}`);
          } else if (lineData.theoretical_capacity !== undefined) {
            theoreticalCapacity = parseFloat(lineData.theoretical_capacity);
            console.log(`从 theoretical_capacity 字段获取理论产量: ${theoreticalCapacity}`);
          } else if (lineData.theoreticalCapacity !== undefined) {
            theoreticalCapacity = parseFloat(lineData.theoreticalCapacity);
            console.log(`从 theoreticalCapacity 字段获取理论产量: ${theoreticalCapacity}`);
          }

          // 检查数据有效性
          if (realCapacity !== null && theoreticalCapacity !== null && !isNaN(realCapacity) && !isNaN(theoreticalCapacity) && theoreticalCapacity > 0) {
            utilization = Math.round((realCapacity / theoreticalCapacity) * 100);
            console.log('产线基本信息中计算产能利用率:', realCapacity, '/', theoreticalCapacity, '=', utilization, '%');
          } else {
            // 数据无效，使用 null
            utilization = null;
            console.warn('产线基本信息中数据无效，无法计算产能利用率');
            if (realCapacity === null) console.warn(`  实际产量为 null`);
            if (theoreticalCapacity === null) console.warn(`  理论产量为 null`);
            if (realCapacity !== null && isNaN(realCapacity)) console.warn(`  实际产量无效: ${realCapacity}`);
            if (theoreticalCapacity !== null && isNaN(theoreticalCapacity)) console.warn(`  理论产量无效: ${theoreticalCapacity}`);
            if (theoreticalCapacity !== null && theoreticalCapacity <= 0) console.warn(`  理论产量小于等于 0: ${theoreticalCapacity}`);
          }

          // 保存原来的产能利用率，如果有的话
          const oldUtilization = this.productionLine ? this.productionLine.utilization : 0;

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

          console.log('产能利用率更新:', oldUtilization, '->', utilization);

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

          // 更新最后更新时间
          this.lastUpdateTime = new Date().toLocaleTimeString();

          // 更新图表
          this.updateChart();
        } else {
          throw new Error(result.error || '获取产线详情失败');
        }
      } catch (error) {
        this.error.productionLine = error.message || '获取产线详情出错';
        console.error('获取产线详情出错:', error);
      } finally {
        this.loading.productionLine = false;
      }

      // 返回 Promise 对象，以便在创建时可以使用 then
      return Promise.resolve();
    },

    // 处理参数变化
    handleParameterChange() {
      console.log('参数变化为:', this.selectedParameter);
      // 打印当前历史数据中的字段
      if (this.lineHistory && this.lineHistory.length > 0) {
        const firstItem = this.lineHistory[0];
        console.log('历史数据第一项字段:', Object.keys(firstItem));
        console.log('历史数据第一项内容:', firstItem);

        // 如果是产能利用率，检查字段名称
        if (this.selectedParameter === 'utilization') {
          console.log('检查产能利用率相关字段:');
          console.log('real_time_capacity:', firstItem.real_time_capacity);
          console.log('theoretical_capacity:', firstItem.theoretical_capacity);
          console.log('output:', firstItem.output);
          console.log('target:', firstItem.target);
        }
      }
      // 只需要更新图表，不需要重新获取数据
      this.updateChart();
    },

    // 处理历史条数变化
    handleLimitChange() {
      console.log('历史条数变化为:', this.historyLimit);
      // 重新获取历史数据
      this.fetchLineHistory(this.historyLimit);
    },

    // 获取产线历史数据
    async fetchLineHistory(limit = 10) {
      if (!this.productionLine || !this.productionLine.id) return;

      console.log('开始获取产线历史数据，条数限制:', limit);
      this.loading.productionLine = true;

      try {
        const response = await fetch(`/api/production_line/status-history?line_id=${this.productionLine.id}&limit=${limit}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取产线历史数据失败: ${response.status}`);
        }

        const result = await response.json();
        console.log('产线历史数据:', JSON.stringify(result, null, 2));

        if (result.success && result.data && result.data.length > 0) {
          // 将数据按时间正序排列
          const sortedData = result.data.sort((a, b) =>
            new Date(a.collection_time) - new Date(b.collection_time)
          );

          console.log('排序后的历史数据长度:', sortedData.length);

          // 检查数据中是否包含必要的字段
          if (sortedData.length > 0) {
            const firstItem = sortedData[0];
            console.log('历史数据第一项字段:', Object.keys(firstItem));
            console.log('历史数据第一项内容:', JSON.stringify(firstItem, null, 2));

            // 检查产能利用率相关字段
            console.log('检查产能利用率相关字段:');
            console.log('real_time_capacity:', firstItem.real_time_capacity, typeof firstItem.real_time_capacity);
            console.log('theoretical_capacity:', firstItem.theoretical_capacity, typeof firstItem.theoretical_capacity);

            // 检查是否有其他可能的字段名称
            for (const key in firstItem) {
              if (key.includes('capacity') || key.includes('output') || key.includes('target') || key.includes('production')) {
                console.log(`可能的产能相关字段: ${key} = ${firstItem[key]}`);
              }
            }

            // 尝试计算产能利用率
            if (firstItem.real_time_capacity !== undefined && firstItem.theoretical_capacity !== undefined) {
              const realCapacity = parseFloat(firstItem.real_time_capacity || 0);
              const theoreticalCapacity = parseFloat(firstItem.theoretical_capacity || 1);
              if (theoreticalCapacity > 0) {
                const utilization = (realCapacity / theoreticalCapacity * 100).toFixed(2);
                console.log('测试计算产能利用率:', realCapacity, '/', theoreticalCapacity, '=', utilization, '%');

                // 检查数据类型
                console.log('数据类型检查:');
                console.log('real_time_capacity 原始值:', firstItem.real_time_capacity, '类型:', typeof firstItem.real_time_capacity);
                console.log('real_time_capacity 解析后:', realCapacity, '类型:', typeof realCapacity);
                console.log('theoretical_capacity 原始值:', firstItem.theoretical_capacity, '类型:', typeof firstItem.theoretical_capacity);
                console.log('theoretical_capacity 解析后:', theoreticalCapacity, '类型:', typeof theoreticalCapacity);
                console.log('utilization 计算结果:', utilization, '类型:', typeof utilization);
                console.log('utilization 解析后:', parseFloat(utilization), '类型:', typeof parseFloat(utilization));
              } else {
                console.warn('理论产能为0或负数，无法计算产能利用率');
              }
            } else {
              console.warn('缺少计算产能利用率所需的字段');
              if (firstItem.real_time_capacity === undefined) console.warn('缺少 real_time_capacity 字段');
              if (firstItem.theoretical_capacity === undefined) console.warn('缺少 theoretical_capacity 字段');
            }
          }

          // 不需要预处理数据，直接使用原始数据
          // 产能利用率将在需要时计算
          const processedData = sortedData;

          // 检查数据中是否包含计算产能利用率所需的字段
          let validCount = 0;
          let invalidCount = 0;

          sortedData.forEach((item, index) => {
            if (item.real_time_capacity !== undefined && item.theoretical_capacity !== undefined) {
              const realCapacity = parseFloat(item.real_time_capacity);
              const theoreticalCapacity = parseFloat(item.theoretical_capacity);

              if (!isNaN(realCapacity) && !isNaN(theoreticalCapacity) && theoreticalCapacity > 0) {
                validCount++;
                const utilization = (realCapacity / theoreticalCapacity * 100).toFixed(2);
                console.log(`原始数据项 ${index} 可计算产能利用率:`, realCapacity, '/', theoreticalCapacity, '=', utilization, '%');
              } else {
                invalidCount++;
                console.warn(`原始数据项 ${index} 数据无效，无法计算产能利用率`);
              }
            } else {
              invalidCount++;
              console.warn(`原始数据项 ${index} 缺少计算产能利用率所需的字段`);
            }
          });

          console.log('原始数据统计:',
            '总数据数:', sortedData.length,
            '可计算产能利用率数据数:', validCount,
            '无效数据数:', invalidCount,
            '有效数据比例:', (validCount / sortedData.length * 100).toFixed(2) + '%');

          // 将处理后的数据设置到 lineHistory
          this.lineHistory = processedData;

          // 创建一个新数组，触发Vue的响应式更新
          this.lineHistory = [...this.lineHistory];

          console.log('处理后的历史数据:', this.lineHistory);

          // 更新图表
          this.updateChart();
        } else {
          console.error('获取产线历史数据失败:', result.error || '未知错误');
        }
      } catch (error) {
        console.error('获取产线历史数据出错:', error);
      } finally {
        this.loading.productionLine = false;
      }
    },

    // 获取最新产线数据
    async fetchLatestLineData() {
      if (!this.productionLine || !this.productionLine.id) return Promise.resolve();

      try {
        // 如果历史数据为空，先获取历史数据
        if (!this.lineHistory || this.lineHistory.length === 0) {
          console.log('历史数据为空，先获取历史数据');
          await this.fetchLineHistory(this.historyLimit);
          return Promise.resolve();
        }

        // 获取最新的一条记录
        const response = await fetch(`/api/production_line/status-history?line_id=${this.productionLine.id}&limit=1`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取产线最新数据失败: ${response.status}`);
        }

        const result = await response.json();
        console.log('获取到最新产线数据:', result);

        if (result.success && result.data && result.data.length > 0) {
          const latestData = result.data[0];

          // 检查是否是新数据
          const isNewData = this.lineHistory.length === 0 ||
                         new Date(latestData.collection_time) > new Date(this.lineHistory[this.lineHistory.length - 1].collection_time);

          if (isNewData) {
            console.log('检测到新数据，添加到历史数据中');
            // 处理新数据，确保有产能利用率字段
            let processedLatestData = latestData;

            // 不需要预处理数据，直接使用原始数据
            // 产能利用率将在需要时计算
            processedLatestData = latestData;

            // 检查新数据是否可以计算产能利用率
            if (latestData.real_time_capacity !== undefined && latestData.theoretical_capacity !== undefined) {
              const realCapacity = parseFloat(latestData.real_time_capacity);
              const theoreticalCapacity = parseFloat(latestData.theoretical_capacity);

              if (!isNaN(realCapacity) && !isNaN(theoreticalCapacity) && theoreticalCapacity > 0) {
                const utilization = (realCapacity / theoreticalCapacity * 100).toFixed(2);
                console.log('新数据可计算产能利用率:', realCapacity, '/', theoreticalCapacity, '=', utilization, '%');
              } else {
                console.warn('新数据数据无效，无法计算产能利用率');
                if (isNaN(realCapacity)) console.warn(`  real_time_capacity 无效: ${latestData.real_time_capacity}`);
                if (isNaN(theoreticalCapacity)) console.warn(`  theoretical_capacity 无效: ${latestData.theoretical_capacity}`);
                if (theoreticalCapacity <= 0) console.warn(`  theoretical_capacity 小于等于 0: ${theoreticalCapacity}`);
              }
            } else {
              console.warn('新数据缺少计算产能利用率所需的字段');
              if (latestData.real_time_capacity === undefined) console.warn(`  缺少 real_time_capacity 字段`);
              if (latestData.theoretical_capacity === undefined) console.warn(`  缺少 theoretical_capacity 字段`);
            }

            // 添加处理后的新数据到历史数据中
            this.lineHistory.push(processedLatestData);

            // 如果历史数据超过限制，删除最早的数据
            const limit = parseInt(this.historyLimit);
            console.log('当前历史条数限制:', limit);

            while (this.lineHistory.length > limit) {
              this.lineHistory.shift();
            }

            // 对数据进行排序，确保按时间正序排列
            this.lineHistory.sort((a, b) => new Date(a.collection_time) - new Date(b.collection_time));

            // 创建一个新数组，触发Vue的响应式更新
            this.lineHistory = [...this.lineHistory];
            console.log('更新后的历史数据长度:', this.lineHistory.length);
            console.log('处理后的历史数据:', this.lineHistory);

            // 更新图表
            this.updateChart();

            // 更新图表，但不更新产线基本信息
            // 产线基本信息将在自动刷新时更新
            // this.fetchProductionLineDetail(this.productionLine.id);
          } else {
            // 即使没有新数据，也更新图表，确保图表显示
            console.log('没有新数据，但仍然更新图表');
            this.updateChart();
          }
        } else if (this.lineHistory.length > 0) {
          // 即使没有获取到数据，也更新图表，确保图表显示
          console.log('没有获取到数据，但仍然更新图表');
          this.updateChart();
        }
      } catch (error) {
        console.error('获取产线最新数据出错:', error);
        // 即使出错，也尝试更新图表
        if (this.lineHistory && this.lineHistory.length > 0) {
          this.updateChart();
        }
      }
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

          // 先获取最新数据，再更新产线基本信息
          // 这样可以确保历史数据不会被产线基本信息影响
          this.fetchLatestLineData().then(() => {
            // 获取最新数据后，再更新产线基本信息
            if (this.productionLine && this.productionLine.id) {
              console.log('自动刷新: 更新产线基本信息');
              this.fetchProductionLineDetail(this.productionLine.id);
            }
          });

          // 更新最后更新时间
          this.lastUpdateTime = new Date().toLocaleTimeString();
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

    // 初始化图表
    initChart() {
      if (this.chartInstance) {
        this.chartInstance.dispose();
      }

      const chartDom = this.$refs.chartContainer;
      if (!chartDom) return;

      // 使用 echarts 初始化图表
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

      // 更新最后更新时间
      this.lastUpdateTime = new Date().toLocaleTimeString();

      // 打印历史数据中的产能利用率字段
      if (this.lineHistory && this.lineHistory.length > 0) {
        console.log('检查历史数据中的产能利用率字段:');
        console.log('历史数据长度:', this.lineHistory.length);
        console.log('历史数据时间范围:',
          new Date(this.lineHistory[0].collection_time).toLocaleString(), '到',
          new Date(this.lineHistory[this.lineHistory.length-1].collection_time).toLocaleString());

        // 统计有效数据数量
        let calculatedCount = 0;
        let missingCount = 0;

        this.lineHistory.forEach((item, index) => {
          const date = new Date(item.collection_time);
          const timeStr = `${date.getMonth()+1}-${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;

          // 检查数据有效性
          let status = '无效';

          // 尝试从动态表中获取实际产量
          let realCapacity = null;
          if (item.output !== undefined) {
            realCapacity = parseFloat(item.output);
            console.log(`数据项 ${index} 从 output 字段获取实际产量: ${realCapacity}`);
          } else if (item.real_time_capacity !== undefined) {
            realCapacity = parseFloat(item.real_time_capacity);
            console.log(`数据项 ${index} 从 real_time_capacity 字段获取实际产量: ${realCapacity}`);
          } else if (item.realTimeCapacity !== undefined) {
            realCapacity = parseFloat(item.realTimeCapacity);
            console.log(`数据项 ${index} 从 realTimeCapacity 字段获取实际产量: ${realCapacity}`);
          }

          // 尝试从静态表中获取理论产量
          let theoreticalCapacity = null;
          if (item.target !== undefined) {
            theoreticalCapacity = parseFloat(item.target);
            console.log(`数据项 ${index} 从 target 字段获取理论产量: ${theoreticalCapacity}`);
          } else if (item.theoretical_capacity !== undefined) {
            theoreticalCapacity = parseFloat(item.theoretical_capacity);
            console.log(`数据项 ${index} 从 theoretical_capacity 字段获取理论产量: ${theoreticalCapacity}`);
          } else if (item.theoreticalCapacity !== undefined) {
            theoreticalCapacity = parseFloat(item.theoreticalCapacity);
            console.log(`数据项 ${index} 从 theoreticalCapacity 字段获取理论产量: ${theoreticalCapacity}`);
          }

          // 如果没有在当前数据项中找到理论产量，尝试使用产线基本信息中的理论产量
          if (theoreticalCapacity === null && this.productionLine) {
            if (this.productionLine.target !== undefined) {
              theoreticalCapacity = parseFloat(this.productionLine.target);
              console.log(`数据项 ${index} 从产线基本信息的 target 字段获取理论产量: ${theoreticalCapacity}`);
            } else if (this.productionLine.theoretical_capacity !== undefined) {
              theoreticalCapacity = parseFloat(this.productionLine.theoretical_capacity);
              console.log(`数据项 ${index} 从产线基本信息的 theoretical_capacity 字段获取理论产量: ${theoreticalCapacity}`);
            }
          }

          if (realCapacity !== null && theoreticalCapacity !== null && !isNaN(realCapacity) && !isNaN(theoreticalCapacity) && theoreticalCapacity > 0) {
            status = '可计算';
            calculatedCount++;

            // 计算产能利用率，但不保存
            const utilization = (realCapacity / theoreticalCapacity * 100).toFixed(2);
            console.log(`数据项 ${index} 计算产能利用率:`, realCapacity, '/', theoreticalCapacity, '=', utilization, '%');
          } else {
            status = '数据无效';
            missingCount++;
            console.warn(`数据项 ${index} 数据无效，无法计算产能利用率`);
            if (realCapacity === null) console.warn(`  实际产量为 null`);
            if (theoreticalCapacity === null) console.warn(`  理论产量为 null`);
            if (realCapacity !== null && isNaN(realCapacity)) console.warn(`  实际产量无效: ${realCapacity}`);
            if (theoreticalCapacity !== null && isNaN(theoreticalCapacity)) console.warn(`  理论产量无效: ${theoreticalCapacity}`);
            if (theoreticalCapacity !== null && theoreticalCapacity <= 0) console.warn(`  理论产量小于等于 0: ${theoreticalCapacity}`);
          }

          console.log(`数据项 ${index} [${timeStr}] ${status}:`,
            '实际产量:', realCapacity,
            '理论产量:', theoreticalCapacity);
        });

        console.log('数据统计:',
          '总数据数:', this.lineHistory.length,
          '可计算数据数:', calculatedCount,
          '无效数据数:', missingCount,
          '有效数据比例:', (calculatedCount / this.lineHistory.length * 100).toFixed(2) + '%');
      }

      console.log('开始处理图表数据，数据长度:', this.lineHistory.length, '当前选择的参数:', this.selectedParameter);

      const xAxisData = [];
      const seriesData = [];

      // 准备图表数据
      this.lineHistory.forEach(item => {
        // 格式化时间
        const date = new Date(item.collection_time);
        const timeStr = `${date.getMonth()+1}-${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
        xAxisData.push(timeStr);

        // 获取数据值
        console.log('处理数据项:', item);

        if (this.selectedParameter === 'utilization') {
          // 如果是产能利用率，计算百分比
          // 打印所有字段名称，便于调试
          console.log('数据项字段名称:', Object.keys(item));
          console.log('数据项内容:', JSON.stringify(item, null, 2));

          // 仅使用数据项中的利用率字段或计算值，不使用产线基本信息
          // 这样可以确保每个历史数据点都使用自己的值

          // 直接计算产能利用率，不依赖于 utilization 字段
          // 从动态表中获取实际产量，从静态表中获取理论产量

          // 检查所有可能的字段名称
          console.log('检查所有可能的字段名称:');
          for (const key in item) {
            console.log(`  ${key}: ${item[key]}`);
          }

          // 尝试从动态表中获取实际产量
          let realCapacity = null;
          if (item.output !== undefined) {
            realCapacity = parseFloat(item.output);
            console.log(`从 output 字段获取实际产量: ${realCapacity}`);
          } else if (item.real_time_capacity !== undefined) {
            realCapacity = parseFloat(item.real_time_capacity);
            console.log(`从 real_time_capacity 字段获取实际产量: ${realCapacity}`);
          } else if (item.realTimeCapacity !== undefined) {
            realCapacity = parseFloat(item.realTimeCapacity);
            console.log(`从 realTimeCapacity 字段获取实际产量: ${realCapacity}`);
          }

          // 尝试从静态表中获取理论产量
          let theoreticalCapacity = null;
          if (item.target !== undefined) {
            theoreticalCapacity = parseFloat(item.target);
            console.log(`从 target 字段获取理论产量: ${theoreticalCapacity}`);
          } else if (item.theoretical_capacity !== undefined) {
            theoreticalCapacity = parseFloat(item.theoretical_capacity);
            console.log(`从 theoretical_capacity 字段获取理论产量: ${theoreticalCapacity}`);
          } else if (item.theoreticalCapacity !== undefined) {
            theoreticalCapacity = parseFloat(item.theoreticalCapacity);
            console.log(`从 theoreticalCapacity 字段获取理论产量: ${theoreticalCapacity}`);
          }

          // 如果没有在当前数据项中找到理论产量，尝试使用产线基本信息中的理论产量
          if (theoreticalCapacity === null && this.productionLine) {
            if (this.productionLine.target !== undefined) {
              theoreticalCapacity = parseFloat(this.productionLine.target);
              console.log(`从产线基本信息的 target 字段获取理论产量: ${theoreticalCapacity}`);
            } else if (this.productionLine.theoretical_capacity !== undefined) {
              theoreticalCapacity = parseFloat(this.productionLine.theoretical_capacity);
              console.log(`从产线基本信息的 theoretical_capacity 字段获取理论产量: ${theoreticalCapacity}`);
            }
          }

          // 检查数据有效性
          if (realCapacity !== null && theoreticalCapacity !== null && !isNaN(realCapacity) && !isNaN(theoreticalCapacity) && theoreticalCapacity > 0) {
            // 计算产能利用率
            const utilization = (realCapacity / theoreticalCapacity * 100).toFixed(2);
            console.log(`数据项 ${xAxisData.length-1} 计算产能利用率:`, realCapacity, '/', theoreticalCapacity, '=', utilization, '%');
            seriesData.push(parseFloat(utilization));
          } else {
            // 数据无效，使用 null
            console.warn(`数据项 ${xAxisData.length-1} 数据无效，无法计算产能利用率，使用 null`);
            if (realCapacity === null) console.warn(`  实际产量为 null`);
            if (theoreticalCapacity === null) console.warn(`  理论产量为 null`);
            if (realCapacity !== null && isNaN(realCapacity)) console.warn(`  实际产量无效: ${realCapacity}`);
            if (theoreticalCapacity !== null && isNaN(theoreticalCapacity)) console.warn(`  理论产量无效: ${theoreticalCapacity}`);
            if (theoreticalCapacity !== null && theoreticalCapacity <= 0) console.warn(`  理论产量小于等于 0: ${theoreticalCapacity}`);
            seriesData.push(null);
          }

          /* 以下代码暂时不使用
          // 直接使用产线详情中的产能利用率
          if (this.productionLine && this.productionLine.utilization !== undefined) {
            console.log('使用产线详情中的产能利用率:', this.productionLine.utilization);
            seriesData.push(parseFloat(this.productionLine.utilization));
            return;
          }

          // 如果数据项中有利用率字段，直接使用
          if (item.utilization !== undefined) {
            console.log('使用数据项中的利用率字段:', item.utilization);
            seriesData.push(parseFloat(item.utilization));
            return;
          }

          // 尝试不同的字段名称
          let realCapacity = 0;
          let theoreticalCapacity = 0;

          // 检查字段名称的可能变化
          if (item.real_time_capacity !== undefined) {
            realCapacity = parseFloat(item.real_time_capacity || 0);
          } else if (item.realTimeCapacity !== undefined) {
            realCapacity = parseFloat(item.realTimeCapacity || 0);
          } else if (item.output !== undefined) {
            realCapacity = parseFloat(item.output || 0);
          }

          if (item.theoretical_capacity !== undefined) {
            theoreticalCapacity = parseFloat(item.theoretical_capacity || 1);
          } else if (item.theoreticalCapacity !== undefined) {
            theoreticalCapacity = parseFloat(item.theoreticalCapacity || 1);
          } else if (item.target !== undefined) {
            theoreticalCapacity = parseFloat(item.target || 1);
          }

          console.log('计算产能利用率:', realCapacity, '/', theoreticalCapacity);

          // 确保理论产能不为0，避免除以0错误
          if (theoreticalCapacity > 0) {
            const utilization = (realCapacity / theoreticalCapacity * 100).toFixed(2);
            console.log('计算结果:', utilization);
            seriesData.push(parseFloat(utilization));
          } else {
            console.log('理论产能为0，不能计算利用率');
            seriesData.push(0); // 如果理论产能为0，则利用率为0
          }
          */
        } else if (item[this.selectedParameter] !== undefined && item[this.selectedParameter] !== null) {
          // 如果是其他数据，直接使用
          console.log('使用直接数据:', this.selectedParameter, '=', item[this.selectedParameter]);
          seriesData.push(parseFloat(item[this.selectedParameter]));
        } else {
          // 如果没有数据，使用null
          console.log('没有有效数据，使用null');
          seriesData.push(null);
        }
      });

      console.log('处理后的图表数据:', seriesData);
      console.log('图表数据长度:', seriesData.length);
      console.log('图表X轴数据:', xAxisData);
      console.log('图表X轴数据长度:', xAxisData.length);

      // 统计有效数据数量
      const validDataCount = seriesData.filter(value => value !== null && value !== undefined).length;
      const nullDataCount = seriesData.filter(value => value === null || value === undefined).length;
      console.log('图表数据统计:',
        '总数据数:', seriesData.length,
        '有效数据数:', validDataCount,
        '空数据数:', nullDataCount,
        '有效数据比例:', (validDataCount / seriesData.length * 100).toFixed(2) + '%');

      // 如果所有数据都是空的，输出警告
      if (validDataCount === 0) {
        console.warn('警告: 所有图表数据都是空的，图表将不显示任何数据点');
      }

      // 检查是否有有效数据
      const hasValidData = seriesData.some(value => value !== null && value !== undefined);
      if (!hasValidData) {
        console.log('没有有效数据，尝试切换到其他参数');
        // 如果当前参数没有有效数据，尝试切换到其他参数
        const parameters = ['real_time_capacity', 'utilization'];
        for (const param of parameters) {
          if (param !== this.selectedParameter) {
            const tempData = this.lineHistory.map(item => {
              if (param === 'utilization') {
                // 仅使用数据项中的利用率字段或计算值，不使用产线基本信息
                // 这样可以确保每个历史数据点都使用自己的值

                // 直接计算产能利用率，不依赖于 utilization 字段
                // 从动态表中获取实际产量，从静态表中获取理论产量

                // 尝试从动态表中获取实际产量
                let realCapacity = null;
                if (item.output !== undefined) {
                  realCapacity = parseFloat(item.output);
                  console.log(`从 output 字段获取实际产量: ${realCapacity}`);
                } else if (item.real_time_capacity !== undefined) {
                  realCapacity = parseFloat(item.real_time_capacity);
                  console.log(`从 real_time_capacity 字段获取实际产量: ${realCapacity}`);
                } else if (item.realTimeCapacity !== undefined) {
                  realCapacity = parseFloat(item.realTimeCapacity);
                  console.log(`从 realTimeCapacity 字段获取实际产量: ${realCapacity}`);
                }

                // 尝试从静态表中获取理论产量
                let theoreticalCapacity = null;
                if (item.target !== undefined) {
                  theoreticalCapacity = parseFloat(item.target);
                  console.log(`从 target 字段获取理论产量: ${theoreticalCapacity}`);
                } else if (item.theoretical_capacity !== undefined) {
                  theoreticalCapacity = parseFloat(item.theoretical_capacity);
                  console.log(`从 theoretical_capacity 字段获取理论产量: ${theoreticalCapacity}`);
                } else if (item.theoreticalCapacity !== undefined) {
                  theoreticalCapacity = parseFloat(item.theoreticalCapacity);
                  console.log(`从 theoreticalCapacity 字段获取理论产量: ${theoreticalCapacity}`);
                }

                // 如果没有在当前数据项中找到理论产量，尝试使用产线基本信息中的理论产量
                if (theoreticalCapacity === null && this.productionLine && this.productionLine.target) {
                  theoreticalCapacity = parseFloat(this.productionLine.target);
                  console.log(`从产线基本信息中获取理论产量: ${theoreticalCapacity}`);
                }

                // 检查数据有效性
                if (realCapacity !== null && theoreticalCapacity !== null && !isNaN(realCapacity) && !isNaN(theoreticalCapacity) && theoreticalCapacity > 0) {
                  // 计算产能利用率
                  const utilization = (realCapacity / theoreticalCapacity * 100).toFixed(2);
                  console.log('从数据项计算产能利用率:', realCapacity, '/', theoreticalCapacity, '=', utilization, '%');
                  return parseFloat(utilization);
                } else {
                  // 数据无效，使用 null
                  console.warn('数据无效，无法计算产能利用率，使用 null');
                  if (realCapacity === null) console.warn(`  实际产量为 null`);
                  if (theoreticalCapacity === null) console.warn(`  理论产量为 null`);
                  if (realCapacity !== null && isNaN(realCapacity)) console.warn(`  实际产量无效: ${realCapacity}`);
                  if (theoreticalCapacity !== null && isNaN(theoreticalCapacity)) console.warn(`  理论产量无效: ${theoreticalCapacity}`);
                  if (theoreticalCapacity !== null && theoreticalCapacity <= 0) console.warn(`  理论产量小于等于 0: ${theoreticalCapacity}`);
                  return null;
                }
              } else if (item[param] !== undefined && item[param] !== null) {
                return parseFloat(item[param]);
              }
              return null;
            });

            if (tempData.some(value => value !== null && value !== undefined)) {
              console.log(`找到有效参数: ${param}`);
              this.selectedParameter = param;
              // 重新调用更新图表
              this.updateChart();
              return;
            }
          }
        }
      }

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

    // 获取参数标题
    getParameterTitle() {
      const titleMap = {
        'real_time_capacity': '实际产能',
        'utilization': '产能利用率'
      };
      return titleMap[this.selectedParameter] || this.selectedParameter;
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
    },
    viewDeviceDetail(device) {
      this.$router.push(`/supervisor/equipment-detail/${device.id}`);
    },
    assignMaintenance(device) {
      // 实现设备维护分配逻辑
      console.log('分配设备维护:', device);
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
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.refresh-control {
  display: flex;
  align-items: center;
  gap: 10px;
}

.last-update {
  font-size: 14px;
  color: #666;
}

.refresh-btn {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #f5f5f5;
  cursor: pointer;
  font-size: 14px;
}

.refresh-btn.auto-refresh {
  background-color: #e3f2fd;
  color: #2196F3;
  border-color: #2196F3;
}

.refresh-icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  margin-right: 5px;
  background-color: #666;
  mask-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>');
  mask-repeat: no-repeat;
  mask-position: center;
  mask-size: contain;
}

.info-content {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
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