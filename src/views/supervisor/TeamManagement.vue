<template>
  <div class="team">
    <header class="header">
      <h1>团队管理</h1>
    </header>

    <div class="content">
      <!-- 角色概览卡片 -->
      <div class="department-cards">
        <div class="dept-card" v-for="role in roles" :key="role.id">
          <div class="dept-header">
            <h3>{{ role.name }}</h3>
            <span class="member-count">{{ role.memberCount }}人</span>
          </div>
          <div class="dept-stats">
            <div class="stat-item">
              <span class="label">在岗率</span>
              <span class="value">{{ role.activeRate }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 员工列表 -->
      <div class="employee-section">
        <div class="section-header">
          <h3>员工管理</h3>
          <div class="header-actions">
            <button class="view-btn" @click="showLeaveManagement = true">
              <i class="calendar-icon"></i> 请假管理
            </button>
          </div>
        </div>

        <div class="filter-bar">
          <select v-model="filterRole" class="filter-select">
            <option value="">全部角色</option>
            <option v-for="role in roles" :key="role.id" :value="role.id">
              {{ role.name }}
            </option>
          </select>
          <!-- 添加组号筛选下拉框 -->
          <select v-model="filterGroup" class="filter-select">
            <option value="">全部组号</option>
            <option v-for="group in availableGroups" :key="group" :value="group">
              {{ group }}
            </option>
          </select>
          <input
            type="text"
            v-model="searchKeyword"
            class="search-input"
            placeholder="搜索员工姓名"
          >
        </div>

        <div class="employee-list">
          <table>
            <thead>
              <tr>
                <th>工号</th>
                <th>姓名</th>
                <th>分组号</th>
                <th>角色</th>
                <th>联系方式</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="emp in filteredEmployees" :key="emp.id">
                <td>{{ emp.id }}</td>
                <td>{{ emp.name }}</td>
                <td>{{ emp.group_id || '未分组' }}</td>
                <td>{{ emp.roleName }}</td>
                <td>{{ emp.phone }}</td>
                <td>
                  <span :class="['status-tag', getStatusClass(emp.status)]">
                    {{ emp.status || '未知' }}
                  </span>
                </td>
                <td>
                  <button class="action-btn view" @click="viewEmployeeDetail(emp)">详情</button>
                  <button class="action-btn edit" @click="showGroupChangeModal(emp)">分组</button>
                  <button class="action-btn status" @click="showUpdateStatusModal(emp)">修改状态</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>



    <!-- 分组调整模态框 -->
    <div class="modal" v-if="showGroupChange">
      <div class="modal-content">
        <div class="modal-header">
          <h3>调整员工分组</h3>
          <span class="close-btn" @click="showGroupChange = false">&times;</span>
        </div>
        <div class="modal-body">
          <div class="employee-info">
            <div class="info-item">
              <label>工号：</label>
              <span>{{ selectedEmployee.id }}</span>
            </div>
            <div class="info-item">
              <label>姓名：</label>
              <span>{{ selectedEmployee.name }}</span>
            </div>
            <div class="info-item">
              <label>角色：</label>
              <span>{{ selectedEmployee.roleName }}</span>
            </div>
            <div class="info-item">
              <label>当前分组：</label>
              <span>{{ selectedEmployee.group_id || '未分组' }}</span>
            </div>
          </div>

          <div class="form-group">
            <label>新分组：</label>
            <div class="group-selection">
              <div class="group-options">
                <div
                  v-for="group in availableGroups"
                  :key="group"
                  :class="['group-option', newGroupId === group ? 'selected' : '']"
                  @click="newGroupId = group"
                >
                  {{ group }}
                </div>
                <div
                  :class="['group-option', newGroupId === 'new' ? 'selected' : '']"
                  @click="newGroupId = 'new'"
                >
                  新建分组
                </div>
              </div>
              <div v-if="newGroupId === 'new'" class="new-group-input">
                <input
                  type="text"
                  v-model="customGroupId"
                  class="form-control"
                  placeholder="请输入新分组号"
                >
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showGroupChange = false">取消</button>
          <button
            class="confirm-btn"
            :disabled="!isValidGroupSelection || groupUpdateLoading"
            @click="updateEmployeeGroup"
          >
            {{ groupUpdateLoading ? '更新中...' : '确认更新' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 请假管理模态框 -->
    <div class="modal" v-if="showLeaveManagement">
      <div class="modal-content leave-modal-content">
        <div class="modal-header">
          <h3>请假管理</h3>
          <span class="close-btn" @click="showLeaveManagement = false">&times;</span>
        </div>
        <div class="modal-body">
          <div class="tabs">
            <div
              class="tab"
              :class="{ active: activeLeaveTab === 'pending' }"
              @click="activeLeaveTab = 'pending'"
            >
              待审批申请
            </div>
            <div
              class="tab"
              :class="{ active: activeLeaveTab === 'history' }"
              @click="activeLeaveTab = 'history'"
            >
              历史记录
            </div>
          </div>

          <!-- 待审批申请列表 -->
          <div v-if="activeLeaveTab === 'pending'" class="tab-content">
            <PendingLeaveList
              :approver-id="currentManager.id"
              :is-manager="true"
              ref="pendingLeaveList"
              @leave-approved="handleLeaveApproved"
              @leave-rejected="handleLeaveRejected"
            />
          </div>

          <!-- 历史记录列表 -->
          <div v-if="activeLeaveTab === 'history'" class="tab-content">
            <div class="leave-list">
              <div class="leave-item" v-for="(leave, index) in leaveRequests" :key="index">
                <div class="leave-header">
                  <span class="employee-name">{{ leave.employeeName }}</span>
                  <span :class="['status-tag', leave.status]">{{ leave.statusText }}</span>
                </div>
                <div class="leave-details">
                  <div class="leave-type">{{ leave.type }}</div>
                  <div class="leave-period">{{ leave.startDate }} 至 {{ leave.endDate }}</div>
                  <div class="leave-reason">
                    <div class="reason-label">请假原因：</div>
                    <div class="reason-content">{{ leave.reason }}</div>
                  </div>
                  <div class="approval-info">
                    <div class="approval-time">审批时间：{{ leave.approvalTime }}</div>
                    <div class="approver-info">审批人：{{ leave.approverName || '未知' }} ({{ leave.approverRole || '未知' }})</div>
                    <div class="approval-notes" v-if="leave.notes">备注：{{ leave.notes }}</div>
                  </div>
                </div>
              </div>

              <div v-if="leaveRequests.length === 0" class="empty-state">
                暂无历史记录
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 修改状态模态框 -->
    <div class="modal" v-if="showUpdateStatus">
      <div class="modal-content">
        <div class="modal-header">
          <h3>修改员工状态</h3>
          <span class="close-btn" @click="showUpdateStatus = false">&times;</span>
        </div>
        <div class="modal-body">
          <div class="employee-info">
            <div class="info-item">
              <label>工号：</label>
              <span>{{ selectedEmployee.id }}</span>
            </div>
            <div class="info-item">
              <label>姓名：</label>
              <span>{{ selectedEmployee.name }}</span>
            </div>
            <div class="info-item">
              <label>当前状态：</label>
              <span class="status-tag" :class="getStatusClass(selectedEmployee.status)">
                {{ selectedEmployee.status || '未知' }}
              </span>
            </div>
          </div>

          <div class="form-group">
            <label>新状态：</label>
            <select v-model="newStatus" class="form-control">
              <option value="">请选择新状态</option>
              <option value="在岗">在岗</option>
              <option value="请假">请假</option>
              <option value="离岗">离岗</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showUpdateStatus = false">取消</button>
          <button
            class="confirm-btn"
            :disabled="!newStatus || statusUpdateLoading"
            @click="updateEmployeeStatus"
          >
            {{ statusUpdateLoading ? '更新中...' : '确认更新' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 员工详情模态框 -->
    <div class="modal" v-if="showEmployeeDetail">
      <div class="modal-content">
        <div class="modal-header">
          <h3>员工详情</h3>
          <span class="close-btn" @click="closeEmployeeDetail">&times;</span>
        </div>
        <div class="modal-body">
          <div class="detail-item">
            <label>工号</label>
            <div class="value">{{ selectedEmployee.id }}</div>
          </div>
          <div class="detail-item">
            <label>姓名</label>
            <div class="value">{{ selectedEmployee.name }}</div>
          </div>
          <div class="detail-item">
            <label>角色</label>
            <div class="value">{{ selectedEmployee.roleName }}</div>
          </div>
          <div class="detail-item">
            <label>分组号</label>
            <div class="value">{{ selectedEmployee.group_id || '未分组' }}</div>
          </div>
          <div class="detail-item">
            <label>联系方式</label>
            <div class="value">{{ selectedEmployee.phone }}</div>
          </div>
          <div class="detail-item">
            <label>状态</label>
            <div class="value">
              <span :class="['status-tag', getStatusClass(selectedEmployee.status)]">
                {{ selectedEmployee.status || '未知' }}
              </span>
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
import PendingLeaveList from '@/components/PendingLeaveList.vue'

export default {
  name: 'TeamManagement',
  components: {
    SupervisorNav,
    PendingLeaveList
  },
  data() {
    return {
      roles: [],
      employees: [], // 清空本地数据,改为从后端获取
      filterRole: '',
      filterGroup: '', // 添加组号筛选数据
      searchKeyword: '',
      showLeaveManagement: false,
      showUpdateStatus: false,
      showGroupChange: false,
      showEmployeeDetail: false,
      selectedEmployee: {},
      currentManager: {
        id: '',
        name: ''
      },
      leaveRequests: [],
      activeLeaveTab: 'pending',
      newStatus: '',
      statusUpdateLoading: false,
      newGroupId: '',
      customGroupId: '',
      groupUpdateLoading: false
    }
  },
  async created() {
    // 获取当前管理员信息
    const userInfoStr = localStorage.getItem('userInfo') || '{}';
    const userInfo = JSON.parse(userInfoStr);

    this.currentManager = {
      id: userInfo.employee_id,
      name: userInfo.username
    };

    // 组件创建时获取用户列表
    await this.fetchEmployees();

    // 获取角色数据
    await this.fetchRoles();

    // 获取已处理的请假记录
    await this.fetchProcessedLeaveRequests();
  },
  computed: {
    // 获取所有可用的组号
    availableGroups() {
      const groups = new Set();
      this.employees.forEach(emp => {
        if (emp.group_id) {
          groups.add(emp.group_id);
        }
      });
      return Array.from(groups).sort();
    },

    // 检查分组选择是否有效
    isValidGroupSelection() {
      if (this.newGroupId === 'new') {
        return this.customGroupId && this.customGroupId.trim() !== '';
      }
      return this.newGroupId && this.newGroupId !== this.selectedEmployee.group_id;
    },

    filteredEmployees() {
      return this.employees.filter(emp => {
        const roleMatch = !this.filterRole || emp.role === this.filterRole;
        const groupMatch = !this.filterGroup || emp.group_id === this.filterGroup;
        const searchMatch = !this.searchKeyword ||
          emp.name.toLowerCase().includes(this.searchKeyword.toLowerCase()) ||
          emp.id.toLowerCase().includes(this.searchKeyword.toLowerCase()) ||
          (emp.group_id && emp.group_id.toLowerCase().includes(this.searchKeyword.toLowerCase()));

        return roleMatch && groupMatch && searchMatch;
      });
    }
  },
  methods: {
    // 获取用户列表
    async fetchEmployees() {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/users', {
          credentials: 'include',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        const data = await response.json();

        if (data.success && Array.isArray(data.data)) {
          // 处理返回的数据,添加角色名称显示
          this.employees = data.data.map(user => ({
            ...user,
            roleName: this.getRoleName(user.role)
          }));
        } else {
          console.error('获取用户列表失败:', data.error || '未知错误');
          this.$message.error('获取用户列表失败');
        }
      } catch (error) {
        console.error('请求用户列表出错:', error);
        this.$message.error('获取用户列表失败');
      }
    },
    // 获取角色数据
    async fetchRoles() {
      try {
        // 初始化角色数据结构
        const roleStats = {
          'supervisor': {
            id: 'supervisor',
            name: '厂长',
            memberCount: 0,
            activeRate: 0
          },
          'foreman': {
            id: 'foreman',
            name: '工长',
            memberCount: 0,
            activeRate: 0
          },
          'member': {
            id: 'member',
            name: '产线工人',
            memberCount: 0,
            activeRate: 0
          },
          'safety_officer': {
            id: 'safety_officer',
            name: '安全员',
            memberCount: 0,
            activeRate: 0
          }
        };

        // 计算每个角色的成员数量
        this.employees.forEach(emp => {
          if (emp.role && roleStats[emp.role]) {
            roleStats[emp.role].memberCount++;
          }
        });

        // 计算每个角色的在岗率
        Object.keys(roleStats).forEach(role => {
          const roleEmployees = this.employees.filter(emp => emp.role === role);
          if (roleEmployees.length > 0) {
            const activeEmployees = roleEmployees.filter(emp => emp.status === '在岗');
            roleStats[role].activeRate = Math.round((activeEmployees.length / roleEmployees.length) * 100);
          }
        });

        // 将结果转换为数组
        this.roles = Object.values(roleStats);

      } catch (error) {
        console.error('计算角色数据出错:', error);
        // 初始化空的角色数组
        this.roles = [
          {
            id: 'supervisor',
            name: '厂长',
            memberCount: 0,
            activeRate: 0
          },
          {
            id: 'foreman',
            name: '工长',
            memberCount: 0,
            activeRate: 0
          },
          {
            id: 'member',
            name: '产线工人',
            memberCount: 0,
            activeRate: 0
          },
          {
            id: 'safety_officer',
            name: '安全员',
            memberCount: 0,
            activeRate: 0
          }
        ];
      }
    },

    // 获取角色显示名称
    getRoleName(role) {
      const roleNames = {
        'supervisor': '厂长',
        'foreman': '工长',
        'member': '产线工人',
        'safety_officer': '安全员'
      };
      return roleNames[role] || role;
    },

    // 查看员工详情
    viewEmployeeDetail(employee) {
      this.selectedEmployee = { ...employee };
      this.showEmployeeDetail = true;
    },

    // 关闭员工详情
    closeEmployeeDetail() {
      this.showEmployeeDetail = false;
      this.selectedEmployee = {};
    },

    // 显示分组调整模态框
    showGroupChangeModal(employee) {
      this.selectedEmployee = { ...employee };
      this.newGroupId = '';
      this.customGroupId = '';
      this.showGroupChange = true;
    },

    // 更新员工分组
    async updateEmployeeGroup() {
      if (!this.isValidGroupSelection || this.groupUpdateLoading) return;

      this.groupUpdateLoading = true;

      // 确定要使用的组号
      const groupId = this.newGroupId === 'new' ? this.customGroupId.trim() : this.newGroupId;

      try {
        const response = await fetch('/api/update-group', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            employee_id: this.selectedEmployee.id,
            group_id: groupId
          })
        });

        const result = await response.json();

        if (result.success) {
          alert('员工分组更新成功');
          this.showGroupChange = false;

          // 更新本地数据
          const index = this.employees.findIndex(emp => emp.id === this.selectedEmployee.id);
          if (index !== -1) {
            this.$set(this.employees[index], 'group_id', groupId);
          }

          // 刷新员工列表
          await this.fetchEmployees();
        } else {
          alert(`更新员工分组失败: ${result.error}`);
        }
      } catch (error) {
        console.error('更新员工分组出错:', error);
        alert('更新员工分组失败，请重试');
      } finally {
        this.groupUpdateLoading = false;
      }
    },

    // 获取状态类名
    getStatusClass(status) {
      switch (status) {
        case '在岗': return 'status-active';
        case '请假': return 'status-leave';
        case '离岗': return 'status-off';
        default: return '';
      }
    },

    // 显示修改状态模态框
    showUpdateStatusModal(employee) {
      this.selectedEmployee = { ...employee };
      this.newStatus = '';
      this.showUpdateStatus = true;
    },

    // 更新员工状态
    async updateEmployeeStatus() {
      if (!this.newStatus || this.statusUpdateLoading) return;

      this.statusUpdateLoading = true;

      try {
        const response = await fetch('/api/attendance/update-status', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            employee_id: this.selectedEmployee.id,
            status: this.newStatus
          })
        });

        const result = await response.json();

        if (result.success) {
          alert('员工状态更新成功');
          this.showUpdateStatus = false;

          // 更新本地数据
          const index = this.employees.findIndex(emp => emp.id === this.selectedEmployee.id);
          if (index !== -1) {
            this.$set(this.employees[index], 'status', this.newStatus);
          }

          // 刷新员工列表
          await this.fetchEmployees();
        } else {
          alert(`更新员工状态失败: ${result.error}`);
        }
      } catch (error) {
        console.error('更新员工状态出错:', error);
        alert('更新员工状态失败，请重试');
      } finally {
        this.statusUpdateLoading = false;
      }
    },

    // 处理请假审批通过
    handleLeaveApproved(leaveRequest) {
      // 将审批通过的请假添加到历史记录
      this.leaveRequests.unshift({
        employeeId: leaveRequest.employee_id,
        employeeName: leaveRequest.employee_name,
        type: leaveRequest.leave_type,
        startDate: leaveRequest.start_date,
        endDate: leaveRequest.end_date,
        reason: leaveRequest.reason,
        status: 'approved',
        statusText: '已批准',
        approvalTime: new Date().toLocaleString()
      });

      // 刷新员工列表
      this.fetchEmployees();
    },

    // 处理请假审批拒绝
    handleLeaveRejected(leaveRequest) {
      // 将审批拒绝的请假添加到历史记录
      this.leaveRequests.unshift({
        employeeId: leaveRequest.employee_id,
        employeeName: leaveRequest.employee_name,
        type: leaveRequest.leave_type,
        startDate: leaveRequest.start_date,
        endDate: leaveRequest.end_date,
        reason: leaveRequest.reason,
        status: 'rejected',
        statusText: '已拒绝',
        approvalTime: new Date().toLocaleString()
      });
    },

    // 获取已处理的请假记录
    async fetchProcessedLeaveRequests() {
      try {
        const response = await fetch('/api/attendance/processed-leaves?all=true', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        const result = await response.json();

        if (result.success && Array.isArray(result.data)) {
          // 将后端返回的数据转换为前端需要的格式
          this.leaveRequests = result.data.map(leave => ({
            id: leave.id,
            employeeId: leave.employee_id,
            employeeName: leave.employee_name,
            type: leave.leave_type,
            startDate: leave.start_date,
            endDate: leave.end_date,
            reason: leave.reason,
            status: leave.status === '已批准' ? 'approved' : 'rejected',
            statusText: leave.status,
            approvalTime: leave.approval_time,
            approverName: leave.approver_name,
            approverRole: leave.approver_role,
            notes: leave.approval_notes
          }));
        } else {
          console.error('获取已处理请假记录失败:', result.error || '未知错误');
        }
      } catch (error) {
        console.error('获取已处理请假记录出错:', error);
      }
    }
  }
}
</script>

<style scoped>
.team {
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

.department-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.dept-card {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.dept-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.dept-header h3 {
  margin: 0;
  font-size: 16px;
}

.member-count {
  background: #e3f2fd;
  color: #2196F3;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
}

.dept-stats {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 10px;
}

.stat-item {
  text-align: center;
}

.stat-item .label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.stat-item .value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.employee-section {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.filter-select,
.search-input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 150px;
}

.search-input {
  flex: 1;
}



.employee-list table {
  width: 100%;
  border-collapse: collapse;
}

.employee-list th,
.employee-list td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.employee-list th {
  background: #f5f5f5;
  font-weight: bold;
}

.status-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-tag.status-active {
  background: #e8f5e9;
  color: #4CAF50;
}

.status-tag.status-leave {
  background: #fff8e1;
  color: #FFC107;
}

.status-tag.status-off {
  background: #f5f5f5;
  color: #666;
}

.status-tag.leave {
  background: #fff3e0;
  color: #ff9800;
}

.action-btn {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 5px;
}

.action-btn.edit {
  background: #2196F3;
  color: white;
}

.action-btn.status {
  background: #e3f2fd;
  color: #2196F3;
}

.view-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  margin-right: 10px;
}

.calendar-icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  margin-right: 5px;
  position: relative;
}

.calendar-icon::before {
  content: '📅';
}

.header-actions {
  display: flex;
}

.leave-modal-content {
  max-width: 800px;
  width: 95%;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #eee;
  margin-bottom: 15px;
}

.tab {
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.tab.active {
  border-bottom-color: #2196F3;
  color: #2196F3;
  font-weight: 500;
}

.tab-content {
  padding: 10px 0;
}

.empty-state {
  padding: 30px 0;
  text-align: center;
  color: #999;
}

.leave-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.leave-item {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
}

.leave-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.employee-name {
  font-weight: 600;
}

.leave-details {
  margin-bottom: 15px;
}

.leave-period {
  margin: 5px 0;
  color: #666;
}

.leave-reason {
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
  margin-bottom: 10px;
}

.reason-label {
  font-weight: 500;
  margin-bottom: 5px;
  color: #555;
}

.reason-content {
  white-space: pre-line;
}

.approval-info {
  padding: 10px;
  background-color: #f0f8ff;
  border-radius: 4px;
  font-size: 14px;
  color: #555;
}

.approval-time, .approver-info {
  margin-bottom: 5px;
}

.approval-notes {
  font-style: italic;
  color: #666;
}

.group-selection {
  margin-top: 10px;
}

.group-options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
}

.group-option {
  padding: 8px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.group-option:hover {
  border-color: #2196F3;
  color: #2196F3;
}

.group-option.selected {
  background-color: #e3f2fd;
  border-color: #2196F3;
  color: #2196F3;
  font-weight: 500;
}

.new-group-input {
  margin-top: 10px;
}

.new-group-input input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.info-item {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}

.info-item label {
  width: 100px;
  font-weight: 500;
}

.info-item span {
  flex: 1;
}

.form-control {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.cancel-btn {
  background-color: #f5f5f5;
  color: #333;
  border: none;
  border-radius: 4px;
  padding: 8px 15px;
  cursor: pointer;
}

.confirm-btn {
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 15px;
  cursor: pointer;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
}

.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #666;
}

.form-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn.cancel {
  background: #f5f5f5;
  color: #666;
}

.btn.submit {
  background: #4CAF50;
  color: white;
}

/* 员工详情样式 */
.detail-item {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
}

.detail-item label {
  font-weight: 500;
  color: #666;
  margin-bottom: 5px;
}

.detail-item .value {
  padding: 5px 0;
}

.action-btn.view {
  background-color: #2196F3;
  color: white;
}
</style>
