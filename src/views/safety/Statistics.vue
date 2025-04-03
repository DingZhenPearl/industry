<template>
  <div class="statistics">
    <header class="header">
      <h1>安全统计</h1>
    </header>
    
    <div class="content">
      <div class="stat-cards">
        <div class="stat-card">
          <h3>本月预警总数</h3>
          <div class="stat-value">15</div>
        </div>
        <div class="stat-card">
          <h3>已处理预警</h3>
          <div class="stat-value">13</div>
        </div>
        <div class="stat-card">
          <h3>安全巡检次数</h3>
          <div class="stat-value">24</div>
        </div>
      </div>

      <div class="chart-section">
        <h3>预警趋势</h3>
        <div class="chart-placeholder">
          图表区域
        </div>
      </div>

      <div class="data-section">
        <h3>安全隐患统计</h3>
        <table>
          <thead>
            <tr>
              <th>类型</th>
              <th>数量</th>
              <th>处理率</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in statData" :key="index">
              <td>{{ item.type }}</td>
              <td>{{ item.count }}</td>
              <td>{{ item.rate }}%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <SafetyNav />
  </div>
</template>

<script>
import SafetyNav from '@/components/SafetyNav.vue'

export default {
  name: 'SafetyStatistics',
  components: {
    SafetyNav
  },
  data() {
    return {
      statData: [
        { type: '设备故障', count: 8, rate: 87.5 },
        { type: '环境异常', count: 5, rate: 100 },
        { type: '操作违规', count: 2, rate: 100 }
      ]
    }
  }
}
</script>

<style scoped>
.statistics {
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

.stat-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-card h3 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #2196F3;
}

.chart-section {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chart-placeholder {
  height: 200px;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  margin-top: 15px;
}

.data-section {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  font-weight: bold;
  color: #333;
}

td {
  color: #666;
}
</style>
