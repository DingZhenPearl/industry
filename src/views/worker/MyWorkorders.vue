<template>
  <div class="my-workorders">
    <header class="header">
      <h1>我的工单</h1>
    </header>
    
    <div class="content">
      <!-- 工单筛选区域 -->
      <div class="filter-section">
        <div class="filter-bar">
          <div class="filter-item">
            <label class="filter-label">状态</label>
            <select v-model="workorderFilter.status" class="filter-select">
              <option value="all">全部工单</option>
              <option value="pending">待接收</option>
              <option value="accepted">已接收</option>
              <option value="processing">进行中</option>
              <option value="completed">已完成</option>
            </select>
          </div>
          <div class="filter-item">
            <label class="filter-label">类型</label>
            <select v-model="workorderFilter.type" class="filter-select">
              <option value="all">全部类型</option>
              <option value="production">生产工单</option>
              <option value="maintenance">设备维护</option>
              <option value="quality">质量检查</option>
              <option value="inspection">巡检工单</option>
            </select>
          </div>
        </div>
        <div class="search-box">
          <i class="search-icon">🔍</i>
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
        <div class="workorder-card pending">
          <div class="card-icon">📋</div>
          <div class="card-content">
            <h3>待接收工单</h3>
            <div class="count">{{ pendingWorkordersCount }}</div>
          </div>
        </div>
        <div class="workorder-card processing">
          <div class="card-icon">⚙️</div>
          <div class="card-content">
            <h3>进行中工单</h3>
            <div class="count">{{ processingWorkordersCount }}</div>
          </div>
        </div>
        <div class="workorder-card completed">
          <div class="card-icon">✅</div>
          <div class="card-content">
            <h3>已完成工单</h3>
            <div class="count">{{ completedWorkordersCount }}</div>
          </div>
        </div>
      </div>

      <!-- 工单列表 -->
      <div class="workorder-list">
        <div class="workorder-item" v-for="workorder in filteredWorkorders" :key="workorder.id" :class="workorder.status">
          <div class="workorder-header">
            <div class="workorder-left">
              <span class="workorder-type-icon" :class="workorder.type === '生产工单' ? 'production' : 
                                                      workorder.type === '设备维护' ? 'maintenance' : 
                                                      workorder.type === '质量检查' ? 'quality' : 'inspection'"></span>
              <span class="workorder-number">{{ workorder.number }}</span>
            </div>
            <span class="workorder-status" :class="workorder.status">{{ workorder.statusText }}</span>
          </div>
          <div class="workorder-body">
            <h3 class="workorder-title">{{ workorder.type }}</h3>
            <p class="workorder-desc">{{ workorder.description }}</p>
            <div class="workorder-meta">
              <div class="meta-item">
                <i class="meta-icon person"></i>
                <span>{{ workorder.assignedBy }}</span>
              </div>
              <div class="meta-item">
                <i class="meta-icon time"></i>
                <span>{{ workorder.deadline }}</span>
              </div>
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
            <button class="detail-btn" @click="viewWorkorderDetail(workorder)">
              <i class="detail-icon"></i>
              查看详情
            </button>
          </div>
        </div>
        <div class="empty-tip" v-if="filteredWorkorders.length === 0">
          <div class="empty-icon">📋</div>
          <p>暂无工单</p>
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
        
        <!-- 工单状态概览 -->
        <div class="workorder-overview">
          <div class="overview-header">
            <div class="overview-number">{{ selectedWorkorder.number }}</div>
            <div class="overview-status" :class="selectedWorkorder.status">{{ selectedWorkorder.statusText }}</div>
          </div>
          <div class="overview-type">{{ selectedWorkorder.type }}</div>
          <div class="overview-progress">
            <div class="progress-bar">
              <div 
                class="progress" 
                :style="{ width: (selectedWorkorder.progress || 0) + '%' }"
                :class="selectedWorkorder.status"
              ></div>
            </div>
            <span class="progress-text">{{ selectedWorkorder.progress || 0 }}%</span>
          </div>
        </div>
        
        <div class="modal-body">
          <div class="detail-section">
            <h4 class="section-title">基本信息</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <label>工单类型</label>
                <div class="value">{{ selectedWorkorder.type }}</div>
              </div>
              <div class="detail-item">
                <label>所属产线</label>
                <div class="value">{{ selectedWorkorder.productionLine }}</div>
              </div>
              <div class="detail-item full-width">
                <label>工单描述</label>
                <div class="value description">{{ selectedWorkorder.description }}</div>
              </div>
            </div>
          </div>
          
          <div class="detail-section">
            <h4 class="section-title">时间信息</h4>
            <div class="detail-grid">
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
            </div>
          </div>
          
          <div class="detail-section">
            <h4 class="section-title">责任信息</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <label>下发人</label>
                <div class="value">{{ selectedWorkorder.assignedBy }}</div>
              </div>
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
  background-color: #f5f7fa;
}

.header {
  background-color: #2196F3;
  color: white;
  padding: 15px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.content {
  flex: 1;
  padding: 15px;
}

/* 筛选区域样式 */
.filter-section {
  background: white;
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.filter-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.filter-item {
  flex: 1;
}

.filter-label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.filter-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #f9f9f9;
  color: #333;
  font-size: 14px;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24'%3E%3Cpath fill='%23666' d='M7 10l5 5 5-5z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  cursor: pointer;
}

.search-box {
  position: relative;
  flex: 2;
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
  font-size: 16px;
}

.search-input {
  width: 100%;
  padding: 10px 10px 10px 35px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #f9f9f9;
  font-size: 14px;
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
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  display: flex;
  align-items: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.workorder-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.card-icon {
  font-size: 24px;
  margin-right: 15px;
}

.card-content {
  flex: 1;
}

.workorder-card h3 {
  margin: 0 0 5px 0;
  font-size: 14px;
  color: #666;
}

.count {
  font-size: 24px;
  font-weight: bold;
}

.workorder-card.pending .count {
  color: #2196F3;
}

.workorder-card.processing .count {
  color: #ff9800;
}

.workorder-card.completed .count {
  color: #4CAF50;
}

/* 工单列表样式 */
.workorder-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.workorder-item {
  background: white;
  border-radius: 12px;
  padding: 15px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  border-left: 4px solid transparent;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.workorder-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.workorder-item.pending {
  border-left-color: #2196F3;
}

.workorder-item.accepted {
  border-left-color: #4CAF50;
}

.workorder-item.processing {
  border-left-color: #ff9800;
}

.workorder-item.completed {
  border-left-color: #9e9e9e;
}

.workorder-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.workorder-left {
  display: flex;
  align-items: center;
}

.workorder-type-icon {
  display: inline-block;
  width: 20px;
  height: 20px;
  margin-right: 8px;
  border-radius: 50%;
  background-position: center;
  background-repeat: no-repeat;
  background-size: 12px;
}

.workorder-type-icon.production {
  background-color: #e3f2fd;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='%232196F3' d='M19.8 10.7L4.2 5l-.7 1.9L17.6 12H5c-1.1 0-2 .9-2 2v4c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-5.5c0-.8-.5-1.6-1.2-1.8z'/%3E%3C/svg%3E");
}

.workorder-type-icon.maintenance {
  background-color: #e8f5e9;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='%234CAF50' d='M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z'/%3E%3C/svg%3E");
}

.workorder-type-icon.quality {
  background-color: #e8eaf6;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='%233F51B5' d='M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-9 14l-5-5 1.4-1.4L10 14.2l7.6-7.6L19 8l-9 9z'/%3E%3C/svg%3E");
}

.workorder-type-icon.inspection {
  background-color: #fff3e0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='%23FF9800' d='M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z'/%3E%3C/svg%3E");
}

.workorder-number {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.workorder-status {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
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
  margin: 0 0 8px 0;
  color: #333;
  font-weight: 600;
}

.workorder-desc {
  color: #666;
  margin: 0 0 12px 0;
  font-size: 14px;
  line-height: 1.5;
}

.workorder-meta {
  display: flex;
  gap: 15px;
  color: #999;
  font-size: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
}

.meta-icon {
  margin-right: 5px;
  font-size: 14px;
}

.meta-icon.person:before {
  content: '👤';
}

.meta-icon.time:before {
  content: '⏱️';
}

.workorder-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.action-btn {
  padding: 8px 14px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
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
  display: flex;
  align-items: center;
  padding: 8px 14px;
  border: none;
  border-radius: 8px;
  background: #f5f5f5;
  color: #666;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.detail-btn:hover {
  background: #eeeeee;
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.detail-icon:before {
  content: '👁️';
  margin-right: 5px;
}

.empty-tip {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
  color: #ddd;
}

.empty-tip p {
  font-size: 16px;
  margin: 0;
}

/* 模态框样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(3px);
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 550px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 5px 25px rgba(0,0,0,0.2);
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
  font-size: 18px;
  color: #333;
}

.close-btn {
  font-size: 24px;
  cursor: pointer;
  color: #999;
  transition: color 0.3s ease;
}

.close-btn:hover {
  color: #666;
}

/* 工单概览样式 */
.workorder-overview {
  padding: 20px;
  background-color: #f9f9f9;
  border-bottom: 1px solid #eee;
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.overview-number {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.overview-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.overview-type {
  font-size: 16px;
  color: #666;
  margin-bottom: 15px;
}

.overview-progress {
  margin-top: 15px;
}

.progress-bar {
  height: 10px;
  background: #f0f0f0;
  border-radius: 5px;
  overflow: hidden;
  margin-bottom: 5px;
}

.progress {
  height: 100%;
  border-radius: 5px;
  transition: width 0.5s ease;
}

.progress.pending {
  background: #2196F3;
}

.progress.accepted {
  background: #4CAF50;
}

.progress.processing {
  background: #ff9800;
}

.progress.completed {
  background: #4CAF50;
}

.progress-text {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

/* 详情内容样式 */
.modal-body {
  padding: 20px;
}

.detail-section {
  margin-bottom: 25px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 15px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.detail-item {
  margin-bottom: 0;
}

.full-width {
  grid-column: span 2;
}

.detail-item label {
  display: block;
  font-size: 13px;
  color: #666;
  margin-bottom: 5px;
}

.detail-item .value {
  font-size: 15px;
  color: #333;
}

.detail-item .description {
  white-space: pre-line;
  line-height: 1.5;
}

.form-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  min-height: 80px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 15px 20px;
  border-top: 1px solid #eee;
  background-color: #f9f9f9;
}

.btn {
  padding: 10px 18px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
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
