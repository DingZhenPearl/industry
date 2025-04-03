<template>
  <div class="inspection">
    <header class="header">
      <h1>安全巡检</h1>
    </header>
    
    <div class="content">
      <div class="task-filter">
        <select v-model="filterStatus" class="filter-select">
          <option value="all">全部任务</option>
          <option value="pending">待巡检</option>
          <option value="completed">已完成</option>
        </select>
        <button class="add-btn" @click="addInspection">新建巡检</button>
      </div>

      <div class="task-list">
        <div class="task-item" v-for="(task, index) in filteredTasks" :key="index">
          <div class="task-header">
            <span class="task-name">{{ task.name }}</span>
            <span class="task-status" :class="task.status">{{ task.statusText }}</span>
          </div>
          <div class="task-info">
            <p>区域：{{ task.area }}</p>
            <p>时间：{{ task.time }}</p>
          </div>
          <div class="task-actions" v-if="task.status === 'pending'">
            <button class="start-btn" @click="startInspection(task)">开始巡检</button>
          </div>
        </div>
      </div>
    </div>

    <SafetyNav />
  </div>
</template>

<script>
import SafetyNav from '@/components/SafetyNav.vue'

export default {
  name: 'SafetyInspection',
  components: {
    SafetyNav
  },
  data() {
    return {
      filterStatus: 'all',
      tasks: [
        {
          id: 1,
          name: '日常安全巡检',
          area: '一号生产线',
          time: '2023-07-10 14:00',
          status: 'pending',
          statusText: '待巡检'
        },
        {
          id: 2,
          name: '设备安全检查',
          area: '二号生产线',
          time: '2023-07-10 16:00',
          status: 'completed',
          statusText: '已完成'
        }
      ]
    }
  },
  computed: {
    filteredTasks() {
      if (this.filterStatus === 'all') return this.tasks
      return this.tasks.filter(task => task.status === this.filterStatus)
    }
  },
  methods: {
    addInspection() {
      console.log('新建巡检任务')
    },
    startInspection(task) {
      console.log('开始巡检:', task)
    }
  }
}
</script>

<style scoped>
.inspection {
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

.task-filter {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.filter-select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.add-btn {
  padding: 8px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.task-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.task-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.task-name {
  font-weight: bold;
}

.task-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.task-status.pending {
  background: #fff3e0;
  color: #ff9800;
}

.task-status.completed {
  background: #e8f5e9;
  color: #4CAF50;
}

.task-info {
  color: #666;
  font-size: 14px;
  margin-bottom: 10px;
}

.task-info p {
  margin: 5px 0;
}

.start-btn {
  padding: 8px 16px;
  background: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
