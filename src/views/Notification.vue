<template>
  <div class="notification">
    <header class="header">
      <h1>通知</h1>
      <div class="refresh-btn" @click="refreshTasks">
        <i class="refresh-icon"></i>
      </div>
    </header>
    
    <div class="content">
      <div class="task-list">
        <div class="task-card" v-for="(task, index) in tasks" :key="index">
          <div class="task-header">
            <div class="task-type">
              <i class="task-icon"></i>
              <span>{{ task.type }}</span>
            </div>
            <div class="task-actions">
              <span class="action-btn">操作按钮</span>
            </div>
          </div>
          <div class="task-info">
            <div class="info-item">
              <span class="label">任务描述:</span>
              <span class="value">{{ task.description }}</span>
            </div>
            <div class="info-item">
              <span class="label">开始时间:</span>
              <span class="value">{{ task.startTime }}</span>
            </div>
            <div class="info-item">
              <span class="label">结束时间:</span>
              <span class="value">{{ task.endTime }}</span>
            </div>
            <div class="info-item">
              <span class="label">状态:</span>
              <span class="value">{{ task.status }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <BottomNav />
  </div>
</template>

<script>
import BottomNav from '@/components/BottomNav.vue'

export default {
  components: {
    BottomNav
  },
  name: 'NotificationPage',
  data() {
    return {
      tasks: [
        {
          type: '排班任务',
          description: '对花都新工厂一机加线产线进行巡检',
          startTime: '2023-07-02-00',
          endTime: '2023-07-02-01',
          status: '待确认人员'
        },
        {
          type: '排班任务',
          description: '对花都新工厂一机加线产线进行巡检',
          startTime: '2023-07-02-02',
          endTime: '2023-07-02-04',
          status: '待确认班组'
        },
        {
          type: '排班任务',
          description: '对花都新工厂一机加线产线进行巡检',
          startTime: '2023-07-03-00',
          endTime: '2023-07-03-02',
          status: '待确认人员'
        }
      ]
    }
  },
  methods: {
    refreshTasks() {
      // 刷新任务列表的逻辑
      console.log('刷新任务列表')
    }
  }
}
</script>

<style scoped>
.notification {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.header {
  background-color: #2196F3;
  color: white;
  padding: 15px 20px;
  text-align: center;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.refresh-btn {
  position: absolute;
  right: 20px;
  width: 24px;
  height: 24px;
}

.refresh-icon {
  display: inline-block;
  width: 24px;
  height: 24px;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white"><path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>');
  background-size: contain;
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 10px;
  background-color: #f5f5f5;
  overflow-y: auto;
}

.task-list {
  width: 100%;
}

.task-card {
  background-color: white;
  border-radius: 8px;
  margin-bottom: 15px;
  padding: 15px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.task-type {
  display: flex;
  align-items: center;
}

.task-icon {
  display: inline-block;
  width: 20px;
  height: 20px;
  margin-right: 8px;
  background-color: #2196F3;
  border-radius: 4px;
}

.task-actions .action-btn {
  color: #2196F3;
  font-size: 14px;
}

.task-info {
  display: flex;
  flex-direction: column;
}

.info-item {
  display: flex;
  margin-bottom: 10px;
  font-size: 14px;
}

.info-item .label {
  color: #666;
  width: 80px;
  flex-shrink: 0;
}

.info-item .value {
  color: #333;
  flex: 1;
}

.bottom-nav {
  display: flex;
  justify-content: space-around;
  background-color: #f8f8f8;
  padding: 10px 0;
  border-top: 1px solid #e0e0e0;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}

.nav-icon {
  width: 24px;
  height: 24px;
  margin-bottom: 5px;
  background-color: #666;
  border-radius: 50%;
}

.nav-item.active {
  color: #2196F3;
}

.nav-item.active .nav-icon {
  background-color: #2196F3;
}
</style>