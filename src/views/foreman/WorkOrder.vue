<template>
  <div class="workorder">
    <header class="header">
      <div class="tab-header">
        <div 
          class="tab-item" 
          :class="{ active: currentTab === 'workorder' }" 
          @click="currentTab = 'workorder'"
        >
          工单管理
        </div>
        <div 
          class="tab-item" 
          :class="{ active: currentTab === 'schedule' }" 
          @click="currentTab = 'schedule'"
        >
          排班管理
        </div>
      </div>
    </header>
    
    <div class="content">
      <!-- 工单管理内容 -->
      <div v-if="currentTab === 'workorder'" class="workorder-list">
        <div class="workorder-item" v-for="(item, index) in workorders" :key="index">
          <div class="workorder-header">
            <span class="order-number">工单号：{{ item.number }}</span>
            <span class="order-status" :class="item.status">{{ item.statusText }}</span>
          </div>
          <div class="workorder-body">
            <p>{{ item.description }}</p>
            <div class="workorder-info">
              <span>负责人：{{ item.owner }}</span>
              <span>截止时间：{{ item.deadline }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 排班管理内容 -->
      <div v-else class="schedule-content">
        <div class="schedule-list">
          <div class="schedule-item" v-for="(item, index) in schedules" :key="index">
            <div class="schedule-header">
              <span class="schedule-title">{{ item.title }}</span>
              <span class="schedule-time">{{ item.time }}</span>
            </div>
            <div class="schedule-members">
              <span v-for="(member, mIndex) in item.members" :key="mIndex">
                {{ member }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <ForemanNav />
  </div>
</template>

<script>
import ForemanNav from '@/components/ForemanNav.vue'

export default {
  name: 'WorkOrder',
  components: {
    ForemanNav
  },
  data() {
    return {
      currentTab: 'workorder',
      workorders: [
        {
          number: 'WO2023001',
          status: 'pending',
          statusText: '待处理',
          description: '一号生产线设备维护',
          owner: '张工',
          deadline: '2023-07-30'
        },
        {
          number: 'WO2023002',
          status: 'processing',
          statusText: '进行中',
          description: '二号生产线质量检查',
          owner: '李工',
          deadline: '2023-07-31'
        }
      ],
      schedules: [
        {
          title: '早班',
          time: '06:00-14:00',
          members: ['张三', '李四', '王五']
        },
        {
          title: '中班',
          time: '14:00-22:00',
          members: ['赵六', '孙七', '周八']
        },
        {
          title: '夜班',
          time: '22:00-06:00',
          members: ['吴九', '郑十', '钱十一']
        }
      ]
    }
  }
}
</script>

<style scoped>
.workorder {
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
  margin-bottom: 10px;
}

.order-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
}

.order-status.pending {
  background-color: #ffd700;
  color: #333;
}

.order-status.processing {
  background-color: #2196F3;
  color: white;
}

.workorder-body {
  font-size: 14px;
}

.workorder-info {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  color: #666;
}

.tab-header {
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.tab-item {
  padding: 10px 20px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  position: relative;
}

.tab-item.active {
  color: white;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: white;
}

.schedule-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.schedule-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.schedule-title {
  font-weight: bold;
  color: #333;
}

.schedule-time {
  color: #666;
}

.schedule-members {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.schedule-members span {
  background-color: #f5f5f5;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
}
</style>
