<template>
  <div class="workorders">
    <header class="header">
      <h1>工单管理</h1>
    </header>
    
    <div class="content">
      <!-- 工单统计卡片 -->
      <div class="stat-cards">
        <div class="stat-card">
          <h3>待处理工单</h3>
          <div class="count pending">{{ pendingCount }}</div>
        </div>
        <div class="stat-card">
          <h3>处理中工单</h3>
          <div class="count processing">{{ processingCount }}</div>
        </div>
        <div class="stat-card">
          <h3>已完成工单</h3>
          <div class="count completed">{{ completedCount }}</div>
        </div>
      </div>

      <!-- 工单筛选区 -->
      <div class="filter-bar">
        <select v-model="filterType" class="filter-select">
          <option value="all">全部工单</option>
          <option value="maintenance">维护工单</option>
          <option value="inspection">巡检工单</option>
          <option value="repair">维修工单</option>
        </select>
        <select v-model="filterStatus" class="filter-select">
          <option value="all">全部状态</option>
          <option value="pending">待处理</option>
          <option value="processing">处理中</option>
          <option value="completed">已完成</option>
        </select>
        <input 
          type="text" 
          v-model="searchKeyword"
          class="search-input"
          placeholder="搜索工单编号/提交人"
        >
      </div>

      <!-- 工单列表 -->
      <div class="workorder-list">
        <div class="workorder-item" v-for="item in filteredWorkorders" :key="item.id">
          <div class="workorder-header">
            <span class="workorder-number">{{ item.number }}</span>
            <span :class="['workorder-status', item.status]">{{ item.statusText }}</span>
          </div>
          <div class="workorder-content">
            <h3>{{ item.title }}</h3>
            <p class="description">{{ item.description }}</p>
            <div class="workorder-info">
              <span>类型：{{ item.typeText }}</span>
              <span>位置：{{ item.location }}</span>
            </div>
            <div class="workorder-meta">
              <span>提交人：{{ item.submitter }}</span>
              <span>提交时间：{{ item.submitTime }}</span>
            </div>
            <div class="workorder-handler" v-if="item.handler">
              <span>处理人：{{ item.handler }}</span>
              <span>更新时间：{{ item.updateTime }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <SupervisorNav />
  </div>
</template>

<script>
import SupervisorNav from '@/components/SupervisorNav.vue'

export default {
  name: 'WorkOrders',
  components: {
    SupervisorNav
  },
  data() {
    return {
      filterType: 'all',
      filterStatus: 'all',
      searchKeyword: '',
      workorders: [
        {
          id: 1,
          number: 'WO2023001',
          type: 'maintenance',
          typeText: '维护工单',
          title: '设备定期维护',
          description: '一号生产线主轴承定期维护检查',
          location: '一号生产线',
          submitter: '张工',
          submitTime: '2023-07-10 09:30',
          status: 'pending',
          statusText: '待处理'
        },
        {
          id: 2,
          number: 'WO2023002',
          type: 'repair',
          typeText: '维修工单',
          title: '设备故障维修',
          description: '二号生产线传送带异常，需要维修',
          location: '二号生产线',
          submitter: '李工',
          submitTime: '2023-07-10 10:15',
          status: 'processing',
          statusText: '处理中',
          handler: '王工',
          updateTime: '2023-07-10 10:30'
        },
        {
          id: 3,
          number: 'WO2023003',
          type: 'inspection',
          typeText: '巡检工单',
          title: '日常安全巡检',
          description: '车间安全设施巡检任务',
          location: '总装车间',
          submitter: '赵工',
          submitTime: '2023-07-10 08:00',
          status: 'completed',
          statusText: '已完成',
          handler: '刘工',
          updateTime: '2023-07-10 09:45'
        }
      ]
    }
  },
  computed: {
    pendingCount() {
      return this.workorders.filter(w => w.status === 'pending').length
    },
    processingCount() {
      return this.workorders.filter(w => w.status === 'processing').length
    },
    completedCount() {
      return this.workorders.filter(w => w.status === 'completed').length
    },
    filteredWorkorders() {
      return this.workorders.filter(w => {
        const typeMatch = this.filterType === 'all' || w.type === this.filterType
        const statusMatch = this.filterStatus === 'all' || w.status === this.filterStatus
        const searchMatch = !this.searchKeyword || 
          w.number.includes(this.searchKeyword) || 
          w.submitter.includes(this.searchKeyword)
        return typeMatch && statusMatch && searchMatch
      })
    }
  }
}
</script>

<style scoped>
.workorders {
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
  color: #666;
  font-size: 14px;
}

.count {
  font-size: 24px;
  font-weight: bold;
}

.count.pending { color: #ff9800; }
.count.processing { color: #2196F3; }
.count.completed { color: #4CAF50; }

.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.filter-select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 120px;
}

.search-input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.workorder-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.workorder-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.workorder-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.workorder-number {
  font-weight: bold;
  color: #333;
}

.workorder-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.workorder-status.pending {
  background: #fff3e0;
  color: #ff9800;
}

.workorder-status.processing {
  background: #e3f2fd;
  color: #2196F3;
}

.workorder-status.completed {
  background: #e8f5e9;
  color: #4CAF50;
}

.workorder-content h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.description {
  color: #666;
  margin-bottom: 10px;
}

.workorder-info {
  display: flex;
  gap: 15px;
  color: #333;
  margin-bottom: 8px;
}

.workorder-meta, .workorder-handler {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #666;
  margin-top: 8px;
}
</style>
