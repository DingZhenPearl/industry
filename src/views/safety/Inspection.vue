<template>
  <div class="inspection">
    <header class="header">
      <h1>产线安全巡检</h1>
    </header>

    <div class="content">
      <div class="task-filter">
        <select v-model="filterStatus" class="filter-select">
          <option value="all">全部工单</option>
          <option value="pending">待巡检</option>
          <option value="processing">巡检中</option>
          <option value="completed">已完成</option>
          <option value="cancelled">已取消</option>
        </select>
        <button class="add-btn" @click="addInspection">新建巡检</button>
      </div>

      <!-- 加载中提示 -->
      <div class="loading-container" v-if="loading">
        <div class="loading-spinner"></div>
        <p>正在加载工单数据...</p>
      </div>

      <!-- 错误提示 -->
      <div class="error-container" v-if="error">
        <p class="error-message">{{ error }}</p>
        <button class="retry-btn" @click="fetchWorkorders">重试</button>
      </div>

      <!-- 空数据提示 -->
      <div class="empty-container" v-if="!loading && !error && filteredTasks.length === 0">
        <p>没有找到相关工单</p>
      </div>

      <!-- 工单列表 -->
      <div class="task-list" v-if="!loading && !error && filteredTasks.length > 0">
        <div class="task-item" v-for="(task, index) in filteredTasks" :key="index">
          <div class="task-header">
            <span class="task-id">#{{ task.id }}</span>
            <span class="task-status" :class="task.status">{{ task.statusText }}</span>
          </div>
          <div class="task-title">
            <h3>{{ task.name }}</h3>
          </div>
          <div class="task-info">
            <p><strong>产线信息：</strong>{{ task.area }}</p>
            <p><strong>描述：</strong>{{ task.description }}</p>
            <p><strong>发出人：</strong>{{ task.creator_name }} ({{ task.creator }})</p>
            <p><strong>负责工长：</strong>{{ task.foreman_name }} ({{ task.foreman }})</p>
            <div class="task-dates">
              <p><strong>创建时间：</strong>{{ task.time }}</p>
              <p v-if="task.deadline"><strong>截止时间：</strong>{{ task.deadline }}</p>
            </div>
          </div>
          <div class="task-actions">
            <button class="detail-btn" @click="viewTaskDetail(task)">查看详情</button>
            <button class="start-btn" v-if="task.status === 'pending'" @click="startInspection(task)">开始巡检</button>
            <button class="complete-btn" v-if="task.status === 'processing'" @click="completeInspection(task)">完成巡检</button>
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
      tasks: [],
      loading: false,
      error: null,
      // 用户名缓存
      usernameCache: {}
    }
  },
  created() {
    this.fetchWorkorders();
  },
  computed: {
    filteredTasks() {
      if (this.filterStatus === 'all') return this.tasks
      return this.tasks.filter(task => task.status === this.filterStatus)
    }
  },
  methods: {
    // 从后端获取工单数据
    async fetchWorkorders() {
      this.loading = true;
      this.error = null;

      try {
        // 获取当前登录用户的组号
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
        const groupId = userInfo.group_id;

        if (!groupId) {
          console.error('未找到组号信息');
          this.error = '无法获取您的组号信息，请重新登录';
          return;
        }

        // 获取安全员组的产线巡检工单
        const response = await fetch(`/api/workorders/safety-inspection-workorders?group_id=${groupId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取工单失败: ${response.status}`);
        }

        const data = await response.json();
        console.log('安全员产线巡检工单数据:', data);

        if (data.success) {
          this.tasks = this.formatWorkorders(data.data || []);
        } else {
          this.error = data.error || '获取工单失败';
        }
      } catch (error) {
        console.error('获取工单数据出错:', error);
        this.error = error.message || '获取工单数据出错';
      } finally {
        this.loading = false;
      }
    },

    // 格式化工单数据
    formatWorkorders(workorders) {
      return workorders.map(wo => {
        // 根据状态设置状态文本
        let statusText = '未知';
        let status = wo.status;

        switch(wo.status) {
          case '未接受':
          case 'pending':
            statusText = '待巡检';
            status = 'pending';
            break;

          case '已完成':
          case 'completed':
            statusText = '已完成';
            status = 'completed';
            break;

          case '已接受':
          case 'accepted':
            statusText = '巡检中';
            status = 'processing';
            break;

          case '已取消':
          case 'cancelled':
            statusText = '已取消';
            status = 'cancelled';
            break;
        }

        return {
          id: wo.workorder_number,
          name: wo.task_type,
          area: wo.production_line,
          time: this.formatDateTime(wo.created_at),
          deadline: this.formatDateTime(wo.deadline),
          status: status,
          statusText: statusText,
          description: wo.task_details,
          creator: wo.creator,
          creator_name: wo.creator_name || wo.creator,
          foreman: wo.foreman,
          foreman_name: wo.foreman_name || wo.foreman,
          team_members: wo.team_members,
          team_member_name: wo.team_member_name || wo.team_members,
          note: wo.note || '',
          // 保存原始工单数据
          original: wo
        };
      });
    },

    // 格式化日期时间
    formatDateTime(dateTimeStr) {
      if (!dateTimeStr) return '';

      const date = new Date(dateTimeStr);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    },

    addInspection() {
      console.log('新建巡检任务');
      alert('新建巡检功能开发中');
    },

    startInspection(task) {
      console.log('开始巡检:', task);

      // 更新工单状态为已接受
      this.updateWorkOrderStatus(task.id, '已接受');
    },

    completeInspection(task) {
      console.log('完成巡检:', task);

      // 更新工单状态为已完成
      this.updateWorkOrderStatus(task.id, '已完成');
    },

    viewTaskDetail(task) {
      console.log('查看工单详情:', task);
      alert(`工单详情\n\n工单编号: ${task.id}\n类型: ${task.name}\n状态: ${task.statusText}\n产线: ${task.area}\n描述: ${task.description}\n发出人: ${task.creator_name}\n工长: ${task.foreman_name}\n创建时间: ${task.time}`);
    },

    // 更新工单状态
    async updateWorkOrderStatus(workorderNumber, newStatus) {
      try {
        const response = await fetch('/api/workorders/update-workorder', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            workorder_number: workorderNumber,
            update_data: {
              status: newStatus
            }
          })
        });

        if (!response.ok) {
          throw new Error(`更新工单状态失败: ${response.status}`);
        }

        const data = await response.json();
        console.log('更新工单状态响应:', data);

        if (data.success) {
          // 更新成功，重新获取工单列表
          this.fetchWorkorders();
          alert('工单状态更新成功');
        } else {
          alert(`更新失败: ${data.error || '未知错误'}`);
        }
      } catch (error) {
        console.error('更新工单状态出错:', error);
        alert(`更新工单状态出错: ${error.message}`);
      }
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

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container {
  background-color: #ffebee;
  border: 1px solid #ffcdd2;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
  text-align: center;
}

.error-message {
  color: #d32f2f;
  margin-bottom: 10px;
}

.retry-btn {
  padding: 8px 16px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.empty-container {
  text-align: center;
  padding: 30px;
  color: #757575;
  background-color: #f5f5f5;
  border-radius: 4px;
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
  align-items: center;
}

.task-id {
  font-size: 14px;
  color: #757575;
}

.task-title h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.task-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.task-status.pending {
  background: #fff3e0;
  color: #ff9800;
}

.task-status.processing {
  background: #e3f2fd;
  color: #2196F3;
}

.task-status.completed {
  background: #e8f5e9;
  color: #4CAF50;
}

.task-status.cancelled {
  background: #f5f5f5;
  color: #757575;
}

.task-info {
  color: #666;
  font-size: 14px;
  margin-bottom: 15px;
}

.task-info p {
  margin: 8px 0;
}

.task-dates {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 12px;
  color: #757575;
}

.task-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.detail-btn {
  padding: 8px 16px;
  background: #9e9e9e;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.start-btn {
  padding: 8px 16px;
  background: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.complete-btn {
  padding: 8px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
