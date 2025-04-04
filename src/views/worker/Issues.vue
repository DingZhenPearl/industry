<template>
  <div class="issues">
    <header class="header">
      <h1>故障上报</h1>
    </header>
    
    <div class="content">
      <div class="action-bar">
        <button class="add-btn" @click="showReportModal = true">
          <i class="plus-icon">+</i> 上报工单
        </button>
      </div>
      
      <div class="issues-list">
        <div class="issue-item" v-for="(issue, index) in issues" :key="index">
          <div class="issue-header">
            <span class="issue-type">{{ issue.type }}</span>
            <span class="issue-time">{{ issue.time }}</span>
          </div>
          <div class="issue-content">
            <p>{{ issue.description }}</p>
            <div class="issue-location">位置：{{ issue.location }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 上报工单模态框 -->
    <div class="modal" v-if="showReportModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>创建任务</h3>
          <span class="close-btn" @click="showReportModal = false">&times;</span>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>任务类型</label>
            <select v-model="newIssue.type" class="form-input">
              <option value="">请选择任务类型</option>
              <option value="maintenance">运维任务</option>
              <option value="inspection">巡检任务</option>
            </select>
          </div>
          <div class="form-group">
            <label>工单编号</label>
            <input type="text" v-model="newIssue.orderNumber" class="form-input" placeholder="自动生成" disabled>
          </div>
          <div class="form-group">
            <label>发现时间</label>
            <input type="datetime-local" v-model="newIssue.discoveryTime" class="form-input">
          </div>
          <div class="form-group">
            <label>产线信息</label>
            <select v-model="newIssue.productionLine" class="form-input">
              <option value="">请选择产线信息</option>
              <option value="line1">一号生产线</option>
              <option value="line2">二号生产线</option>
              <option value="line3">三号生产线</option>
            </select>
          </div>
          <div class="form-group">
            <label>设备位置</label>
            <input type="text" v-model="newIssue.location" class="form-input" placeholder="请输入设备位置">
          </div>
          <div class="form-group">
            <label>设备名称</label>
            <input type="text" v-model="newIssue.deviceName" class="form-input" placeholder="请输入设备名称">
          </div>
          <div class="form-group">
            <label>问题描述</label>
            <textarea v-model="newIssue.description" class="form-input" rows="3" placeholder="请输入问题描述"></textarea>
          </div>
          <div class="form-group">
            <label>上报员工</label>
            <input type="text" v-model="newIssue.reporter" class="form-input" placeholder="自动填写" disabled>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="showReportModal = false">取消</button>
          <button class="btn submit" @click="submitIssue">提交</button>
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
      issues: [
        {
          type: '运维任务',
          time: '2023-07-10 10:30',
          description: '设备温度异常升高',
          location: '一号生产线'
        }
      ],
      newIssue: {
        type: '',
        orderNumber: '202403194678',
        discoveryTime: '',
        productionLine: '',
        location: '',
        deviceName: '',
        description: '',
        reporter: 'test-bz1zy1'
      }
    }
  },
  methods: {
    submitIssue() {
      if (!this.newIssue.type || !this.newIssue.location || !this.newIssue.description) {
        alert('请填写完整信息');
        return;
      }
      this.issues.push({
        ...this.newIssue,
        time: new Date().toLocaleString()
      });
      this.resetNewIssue();
      this.showReportModal = false;
      alert('工单上报成功');
    },
    resetNewIssue() {
      this.newIssue = {
        type: '',
        orderNumber: '202403194678',
        discoveryTime: '',
        productionLine: '',
        location: '',
        deviceName: '',
        description: '',
        reporter: 'test-bz1zy1'
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
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  background-color: #4285F4;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.plus-icon {
  font-size: 18px;
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

.issue-time {
  color: #666;
  font-size: 14px;
}

.issue-content {
  color: #666;
}

.issue-location {
  margin-top: 5px;
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
