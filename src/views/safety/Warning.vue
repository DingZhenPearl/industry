<template>
  <div class="safety-warning">
    <header class="header">
      <h1>设备维护工单</h1>
    </header>

    <div class="content">
      <!-- 工单处理内容 -->
      <div class="workorder-list">
        <!-- 日期筛选 -->
        <div class="date-filter-container">
          <div class="date-filter">
            <button
              class="date-filter-btn"
              :class="{ active: !showAllWorkorders }"
              @click="toggleWorkorderDateFilter(false)"
            >
              仅显示今日工单
            </button>
            <button
              class="date-filter-btn"
              :class="{ active: showAllWorkorders }"
              @click="toggleWorkorderDateFilter(true)"
            >
              显示全部工单
            </button>
          </div>
        </div>

        <div class="workorder-filter">
          <select v-model="workorderFilter" class="filter-select">
            <option value="all">全部工单</option>
            <option value="pending">待处理</option>
            <option value="processing">处理中</option>
            <option value="completed">已完成</option>
            <option value="cancelled">已取消</option>
          </select>
          <button class="refresh-btn" @click="fetchWorkorders">刷新</button>
        </div>

        <!-- 加载中提示 -->
        <div class="loading-container" v-if="loading">
          <div class="loading-spinner"></div>
          <p>正在加载设备维护工单数据...</p>
        </div>

        <!-- 错误提示 -->
        <div class="error-container" v-if="error">
          <p class="error-message">{{ error }}</p>
          <button class="retry-btn" @click="fetchWorkorders">重试</button>
        </div>

        <!-- 空数据提示 -->
        <div class="empty-container" v-if="!loading && !error && filteredWorkorders.length === 0">
          <p>没有找到相关设备维护工单</p>
        </div>

        <!-- 工单列表 -->
        <div class="workorder-items" v-if="!loading && !error && filteredWorkorders.length > 0">
          <div class="workorder-item" v-for="(item, index) in filteredWorkorders" :key="index">
            <div class="workorder-header">
              <span class="workorder-number">{{ item.number }}</span>
              <span class="workorder-status" :class="item.status">{{ item.statusText }}</span>
            </div>
            <div class="workorder-content">
              <h3 class="workorder-title">
                {{ item.title }}
                <span class="emergency-badge" v-if="item.original && item.original.extension_fields && getExtensionFields(item.original.extension_fields).is_emergency">⚡ 紧急</span>
              </h3>
              <p>{{ item.description }}</p>
              <div class="workorder-meta">
                <span>上报人：{{ item.reporter }}</span>
                <span>位置：{{ item.location }}</span>
              </div>
              <div class="workorder-time">上报时间：{{ item.submitTime }}</div>
            </div>
            <div class="workorder-actions">
              <button
                class="action-btn"
                @click="showWorkorderDetail(item)"
              >查看详情</button>
              <button
                class="action-btn primary"
                @click="startProcessWorkorder(item)"
                v-if="item.status === 'pending'"
              >开始处理</button>
              <button
                class="action-btn primary"
                @click="showCompleteWorkorderModal(item)"
                v-else-if="item.status === 'processing'"
              >完成工单</button>
            </div>
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
            <div class="value">
              {{ selectedWorkorder.title }}
              <span class="emergency-badge" v-if="selectedWorkorder.original && selectedWorkorder.original.extension_fields && getExtensionFields(selectedWorkorder.original.extension_fields).is_emergency">⚡ 紧急</span>
            </div>
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
          <div class="detail-item" v-if="selectedWorkorder.original && selectedWorkorder.original.foreman">
            <label>负责工长</label>
            <div class="value">{{ selectedWorkorder.original.foreman_name || selectedWorkorder.original.foreman }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkorder.original && selectedWorkorder.original.team_members">
            <label>负责组员</label>
            <div class="value">{{ selectedWorkorder.original.team_member_name || selectedWorkorder.original.team_members }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkorder.original && selectedWorkorder.original.team">
            <label>负责班组</label>
            <div class="value">{{ selectedWorkorder.original.team }}</div>
          </div>
          <div class="detail-item">
            <label>创建时间</label>
            <div class="value">{{ selectedWorkorder.submitTime }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkorder.original && selectedWorkorder.original.start_time">
            <label>开始时间</label>
            <div class="value">{{ formatDateTime(selectedWorkorder.original.start_time) }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkorder.original && selectedWorkorder.original.deadline">
            <label>截止时间</label>
            <div class="value">{{ formatDateTime(selectedWorkorder.original.deadline) }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkorder.original && selectedWorkorder.original.actual_end_time">
            <label>实际完成时间</label>
            <div class="value">{{ formatDateTime(selectedWorkorder.original.actual_end_time) }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkorder.handlerNote">
            <label>处理记录</label>
            <div class="value note-content">{{ selectedWorkorder.handlerNote }}</div>
          </div>
          <!-- 设备维修工单的扩展字段 -->
          <div class="detail-item" v-if="selectedWorkorder.original && selectedWorkorder.original.extension_fields && getExtensionFields(selectedWorkorder.original.extension_fields).device_id">
            <label>设备编号</label>
            <div class="value">{{ getExtensionFields(selectedWorkorder.original.extension_fields).device_id }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkorder.original && selectedWorkorder.original.extension_fields && getExtensionFields(selectedWorkorder.original.extension_fields).device_name">
            <label>设备名称</label>
            <div class="value">{{ getExtensionFields(selectedWorkorder.original.extension_fields).device_name }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkorder.original && selectedWorkorder.original.extension_fields && getExtensionFields(selectedWorkorder.original.extension_fields).device_info">
            <label>设备信息</label>
            <div class="value">{{ getExtensionFields(selectedWorkorder.original.extension_fields).device_info }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkorder.original && selectedWorkorder.original.extension_fields && getExtensionFields(selectedWorkorder.original.extension_fields).discovery_time">
            <label>发现时间</label>
            <div class="value">{{ formatDateTime(getExtensionFields(selectedWorkorder.original.extension_fields).discovery_time) }}</div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="showWorkorderDetailModal = false">关闭</button>
        </div>
      </div>
    </div>

    <!-- 完成工单模态框 -->
    <div class="modal" v-if="showCompleteModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>完成工单</h3>
          <span class="close-btn" @click="showCompleteModal = false">&times;</span>
        </div>
        <div class="modal-body">
          <div class="detail-item">
            <label>工单编号</label>
            <div class="value">{{ selectedWorkorder.number }}</div>
          </div>
          <div class="detail-item">
            <label>工单标题</label>
            <div class="value">{{ selectedWorkorder.title }}</div>
          </div>
          <div class="detail-item">
            <label>设备位置</label>
            <div class="value">{{ selectedWorkorder.location }}</div>
          </div>
          <div class="detail-item">
            <label>处理记录</label>
            <textarea
              v-model="handlerNote"
              class="form-input"
              rows="5"
              placeholder="请输入处理记录"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="showCompleteModal = false">取消</button>
          <button class="btn submit" @click="completeWorkorder">提交</button>
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
      workorderFilter: 'all',
      showWorkorderDetailModal: false,
      showCompleteModal: false,
      handlerNote: '',
      selectedWorkorder: {},
      loading: false,
      error: null,
      workorders: [],
      // 工单日期筛选
      showAllWorkorders: false,
      // 用户名缓存
      usernameCache: {}
    }
  },
  created() {
    this.fetchWorkorders();
  },
  computed: {
    filteredWorkorders() {
      if (this.workorderFilter === 'all') return this.workorders;
      return this.workorders.filter(item => item.status === this.workorderFilter);
    }
  },
  methods: {
    // 切换工单日期筛选
    toggleWorkorderDateFilter(showAll) {
      if (this.showAllWorkorders !== showAll) {
        this.showAllWorkorders = showAll;
        this.fetchWorkorders();
      }
    },

    // 从后端获取工单数据
    async fetchWorkorders() {
      this.loading = true;
      this.error = null;

      try {
        // 获取当前登录用户的组号
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
        const groupId = userInfo.group_id;

        if (!groupId) {
          console.error('未找到组号信息');
          this.error = '无法获取您的组号信息，请重新登录';
          return;
        }

        // 获取安全员组的设备维护工单
        const showAllParam = this.showAllWorkorders ? '&showAll=true' : '';
        const response = await fetch(`/api/workorders/safety-maintenance-workorders?group_id=${groupId}${showAllParam}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取工单失败: ${response.status}`);
        }

        const data = await response.json();
        console.log('安全员设备维护工单数据:', data);

        if (data.success) {
          this.workorders = this.formatWorkorders(data.data || []);
        } else {
          this.error = data.error || '获取工单失败';
        }
      } catch (error) {
        console.error('获取工单数据出错:', error);
        this.error = error.message || '获取工单数据出错';
      } finally {
        this.loading = false;
      }
    },

    // 格式化工单数据
    formatWorkorders(workorders) {
      return workorders.map(wo => {
        // 根据状态设置状态文本
        let statusText = '未知';
        let status = wo.status;

        switch(wo.status) {
          case '未接受':
          case 'pending':
            statusText = '待处理';
            status = 'pending';
            break;

          case '已完成':
          case 'completed':
            statusText = '已完成';
            status = 'completed';
            break;

          case '已接受':
          case 'accepted':
            statusText = '处理中';
            status = 'processing';
            break;

          case '已取消':
          case 'cancelled':
            statusText = '已取消';
            status = 'cancelled';
            break;
        }

        return {
          id: wo.id,
          number: wo.workorder_number,
          title: wo.task_type,
          description: wo.task_details,
          location: wo.production_line,
          reporter: wo.creator_name || wo.creator,
          submitTime: this.formatDateTime(wo.created_at),
          status: status,
          statusText: statusText,
          handlerNote: wo.note || '',
          // 保存原始工单数据
          original: wo
        };
      });
    },

    // 格式化日期时间
    formatDateTime(dateTimeStr) {
      if (!dateTimeStr) return '';

      const date = new Date(dateTimeStr);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    },



    showWorkorderDetail(workorder) {
      this.selectedWorkorder = { ...workorder };
      this.showWorkorderDetailModal = true;
    },

    // 开始处理工单
    async startProcessWorkorder(workorder) {
      this.selectedWorkorder = { ...workorder };
      // 直接更新工单状态为已接受，不需要处理记录
      const success = await this.updateWorkOrderStatus(workorder.number, '已接受');

      if (success) {
        alert('已开始处理工单');
      }
    },

    // 显示完成工单模态框
    showCompleteWorkorderModal(workorder) {
      this.selectedWorkorder = { ...workorder };
      this.handlerNote = '';
      this.showCompleteModal = true;
    },

    // 解析扩展字段
    getExtensionFields(extensionFields) {
      if (!extensionFields) return {};

      try {
        let fields = extensionFields;

        // 如果是字符串，尝试解析为JSON
        if (typeof extensionFields === 'string') {
          fields = JSON.parse(extensionFields);
        }

        // 处理嵌套对象，将其转换为字符串表示
        const result = {};
        for (const key in fields) {
          const value = fields[key];
          if (value === null) {
            result[key] = '无';
          } else if (typeof value === 'object') {
            result[key] = JSON.stringify(value);
          } else {
            result[key] = value;
          }
        }

        return result;
      } catch (error) {
        console.error('解析扩展字段失败:', error);
        return { error: '解析扩展字段失败', raw: String(extensionFields) };
      }
    },

    // 更新工单状态
    async updateWorkOrderStatus(workorderNumber, newStatus, note) {
      try {
        // 准备更新数据
        const updateData = {
          status: newStatus,
          note: note
        };

        // 如果是完成状态，添加完成时间
        if (newStatus === '已完成') {
          // 格式化日期时间为MySQL兼容格式
          const now = new Date();
          const formatDate = (date) => {
            return date.getFullYear() + '-' +
                   String(date.getMonth() + 1).padStart(2, '0') + '-' +
                   String(date.getDate()).padStart(2, '0') + ' ' +
                   String(date.getHours()).padStart(2, '0') + ':' +
                   String(date.getMinutes()).padStart(2, '0') + ':' +
                   String(date.getSeconds()).padStart(2, '0');
          };

          updateData.actual_end_time = formatDate(now);
        }

        const response = await fetch('/api/workorders/update-workorder', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            workorder_number: workorderNumber,
            update_data: updateData
          })
        });

        if (!response.ok) {
          throw new Error(`更新工单状态失败: ${response.status}`);
        }

        const data = await response.json();
        console.log('更新工单状态响应:', data);

        if (data.success) {
          // 更新成功，重新获取工单列表
          this.fetchWorkorders();
          return true;
        } else {
          alert(`更新失败: ${data.error || '未知错误'}`);
          return false;
        }
      } catch (error) {
        console.error('更新工单状态出错:', error);
        alert(`更新工单状态出错: ${error.message}`);
        return false;
      }
    },



    async completeWorkorder() {
      if (!this.handlerNote.trim()) {
        alert('请填写处理记录');
        return;
      }

      // 更新工单状态为已完成
      const success = await this.updateWorkOrderStatus(this.selectedWorkorder.number, '已完成', this.handlerNote);

      if (success) {
        this.showCompleteModal = false;
        alert('工单已完成');
      }
    },


  }
}
</script>

<style scoped>
/* 紧急工单标记样式 */
.emergency-badge {
  display: inline-block;
  background-color: #ff4d4f;
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 8px;
  font-weight: bold;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
  100% {
    opacity: 1;
  }
}

/* 日期筛选按钮样式 */
.date-filter-container {
  margin-bottom: 15px;
}

.date-filter {
  display: flex;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #ddd;
  width: fit-content;
}

.date-filter-btn {
  padding: 8px 12px;
  background-color: #f5f5f5;
  border: none;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.date-filter-btn.active {
  background-color: #2196F3;
  color: white;
}

.date-filter-btn:hover:not(.active) {
  background-color: #e0e0e0;
}

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
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  flex: 1;
  margin-right: 10px;
  background-color: white;
}

.refresh-btn {
  padding: 8px 16px;
  background: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
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

.error-container {
  background-color: #ffebee;
  border: 1px solid #ffcdd2;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
  text-align: center;
}

.error-message {
  color: #d32f2f;
  margin-bottom: 10px;
}

.retry-btn {
  padding: 8px 16px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.empty-container {
  text-align: center;
  padding: 30px;
  color: #757575;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.workorder-items {
  display: flex;
  flex-direction: column;
  gap: 15px;
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

.detail-item .value.note-content {
  white-space: pre-wrap;
  background-color: #f9f9f9;
  padding: 10px;
  border-radius: 4px;
  border-left: 3px solid #2196F3;
}

.extension-field-item {
  margin-bottom: 8px;
  padding: 6px 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  display: flex;
}

.extension-field-key {
  font-weight: bold;
  color: #2196F3;
  margin-right: 8px;
  min-width: 100px;
}

.extension-field-value {
  flex: 1;
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
