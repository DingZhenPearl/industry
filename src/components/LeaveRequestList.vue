<template>
  <div class="leave-request-list">
    <div class="list-header">
      <h3>请假记录</h3>
      <div class="filter-controls">
        <select v-model="statusFilter" class="status-filter" @change="fetchLeaveRequests">
          <option value="">全部状态</option>
          <option value="待审批">待审批</option>
          <option value="已批准">已批准</option>
          <option value="已拒绝">已拒绝</option>
          <option value="已取消">已取消</option>
        </select>
      </div>
    </div>
    
    <div class="list-body">
      <div v-if="loading" class="loading-state">
        加载中...
      </div>
      
      <div v-else-if="leaveRequests.length === 0" class="empty-state">
        暂无请假记录
      </div>
      
      <div v-else class="leave-items">
        <div v-for="leave in leaveRequests" :key="leave.id" class="leave-item">
          <div class="leave-header">
            <div class="leave-type" :class="getLeaveTypeClass(leave.leave_type)">
              {{ leave.leave_type }}
            </div>
            <div class="leave-status" :class="getStatusClass(leave.status)">
              {{ leave.status }}
            </div>
          </div>
          
          <div class="leave-dates">
            <div class="date-range">
              {{ leave.start_date }} 至 {{ leave.end_date }}
            </div>
            <div class="date-count">
              共 {{ calculateDays(leave.start_date, leave.end_date) }} 天
            </div>
          </div>
          
          <div class="leave-reason">
            <div class="reason-label">请假原因：</div>
            <div class="reason-content">{{ leave.reason || '无' }}</div>
          </div>
          
          <div class="leave-footer">
            <div class="leave-time">
              申请时间：{{ formatDateTime(leave.created_at) }}
            </div>
            
            <div class="leave-actions" v-if="leave.status === '待审批'">
              <button class="cancel-btn" @click="cancelLeaveRequest(leave.id)">
                取消申请
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LeaveRequestList',
  props: {
    employeeId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      leaveRequests: [],
      statusFilter: '',
      loading: false
    };
  },
  methods: {
    async fetchLeaveRequests() {
      this.loading = true;
      
      try {
        let url = `/api/attendance/leave-records/${this.employeeId}`;
        if (this.statusFilter) {
          url += `?status=${encodeURIComponent(this.statusFilter)}`;
        }
        
        const response = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (!response.ok) {
          throw new Error(`获取请假记录失败: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success && result.data) {
          this.leaveRequests = result.data;
        } else {
          console.error('获取请假记录失败:', result.error);
        }
      } catch (error) {
        console.error('获取请假记录出错:', error);
      } finally {
        this.loading = false;
      }
    },
    async cancelLeaveRequest(leaveId) {
      if (!confirm('确定要取消这个请假申请吗？')) {
        return;
      }
      
      try {
        const response = await fetch('/api/attendance/cancel-leave', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            leave_id: leaveId,
            employee_id: this.employeeId
          })
        });
        
        const result = await response.json();
        
        if (result.success) {
          alert('请假申请已取消');
          this.fetchLeaveRequests();
        } else {
          alert(`取消请假申请失败: ${result.error}`);
        }
      } catch (error) {
        console.error('取消请假申请出错:', error);
        alert('取消请假申请失败，请重试');
      }
    },
    getLeaveTypeClass(type) {
      switch (type) {
        case '事假': return 'type-personal';
        case '病假': return 'type-sick';
        case '年假': return 'type-annual';
        default: return 'type-other';
      }
    },
    getStatusClass(status) {
      switch (status) {
        case '待审批': return 'status-pending';
        case '已批准': return 'status-approved';
        case '已拒绝': return 'status-rejected';
        case '已取消': return 'status-cancelled';
        default: return '';
      }
    },
    calculateDays(startDate, endDate) {
      if (!startDate || !endDate) return 0;
      
      const start = new Date(startDate);
      const end = new Date(endDate);
      const diffTime = Math.abs(end - start);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
      
      return diffDays;
    },
    formatDateTime(dateTimeString) {
      if (!dateTimeString) return '';
      
      const date = new Date(dateTimeString);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      });
    }
  },
  mounted() {
    this.fetchLeaveRequests();
  }
};
</script>

<style scoped>
.leave-request-list {
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

.leave-items {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.leave-item {
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 15px;
  transition: all 0.3s;
}

.leave-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.leave-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.leave-type, .leave-status {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
}

.type-personal {
  background-color: #e6f7ff;
  color: #1890ff;
}

.type-sick {
  background-color: #fff2e8;
  color: #fa541c;
}

.type-annual {
  background-color: #f6ffed;
  color: #52c41a;
}

.type-other {
  background-color: #f9f0ff;
  color: #722ed1;
}

.status-pending {
  background-color: #fff7e6;
  color: #fa8c16;
}

.status-approved {
  background-color: #f6ffed;
  color: #52c41a;
}

.status-rejected {
  background-color: #fff1f0;
  color: #f5222d;
}

.status-cancelled {
  background-color: #f5f5f5;
  color: #666;
}

.leave-dates {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.date-range {
  font-weight: 500;
}

.date-count {
  color: #666;
}

.leave-reason {
  margin-bottom: 15px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.reason-label {
  font-weight: 500;
  margin-bottom: 5px;
}

.leave-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #999;
}

.leave-actions {
  display: flex;
  gap: 10px;
}

.cancel-btn {
  padding: 4px 10px;
  background-color: #f5f5f5;
  color: #666;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.cancel-btn:hover {
  background-color: #fafafa;
  color: #f5222d;
}
</style>
