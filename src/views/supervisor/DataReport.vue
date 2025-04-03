<template>
  <div class="report">
    <header class="header">
      <h1>数据报表</h1>
    </header>
    
    <div class="content">
      <div class="report-filters">
        <select v-model="timeRange" class="filter-select">
          <option value="day">今日</option>
          <option value="week">本周</option>
          <option value="month">本月</option>
        </select>
        <button class="export-btn">导出报表</button>
      </div>
      
      <div class="report-content">
        <div class="data-table">
          <!-- 报表数据表格 -->
          <table>
            <thead>
              <tr>
                <th>日期</th>
                <th>产量</th>
                <th>合格率</th>
                <th>设备状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in reportData" :key="index">
                <td>{{ item.date }}</td>
                <td>{{ item.output }}</td>
                <td>{{ item.quality }}%</td>
                <td>{{ item.status }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <SupervisorNav />
  </div>
</template>

<script>
import SupervisorNav from '@/components/SupervisorNav.vue'

export default {
  name: 'DataReport',
  components: {
    SupervisorNav
  },
  data() {
    return {
      timeRange: 'day',
      reportData: [
        {date: '2023-07-01', output: 1000, quality: 98, status: '正常'},
        {date: '2023-07-02', output: 980, quality: 97, status: '正常'},
        {date: '2023-07-03', output: 1020, quality: 99, status: '正常'}
      ]
    }
  }
}
</script>

<style scoped>
.report {
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

.report-filters {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.filter-select {
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.export-btn {
  padding: 8px 16px;
  background: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.data-table {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f5f5f5;
  font-weight: bold;
}
</style>
