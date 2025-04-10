<template>
  <div class="workorders">
    <header class="header">
      <h1>工单管理</h1>
    </header>

    <div class="content">
      <!-- 工单统计卡片 -->
      <div class="stat-cards">
        <div class="stat-card">
          <h3>待处理工单</h3>
          <div class="count pending">{{ pendingCount }}</div>
        </div>
        <div class="stat-card">
          <h3>处理中工单</h3>
          <div class="count processing">{{ processingCount }}</div>
        </div>
        <div class="stat-card">
          <h3>已完成工单</h3>
          <div class="count completed">{{ completedCount }}</div>
        </div>
      </div>

      <!-- 工单筛选区 -->
      <div class="filter-bar">
        <select v-model="filterType" class="filter-select">
          <option value="all">全部工单</option>
          <option value="设备维护">设备维护</option>
          <option value="产线巡检">产线巡检</option>
          <option value="排班任务">排班任务</option>
        </select>
        <select v-model="filterStatus" class="filter-select">
          <option value="all">全部状态</option>
          <option value="未接受">未接受</option>
          <option value="进行中">进行中</option>
          <option value="已完成">已完成</option>
          <option value="已取消">已取消</option>
        </select>
        <input
          type="text"
          v-model="searchKeyword"
          class="search-input"
          placeholder="搜索工单编号/提交人"
        >
      </div>

      <!-- 加载状态 -->
      <div class="loading-container" v-if="loading">
        <div class="loading-spinner"></div>
        <p>正在加载工单数据...</p>
      </div>

      <!-- 空数据提示 -->
      <div class="empty-container" v-else-if="workorders.length === 0">
        <p>暂无工单数据</p>
      </div>

      <!-- 工单列表 -->
      <div class="workorder-list" v-else>
        <div class="workorder-item" v-for="item in filteredWorkorders" :key="item.id">
          <div class="workorder-header">
            <span class="workorder-number">{{ item.number }}</span>
            <span :class="['workorder-status', item.status]">{{ item.status }}</span>
          </div>
          <div class="workorder-content">
            <h3>{{ item.title }}</h3>
            <p class="description">{{ item.description }}</p>
            <div class="workorder-info">
              <span>类型：{{ item.typeText }}</span>
              <span>位置：{{ item.location }}</span>
            </div>
            <div class="workorder-meta">
              <span>提交人：{{ item.submitter }}</span>
              <span>提交时间：{{ item.submitTime }}</span>
            </div>
            <div class="workorder-handler" v-if="item.handler">
              <span>处理人：{{ item.handler }}</span>
              <span>更新时间：{{ item.updateTime }}</span>
            </div>
            <div class="workorder-actions">
              <button class="detail-btn" @click="viewWorkOrderDetail(item)">查看详情</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <SupervisorNav />

    <!-- 工单详情模态框 -->
    <div class="modal" v-if="showDetailModal" @click.self="closeDetailModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>工单详情</h2>
          <button class="close-btn" @click="closeDetailModal">&times;</button>
        </div>
        <!-- 详情加载状态 -->
        <div class="modal-body loading-container" v-if="detailLoading">
          <div class="loading-spinner"></div>
          <p>正在加载工单详情...</p>
        </div>

        <!-- 详情内容 -->
        <div class="modal-body" v-else-if="selectedWorkOrder">
          <div class="detail-item">
            <label>工单编号</label>
            <div class="value">{{ selectedWorkOrder.number }}</div>
          </div>
          <div class="detail-item">
            <label>工单状态</label>
            <div class="value">
              <span class="status-tag" :class="selectedWorkOrder.status">
                {{ selectedWorkOrder.status }}
              </span>
            </div>
          </div>
          <div class="detail-item">
            <label>任务类型</label>
            <div class="value">{{ selectedWorkOrder.typeText }}</div>
          </div>
          <div class="detail-item">
            <label>任务描述</label>
            <div class="value description">{{ selectedWorkOrder.description }}</div>
          </div>
          <div class="detail-item">
            <label>产线信息</label>
            <div class="value">{{ selectedWorkOrder.location }}</div>
          </div>
          <div class="detail-item">
            <label>发出人</label>
            <div class="value">{{ selectedWorkOrder.submitter }}</div>
          </div>
          <div class="detail-item">
            <label>负责工长</label>
            <div class="value">{{ selectedWorkOrder.foreman || '未指定' }}</div>
          </div>
          <div class="detail-item">
            <label>负责班组</label>
            <div class="value">{{ selectedWorkOrder.team || '未指定' }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkOrder.handler">
            <label>负责组员</label>
            <div class="value">{{ selectedWorkOrder.handler }}</div>
          </div>
          <div class="detail-item">
            <label>创建时间</label>
            <div class="value">{{ selectedWorkOrder.submitTime }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkOrder.updateTime">
            <label>更新时间</label>
            <div class="value">{{ selectedWorkOrder.updateTime }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkOrder.startTime">
            <label>开始时间</label>
            <div class="value">{{ selectedWorkOrder.startTime }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkOrder.deadline">
            <label>截止时间</label>
            <div class="value">{{ selectedWorkOrder.deadline }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkOrder.actualEndTime">
            <label>实际结束时间</label>
            <div class="value">{{ selectedWorkOrder.actualEndTime }}</div>
          </div>

          <!-- 扩展字段显示 -->
          <div class="detail-section" v-if="selectedWorkOrder.extension_fields && Object.keys(selectedWorkOrder.extension_fields).length > 0">
            <h3>扩展信息</h3>
            <div class="detail-item" v-for="(value, key) in selectedWorkOrder.extension_fields" :key="key">
              <label>{{ formatExtensionKey(key) }}</label>
              <div class="value">{{ formatExtensionValue(value) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SupervisorNav from '@/components/SupervisorNav.vue'
import { Message } from 'element-ui'

export default {
  name: 'WorkOrders',
  components: {
    SupervisorNav
  },
  data() {
    return {
      filterType: 'all',
      filterStatus: 'all',
      searchKeyword: '',
      workorders: [],
      loading: false,
      showDetailModal: false,
      selectedWorkOrder: null,
      detailLoading: false
    }
  },
  created() {
    // 获取所有工单数据
    this.fetchAllWorkorders();
  },
  methods: {
    // 获取所有工单
    async fetchAllWorkorders() {
      try {
        this.loading = true;
        const response = await fetch('/api/workorders/all-workorders', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('原始工单数据:', data);

        if (data.success && Array.isArray(data.data)) {
          // 处理工单数据
          this.workorders = data.data.map(workorder => {
            // 将数据库中的字段映射到前端显示字段
            return {
              id: workorder.id || Math.random().toString(36).substring(2, 9),
              number: workorder.workorder_number,
              type: workorder.task_type,
              typeText: this.getTypeText(workorder.task_type),
              title: this.getWorkOrderTitle(workorder),
              description: workorder.task_details,
              location: workorder.production_line,
              submitter: workorder.creator,
              submitTime: this.formatDateTime(workorder.created_at),
              status: workorder.status,
              handler: workorder.team_members,
              updateTime: this.formatDateTime(workorder.updated_at),
              extension_fields: workorder.extension_fields
            };
          });
        } else {
          console.error('获取工单列表失败:', data.error || '未知错误');
          Message.error('获取工单列表失败');
        }
      } catch (error) {
        console.error('请求工单列表出错:', error);
        Message.error('获取工单列表失败');
      } finally {
        this.loading = false;
      }
    },

    // 格式化日期时间
    formatDateTime(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleString();
    },



    // 获取类型显示文本
    getTypeText(type) {
      if (!type) return '未知类型';

      const typeMap = {
        // 英文类型映射
        'schedule': '排班任务',
        'maintenance': '设备维护',
        'inspection': '产线巡检',
        // 中文类型直接返回
        '排班任务': '排班任务',
        '设备维护': '设备维护',
        '产线巡检': '产线巡检'
      };
      return typeMap[type] || type;
    },

    // 根据工单数据生成标题
    getWorkOrderTitle(workorder) {
      const type = workorder.task_type;

      // 处理英文类型
      if (type === 'maintenance' || type === '设备维护') {
        return `设备维护: ${workorder.production_line}`;
      } else if (type === 'inspection' || type === '产线巡检') {
        return `产线巡检: ${workorder.production_line}`;
      } else if (type === 'schedule' || type === '排班任务') {
        return `排班任务: ${workorder.production_line}`;
      } else {
        // 其他类型或未知类型
        return workorder.task_details ?
          (workorder.task_details.substring(0, 20) + (workorder.task_details.length > 20 ? '...' : '')) :
          `${type}: ${workorder.production_line}`;
      }
    },

    // 查看工单详情
    async viewWorkOrderDetail(workorder) {
      this.selectedWorkOrder = { ...workorder };
      this.showDetailModal = true;

      // 如果需要从后端获取更详细的工单信息，可以在这里调用API
      try {
        this.detailLoading = true;
        const response = await fetch(`/api/workorders/workorder-detail?number=${workorder.number}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('工单详情数据:', data);

        if (data.success && data.data) {
          // 合并详细数据到当前选中的工单
          const detailData = data.data;

          // 添加额外的详细信息
          this.selectedWorkOrder.foreman = detailData.foreman;
          this.selectedWorkOrder.team = detailData.team;
          this.selectedWorkOrder.startTime = this.formatDateTime(detailData.start_time);
          this.selectedWorkOrder.deadline = this.formatDateTime(detailData.deadline);
          this.selectedWorkOrder.actualEndTime = this.formatDateTime(detailData.actual_end_time);

          // 如果有扩展字段，确保它是对象形式
          if (typeof detailData.extension_fields === 'string') {
            try {
              this.selectedWorkOrder.extension_fields = JSON.parse(detailData.extension_fields);
            } catch (e) {
              console.error('解析扩展字段失败:', e);
            }
          } else {
            this.selectedWorkOrder.extension_fields = detailData.extension_fields || {};
          }
        }
      } catch (error) {
        console.error('获取工单详情出错:', error);
        Message.error('获取工单详情失败');
      } finally {
        this.detailLoading = false;
      }
    },

    // 关闭工单详情模态框
    closeDetailModal() {
      this.showDetailModal = false;
      this.selectedWorkOrder = null;
    },

    // 格式化扩展字段的键
    formatExtensionKey(key) {
      // 将下划线转换为空格，首字母大写
      return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    },

    // 格式化扩展字段的值
    formatExtensionValue(value) {
      if (value === null || value === undefined) {
        return '-';
      }

      // 如果是日期字符串，尝试格式化
      if (typeof value === 'string' && value.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/)) {
        return this.formatDateTime(value);
      }

      return value;
    }
  },
  computed: {
    pendingCount() {
      return this.workorders.filter(w => w.status === 'pending' || w.status === '未接受').length
    },
    processingCount() {
      return this.workorders.filter(w => w.status === 'processing' || w.status === '进行中').length
    },
    completedCount() {
      return this.workorders.filter(w => w.status === 'completed' || w.status === '已完成').length
    },
    filteredWorkorders() {
      return this.workorders.filter(w => {
        // 处理类型匹配，只保留前三种类型
        let typeMatch = this.filterType === 'all';
        if (!typeMatch) {
          // 英文类型对应关系
          const typeMapping = {
            'maintenance': '设备维护',
            'inspection': '产线巡检',
            'schedule': '排班任务'
          };

          // 直接匹配
          if (w.type === this.filterType) {
            typeMatch = true;
          }
          // 英文类型匹配中文类型
          else if (typeMapping[w.type] === this.filterType) {
            typeMatch = true;
          }
          // 中文类型匹配英文类型
          else if (w.type === typeMapping[this.filterType]) {
            typeMatch = true;
          }
        }

        const statusMatch = this.filterStatus === 'all' || w.status === this.filterStatus;
        const searchMatch = !this.searchKeyword ||
          w.number.includes(this.searchKeyword) ||
          (w.submitter && w.submitter.includes(this.searchKeyword));

        return typeMatch && statusMatch && searchMatch;
      });
    }
  }
}
</script>

<style scoped>
.workorders {
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

.stat-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-card h3 {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 14px;
}

.count {
  font-size: 24px;
  font-weight: bold;
}

.count.pending { color: #ff9800; }
.count.processing { color: #2196F3; }
.count.completed { color: #4CAF50; }

.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.filter-select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 120px;
}

.search-input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

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
  color: #333;
}

.workorder-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.workorder-status.pending, .workorder-status.\u672a\u63a5\u53d7 {
  background: #fff3e0;
  color: #ff9800;
}

.workorder-status.processing, .workorder-status.\u8fdb\u884c\u4e2d {
  background: #e3f2fd;
  color: #2196F3;
}

.workorder-status.completed, .workorder-status.\u5df2\u5b8c\u6210 {
  background: #e8f5e9;
  color: #4CAF50;
}

.workorder-status.cancelled, .workorder-status.\u5df2\u53d6\u6d88 {
  background: #f5f5f5;
  color: #9e9e9e;
}

.workorder-content h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.description {
  color: #666;
  margin-bottom: 10px;
}

.workorder-info {
  display: flex;
  gap: 15px;
  color: #333;
  margin-bottom: 8px;
}

.workorder-meta, .workorder-handler {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #666;
  margin-top: 8px;
}

/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #2196F3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 空数据提示样式 */
.empty-container {
  text-align: center;
  padding: 40px 0;
  color: #666;
  font-size: 16px;
}

/* 工单操作按钮 */
.workorder-actions {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

.detail-btn {
  background-color: #2196F3;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.detail-btn:hover {
  background-color: #0b7dda;
}

/* 模态框样式 */
.modal {
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
  width: 80%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
}

/* 详情页样式 */
.detail-item {
  margin-bottom: 15px;
  display: flex;
}

.detail-item label {
  width: 120px;
  font-weight: bold;
  color: #666;
  flex-shrink: 0;
}

.detail-item .value {
  flex: 1;
}

.detail-item .description {
  white-space: pre-wrap;
}

.status-tag {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 14px;
}

.status-tag.pending, .status-tag.未接受 {
  background-color: #ffecb3;
  color: #ff9800;
}

.status-tag.processing, .status-tag.进行中 {
  background-color: #e3f2fd;
  color: #2196F3;
}

.status-tag.completed, .status-tag.已完成 {
  background-color: #e8f5e9;
  color: #4caf50;
}

.status-tag.cancelled, .status-tag.已取消 {
  background-color: #f5f5f5;
  color: #9e9e9e;
}

.detail-section {
  margin-top: 20px;
  border-top: 1px solid #eee;
  padding-top: 15px;
}

.detail-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
  font-size: 18px;
}
</style>
