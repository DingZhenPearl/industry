<template>
  <div class="efficiency">
    <header class="header">
      <h1>效率分析</h1>
    </header>
    
    <div class="content">
      <!-- 增加时间选择器和筛选条件 -->
      <div class="filter-bar">
        <div class="date-range">
          <span>统计时间：</span>
          <select v-model="timeRange" class="select-input">
            <option value="today">今日</option>
            <option value="week">本周</option>
            <option value="month">本月</option>
            <option value="custom">自定义</option>
          </select>
        </div>
        <div class="line-filter">
          <span>产线筛选：</span>
          <select v-model="selectedLine" class="select-input">
            <option value="all">全部产线</option>
            <option v-for="line in productionLines" :key="line.id" :value="line.id">
              {{ line.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- 效率指标卡片 -->
      <div class="metric-cards">
        <div class="metric-card">
          <div class="metric-icon productivity"></div>
          <div class="metric-info">
            <div class="metric-name">生产效率</div>
            <div class="metric-value">92%</div>
            <div class="metric-trend up">↑2.5%</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon quality"></div>
          <div class="metric-info">
            <div class="metric-name">产品合格率</div>
            <div class="metric-value">98%</div>
            <div class="metric-trend up">↑1.2%</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon efficiency"></div>
          <div class="metric-info">
            <div class="metric-name">设备利用率</div>
            <div class="metric-value">85%</div>
            <div class="metric-trend down">↓0.8%</div>
          </div>
        </div>
      </div>

      <!-- 效率分析图表 -->
      <div class="chart-section">
        <h3 class="section-title">效率趋势分析</h3>
        <div class="chart-container">
          <div class="chart-placeholder">
            此处将显示效率趋势图表
          </div>
        </div>
      </div>

      <!-- 效率详情表格 -->
      <div class="efficiency-table">
        <h3 class="section-title">效率详情数据</h3>
        <table>
          <thead>
            <tr>
              <th>产线名称</th>
              <th>生产效率</th>
              <th>合格率</th>
              <th>设备利用率</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="line in tableData" :key="line.id">
              <td>{{ line.name }}</td>
              <td>{{ line.productivity }}%</td>
              <td>{{ line.quality }}%</td>
              <td>{{ line.utilization }}%</td>
              <td>
                <button class="detail-btn">查看详情</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <SupervisorNav />
  </div>
</template>

<script>
import SupervisorNav from '@/components/SupervisorNav.vue'

export default {
  name: 'EfficiencyAnalysis',
  components: {
    SupervisorNav
  },
  data() {
    return {
      timeRange: 'today',
      selectedLine: 'all',
      productionLines: [
        { id: 1, name: '一号生产线' },
        { id: 2, name: '二号生产线' },
        { id: 3, name: '三号生产线' }
      ],
      tableData: [
        {
          id: 1,
          name: '一号生产线',
          productivity: 92,
          quality: 98,
          utilization: 85
        },
        {
          id: 2,
          name: '二号生产线',
          productivity: 88,
          quality: 97,
          utilization: 82
        },
        {
          id: 3,
          name: '三号生产线',
          productivity: 95,
          quality: 99,
          utilization: 88
        }
      ]
    }
  }
}
</script>

<style scoped>
.efficiency {
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

.efficiency-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #2196F3;
  margin: 15px 0;
}

.stat-chart {
  height: 200px;
  background: #f5f5f5;
  border-radius: 4px;
}

.filter-bar {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.select-input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-left: 8px;
}

.metric-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.metric-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  margin-right: 15px;
}

.metric-info {
  flex: 1;
}

.metric-name {
  color: #666;
  margin-bottom: 5px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.metric-trend {
  font-size: 14px;
  margin-top: 5px;
}

.metric-trend.up {
  color: #4CAF50;
}

.metric-trend.down {
  color: #f44336;
}

.chart-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chart-placeholder {
  height: 300px;
  background: #f5f5f5;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.efficiency-table table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.efficiency-table th,
.efficiency-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.efficiency-table th {
  background: #f5f5f5;
  font-weight: bold;
}

.detail-btn {
  padding: 6px 12px;
  background: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.detail-btn:hover {
  background: #1976D2;
}
</style>
