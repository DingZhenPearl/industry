<template>
  <div class="team">
    <header class="header">
      <h1>团队管理</h1>
    </header>

    <div class="content">
      <ul class="worker-list">
        <li v-for="worker in workers" :key="worker.id" class="worker-item">
          <div class="worker-info">
            <span class="worker-name">{{ worker.name }}</span>
            <span class="worker-id">工号: {{ worker.id }}</span>
          </div>
          <div class="worker-status">
            <span :class="['status-indicator', worker.status === '在线' ? 'online' : 'offline']"></span>
            {{ worker.status }}
          </div>
        </li>
      </ul>
    </div>

    <ForemanNav />
  </div>
</template>

<script>
import ForemanNav from '@/components/ForemanNav.vue'

export default {
  name: 'ForemanTeam',
  components: {
    ForemanNav
  },
  data() {
    return {
      workers: [
        { id: 'W001', name: '张三', status: '在线' },
        { id: 'W002', name: '李四', status: '离线' },
        { id: 'W003', name: '王五', status: '在线' },
        { id: 'W004', name: '赵六', status: '在线' }
      ]
    }
  }
}
</script>

<style scoped>
.team {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding-bottom: 60px; /* Adjust based on nav height */
}

.header {
  background-color: #2196F3; /* Blue */
  color: white;
  padding: 15px;
  text-align: center; /* Center title */
}

.content {
  flex: 1;
  padding: 15px;
  background-color: #f4f4f4; /* Light grey background */
}

.worker-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.worker-item {
  background-color: white;
  border-radius: 8px;
  margin-bottom: 10px;
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.worker-info {
  display: flex;
  flex-direction: column;
}

.worker-name {
  font-weight: bold;
  font-size: 1.1em;
  margin-bottom: 5px;
}

.worker-id {
  color: #666;
  font-size: 0.9em;
}

.worker-status {
  display: flex;
  align-items: center;
  font-size: 0.9em;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 8px;
  display: inline-block;
}

.status-indicator.online {
  background-color: #4CAF50; /* Green */
}

.status-indicator.offline {
  background-color: #f44336; /* Red */
}
</style>
