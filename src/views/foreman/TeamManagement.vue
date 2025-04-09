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
                <td>{{ getLineName(emp.lineId) }}</td>
                <td>{{ emp.phone }}</td>
                <td>
                  <span :class="['status-tag', emp.status]">
                    {{ emp.statusText }}
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
        {
          id: 1,
          name: '一号生产线',
          status: 'running',
          statusText: '运行中',
          runningDevices: 8,
          totalDevices: 10,
          utilization: 85,
          assignedTo: 1 // 分配给当前工长的ID
        },
        {
          id: 2,
          name: '二号生产线',
          status: 'warning',
          statusText: '预警',
          runningDevices: 6,
          totalDevices: 8,
          utilization: 75,
          assignedTo: 1 // 分配给当前工长的ID
        }
      ],
      // 员工列表
      employees: [
        { 
          id: 'W001', 
          name: '张三', 
          lineId: 1,
          group_id: 'A', // 添加分组号示例
          phone: '13800138001', 
          status: 'active', 
          statusText: '在岗',
          skillLevel: '高级',
          joinDate: '2022-05-15',
          attendance: '24/26',
          completionRate: 98
        },
        { 
          id: 'W002', 
          name: '李四', 
          lineId: 1,
          group_id: 'B', // 添加分组号示例
          phone: '13800138002', 
          status: 'leave', 
          statusText: '请假',
          skillLevel: '中级',
          joinDate: '2022-08-20',
          attendance: '20/26',
          completionRate: 92
        },
        { 
          id: 'W003', 
          name: '王五', 
          lineId: 2,
          phone: '13800138003', 
          status: 'task', 
          statusText: '任务中',
          skillLevel: '高级',
          joinDate: '2022-03-10',
          attendance: '26/26',
          completionRate: 95
        },
        { 
          id: 'W004', 
          name: '赵六', 
          lineId: 2,
          group_id: 'C', // 添加分组号示例
          phone: '13800138004', 
          status: 'active', 
          statusText: '在岗',
          skillLevel: '初级',
          joinDate: '2023-01-05',
          attendance: '22/26',
          completionRate: 88
        }
      ],
      // 请假申请
      leaveRequests: [
        {
          employeeId: 'W002',
          employeeName: '李四',
          type: '病假',
          startDate: '2023-07-15',
          endDate: '2023-07-18',
          reason: '感冒发烧，需要休息',
          status: 'approved',
          statusText: '已批准'
        },
        {
          employeeId: 'W004',
          employeeName: '赵六',
          type: '事假',
          startDate: '2023-07-20',
          endDate: '2023-07-21',
          reason: '家中有事，需要请假处理',
          status: 'pending',
          statusText: '待审批'
        }
      ],
      filterLine: '',
      filterStatus: '',
      searchKeyword: '',
      showEmployeeDetail: false,
      showLeaveManagement: false,
      selectedEmployee: {}
    }
  },
  computed: {
    filteredEmployees() {
      return this.employees.filter(emp => {
        // 工长只能看到自己负责产线上的员工
        const lineMatch = !this.filterLine || emp.lineId === parseInt(this.filterLine);
        const statusMatch = !this.filterStatus || emp.status === this.filterStatus;
        const searchMatch = !this.searchKeyword || 
          emp.name.includes(this.searchKeyword) || 
          emp.id.includes(this.searchKeyword) ||
          (emp.group_id && emp.group_id.includes(this.searchKeyword)); // 添加分组号搜索
        return lineMatch && statusMatch && searchMatch;
      });
    }
  },
  methods: {
    // 获取产线名称
    getLineName(lineId) {
      const line = this.assignedLines.find(line => line.id === lineId);
      return line ? line.name : '未分配';
    },
    
    // 获取产线员工数量
    getLineWorkerCount(lineId) {
      return this.employees.filter(emp => emp.lineId === lineId).length;
    },
    
    // 获取产线在岗率
    getLineActiveRate(lineId) {
      const lineWorkers = this.employees.filter(emp => emp.lineId === lineId);
      if (lineWorkers.length === 0) return 0;
      
      const activeWorkers = lineWorkers.filter(emp => emp.status === 'active' || emp.status === 'task');
      return Math.round((activeWorkers.length / lineWorkers.length) * 100);
    },
    
    // 获取产线任务完成率
    getLineCompletionRate(lineId) {
      const lineWorkers = this.employees.filter(emp => emp.lineId === lineId);
      if (lineWorkers.length === 0) return 0;
      
      const totalRate = lineWorkers.reduce((sum, worker) => sum + (worker.completionRate || 0), 0);
      return Math.round(totalRate / lineWorkers.length);
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