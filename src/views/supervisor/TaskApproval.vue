<template>
  <div class="approval">
    <header class="header">
      <h1>任务审批</h1>
    </header>
    
    <div class="content">
      <div class="approval-list">
        <div class="approval-item" v-for="(item, index) in approvalTasks" :key="index">
          <div class="task-info">
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
            <div class="task-meta">
              <span>申请人：{{ item.applicant }}</span>
              <span>提交时间：{{ item.submitTime }}</span>
            </div>
          </div>
          <div class="task-actions">
            <button class="approve-btn" @click="handleApprove(item)">同意</button>
            <button class="reject-btn" @click="handleReject(item)">拒绝</button>
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
  name: 'TaskApproval',
  components: {
    SupervisorNav
  },
  data() {
    return {
      approvalTasks: [
        {
          id: 1,
          title: '设备维护申请',
          description: '一号生产线主轴承需要更换',
          applicant: '张工',
          submitTime: '2023-07-01 10:30'
        },
        {
          id: 2,
          title: '加班申请',
          description: '周末加班完成订单生产',
          applicant: '李工',
          submitTime: '2023-07-02 14:20'
        }
      ]
    }
  },
  methods: {
    handleApprove(task) {
      console.log('Approved task:', task)
    },
    handleReject(task) {
      console.log('Rejected task:', task)
    }
  }
}
</script>

<style scoped>
.approval {
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

.approval-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.task-info h3 {
  margin: 0 0 10px 0;
}

.task-meta {
  display: flex;
  justify-content: space-between;
  color: #666;
  font-size: 14px;
  margin-top: 10px;
}

.task-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 15px;
}

.approve-btn, .reject-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.approve-btn {
  background: #4CAF50;
  color: white;
}

.reject-btn {
  background: #f44336;
  color: white;
}
</style>
