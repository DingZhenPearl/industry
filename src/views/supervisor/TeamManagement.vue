<template>
  <div class="team">
    <header class="header">
      <h1>团队管理</h1>
    </header>
    
    <div class="content">
      <!-- 部门概览卡片 -->
      <div class="department-cards">
        <div class="dept-card" v-for="dept in departments" :key="dept.id">
          <div class="dept-header">
            <h3>{{ dept.name }}</h3>
            <span class="member-count">{{ dept.memberCount }}人</span>
          </div>
          <div class="dept-stats">
            <div class="stat-item">
              <span class="label">考勤率</span>
              <span class="value">{{ dept.attendance }}%</span>
            </div>
            <div class="stat-item">
              <span class="label">任务完成率</span>
              <span class="value">{{ dept.completion }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 员工列表 -->
      <div class="employee-section">
        <div class="section-header">
          <h3>员工管理</h3>
          <button class="add-btn" @click="showAddEmployee = true">
            <i class="plus-icon">+</i> 添加员工
          </button>
        </div>
        
        <div class="filter-bar">
          <select v-model="filterDepartment" class="filter-select">
            <option value="">全部部门</option>
            <option v-for="dept in departments" :key="dept.id" :value="dept.id">
              {{ dept.name }}
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
                <th>部门</th>
                <th>职位</th>
                <th>联系方式</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="emp in filteredEmployees" :key="emp.id">
                <td>{{ emp.id }}</td>
                <td>{{ emp.name }}</td>
                <td>{{ emp.department }}</td>
                <td>{{ emp.position }}</td>
                <td>{{ emp.phone }}</td>
                <td>
                  <span :class="['status-tag', emp.status]">
                    {{ emp.statusText }}
                  </span>
                </td>
                <td>
                  <button class="action-btn edit" @click="editEmployee(emp)">编辑</button>
                  <button class="action-btn delete" @click="deleteEmployee(emp)">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 添加/编辑员工模态框 -->
    <div class="modal" v-if="showAddEmployee">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingEmployee ? '编辑员工' : '添加员工' }}</h3>
          <span class="close-btn" @click="closeModal">&times;</span>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>工号</label>
            <input type="text" v-model="employeeForm.id" class="form-input">
          </div>
          <div class="form-group">
            <label>姓名</label>
            <input type="text" v-model="employeeForm.name" class="form-input">
          </div>
          <div class="form-group">
            <label>部门</label>
            <select v-model="employeeForm.department" class="form-input">
              <option v-for="dept in departments" :key="dept.id" :value="dept.name">
                {{ dept.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>职位</label>
            <input type="text" v-model="employeeForm.position" class="form-input">
          </div>
          <div class="form-group">
            <label>联系方式</label>
            <input type="text" v-model="employeeForm.phone" class="form-input">
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeModal">取消</button>
          <button class="btn submit" @click="saveEmployee">保存</button>
        </div>
      </div>
    </div>

    <SupervisorNav />
  </div>
</template>

<script>
import SupervisorNav from '@/components/SupervisorNav.vue'

export default {
  name: 'TeamManagement',
  components: {
    SupervisorNav
  },
  data() {
    return {
      departments: [
        { id: 1, name: '生产部', memberCount: 45, attendance: 98, completion: 95 },
        { id: 2, name: '质检部', memberCount: 20, attendance: 96, completion: 92 },
        { id: 3, name: '设备部', memberCount: 15, attendance: 97, completion: 94 }
      ],
      employees: [
        { id: 'EMP001', name: '张三', department: '生产部', position: '生产主管', phone: '13800138000', status: 'active', statusText: '在职' },
        { id: 'EMP002', name: '李四', department: '质检部', position: '质检员', phone: '13800138001', status: 'active', statusText: '在职' },
        { id: 'EMP003', name: '王五', department: '设备部', position: '设备工程师', phone: '13800138002', status: 'leave', statusText: '请假' }
      ],
      filterDepartment: '',
      searchKeyword: '',
      showAddEmployee: false,
      editingEmployee: null,
      employeeForm: {
        id: '',
        name: '',
        department: '',
        position: '',
        phone: ''
      }
    }
  },
  computed: {
    filteredEmployees() {
      return this.employees.filter(emp => {
        const departmentMatch = !this.filterDepartment || emp.department === this.filterDepartment;
        const searchMatch = !this.searchKeyword || 
          emp.name.includes(this.searchKeyword) || 
          emp.id.includes(this.searchKeyword);
        return departmentMatch && searchMatch;
      });
    }
  },
  methods: {
    editEmployee(employee) {
      this.editingEmployee = employee;
      this.employeeForm = { ...employee };
      this.showAddEmployee = true;
    },
    deleteEmployee(employee) {
      if (confirm('确定要删除该员工吗？')) {
        this.employees = this.employees.filter(emp => emp.id !== employee.id);
      }
    },
    closeModal() {
      this.showAddEmployee = false;
      this.editingEmployee = null;
      this.employeeForm = {
        id: '',
        name: '',
        department: '',
        position: '',
        phone: ''
      };
    },
    saveEmployee() {
      if (this.editingEmployee) {
        const index = this.employees.findIndex(emp => emp.id === this.editingEmployee.id);
        if (index !== -1) {
          this.employees[index] = { 
            ...this.employeeForm,
            status: 'active',
            statusText: '在职'
          };
        }
      } else {
        this.employees.push({ 
          ...this.employeeForm,
          status: 'active',
          statusText: '在职'
        });
      }
      this.closeModal();
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
  grid-template-columns: repeat(2, 1fr);
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

.add-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
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

.status-tag.active {
  background: #e8f5e9;
  color: #4CAF50;
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

.action-btn.delete {
  background: #f44336;
  color: white;
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
</style>
