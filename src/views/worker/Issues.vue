<template>
  <div class="issues">
    <header class="header">
      <h1>故障上报</h1>
    </header>

    <div class="content">
      <div class="action-bar">
        <button class="add-btn" @click="showReportModal = true">
          <i class="plus-icon">+</i> 上报故障
        </button>
        <button class="refresh-btn" @click="fetchSubmittedWorkorders">
          <i class="refresh-icon">↻</i> 刷新
        </button>
      </div>

      <!-- 加载中提示 -->
      <div class="loading-container" v-if="loading">
        <div class="loading-spinner"></div>
        <p>正在加载数据...</p>
      </div>

      <!-- 错误提示 -->
      <div class="error-container" v-if="error">
        <p class="error-message">{{ error }}</p>
        <button class="retry-btn" @click="fetchSubmittedWorkorders">重试</button>
      </div>

      <div class="issues-list" v-if="!loading && !error">
        <div class="issue-item" v-for="issue in workorders" :key="issue.workorder_number">
          <div class="issue-header">
            <span class="issue-type">设备维护</span>
            <span class="issue-status" :class="issue.status">{{ issue.statusText }}</span>
          </div>
          <div class="issue-content">
            <div class="issue-number">工单编号: {{ issue.workorder_number }}</div>
            <p>{{ issue.task_details }}</p>
            <div class="issue-info">
              <div class="issue-device">设备: {{ issue.extension_fields?.device_name || '未指定' }}</div>
              <div class="issue-time">上报时间: {{ formatDateTime(issue.created_at) }}</div>
            </div>
          </div>
        </div>
        <div class="empty-tip" v-if="workorders.length === 0">
          <div class="empty-icon">📋</div>
          <p>暂无故障上报记录</p>
        </div>
      </div>
    </div>

    <!-- 上报故障模态框 -->
    <div class="modal" v-if="showReportModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>上报设备故障</h3>
          <span class="close-btn" @click="showReportModal = false">&times;</span>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>设备选择 <span class="required">*</span></label>
            <select v-model="newIssue.deviceId" class="form-input" @change="onDeviceChange">
              <option value="">请选择设备</option>
              <option v-for="device in myDevices" :key="device.id" :value="device.id">
                {{ device.name }} ({{ device.code }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>发现时间 <span class="required">*</span></label>
            <input type="datetime-local" v-model="newIssue.discoveryTime" class="form-input">
          </div>
          <div class="form-group">
            <label>故障描述 <span class="required">*</span></label>
            <textarea v-model="newIssue.description" class="form-input" rows="3" placeholder="请详细描述设备故障情况"></textarea>
          </div>
          <div class="form-group">
            <label>上报员工</label>
            <input type="text" :value="currentUserInfo.username + ' (' + currentUserInfo.employee_id + ')'" class="form-input" disabled>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="showReportModal = false">取消</button>
          <button class="btn submit" @click="submitIssue" :disabled="isSubmitting">{{ isSubmitting ? '提交中...' : '提交' }}</button>
        </div>
      </div>
    </div>

    <WorkerNav />
  </div>
</template>

<script>
import WorkerNav from '@/components/WorkerNav.vue'

export default {
  name: 'WorkerIssues',
  components: {
    WorkerNav
  },
  data() {
    return {
      showReportModal: false,
      loading: false,
      error: null,
      isSubmitting: false,
      workorders: [],
      myDevices: [],
      currentUserInfo: {},
      newIssue: {
        deviceId: '',
        deviceName: '',
        deviceCode: '',
        productionLine: '',
        productionLineId: '',
        discoveryTime: this.getCurrentDateTime(),
        description: ''
      }
    }
  },
  created() {
    // 获取当前用户信息
    this.getCurrentUserInfo();
    // 获取工人负责的设备
    this.fetchWorkerDevices();
    // 获取工人提交的工单
    this.fetchSubmittedWorkorders();
  },
  methods: {
    // 获取当前用户信息
    getCurrentUserInfo() {
      const userInfoStr = localStorage.getItem('userInfo');
      if (userInfoStr) {
        try {
          this.currentUserInfo = JSON.parse(userInfoStr);
        } catch (error) {
          console.error('解析用户信息失败:', error);
          this.currentUserInfo = {};
        }
      }
    },

    // 获取当前日期时间
    getCurrentDateTime() {
      const now = new Date();
      return now.toISOString().slice(0, 16);
    },

    // 格式化日期时间
    formatDateTime(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleString();
    },

    // 获取工人负责的设备
    async fetchWorkerDevices() {
      this.loading = true;
      this.error = null;

      try {
        // 获取当前登录用户的工号
        const employeeId = this.currentUserInfo.employee_id;

        if (!employeeId) {
          this.error = '无法获取您的工号信息，请重新登录';
          return;
        }

        // 获取工人所在组的设备信息
        const groupId = this.currentUserInfo.group_id;
        const response = await fetch(`/api/equipment/with-status?group_id=${groupId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取设备信息失败: ${response.status}`);
        }

        const result = await response.json();
        console.log('设备信息:', result);

        if (result.success && result.data) {
          // 过滤出工人负责的设备
          this.myDevices = result.data
            .filter(device => device.worker_id === employeeId)
            .map(device => ({
              id: device.id,
              name: device.equipment_name,
              code: device.equipment_code,
              lineId: device.line_id,
              lineName: device.line_name || '未知产线'
            }));
        } else {
          this.error = result.error || '获取设备信息失败';
        }
      } catch (error) {
        console.error('获取设备信息出错:', error);
        this.error = error.message || '获取设备信息出错';
      } finally {
        this.loading = false;
      }
    },

    // 获取工人提交的工单
    async fetchSubmittedWorkorders() {
      this.loading = true;
      this.error = null;

      try {
        // 获取当前登录用户的工号
        const employeeId = this.currentUserInfo.employee_id;

        if (!employeeId) {
          this.error = '无法获取您的工号信息，请重新登录';
          return;
        }

        // 获取工人提交的工单
        const response = await fetch(`/api/workorders/worker-submitted-workorders?employee_id=${employeeId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取工单失败: ${response.status}`);
        }

        const result = await response.json();
        console.log('工人提交的工单:', result);

        if (result.success && result.data) {
          // 过滤出设备维护类型的工单
          this.workorders = result.data
            .filter(wo => wo.task_type === '设备维护')
            .map(wo => {
              // 设置状态文本
              let statusText = '未知';
              let status = '';

              switch(wo.status) {
                case '未接受':
                  statusText = '待处理';
                  status = 'pending';
                  break;
                case '已接受':
                  statusText = '处理中';
                  status = 'processing';
                  break;
                case '已完成':
                  statusText = '已完成';
                  status = 'completed';
                  break;
                case '已取消':
                  statusText = '已取消';
                  status = 'cancelled';
                  break;
              }

              return {
                ...wo,
                statusText,
                status
              };
            });
        } else {
          this.error = result.error || '获取工单失败';
        }
      } catch (error) {
        console.error('获取工单出错:', error);
        this.error = error.message || '获取工单出错';
      } finally {
        this.loading = false;
      }
    },

    // 设备选择变更处理
    onDeviceChange() {
      if (!this.newIssue.deviceId) {
        this.newIssue.deviceName = '';
        this.newIssue.deviceCode = '';
        this.newIssue.productionLine = '';
        this.newIssue.productionLineId = '';
        return;
      }

      // 查找选中的设备信息
      const selectedDevice = this.myDevices.find(device => device.id === this.newIssue.deviceId);
      if (selectedDevice) {
        this.newIssue.deviceName = selectedDevice.name;
        this.newIssue.deviceCode = selectedDevice.code;
        this.newIssue.productionLine = selectedDevice.lineName;
        this.newIssue.productionLineId = selectedDevice.lineId;
      }
    },

    // 提交故障上报
    async submitIssue() {
      // 验证表单
      if (!this.newIssue.deviceId || !this.newIssue.discoveryTime || !this.newIssue.description) {
        alert('请填写所有必填字段');
        return;
      }

      this.isSubmitting = true;

      try {
        // 格式化日期时间为MySQL兼容格式
        const formatDate = (dateTimeStr) => {
          const date = new Date(dateTimeStr);
          return date.getFullYear() + '-' +
                 String(date.getMonth() + 1).padStart(2, '0') + '-' +
                 String(date.getDate()).padStart(2, '0') + ' ' +
                 String(date.getHours()).padStart(2, '0') + ':' +
                 String(date.getMinutes()).padStart(2, '0') + ':' +
                 String(date.getSeconds()).padStart(2, '0');
        };

        // 准备工单数据
        const workorderData = {
          task_type: '设备维护',
          task_details: this.newIssue.description,
          start_time: formatDate(new Date()),
          deadline: formatDate(new Date(Date.now() + 24 * 60 * 60 * 1000)), // 默认截止时间为24小时后
          creator: this.currentUserInfo.employee_id,
          production_line: this.newIssue.productionLineId,
          team: this.currentUserInfo.group_id, // 添加组号，与工长上传的格式一致
          extension_fields: {
            device_id: this.newIssue.deviceId,
            device_name: this.newIssue.deviceName,
            device_info: `${this.newIssue.deviceName} (${this.newIssue.deviceCode})`, // 添加设备完整信息，与工长上传的格式一致
            discovery_time: formatDate(this.newIssue.discoveryTime)
          }
        };

        // 发送请求创建工单
        const response = await fetch('/api/workorders/create-workorder', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(workorderData)
        });

        const result = await response.json();

        if (result.success) {
          alert('故障上报成功');
          this.resetNewIssue();
          this.showReportModal = false;
          // 重新获取工单列表
          this.fetchSubmittedWorkorders();
        } else {
          alert(`故障上报失败: ${result.error || '未知错误'}`);
        }
      } catch (error) {
        console.error('提交故障上报出错:', error);
        alert(`提交故障上报出错: ${error.message || '未知错误'}`);
      } finally {
        this.isSubmitting = false;
      }
    },

    // 重置表单
    resetNewIssue() {
      this.newIssue = {
        deviceId: '',
        deviceName: '',
        deviceCode: '',
        productionLine: '',
        productionLineId: '',
        discoveryTime: this.getCurrentDateTime(),
        description: ''
      };
    }
  }
}
</script>

<style scoped>
.issues {
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

.action-bar {
  padding: 10px 15px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-between;
}

.add-btn, .refresh-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.add-btn {
  background-color: #4285F4;
  color: white;
}

.refresh-btn {
  background-color: #f5f5f5;
  color: #333;
}

.plus-icon, .refresh-icon {
  font-size: 18px;
}

.loading-container, .error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  background: white;
  border-radius: 8px;
  margin-top: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  color: #f44336;
  margin-bottom: 15px;
}

.retry-btn {
  background-color: #f44336;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.empty-tip {
  text-align: center;
  padding: 30px;
  color: #999;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 10px;
  color: #ddd;
}

.issues-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 15px;
}

.issue-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.issue-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.issue-type {
  font-weight: bold;
  color: #333;
}

.issue-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.issue-status.pending {
  background: #e3f2fd;
  color: #2196F3;
}

.issue-status.processing {
  background: #e8f5e9;
  color: #4CAF50;
}

.issue-status.completed {
  background: #f5f5f5;
  color: #9e9e9e;
}

.issue-status.cancelled {
  background: #ffebee;
  color: #f44336;
}

.issue-content {
  color: #666;
}

.issue-number {
  font-weight: 500;
  color: #333;
  margin-bottom: 5px;
}

.issue-info {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 14px;
  color: #666;
}

.issue-device, .issue-time {
  font-size: 14px;
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
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
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
  color: #333;
}

.form-group .required {
  color: #f44336;
  margin-left: 2px;
}

.form-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
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
  background: #2196F3;
  color: white;
}
</style>
