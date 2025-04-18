<template>
  <div class="safety-warning">
    <header class="header">
      <div class="tab-header">
        <div 
          class="tab-item" 
          :class="{ active: currentTab === 'warnings' }" 
          @click="currentTab = 'warnings'"
        >
          预警处理
        </div>
        <div 
          class="tab-item" 
          :class="{ active: currentTab === 'workorders' }" 
          @click="currentTab = 'workorders'"
        >
          工单处理
        </div>
      </div>
    </header>
    
    <div class="content">
      <!-- 预警处理内容 -->
      <div v-if="currentTab === 'warnings'" class="warning-list">
        <div class="warning-item" v-for="(item, index) in warnings" :key="index">
          <div class="warning-header">
            <span class="warning-type">{{ item.type }}</span>
            <span class="warning-time">{{ item.time }}</span>
          </div>
          <div class="warning-content">
            <p>{{ item.description }}</p>
            <div class="warning-location">位置：{{ item.location }}</div>
          </div>
          <div class="warning-actions">
            <button class="action-btn primary" @click="handleWarning(item)">处理</button>
            <button class="action-btn" @click="ignoreWarning(item)">忽略</button>
          </div>
        </div>
      </div>

      <!-- 工单处理内容 -->
      <div v-else class="workorder-list">
        <div class="workorder-filter">
          <select v-model="workorderFilter" class="filter-select">
            <option value="all">全部工单</option>
            <option value="pending">待处理</option>
            <option value="processing">处理中</option>
            <option value="completed">已完成</option>
          </select>
        </div>
        
        <div class="workorder-item" v-for="(item, index) in filteredWorkorders" :key="index">
          <div class="workorder-header">
            <span class="workorder-number">{{ item.number }}</span>
            <span class="workorder-status" :class="item.status">{{ item.statusText }}</span>
          </div>
          <div class="workorder-content">
            <h3 class="workorder-title">{{ item.title }}</h3>
            <p>{{ item.description }}</p>
            <div class="workorder-meta">
              <span>上报人：{{ item.reporter }}</span>
              <span>位置：{{ item.location }}</span>
            </div>
            <div class="workorder-time">上报时间：{{ item.submitTime }}</div>
          </div>
          <div class="workorder-actions">
            <button 
              class="action-btn primary" 
              @click="showWorkorderDetail(item)"
              v-if="item.status !== 'completed'"
            >处理工单</button>
            <button 
              class="action-btn" 
              @click="showWorkorderDetail(item)"
              v-else
            >查看详情</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 工单详情模态框 -->
    <div class="modal" v-if="showWorkorderDetailModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>工单详情</h3>
          <span class="close-btn" @click="showWorkorderDetailModal = false">&times;</span>
        </div>
        <div class="modal-body">
          <div class="detail-item">
            <label>工单编号</label>
            <div class="value">{{ selectedWorkorder.number }}</div>
          </div>
          <div class="detail-item">
            <label>工单状态</label>
            <div class="value">
              <span class="status-tag" :class="selectedWorkorder.status">
                {{ selectedWorkorder.statusText }}
              </span>
            </div>
          </div>
          <div class="detail-item">
            <label>工单标题</label>
            <div class="value">{{ selectedWorkorder.title }}</div>
          </div>
          <div class="detail-item">
            <label>工单描述</label>
            <div class="value description">{{ selectedWorkorder.description }}</div>
          </div>
          <div class="detail-item">
            <label>设备位置</label>
            <div class="value">{{ selectedWorkorder.location }}</div>
          </div>
          <div class="detail-item">
            <label>上报人员</label>
            <div class="value">{{ selectedWorkorder.reporter }}</div>
          </div>
          <div class="detail-item">
            <label>上报时间</label>
            <div class="value">{{ selectedWorkorder.submitTime }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkorder.handlerNote">
            <label>处理记录</label>
            <div class="value">{{ selectedWorkorder.handlerNote }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkorder.status !== 'completed'">
            <label>处理记录</label>
            <textarea 
              v-model="handlerNote" 
              class="form-input" 
              rows="3" 
              placeholder="请输入处理记录"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="showWorkorderDetailModal = false">关闭</button>
          <button 
            class="btn submit" 
            @click="processWorkorder" 
            v-if="selectedWorkorder.status === 'pending'"
          >开始处理</button>
          <button 
            class="btn submit" 
            @click="completeWorkorder" 
            v-if="selectedWorkorder.status === 'processing'"
          >完成处理</button>
        </div>
      </div>
    </div>

    <SafetyNav />
  </div>
</template>

<script>
import SafetyNav from '@/components/SafetyNav.vue'

export default {
  name: 'SafetyWarning',
  components: {
    SafetyNav
  },
  data() {
    return {
      currentTab: 'warnings',
      workorderFilter: 'all',
      showWorkorderDetailModal: false,
      handlerNote: '',
      selectedWorkorder: {},
      warnings: [
        {
          id: 1,
          type: '设备异常',
          time: '2023-07-10 10:30',
          description: '检测到设备温度异常升高',
          location: '一号生产线'
        },
        {
          id: 2,
          type: '环境预警',
          time: '2023-07-10 09:15',
          description: '空气质量超标',
          location: '生产车间A区'
        }
      ],
      workorders: [
        {
          id: 1,
          number: 'WO2023001',
          title: '一号生产线温度异常',
          description: '一号生产线主轴承温度异常升高，需紧急检查。',
          location: '一号生产线',
          reporter: '张工',
          submitTime: '2023-07-10 10:30',
          status: 'pending',
          statusText: '待处理'
        },
        {
          id: 2,
          number: 'WO2023002',
          title: '二号生产线噪音异常',
          description: '二号生产线传送带噪音异常，需检查。',
          location: '二号生产线',
          reporter: '李工',
          submitTime: '2023-07-10 14:20',
          status: 'processing',
          statusText: '处理中',
          handlerNote: '已初步检查，更换了传送带润滑油，仍需观察。'
        },
        {
          id: 3,
          number: 'WO2023003',
          title: '安全门故障',
          description: '三号车间安全门无法正常关闭，需维修。',
          location: '三号车间',
          reporter: '王工',
          submitTime: '2023-07-09 16:45',
          status: 'completed',
          statusText: '已完成',
          handlerNote: '已维修完成，更换了门锁装置。'
        }
      ]
    }
  },
  computed: {
    filteredWorkorders() {
      if (this.workorderFilter === 'all') return this.workorders;
      return this.workorders.filter(item => item.status === this.workorderFilter);
    }
  },
  methods: {
    handleWarning(warning) {
      console.log('处理预警:', warning);
      // 这里可以添加处理预警的逻辑
    },
    ignoreWarning(warning) {
      console.log('忽略预警:', warning);
      // 这里可以添加忽略预警的逻辑
    },
    showWorkorderDetail(workorder) {
      this.selectedWorkorder = { ...workorder };
      this.handlerNote = workorder.handlerNote || '';
      this.showWorkorderDetailModal = true;
    },
    processWorkorder() {
      if (!this.handlerNote.trim()) {
        alert('请填写处理记录');
        return;
      }
      
      // 更新选中的工单状态为处理中
      this.selectedWorkorder.status = 'processing';
      this.selectedWorkorder.statusText = '处理中';
      this.selectedWorkorder.handlerNote = this.handlerNote;
      
      // 更新工单列表中的状态
      const index = this.workorders.findIndex(w => w.id === this.selectedWorkorder.id);
      if (index !== -1) {
        this.workorders[index] = { ...this.selectedWorkorder };
      }
      
      this.showWorkorderDetailModal = false;
      alert('已开始处理工单');
    },
    completeWorkorder() {
      if (!this.handlerNote.trim()) {
        alert('请填写处理记录');
        return;
      }
      
      // 更新选中的工单状态为已完成
      this.selectedWorkorder.status = 'completed';
      this.selectedWorkorder.statusText = '已完成';
      this.selectedWorkorder.handlerNote = this.handlerNote;
      this.selectedWorkorder.completedTime = new Date().toLocaleString();
      
      // 更新工单列表中的状态
      const index = this.workorders.findIndex(w => w.id === this.selectedWorkorder.id);
      if (index !== -1) {
        this.workorders[index] = { ...this.selectedWorkorder };
      }
      
      this.showWorkorderDetailModal = false;
      alert('工单已完成');
    }
  }
}
</script>

<style scoped>
.safety-warning {
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

.warning-list, .workorder-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.tab-header {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 40px;
}

.tab-item {
  padding: 10px 5px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  position: relative;
}

.tab-item.active {
  color: white;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: white;
}

.warning-item, .workorder-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.warning-header, .workorder-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.warning-type {
  font-weight: bold;
  color: #f44336;
}

.warning-time, .workorder-time {
  color: #666;
  font-size: 14px;
}

.warning-content, .workorder-content {
  margin-bottom: 15px;
}

.warning-location {
  color: #666;
  font-size: 14px;
  margin-top: 5px;
}

.warning-actions, .workorder-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background: #f5f5f5;
  color: #666;
}

.action-btn.primary {
  background: #2196F3;
  color: white;
}

.workorder-filter {
  margin-bottom: 15px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 100%;
  background-color: white;
}

.workorder-number {
  font-weight: bold;
  color: #333;
}

.workorder-title {
  margin: 0 0 10px 0;
  font-size: 16px;
}

.workorder-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.workorder-status.pending, .status-tag.pending {
  background: #fff3e0;
  color: #ff9800;
}

.workorder-status.processing, .status-tag.processing {
  background: #e3f2fd;
  color: #2196F3;
}

.workorder-status.completed, .status-tag.completed {
  background: #e8f5e9;
  color: #4CAF50;
}

.workorder-meta {
  display: flex;
  justify-content: space-between;
  margin: 10px 0;
  font-size: 14px;
  color: #666;
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

.detail-item {
  margin-bottom: 15px;
}

.detail-item label {
  display: block;
  color: #666;
  margin-bottom: 5px;
  font-size: 14px;
}

.detail-item .value {
  color: #333;
  font-size: 15px;
}

.detail-item .value.description {
  white-space: pre-wrap;
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
