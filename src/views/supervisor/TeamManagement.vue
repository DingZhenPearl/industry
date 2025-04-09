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
            <div class="stat-item">
              <span class="label">任务完成率</span>
              <span class="value">{{ role.completion }}%</span>
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
          <!-- 添加组号输入字段 -->
          <div class="form-group">
            <label>组号</label>
            <input type="text" v-model="employeeForm.group_id" class="form-input" placeholder="请输入组号">
          </div>
          <div class="form-group">
            <label>角色</label>
            <select v-model="employeeForm.role" class="form-input">
              <option value="">请选择角色</option>
              <option v-for="role in roles" :key="role.id" :value="role.id">
                {{ role.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>部门</label>
            <input type="text" v-model="employeeForm.department" class="form-input">
          </div>
          <div class="form-group">
            <label>联系方式</label>
            <input type="text" v-model="employeeForm.phone" class="form-input">
          </div>
          <div class="form-group">
            <label>状态</label>
            <select v-model="employeeForm.status" class="form-input">
              <option v-for="option in statusOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
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
      roles: [
        { 
          id: 'supervisor', 
          name: '厂长', 
          memberCount: 1, 
          activeRate: 100, 
          completion: 95 
        },
        { 
          id: 'foreman', 
          name: '工长', 
          memberCount: 4, 
          activeRate: 100, 
          completion: 92 
        },
        { 
          id: 'member',  // 修改这里，从 'worker' 改为 'member'
          name: '产线工人', 
          memberCount: 45, 
          activeRate: 95, 
          completion: 90 
        },
        { 
          id: 'safety_officer',  // 修改这里，从 'safety' 改为 'safety_officer'
          name: '安全员', 
          memberCount: 3, 
          activeRate: 100, 
          completion: 94 
        }
      ],
      employees: [], // 清空本地数据,改为从后端获取
      filterRole: '',
      filterGroup: '', // 添加组号筛选数据
      searchKeyword: '',
      showAddEmployee: false,
      editingEmployee: null,
      employeeForm: {
        id: '',
        name: '', 
        role: '',
        group_id: '', // 添加组号字段
        phone: '',
        status: 'active',
        statusText: '在职'
      }
    }
  },
  created() {
    // 组件创建时获取用户列表
    this.fetchEmployees()
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
        
        if (data.success) {
          // 处理返回的数据,添加角色名称显示
          this.employees = data.data.map(user => ({
            ...user,
            roleName: this.getRoleName(user.role)
          }));
        } else {
          console.error('获取用户列表失败:', data.error);
        }
      } catch (error) {
        console.error('请求用户列表出错:', error);
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
    async saveEmployee() {
      try {
        // 如果是编辑现有员工
        if (this.editingEmployee) {
          // 更新组号
          if (this.employeeForm.group_id !== this.editingEmployee.group_id) {
            const response = await fetch('/api/update-group', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
              },
              body: JSON.stringify({
                username: this.editingEmployee.name, // 使用原始用户名
                role: this.editingEmployee.role,    // 使用原始角色
                group_id: this.employeeForm.group_id
              })
            });
            
            const data = await response.json();
            if (data.success) {
              // 更新本地数据
              const index = this.employees.findIndex(emp => emp.id === this.editingEmployee.id);
              if (index !== -1) {
                this.employees[index] = {
                  ...this.employees[index],
                  group_id: this.employeeForm.group_id
                };
              }
            } else {
              this.$message.error(data.error || '更新组号失败');
              return;
            }
          }
        }
        
        // ...existing code for other employee updates...
        
        this.closeModal();
        // 重新获取最新的员工列表
        await this.fetchEmployees();
        
      } catch (error) {
        console.error('保存员工信息时出错:', error);
        this.$message.error('保存失败，请重试');
      }
    },
    editEmployee(employee) {
      this.editingEmployee = { ...employee }; // 保存完整的原始员工信息
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
        role: '',
        group_id: '', // 重置组号字段
        department: '',
        phone: '',
        status: 'active',
        statusText: '在职'
      };
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
