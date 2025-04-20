<template>
  <div class="employee-status-list">
    <div class="list-header">
      <h3>{{ title }}</h3>
      <div class="filter-controls">
        <select v-model="statusFilter" class="status-filter" @change="filterEmployees">
          <option value="">全部状态</option>
          <option value="在岗">在岗</option>
          <option value="请假">请假</option>
          <option value="离岗">离岗</option>
        </select>
      </div>
    </div>

    <div class="list-body">
      <div v-if="loading" class="loading-state">
        加载中...
      </div>

      <div v-else-if="filteredEmployees.length === 0" class="empty-state">
        暂无员工数据
      </div>

      <div v-else class="employee-table">
        <table>
          <thead>
            <tr>
              <th>工号</th>
              <th>姓名</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="employee in filteredEmployees" :key="employee.id">
              <td>{{ employee.id }}</td>
              <td>{{ employee.name }}</td>
              <td>
                <span class="status-tag" :class="getStatusClass(employee.status)">
                  {{ getStatusText(employee.status) }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button
                    v-if="canUpdateStatus"
                    class="update-btn"
                    @click="showUpdateStatusModal(employee)"
                  >
                    修改状态
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 修改状态模态框 -->
    <div v-if="showModal" class="status-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>修改员工状态</h3>
          <span class="close-btn" @click="showModal = false">&times;</span>
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
                {{ getStatusText(selectedEmployee.status) }}
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
          <button class="cancel-btn" @click="showModal = false">取消</button>
          <button
            class="confirm-btn"
            :disabled="!newStatus || modalLoading"
            @click="updateEmployeeStatus"
          >
            {{ modalLoading ? '更新中...' : '确认更新' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EmployeeStatusList',
  props: {
    employees: {
      type: Array,
      required: true
    },
    title: {
      type: String,
      default: '员工状态'
    },
    loading: {
      type: Boolean,
      default: false
    },
    canUpdateStatus: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      statusFilter: '',
      filteredEmployees: [],
      showModal: false,
      selectedEmployee: {},
      newStatus: '',
      modalLoading: false
    };
  },
  watch: {
    employees: {
      immediate: true,
      handler() {
        this.filterEmployees();
      }
    }
  },
  methods: {
    filterEmployees() {
      if (!this.statusFilter) {
        this.filteredEmployees = [...this.employees];
      } else {
        this.filteredEmployees = this.employees.filter(
          employee => employee.status === this.statusFilter
        );
      }
    },
    getStatusClass(status) {
      switch (status) {
        case '在岗': return 'status-active';
        case '请假': return 'status-leave';
        case '离岗': return 'status-off';
        default: return '';
      }
    },
    getStatusText(status) {
      // 状态值已经是中文，直接返回
      return status || '未知';
    },
    showUpdateStatusModal(employee) {
      this.selectedEmployee = { ...employee };
      this.newStatus = '';
      this.showModal = true;
    },
    async updateEmployeeStatus() {
      if (!this.newStatus || this.modalLoading) return;

      this.modalLoading = true;

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
          this.showModal = false;

          // 更新本地数据
          const index = this.employees.findIndex(emp => emp.id === this.selectedEmployee.id);
          if (index !== -1) {
            this.$set(this.employees[index], 'status', this.newStatus);
            this.filterEmployees();
          }

          // 通知父组件
          this.$emit('status-updated');
        } else {
          alert(`更新员工状态失败: ${result.error}`);
        }
      } catch (error) {
        console.error('更新员工状态出错:', error);
        alert('更新员工状态失败，请重试');
      } finally {
        this.modalLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.employee-status-list {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.list-header h3 {
  margin: 0;
  color: #333;
}

.status-filter {
  padding: 6px 10px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.loading-state, .empty-state {
  padding: 30px 0;
  text-align: center;
  color: #999;
}

.employee-table {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background-color: #fafafa;
  font-weight: 600;
  color: #333;
}

tr:hover {
  background-color: #fafafa;
}

.status-tag {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
}

.status-active {
  background-color: #f6ffed;
  color: #52c41a;
}

.status-leave {
  background-color: #fff7e6;
  color: #fa8c16;
}

.status-off {
  background-color: #f5f5f5;
  color: #666;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.update-btn {
  padding: 4px 10px;
  background-color: #e6f7ff;
  color: #1890ff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.update-btn:hover {
  background-color: #1890ff;
  color: white;
}

/* 模态框样式 */
.status-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  font-size: 24px;
  color: #999;
  cursor: pointer;
}

.close-btn:hover {
  color: #666;
}

.modal-body {
  padding: 20px;
}

.employee-info {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #fafafa;
  border-radius: 6px;
}

.info-item {
  display: flex;
  margin-bottom: 10px;
}

.info-item label {
  width: 80px;
  font-weight: 500;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  padding: 15px 20px;
  border-top: 1px solid #eee;
}

.cancel-btn, .confirm-btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.cancel-btn {
  background-color: #f5f5f5;
  color: #333;
}

.cancel-btn:hover {
  background-color: #e8e8e8;
}

.confirm-btn {
  background-color: #1890ff;
  color: white;
}

.confirm-btn:hover:not(:disabled) {
  background-color: #40a9ff;
}

.confirm-btn:disabled {
  background-color: #f5f5f5;
  color: #d9d9d9;
  cursor: not-allowed;
}
</style>
