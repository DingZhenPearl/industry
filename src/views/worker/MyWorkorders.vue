<template>
  <div class="my-workorders">
    <header class="header">
      <h1>我的工单</h1>
    </header>
    
    <div class="content">
      <!-- 工单筛选区域 -->
      <div class="filter-bar">
        <select v-model="workorderFilter.status" class="filter-select">
          <option value="all">全部工单</option>
          <option value="pending">待接收</option>
          <option value="accepted">已接收</option>
          <option value="processing">进行中</option>
          <option value="completed">已完成</option>
        </select>
        <select v-model="workorderFilter.type" class="filter-select">
          <option value="all">全部类型</option>
          <option value="production">生产工单</option>
          <option value="maintenance">设备维护</option>
          <option value="quality">质量检查</option>
          <option value="inspection">巡检工单</option>
        </select>
        <div class="search-box">
          <input 
            type="text" 
            v-model="searchKeyword" 
            placeholder="搜索工单编号/内容" 
            class="search-input"
          >
        </div>
      </div>

      <!-- 工单卡片统计 -->
      <div class="workorder-cards">
        <div class="workorder-card">
          <h3>待接收工单</h3>
          <div class="count">{{ pendingWorkordersCount }}</div>
        </div>
        <div class="workorder-card">
          <h3>进行中工单</h3>
          <div class="count">{{ processingWorkordersCount }}</div>
        </div>
        <div class="workorder-card">
          <h3>已完成工单</h3>
          <div class="count">{{ completedWorkordersCount }}</div>
        </div>
      </div>

      <!-- 工单列表 -->
      <div class="workorder-list">
        <div class="workorder-item" v-for="workorder in filteredWorkorders" :key="workorder.id">
          <div class="workorder-header">
            <span class="workorder-number">{{ workorder.number }}</span>
            <span class="workorder-status" :class="workorder.status">{{ workorder.statusText }}</span>
          </div>
          <div class="workorder-body">
            <h3 class="workorder-title">{{ workorder.type }}</h3>
            <p class="workorder-desc">{{ workorder.description }}</p>
            <div class="workorder-meta">
              <span>下发人：{{ workorder.assignedBy }}</span>
              <span>截止时间：{{ workorder.deadline }}</span>
            </div>
          </div>
          <div class="workorder-footer">
            <button 
              class="action-btn accept" 
              v-if="workorder.status === 'pending'" 
              @click="acceptWorkorder(workorder)"
            >接收工单</button>
            <button 
              class="action-btn start" 
              v-if="workorder.status === 'accepted'" 
              @click="startWorkorder(workorder)"
            >开始工单</button>
            <button 
              class="action-btn complete" 
              v-if="workorder.status === 'processing'" 
              @click="completeWorkorder(workorder)"
            >完成工单</button>
            <button class="detail-btn" @click="viewWorkorderDetail(workorder)">查看详情</button>
          </div>
        </div>
        <div class="empty-tip" v-if="filteredWorkorders.length === 0">
          暂无工单
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
            <label>工单类型</label>
            <div class="value">{{ selectedWorkorder.type }}</div>
          </div>
          <div class="detail-item">
            <label>工单描述</label>
            <div class="value description">{{ selectedWorkorder.description }}</div>
          </div>
          <div class="detail-item">
            <label>所属产线</label>
            <div class="value">{{ selectedWorkorder.productionLine }}</div>
          </div>
          <div class="detail-item">
            <label>下发人</label>
            <div class="value">{{ selectedWorkorder.assignedBy }}</div>
          </div>
          <div class="detail-item">
            <label>下发时间</label>
            <div class="value">{{ selectedWorkorder.assignTime }}</div>
          </div>
          <div class="detail-item">
            <label>开始时间</label>
            <div class="value">{{ selectedWorkorder.startTime || '未开始' }}</div>
          </div>
          <div class="detail-item">
            <label>截止时间</label>
            <div class="value">{{ selectedWorkorder.deadline }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkorder.status === 'completed'">
            <label>完成时间</label>
            <div class="value">{{ selectedWorkorder.completedTime }}</div>
          </div>
          <div class="detail-item">
            <label>执行进度</label>
            <div class="value">
              <div class="progress-bar">
                <div 
                  class="progress" 
                  :style="{ width: (selectedWorkorder.progress || 0) + '%' }"
                ></div>
              </div>
              <span class="progress-text">{{ selectedWorkorder.progress || 0 }}%</span>
            </div>
          </div>
          <div class="detail-item" v-if="selectedWorkorder.status === 'processing' || selectedWorkorder.status === 'completed'">
            <label>任务备注</label>
            <div class="value" v-if="selectedWorkorder.status === 'completed'">
              {{ selectedWorkorder.note || '无' }}
            </div>
            <textarea 
              v-else
              v-model="taskNote" 
              class="form-input" 
              rows="3"
              placeholder="请输入任务执行备注"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="showWorkorderDetailModal = false">关闭</button>
          <button 
            class="btn accept" 
            v-if="selectedWorkorder.status === 'pending'" 
            @click="acceptWorkorder(selectedWorkorder)"
          >接收工单</button>
          <button 
            class="btn start" 
            v-if="selectedWorkorder.status === 'accepted'" 
            @click="startWorkorder(selectedWorkorder)"
          >开始工单</button>
          <button 
            class="btn complete" 
            v-if="selectedWorkorder.status === 'processing'" 
            @click="completeWorkorder(selectedWorkorder)"
          >完成工单</button>
        </div>
      </div>
    </div>

    <WorkerNav />
  </div>
</template>

<script>
import WorkerNav from '@/components/WorkerNav.vue'

export default {
  name: 'MyWorkorders',
  components: {
    WorkerNav
  },
  data() {
    return {
      // 工单筛选条件
      workorderFilter: {
        status: 'all',
        type: 'all'
      },
      searchKeyword: '',
      
      // 模态框控制
      showWorkorderDetailModal: false,
      selectedWorkorder: {},
      taskNote: '',
      
      // 工单列表数据
      workorders: [
        {
          id: 1,
          number: 'T2023001',
          status: 'pending',
          statusText: '待接收',
          type: '生产工单',
          description: '一号生产线零部件组装',
          productionLine: '一号生产线',
          assignedBy: '张工',
          assignTime: '2023-07-10 09:00',
          deadline: '2023-07-10 17:00',
          progress: 0
        },
        {
          id: 2,
          number: 'T2023002',
          status: 'accepted',
          statusText: '已接收',
          type: '设备维护',
          description: '二号生产线设备日常维护',
          productionLine: '二号生产线',
          assignedBy: '李工',
          assignTime: '2023-07-10 10:30',
          deadline: '2023-07-11 12:00',
          progress: 0
        },
        {
          id: 3,
          number: 'T2023003',
          status: 'processing',
          statusText: '进行中',
          type: '质量检查',
          description: '一号生产线产品质量抽检',
          productionLine: '一号生产线',
          assignedBy: '王工',
          assignTime: '2023-07-09 14:00',
          startTime: '2023-07-09 15:00',
          deadline: '2023-07-10 14:00',
          progress: 60
        },
        {
          id: 4,
          number: 'T2023004',
          status: 'completed',
          statusText: '已完成',
          type: '巡检工单',
          description: '二号生产线安全巡检',
          productionLine: '二号生产线',
          assignedBy: '赵工',
          assignTime: '2023-07-08 09:00',
          startTime: '2023-07-08 09:30',
          deadline: '2023-07-08 17:00',
          completedTime: '2023-07-08 16:30',
          progress: 100,
          note: '巡检完成，设备运行正常，无安全隐患'
        }
      ]
    }
  },
  computed: {
    // 筛选后的工单列表
    filteredWorkorders() {
      return this.workorders.filter(workorder => {
        // 按状态筛选
        const statusMatch = this.workorderFilter.status === 'all' || workorder.status === this.workorderFilter.status;
        
        // 按类型筛选
        const typeMatch = this.workorderFilter.type === 'all' || workorder.type.includes(this.workorderFilter.type === 'production' ? '生产' : 
                                                              this.workorderFilter.type === 'maintenance' ? '维护' :
                                                              this.workorderFilter.type === 'quality' ? '质量' :
                                                              this.workorderFilter.type === 'inspection' ? '巡检' : '');
        
        // 按关键词搜索
        const keywordMatch = !this.searchKeyword || 
                            workorder.number.toLowerCase().includes(this.searchKeyword.toLowerCase()) ||
                            workorder.description.toLowerCase().includes(this.searchKeyword.toLowerCase());
        
        return statusMatch && typeMatch && keywordMatch;
      });
    },
    
    // 待接收工单数量
    pendingWorkordersCount() {
      return this.workorders.filter(workorder => workorder.status === 'pending').length;
    },
    
    // 进行中工单数量
    processingWorkordersCount() {
      return this.workorders.filter(workorder => workorder.status === 'processing' || workorder.status === 'accepted').length;
    },
    
    // 已完成工单数量
    completedWorkordersCount() {
      return this.workorders.filter(workorder => workorder.status === 'completed').length;
    }
  },
  methods: {
    // 查看工单详情
    viewWorkorderDetail(workorder) {
      this.selectedWorkorder = { ...workorder };
      this.taskNote = workorder.note || '';
      this.showWorkorderDetailModal = true;
    },
    
    // 接收工单
    acceptWorkorder(workorder) {
      // 更新工单状态
      const index = this.workorders.findIndex(w => w.id === workorder.id);
      if (index !== -1) {
        this.workorders[index].status = 'accepted';
        this.workorders[index].statusText = '已接收';
        
        // 如果是在详情页操作，同步更新选中的工单
        if (this.selectedWorkorder.id === workorder.id) {
          this.selectedWorkorder.status = 'accepted';
          this.selectedWorkorder.statusText = '已接收';
        }
        
        // 提示用户
        alert('已成功接收工单');
        
        // 如果是在详情页操作，关闭详情页
        if (this.showWorkorderDetailModal) {
          this.showWorkorderDetailModal = false;
        }
      }
    },
    
    // 开始工单
    startWorkorder(workorder) {
      // 更新工单状态
      const index = this.workorders.findIndex(w => w.id === workorder.id);
      if (index !== -1) {
        this.workorders[index].status = 'processing';
        this.workorders[index].statusText = '进行中';
        this.workorders[index].startTime = new Date().toLocaleString();
        this.workorders[index].progress = 10; // 初始进度设为10%
        
        // 如果是在详情页操作，同步更新选中的工单
        if (this.selectedWorkorder.id === workorder.id) {
          this.selectedWorkorder.status = 'processing';
          this.selectedWorkorder.statusText = '进行中';
          this.selectedWorkorder.startTime = new Date().toLocaleString();
          this.selectedWorkorder.progress = 10;
        }
        
        // 提示用户
        alert('已开始执行工单');
      }
    },
    
    // 完成工单
    completeWorkorder(workorder) {
      // 验证是否填写了备注
      if (this.showWorkorderDetailModal && !this.taskNote.trim()) {
        alert('请填写工单执行备注');
        return;
      }
      
      // 更新工单状态
      const index = this.workorders.findIndex(w => w.id === workorder.id);
      if (index !== -1) {
        this.workorders[index].status = 'completed';
        this.workorders[index].statusText = '已完成';
        this.workorders[index].completedTime = new Date().toLocaleString();
        this.workorders[index].progress = 100; // 完成进度设为100%
        
        // 如果是在详情页操作，保存备注
        if (this.showWorkorderDetailModal) {
          this.workorders[index].note = this.taskNote;
        }
        
        // 如果是在详情页操作，同步更新选中的工单
        if (this.selectedWorkorder.id === workorder.id) {
          this.selectedWorkorder.status = 'completed';
          this.selectedWorkorder.statusText = '已完成';
          this.selectedWorkorder.completedTime = new Date().toLocaleString();
          this.selectedWorkorder.progress = 100;
          this.selectedWorkorder.note = this.taskNote;
        }
        
        // 提示用户
        alert('工单已完成');
        
        // 如果是在详情页操作，关闭详情页
        if (this.showWorkorderDetailModal) {
          this.showWorkorderDetailModal = false;
        }
      }
    }
  }
}
</script>

<style scoped>
.my-workorders {
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

/* 筛选栏样式 */
.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.filter-select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  flex: 1;
}

.search-box {
  flex: 2;
}

.search-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

/* 工单卡片样式 */
.workorder-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.workorder-card {
  background: white;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.workorder-card h3 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
}

.count {
  font-size: 24px;
  font-weight: bold;
  color: #2196F3;
}

/* 工单列表样式 */
.workorder-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.workorder-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.workorder-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.workorder-number {
  font-weight: bold;
  color: #666;
}

.workorder-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.workorder-status.pending {
  background: #e3f2fd;
  color: #2196F3;
}

.workorder-status.accepted {
  background: #e8f5e9;
  color: #4CAF50;
}

.workorder-status.processing {
  background: #fff3e0;
  color: #ff9800;
}

.workorder-status.completed {
  background: #f5f5f5;
  color: #9e9e9e;
}

.workorder-body {
  margin-bottom: 15px;
}

.workorder-title {
  font-size: 16px;
  margin: 0 0 5px 0;
  color: #333;
}

.workorder-desc {
  color: #666;
  margin: 0 0 10px 0;
}

.workorder-meta {
  display: flex;
  justify-content: space-between;
  color: #999;
  font-size: 12px;
}

.workorder-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.action-btn.accept {
  background: #e3f2fd;
  color: #2196F3;
}

.action-btn.start {
  background: #e8f5e9;
  color: #4CAF50;
}

.action-btn.complete {
  background: #fff3e0;
  color: #ff9800;
}

.detail-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  background: #f5f5f5;
  color: #666;
  cursor: pointer;
}

.empty-tip {
  text-align: center;
  padding: 30px;
  color: #999;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* 模态框样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-body {
  padding: 15px;
}

.detail-item {
  margin-bottom: 15px;
}

.detail-item label {
  display: block;
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.detail-item .value {
  font-size: 16px;
}

.detail-item .description {
  white-space: pre-line;
}

.status-tag {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-tag.pending {
  background: #e3f2fd;
  color: #2196F3;
}

.status-tag.accepted {
  background: #e8f5e9;
  color: #4CAF50;
}

.status-tag.processing {
  background: #fff3e0;
  color: #ff9800;
}

.status-tag.completed {
  background: #f5f5f5;
  color: #9e9e9e;
}

.progress-bar {
  height: 8px;
  background: #f5f5f5;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 5px;
}

.progress {
  height: 100%;
  background: #4CAF50;
  border-radius: 4px;
}

.progress-text {
  font-size: 14px;
  color: #4CAF50;
}

.form-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 15px;
  border-top: 1px solid #eee;
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

.btn.accept {
  background: #e3f2fd;
  color: #2196F3;
}

.btn.start {
  background: #e8f5e9;
  color: #4CAF50;
}

.btn.complete {
  background: #fff3e0;
  color: #ff9800;
}
</style>
