<template>
  <div class="leave-request-form">
    <div class="form-header">
      <h3>请假申请</h3>
    </div>
    
    <div class="form-body">
      <div class="form-group">
        <label>请假类型</label>
        <select v-model="leaveType" class="form-control">
          <option value="">请选择请假类型</option>
          <option value="事假">事假</option>
          <option value="病假">病假</option>
          <option value="年假">年假</option>
          <option value="其他">其他</option>
        </select>
      </div>
      
      <div class="form-group">
        <label>开始日期</label>
        <input type="date" v-model="startDate" class="form-control" :min="minDate">
      </div>
      
      <div class="form-group">
        <label>结束日期</label>
        <input type="date" v-model="endDate" class="form-control" :min="startDate || minDate">
      </div>
      
      <div class="form-group">
        <label>请假原因</label>
        <textarea v-model="reason" class="form-control" rows="4" placeholder="请输入请假原因"></textarea>
      </div>
      
      <div class="form-actions">
        <button class="cancel-btn" @click="$emit('cancel')">取消</button>
        <button class="submit-btn" :disabled="!isFormValid || loading" @click="submitLeaveRequest">
          {{ loading ? '提交中...' : '提交申请' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LeaveRequestForm',
  props: {
    employeeId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      leaveType: '',
      startDate: '',
      endDate: '',
      reason: '',
      loading: false
    };
  },
  computed: {
    minDate() {
      const today = new Date();
      return today.toISOString().split('T')[0];
    },
    isFormValid() {
      return this.leaveType && this.startDate && this.endDate && this.reason;
    }
  },
  methods: {
    async submitLeaveRequest() {
      if (!this.isFormValid || this.loading) return;
      
      this.loading = true;
      
      try {
        const response = await fetch('/api/attendance/submit-leave', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            employee_id: this.employeeId,
            leave_type: this.leaveType,
            start_date: this.startDate,
            end_date: this.endDate,
            reason: this.reason
          })
        });
        
        const result = await response.json();
        
        if (result.success) {
          alert('请假申请提交成功，等待审批');
          this.$emit('submitted', result.data);
          this.resetForm();
        } else {
          alert(`提交请假申请失败: ${result.error}`);
        }
      } catch (error) {
        console.error('提交请假申请出错:', error);
        alert('提交请假申请失败，请重试');
      } finally {
        this.loading = false;
      }
    },
    resetForm() {
      this.leaveType = '';
      this.startDate = '';
      this.endDate = '';
      this.reason = '';
    }
  }
};
</script>

<style scoped>
.leave-request-form {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.form-header {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.form-header h3 {
  margin: 0;
  color: #333;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.form-control:focus {
  border-color: #40a9ff;
  outline: none;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

textarea.form-control {
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 20px;
}

.cancel-btn, .submit-btn {
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

.submit-btn {
  background-color: #1890ff;
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background-color: #40a9ff;
}

.submit-btn:disabled {
  background-color: #f5f5f5;
  color: #d9d9d9;
  cursor: not-allowed;
}
</style>
