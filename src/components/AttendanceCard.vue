<template>
  <div class="attendance-card">
    <div class="card-header">
      <h3>考勤打卡</h3>
      <div class="current-time">{{ currentTime }}</div>
    </div>

    <div class="card-body">
      <div class="status-info">
        <div class="status-label">今日状态：</div>
        <div class="status-value" :class="statusClass">{{ statusText }}</div>
      </div>

      <div class="check-times" v-if="todayStatus.has_checked_in || todayStatus.has_checked_out">
        <div class="check-time" v-if="todayStatus.has_checked_in">
          <div class="time-label">上班时间：</div>
          <div class="time-value">{{ formatTime(todayStatus.check_in_time) }}</div>
        </div>
        <div class="check-time" v-if="todayStatus.has_checked_out">
          <div class="time-label">下班时间：</div>
          <div class="time-value">{{ formatTime(todayStatus.check_out_time) }}</div>
        </div>
      </div>

      <div class="action-buttons">
        <button
          class="check-in-btn"
          :disabled="todayStatus.has_checked_in || loading"
          @click="checkIn"
        >
          {{ loading && actionType === 'check-in' ? '打卡中...' : '上班打卡' }}
        </button>
        <button
          class="check-out-btn"
          :disabled="!todayStatus.has_checked_in || todayStatus.has_checked_out || loading"
          @click="checkOut"
        >
          {{ loading && actionType === 'check-out' ? '打卡中...' : '下班打卡' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AttendanceCard',
  props: {
    employeeId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      currentTime: '',
      todayStatus: {
        date: '',
        has_checked_in: false,
        has_checked_out: false,
        check_in_time: null,
        check_out_time: null,
        status: '在岗'
      },
      loading: false,
      actionType: '',
      clockInterval: null
    };
  },
  computed: {
    statusText() {
      if (this.todayStatus.status === '请假') {
        return '请假中';
      } else if (!this.todayStatus.has_checked_in) {
        return '未打卡';
      } else if (this.todayStatus.has_checked_in && !this.todayStatus.has_checked_out) {
        return '已上班';
      } else if (this.todayStatus.has_checked_in && this.todayStatus.has_checked_out) {
        return '已下班';
      } else {
        return '未知';
      }
    },
    statusClass() {
      if (this.todayStatus.status === '请假') {
        return 'status-leave';
      } else if (!this.todayStatus.has_checked_in) {
        return 'status-not-checked';
      } else if (this.todayStatus.has_checked_in && !this.todayStatus.has_checked_out) {
        return 'status-checked-in';
      } else if (this.todayStatus.has_checked_in && this.todayStatus.has_checked_out) {
        return 'status-checked-out';
      } else {
        return '';
      }
    }
  },
  methods: {
    updateCurrentTime() {
      const now = new Date();
      this.currentTime = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      });
    },
    formatTime(timeString) {
      if (!timeString) return '';
      const date = new Date(timeString);
      return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      });
    },
    async fetchTodayStatus() {
      try {
        const response = await fetch(`/api/attendance/today-status/${this.employeeId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取今日考勤状态失败: ${response.status}`);
        }

        const result = await response.json();

        if (result.success && result.data) {
          this.todayStatus = result.data;
        } else {
          console.error('获取今日考勤状态失败:', result.error);
        }
      } catch (error) {
        console.error('获取今日考勤状态出错:', error);
      }
    },
    async checkIn() {
      if (this.loading) return;

      this.loading = true;
      this.actionType = 'check-in';

      try {
        const response = await fetch('/api/attendance/check-in', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            employee_id: this.employeeId
          })
        });

        const result = await response.json();

        if (result.success) {
          // 更新状态
          await this.fetchTodayStatus();
        } else {
          alert(`上班打卡失败: ${result.error}`);
        }
      } catch (error) {
        console.error('上班打卡出错:', error);
        alert('上班打卡失败，请重试');
      } finally {
        this.loading = false;
      }
    },
    async checkOut() {
      if (this.loading) return;

      this.loading = true;
      this.actionType = 'check-out';

      try {
        const response = await fetch('/api/attendance/check-out', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            employee_id: this.employeeId
          })
        });

        const result = await response.json();

        if (result.success) {
          // 更新状态
          await this.fetchTodayStatus();
        } else {
          alert(`下班打卡失败: ${result.error}`);
        }
      } catch (error) {
        console.error('下班打卡出错:', error);
        alert('下班打卡失败，请重试');
      } finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    this.updateCurrentTime();
    this.clockInterval = setInterval(this.updateCurrentTime, 1000);
    this.fetchTodayStatus();
  },
  beforeDestroy() {
    if (this.clockInterval) {
      clearInterval(this.clockInterval);
    }
  }
};
</script>

<style scoped>
.attendance-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.card-header h3 {
  margin: 0;
  color: #333;
}

.current-time {
  font-size: 14px;
  color: #666;
}

.status-info {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.status-label {
  font-weight: 600;
  margin-right: 10px;
}

.status-value {
  padding: 4px 10px;
  border-radius: 4px;
  font-weight: 500;
}

.status-not-checked {
  background-color: #f5f5f5;
  color: #666;
}

.status-checked-in {
  background-color: #e6f7ff;
  color: #1890ff;
}

.status-checked-out {
  background-color: #f6ffed;
  color: #52c41a;
}

.status-leave {
  background-color: #fff7e6;
  color: #fa8c16;
}

.check-times {
  margin-bottom: 20px;
}

.check-time {
  display: flex;
  margin-bottom: 8px;
}

.time-label {
  width: 80px;
  font-weight: 500;
}

.time-value {
  color: #333;
}

.action-buttons {
  display: flex;
  gap: 15px;
}

.check-in-btn, .check-out-btn {
  flex: 1;
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.check-in-btn {
  background-color: #1890ff;
  color: white;
}

.check-in-btn:hover:not(:disabled) {
  background-color: #40a9ff;
}

.check-out-btn {
  background-color: #52c41a;
  color: white;
}

.check-out-btn:hover:not(:disabled) {
  background-color: #73d13d;
}

button:disabled {
  background-color: #f5f5f5;
  color: #d9d9d9;
  cursor: not-allowed;
}
</style>
