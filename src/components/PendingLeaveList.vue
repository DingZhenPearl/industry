<template>
  <div class="pending-leave-list">
    <div class="list-header">
      <h3>待审批请假申请</h3>
      <div v-if="isManager" class="header-subtitle">厂长可以审批所有身份的请假申请</div>
    </div>

    <div class="list-body">
      <div v-if="loading" class="loading-state">
        加载中...
      </div>

      <div v-else-if="pendingLeaves.length === 0" class="empty-state">
        暂无待审批的请假申请
      </div>

      <div v-else class="leave-items">
        <div v-for="leave in pendingLeaves" :key="leave.id" class="leave-item">
          <div class="leave-header">
            <div class="employee-info">
              <span class="employee-name">{{ leave.employee_name }}</span>
              <span class="employee-id">({{ leave.employee_id }})</span>
            </div>
            <div class="leave-type" :class="getLeaveTypeClass(leave.leave_type)">
              {{ leave.leave_type }}
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

            <div class="approval-actions">
              <div class="approval-notes">
                <input
                  type="text"
                  v-model="approvalNotes[leave.id]"
                  placeholder="审批备注（可选）"
                  class="notes-input"
                />
              </div>
              <div class="action-buttons">
                <button
                  class="reject-btn"
                  @click="rejectLeave(leave.id)"
                  :disabled="actionLoading[leave.id]"
                >
                  拒绝
                </button>
                <button
                  class="approve-btn"
                  @click="approveLeave(leave.id)"
                  :disabled="actionLoading[leave.id]"
                >
                  批准
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PendingLeaveList',
  props: {
    approverId: {
      type: String,
      required: true
    },
    groupId: {
      type: [String, Number],
      default: null
    },
    isManager: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      pendingLeaves: [],
      approvalNotes: {},
      actionLoading: {},
      loading: false
    };
  },
  methods: {
    async fetchPendingLeaves() {
      this.loading = true;

      try {
        let url = '/api/attendance/pending-leaves';

        // 如果是厂长，获取所有请假申请，不过滤组号
        if (this.isManager) {
          url += '?all=true'; // 添加参数标记这是厂长的请求，获取所有请假
        }
        // 如果是工长或安全员，只获取其组内的请假申请，但不包括自己的请假申请
        else if (this.groupId && this.groupId.toString().trim()) {
          url += `?group_id=${this.groupId}`;

          // 添加审批人ID，排除审批人自己的请假申请
          if (this.approverId && this.approverId.toString().trim()) {
            url += `&approver_id=${this.approverId}`;
          }
        }

        console.log('请求URL:', url); // 调试日志

        const response = await fetch(url, {
          credentials: 'include' // 确保发送会话 cookie
        });

        if (!response.ok) {
          throw new Error(`获取待审批请假申请失败: ${response.status}`);
        }

        const result = await response.json();
        console.log('请求结果:', result); // 调试日志

        if (result.success) {
          this.pendingLeaves = result.data || [];

          // 初始化审批备注和加载状态
          this.pendingLeaves.forEach(leave => {
            if (!this.approvalNotes[leave.id]) {
              this.$set(this.approvalNotes, leave.id, '');
            }
            if (!this.actionLoading[leave.id]) {
              this.$set(this.actionLoading, leave.id, false);
            }
          });
        } else {
          console.error('获取待审批请假申请失败:', result.error);
        }
      } catch (error) {
        console.error('获取待审批请假申请出错:', error);
      } finally {
        this.loading = false;
      }
    },
    async approveLeave(leaveId) {
      if (this.actionLoading[leaveId]) return;

      this.$set(this.actionLoading, leaveId, true);

      try {
        const response = await fetch('/api/attendance/approve-leave', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include', // 确保发送会话 cookie
          body: JSON.stringify({
            leave_id: leaveId,
            approver_id: this.approverId,
            notes: this.approvalNotes[leaveId] || ''
          })
        });

        const result = await response.json();

        if (result.success) {
          alert('请假申请已批准');

          // 触发事件，通知父组件
          const approvedLeave = this.pendingLeaves.find(leave => leave.id === leaveId);
          if (approvedLeave) {
            this.$emit('leave-approved', approvedLeave);
          }

          this.fetchPendingLeaves();
        } else {
          alert(`批准请假申请失败: ${result.error}`);
        }
      } catch (error) {
        console.error('批准请假申请出错:', error);
        alert('批准请假申请失败，请重试');
      } finally {
        this.$set(this.actionLoading, leaveId, false);
      }
    },
    async rejectLeave(leaveId) {
      if (this.actionLoading[leaveId]) return;

      this.$set(this.actionLoading, leaveId, true);

      try {
        const response = await fetch('/api/attendance/reject-leave', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include', // 确保发送会话 cookie
          body: JSON.stringify({
            leave_id: leaveId,
            approver_id: this.approverId,
            notes: this.approvalNotes[leaveId] || ''
          })
        });

        const result = await response.json();

        if (result.success) {
          alert('请假申请已拒绝');

          // 触发事件，通知父组件
          const rejectedLeave = this.pendingLeaves.find(leave => leave.id === leaveId);
          if (rejectedLeave) {
            this.$emit('leave-rejected', rejectedLeave);
          }

          this.fetchPendingLeaves();
        } else {
          alert(`拒绝请假申请失败: ${result.error}`);
        }
      } catch (error) {
        console.error('拒绝请假申请出错:', error);
        alert('拒绝请假申请失败，请重试');
      } finally {
        this.$set(this.actionLoading, leaveId, false);
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
    this.fetchPendingLeaves();
  }
};
</script>

<style scoped>
.pending-leave-list {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.list-header {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.list-header h3 {
  margin: 0;
  color: #333;
}

.header-subtitle {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
  font-style: italic;
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

.employee-info {
  display: flex;
  align-items: center;
  gap: 5px;
}

.employee-name {
  font-weight: 600;
}

.employee-id {
  color: #999;
  font-size: 14px;
}

.leave-type {
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
  flex-direction: column;
  gap: 10px;
}

.leave-time {
  font-size: 14px;
  color: #999;
}

.approval-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notes-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.reject-btn, .approve-btn {
  padding: 6px 15px;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.reject-btn {
  background-color: #fff1f0;
  color: #f5222d;
}

.reject-btn:hover:not(:disabled) {
  background-color: #ff4d4f;
  color: white;
}

.approve-btn {
  background-color: #f6ffed;
  color: #52c41a;
}

.approve-btn:hover:not(:disabled) {
  background-color: #52c41a;
  color: white;
}

button:disabled {
  background-color: #f5f5f5;
  color: #d9d9d9;
  cursor: not-allowed;
}
</style>
