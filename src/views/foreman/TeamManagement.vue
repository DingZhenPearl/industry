<template>
  <div class="team">
    <header class="header">
      <h1>团队管理</h1>
    </header>

    <div class="content">
      <!-- 产线员工概览卡片 -->
      <div class="authority-notice">
        <i class="info-icon"></i>
        <span>您有权管理 <strong>{{ assignedLines.length }}</strong> 条产线上的员工</span>
      </div>

      <!-- 产线员工统计卡片 -->
      <div class="department-cards">
        <div class="dept-card" v-for="line in assignedLines" :key="line.id">
          <div class="dept-header">
            <h3>{{ line.name }}</h3>
            <span class="member-count">{{ getLineWorkerCount(line.id) }}人</span>
          </div>
          <div class="dept-stats">
            <div class="stat-item">
              <span class="label">在岗率</span>
              <span class="value">{{ getLineActiveRate(line.id) }}%</span>
            </div>
            <div class="stat-item">
              <span class="label">任务完成率</span>
              <span class="value">{{ getLineCompletionRate(line.id) }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 员工列表 -->
      <div class="employee-section">
        <div class="section-header">
          <h3>员工管理</h3>
          <button class="view-btn" @click="showLeaveManagement = true">
            <i class="calendar-icon"></i> 请假管理
          </button>
        </div>

        <div class="filter-bar">
          <select v-model="filterLine" class="filter-select">
            <option value="">全部产线</option>
            <option v-for="line in assignedLines" :key="line.id" :value="line.id">
              {{ line.name }}
            </option>
          </select>
          <select v-model="filterStatus" class="filter-select">
            <option value="">全部状态</option>
            <option value="active">在岗</option>
            <option value="leave">请假</option>
            <option value="task">任务中</option>
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
                <th>所属产线</th>
                <th>所属机器</th>
                <th>联系方式</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="emp in filteredEmployees" :key="emp.id" :class="{ 'current-foreman': emp.id === currentForeman.id }">
                <td>{{ emp.id }}</td>
                <td>{{ emp.name }}</td>
                <td>{{ emp.group_id || '未分组' }}</td>
                <td>{{ getLineName(emp.line_id) }}</td>
                <td>{{ emp.machine_id || '未分配' }}</td>
                <td>{{ emp.phone }}</td>
                <td>
                  <span :class="['status-tag', emp.status]">
                    {{ getRoleName(emp.role) }} - {{ getStatusText(emp) }}
                  </span>
                </td>
                <td>
                  <button class="action-btn view" @click="viewEmployeeDetail(emp)">详情</button>
                </td>
              </tr>
            </tbody>
          </table>
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
            <label>所属产线</label>
            <div class="value">{{ getLineName(selectedEmployee.lineId) }}</div>
          </div>
          <div class="detail-item">
            <label>所属机器</label>
            <div class="value">{{ selectedEmployee.machine_id || '未分配' }}</div>
          </div>
          <div class="detail-item">
            <label>联系方式</label>
            <div class="value">{{ selectedEmployee.phone }}</div>
          </div>
          <div class="detail-item">
            <label>状态</label>
            <div class="value">
              <span :class="['status-tag', selectedEmployee.status]">
                {{ selectedEmployee.statusText }}
              </span>
            </div>
          </div>
          <div class="detail-item">
            <label>技能等级</label>
            <div class="value">{{ selectedEmployee.skillLevel || '初级' }}</div>
          </div>
          <div class="detail-item">
            <label>入职时间</label>
            <div class="value">{{ selectedEmployee.joinDate || '2023-01-01' }}</div>
          </div>
          <div class="detail-item">
            <label>本月出勤</label>
            <div class="value">{{ selectedEmployee.attendance || '22/26' }}天</div>
          </div>
          <div class="detail-item">
            <label>任务完成率</label>
            <div class="value">{{ selectedEmployee.completionRate || '95' }}%</div>
          </div>
        </div>
      </div>
    </div>



    <!-- 请假管理模态框 -->
    <div class="modal" v-if="showLeaveManagement">
      <div class="modal-content">
        <div class="modal-header">
          <h3>请假管理</h3>
          <span class="close-btn" @click="showLeaveManagement = false">&times;</span>
        </div>
        <div class="modal-body">
          <div class="leave-list">
            <div class="leave-item" v-for="(leave, index) in leaveRequests" :key="index">
              <div class="leave-header">
                <span class="employee-name">{{ leave.employeeName }}</span>
                <span :class="['status-tag', leave.status]">{{ leave.statusText }}</span>
              </div>
              <div class="leave-details">
                <div class="leave-type">{{ leave.type }}</div>
                <div class="leave-period">{{ leave.startDate }} 至 {{ leave.endDate }}</div>
                <div class="leave-reason">{{ leave.reason }}</div>
              </div>
              <div class="leave-actions" v-if="leave.status === 'pending'">
                <button class="action-btn approve" @click="approveLeave(index)">批准</button>
                <button class="action-btn reject" @click="rejectLeave(index)">拒绝</button>
              </div>
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
  name: 'TeamManagement',
  components: {
    ForemanNav
  },
  data() {
    return {
      // 工长被分配的产线
      assignedLines: [


      ],
      employees: [], // 清空本地数据
      leaveRequests: [

      ],
      filterLine: '',
      filterStatus: '',
      searchKeyword: '',
      showEmployeeDetail: false,
      showLeaveManagement: false,
      selectedEmployee: {},
      currentForeman: null // 存储当前工长信息
    }
  },
  async created() {
    // 获取当前工长信息,并打印完整的用户信息用于调试
    const userInfoStr = localStorage.getItem('userInfo') || '{}';
    console.log('localStorage中的userInfo:', userInfoStr);

    const userInfo = JSON.parse(userInfoStr);
    console.log('解析后的用户信息:', userInfo);

    this.currentForeman = {
      id: userInfo.employee_id,
      name: userInfo.username,
      role: userInfo.role,
      group_id: userInfo.group_id || 99
    };

    console.log('当前工长信息:', this.currentForeman);

    await this.fetchAssignedLines(); // 先获取产线信息
    await this.fetchEmployees();
  },
  computed: {
    filteredEmployees() {
      if (!this.currentForeman || !this.currentForeman.group_id) {
        console.log('当前工长组号未知');
        return [];
      }

      return this.employees.filter(emp => {
        // 首先检查组号是否匹配
        const groupMatch = Number(emp.group_id) === Number(this.currentForeman.group_id);
        if (!groupMatch) {
          console.log(`组号不匹配: ${emp.name}, 组号:${emp.group_id} vs ${this.currentForeman.group_id}`);
          return false;
        }

        // 然后应用其他筛选条件
        const lineMatch = !this.filterLine || emp.line_id === this.filterLine;
        const statusMatch = !this.filterStatus || emp.status === this.filterStatus;
        const searchMatch = !this.searchKeyword ||
          emp.name.includes(this.searchKeyword) ||
          emp.id.includes(this.searchKeyword);

        return lineMatch && statusMatch && searchMatch;
      });
    },

    // 修改产线员工数量统计方法
    getLineWorkerCount() {
      return (lineId) => {
        return this.employees.filter(emp =>
          emp.line_id === lineId &&
          emp.group_id === this.currentForeman.group_id
        ).length;
      };
    },

    // 修改产线在岗率统计方法
    getLineActiveRate() {
      return (lineId) => {
        const lineWorkers = this.employees.filter(emp =>
          emp.line_id === lineId &&
          emp.group_id === this.currentForeman.group_id
        );
        if (lineWorkers.length === 0) return 0;

        const activeWorkers = lineWorkers.filter(emp =>
          emp.status === 'active' || emp.status === 'task'
        );
        return Math.round((activeWorkers.length / lineWorkers.length) * 100);
      };
    },

    // 修改产线任务完成率统计方法
    getLineCompletionRate() {
      return (lineId) => {
        const lineWorkers = this.employees.filter(emp =>
          emp.line_id === lineId &&
          emp.group_id === this.currentForeman.group_id
        );
        if (lineWorkers.length === 0) return 0;

        const totalRate = lineWorkers.reduce((sum, worker) =>
          sum + (worker.completionRate || 0), 0
        );
        return Math.round(totalRate / lineWorkers.length);
      };
    }
  },
  methods: {
    // 获取分配给当前工长的产线信息
    async fetchAssignedLines() {
      try {
        if (!this.currentForeman || !this.currentForeman.group_id) {
          console.log('当前工长组号未知，无法获取产线信息');
          return;
        }

        console.log('开始获取产线数据,工长组号:', this.currentForeman.group_id);
        const response = await fetch(`/api/foreman/assigned-lines?group_id=${this.currentForeman.group_id}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('产线返回数据:', data);

        if (data.success && Array.isArray(data.data)) {
          console.log('原始产线数据:');
          data.data.forEach(line => {
            console.log(`产线 ID: ${line.id}, 名称: ${line.name}, 类型: ${typeof line.id}`);
          });

          this.assignedLines = data.data.map(line => ({
            ...line // 保持原始数据格式
          }));

          console.log('处理后的产线数据:');
          this.assignedLines.forEach(line => {
            console.log(`产线 ID: ${line.id}, 名称: ${line.name}, 类型: ${typeof line.id}`);
          });
        } else {
          throw new Error(data.error || '产线数据格式错误');
        }
      } catch (error) {
        console.error('获取产线列表出错:', error);
      }
    },

    async fetchEmployees() {
      try {
        console.log('开始获取员工数据,工长组号:', this.currentForeman.group_id);
        const response = await fetch(`/api/foreman/team-members?group_id=${this.currentForeman.group_id}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('原始返回数据:', data);

        if (data.success && Array.isArray(data.data)) {
          // 打印原始员工数据中的line_id字段
          console.log('员工原始数据中的line_id字段:');
          data.data.forEach(emp => {
            console.log(`员工 ${emp.name} 的line_id: ${emp.line_id}, 类型: ${typeof emp.line_id}`);
          });

          // 处理员工数据,确保所有需要的字段都存在
          this.employees = data.data.map(emp => {
            return {
              ...emp,
              line_id: emp.line_id || '1', // 如果没有line_id,默认设为1
              status: emp.status || 'active',
              statusText: emp.statusText || this.getStatusText(emp),
              skillLevel: emp.skillLevel || '初级', // 添加默认技能等级
              completionRate: emp.completionRate || Math.floor(Math.random() * 30) + 70 // 添加默认完成率
            };
          });

          // 打印处理后的员工数据
          console.log('处理后的员工数据:');
          this.employees.forEach(emp => {
            console.log(`员工 ${emp.name} 的line_id: ${emp.line_id}, 类型: ${typeof emp.line_id}`);
          });
        } else {
          throw new Error(data.error || '数据格式错误');
        }
      } catch (error) {
        console.error('获取员工列表出错:', error);
      }
    },

    // 获取角色名称显示
    getRoleName(role) {
      const roleMap = {
        'supervisor': '厂长',
        'foreman': '工长',
        'member': '产线工人',
        'safety_officer': '安全员'
      };
      return roleMap[role] || role;
    },

    // 获取状态显示文本
    getStatusText(emp) {
      // 如果是安全员
      if (emp.role === 'safety_officer') {
        return '安全员';
      }

      // 如果是工长
      if (emp.role === 'foreman') {
        // 如果是当前工长
        if (emp.id === this.currentForeman.id) {
          return '当前工长';
        }
        return '同组工长';
      }

      const statusMap = {
        'active': '在岗',
        'leave': '请假',
        'task': '任务中',
        'off': '离岗'
      };
      return statusMap[emp.status] || '未知';
    },

    // 获取产线名称
    getLineName(lineId) {
      console.log(`尝试获取产线名称, 产线 ID: ${lineId}, 类型: ${typeof lineId}`);
      console.log('可用的产线列表:', this.assignedLines);

      const line = this.assignedLines.find(line => line.id === lineId);

      if (line) {
        console.log(`找到产线: ${line.name}`);
        return line.name;
      } else {
        console.log('未找到产线, 返回默认值: 未分配');
        return '未分配';
      }
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

    // 批准请假
    approveLeave(index) {
      this.leaveRequests[index].status = 'approved';
      this.leaveRequests[index].statusText = '已批准';

      // 更新员工状态
      const employeeId = this.leaveRequests[index].employeeId;
      const empIndex = this.employees.findIndex(emp => emp.id === employeeId);
      if (empIndex !== -1) {
        this.employees[empIndex].status = 'leave';
        this.employees[empIndex].statusText = '请假';
      }
    },

    // 拒绝请假
    rejectLeave(index) {
      this.leaveRequests[index].status = 'rejected';
      this.leaveRequests[index].statusText = '已拒绝';
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
  background-color: #f4f4f4;
}

.authority-notice {
  background-color: #e3f2fd;
  border-left: 4px solid #2196F3;
  padding: 10px 15px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  border-radius: 4px;
}

.info-icon {
  width: 20px;
  height: 20px;
  background-color: #2196F3;
  border-radius: 50%;
  margin-right: 10px;
  position: relative;
}

.info-icon::after {
  content: 'i';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-style: italic;
  font-weight: bold;
}

.department-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.dept-card {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dept-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.dept-header h3 {
  margin: 0;
  font-size: 1.1em;
}

.member-count {
  background-color: #e3f2fd;
  color: #2196F3;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.9em;
}

.dept-stats {
  display: flex;
  justify-content: space-between;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.label {
  font-size: 0.8em;
  color: #666;
  margin-bottom: 5px;
}

.value {
  font-weight: bold;
  color: #333;
}

.employee-section {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h3 {
  margin: 0;
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

.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.filter-select, .search-input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  flex: 1;
}

.employee-list table {
  width: 100%;
  border-collapse: collapse;
}

.employee-list th, .employee-list td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.employee-list th {
  background-color: #f9f9f9;
  font-weight: 600;
}

.status-tag {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.8em;
}

.status-tag.active {
  background-color: #e8f5e9;
  color: #4CAF50;
}

.status-tag.leave {
  background-color: #fff8e1;
  color: #FFC107;
}

.status-tag.task {
  background-color: #e3f2fd;
  color: #2196F3;
}

.status-tag.pending {
  background-color: #f5f5f5;
  color: #9e9e9e;
}

.status-tag.approved {
  background-color: #e8f5e9;
  color: #4CAF50;
}

.status-tag.rejected {
  background-color: #ffebee;
  color: #f44336;
}

.action-btn {
  border: none;
  border-radius: 4px;
  padding: 5px 10px;
  margin-right: 5px;
  cursor: pointer;
  font-size: 0.8em;
}

.action-btn.view {
  background-color: #e3f2fd;
  color: #2196F3;
}

.action-btn.assign {
  background-color: #e8f5e9;
  color: #4CAF50;
}

.action-btn.approve {
  background-color: #e8f5e9;
  color: #4CAF50;
}

.action-btn.reject {
  background-color: #ffebee;
  color: #f44336;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
}

.close-btn {
  font-size: 1.5em;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 15px;
}

.modal-footer {
  padding: 15px;
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
  font-weight: 600;
}

.form-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn.cancel {
  background-color: #f5f5f5;
  color: #333;
}

.btn.submit {
  background-color: #2196F3;
  color: white;
}

.detail-item {
  margin-bottom: 15px;
}

.detail-item label {
  display: block;
  font-size: 0.9em;
  color: #666;
  margin-bottom: 5px;
}

.detail-item .value {
  font-weight: 500;
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

/* 当前工长行样式 */
.current-foreman {
  background-color: rgba(33, 150, 243, 0.1);
  font-weight: bold;
}

.current-foreman td {
  position: relative;
}

.current-foreman td:first-child::before {
  content: '(您)';
  color: #2196F3;
  font-size: 0.8em;
  margin-right: 5px;
}

.employee-name {
  font-weight: bold;
}

.leave-details {
  margin-bottom: 15px;
}

.leave-type {
  font-weight: 500;
  margin-bottom: 5px;
}

.leave-period {
  color: #666;
  margin-bottom: 5px;
}

.leave-reason {
  font-style: italic;
  color: #666;
}

.leave-actions {
  display: flex;
  gap: 10px;
}
</style>
