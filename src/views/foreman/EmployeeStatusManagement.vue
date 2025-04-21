<template>
  <div class="employee-status-management">
    <ForemanNav />

    <div class="page-content">
      <h2 class="page-title">员工状态管理</h2>

      <div class="status-container">
        <div class="team-status-section">
          <EmployeeStatusList
            :employees="teamMembers"
            :loading="loading"
            title="团队成员状态"
            @status-updated="handleStatusUpdated"
          />
        </div>

        <div class="leave-requests-section">
          <PendingLeaveList
            :approver-id="currentForeman.id"
            :group-id="currentForeman.group_id"
            ref="pendingLeaveList"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ForemanNav from '@/components/ForemanNav.vue';
import EmployeeStatusList from '@/components/EmployeeStatusList.vue';
import PendingLeaveList from '@/components/PendingLeaveList.vue';

export default {
  name: 'EmployeeStatusManagement',
  components: {
    ForemanNav,
    EmployeeStatusList,
    PendingLeaveList
  },
  data() {
    return {
      currentForeman: {
        id: '',
        name: '',
        group_id: null
      },
      teamMembers: [],
      loading: false
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
            this.currentForeman = {
              id: result.user.employee_id,
              name: result.user.username,
              group_id: result.user.group_id
            };
          } else {
            throw new Error(result.error || '获取用户信息失败');
          }
        } else {
          // 使用 localStorage 中的用户信息
          this.currentForeman = {
            id: userInfo.employee_id,
            name: userInfo.username,
            group_id: userInfo.group_id
          };
        }

        // 获取团队成员
        await this.fetchTeamMembers();
      } catch (error) {
        console.error('获取用户信息出错:', error);
        // 如果出错，可能是会话过期，重定向到登录页面
        if (error.message.includes('未登录') || error.message.includes('过期')) {
          this.$router.push('/login');
        }
      }
    },
    async fetchTeamMembers() {
      this.loading = true;

      try {
        const response = await fetch(`/api/users/foreman/team-members?group_id=${this.currentForeman.group_id}`, {
          credentials: 'include' // 确保发送会话 cookie
        });

        if (!response.ok) {
          throw new Error(`获取团队成员失败: ${response.status}`);
        }

        const result = await response.json();

        if (result.success && result.data) {
          this.teamMembers = result.data;
        } else {
          console.error('获取团队成员失败:', result.error);
        }
      } catch (error) {
        console.error('获取团队成员出错:', error);
      } finally {
        this.loading = false;
      }
    },
    handleStatusUpdated() {
      // 刷新团队成员列表
      this.fetchTeamMembers();
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

.team-status-section, .leave-requests-section {
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
