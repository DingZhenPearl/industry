<template>
  <div class="employee-status-management">
    <SupervisorNav />

    <div class="page-content">
      <h2 class="page-title">员工状态管理</h2>

      <div class="status-container">
        <div class="foreman-status-section">
          <EmployeeStatusList
            :employees="foremen"
            :loading="foremanLoading"
            title="工长状态管理"
            @status-updated="handleStatusUpdated"
          />
        </div>

        <div class="leave-requests-section">
          <PendingLeaveList
            :approver-id="currentManager.id"
            :is-manager="true"
            ref="pendingLeaveList"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SupervisorNav from '@/components/SupervisorNav.vue';
import EmployeeStatusList from '@/components/EmployeeStatusList.vue';
import PendingLeaveList from '@/components/PendingLeaveList.vue';

export default {
  name: 'EmployeeStatusManagement',
  components: {
    SupervisorNav,
    EmployeeStatusList,
    PendingLeaveList
  },
  data() {
    return {
      currentManager: {
        id: '',
        name: ''
      },
      foremen: [],
      foremanLoading: false
    };
  },
  methods: {
    async fetchUserInfo() {
      try {
        // 从 localStorage 获取用户信息
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');

        if (!userInfo || !userInfo.employee_id) {
          // 如果 localStorage 中没有用户信息，尝试从服务器获取
          const response = await fetch('/api/auth/user', {
            credentials: 'include' // 确保发送会话 cookie
          });

          if (!response.ok) {
            throw new Error('获取用户信息失败');
          }

          const result = await response.json();

          if (result.success && result.user) {
            this.currentManager = {
              id: result.user.employee_id,
              name: result.user.username
            };
          } else {
            throw new Error(result.error || '获取用户信息失败');
          }
        } else {
          // 使用 localStorage 中的用户信息
          this.currentManager = {
            id: userInfo.employee_id,
            name: userInfo.username
          };
        }

        // 获取所有工长
        await this.fetchForemen();
      } catch (error) {
        console.error('获取用户信息出错:', error);
        // 如果出错，可能是会话过期，重定向到登录页面
        if (error.message.includes('未登录') || error.message.includes('过期')) {
          this.$router.push('/login');
        }
      }
    },
    async fetchForemen() {
      this.foremanLoading = true;

      try {
        const response = await fetch('/api/users?role=foreman', {
          credentials: 'include' // 确保发送会话 cookie
        });

        if (!response.ok) {
          throw new Error(`获取工长列表失败: ${response.status}`);
        }

        const result = await response.json();

        if (result.success && result.data) {
          this.foremen = result.data;
        } else {
          console.error('获取工长列表失败:', result.error);
        }
      } catch (error) {
        console.error('获取工长列表出错:', error);
      } finally {
        this.foremanLoading = false;
      }
    },
    handleStatusUpdated() {
      // 刷新工长列表
      this.fetchForemen();
    }
  },
  mounted() {
    this.fetchUserInfo();
  }
};
</script>

<style scoped>
.employee-status-management {
  display: flex;
  min-height: 100vh;
  background-color: #f0f2f5;
}

.page-content {
  flex: 1;
  padding: 20px;
}

.page-title {
  margin-bottom: 20px;
  color: #333;
}

.status-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.foreman-status-section, .leave-requests-section {
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .employee-status-management {
    flex-direction: column;
  }

  .page-content {
    padding: 15px;
  }
}
</style>
