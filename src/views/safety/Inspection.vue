<template>
  <div class="inspection">
    <header class="header">
      <h1>产线安全巡检</h1>
    </header>

    <div class="content">
      <div class="task-filter">
        <select v-model="filterStatus" class="filter-select">
          <option value="all">全部工单</option>
          <option value="pending">待巡检</option>
          <option value="processing">巡检中</option>
          <option value="completed">已完成</option>
          <option value="cancelled">已取消</option>
        </select>
        <button class="add-btn" @click="addInspection">新建巡检</button>
      </div>

      <!-- 加载中提示 -->
      <div class="loading-container" v-if="loading">
        <div class="loading-spinner"></div>
        <p>正在加载工单数据...</p>
      </div>

      <!-- 错误提示 -->
      <div class="error-container" v-if="error">
        <p class="error-message">{{ error }}</p>
        <button class="retry-btn" @click="fetchWorkorders">重试</button>
      </div>

      <!-- 空数据提示 -->
      <div class="empty-container" v-if="!loading && !error && filteredTasks.length === 0">
        <p>没有找到相关工单</p>
      </div>

      <!-- 工单列表 -->
      <div class="task-list" v-if="!loading && !error && filteredTasks.length > 0">
        <div class="task-item" v-for="(task, index) in filteredTasks" :key="index">
          <div class="task-header">
            <span class="task-id">#{{ task.id }}</span>
            <span class="task-status" :class="task.status">{{ task.statusText }}</span>
          </div>
          <div class="task-title">
            <h3>
              {{ task.name }}
              <span class="emergency-badge" v-if="task.original && task.original.extension_fields && getExtensionFields(task.original.extension_fields).is_emergency">⚡ 紧急</span>
            </h3>
          </div>
          <div class="task-info">
            <p><strong>产线信息：</strong>{{ task.area }}</p>
            <p><strong>描述：</strong>{{ task.description }}</p>
            <p><strong>发出人：</strong>{{ task.creator_name }} ({{ task.creator }})</p>
            <p><strong>负责工长：</strong>{{ task.foreman_name }} ({{ task.foreman }})</p>
            <div class="task-dates">
              <p><strong>创建时间：</strong>{{ task.time }}</p>
              <p v-if="task.deadline"><strong>截止时间：</strong>{{ task.deadline }}</p>
            </div>
          </div>
          <div class="task-actions">
            <button class="detail-btn" @click="viewTaskDetail(task)">查看详情</button>
            <button class="start-btn" v-if="task.status === 'pending'" @click="startInspection(task)">开始巡检</button>
            <button class="complete-btn" v-if="task.status === 'processing'" @click="completeInspection(task)">完成巡检</button>
          </div>
        </div>
      </div>
    </div>

    <SafetyNav />

    <!-- 完成巡检模态框 -->
    <div class="modal" v-if="showCompleteModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>完成巡检</h3>
          <span class="close-btn" @click="showCompleteModal = false">&times;</span>
        </div>
        <div class="modal-body">
          <div class="detail-item">
            <label>工单编号</label>
            <div class="value">{{ selectedTask.id }}</div>
          </div>
          <div class="detail-item">
            <label>巡检类型</label>
            <div class="value">{{ selectedTask.name }}</div>
          </div>
          <div class="detail-item">
            <label>产线信息</label>
            <div class="value">{{ selectedTask.area }}</div>
          </div>
          <div class="detail-item">
            <label>完成报告</label>
            <textarea
              class="form-input"
              v-model="completionNote"
              rows="5"
              placeholder="请输入巡检完成报告和备注信息"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="showCompleteModal = false">取消</button>
          <button class="btn submit" @click="submitCompletion">提交</button>
        </div>
      </div>
    </div>

    <!-- 查看详情模态框 -->
    <div class="modal" v-if="showDetailModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>工单详情</h3>
          <span class="close-btn" @click="showDetailModal = false">&times;</span>
        </div>
        <div class="modal-body">
          <div class="detail-item">
            <label>工单编号</label>
            <div class="value">{{ detailTask.id }}</div>
          </div>
          <div class="detail-item">
            <label>巡检类型</label>
            <div class="value">
              {{ detailTask.name }}
              <span class="emergency-badge" v-if="detailTask.original && detailTask.original.extension_fields && getExtensionFields(detailTask.original.extension_fields).is_emergency">⚡ 紧急</span>
            </div>
          </div>
          <div class="detail-item">
            <label>工单状态</label>
            <div class="value">
              <span class="status-tag" :class="detailTask.status">{{ detailTask.statusText }}</span>
            </div>
          </div>
          <div class="detail-item">
            <label>产线信息</label>
            <div class="value">{{ detailTask.area }}</div>
          </div>
          <div class="detail-item">
            <label>工单描述</label>
            <div class="value">{{ detailTask.description }}</div>
          </div>
          <div class="detail-item">
            <label>发出人</label>
            <div class="value">{{ detailTask.creator_name }} ({{ detailTask.creator }})</div>
          </div>
          <div class="detail-item">
            <label>负责工长</label>
            <div class="value">{{ detailTask.foreman_name }} ({{ detailTask.foreman }})</div>
          </div>
          <div class="detail-item" v-if="detailTask.team_members">
            <label>负责组员</label>
            <div class="value">{{ detailTask.team_member_name }} ({{ detailTask.team_members }})</div>
          </div>
          <div class="detail-item" v-if="detailTask.team">
            <label>负责班组</label>
            <div class="value">{{ detailTask.team }}</div>
          </div>
          <div class="detail-item">
            <label>创建时间</label>
            <div class="value">{{ detailTask.time }}</div>
          </div>
          <div class="detail-item" v-if="detailTask.original && detailTask.original.start_time">
            <label>开始时间</label>
            <div class="value">{{ formatDateTime(detailTask.original.start_time) }}</div>
          </div>
          <div class="detail-item" v-if="detailTask.deadline">
            <label>截止时间</label>
            <div class="value">{{ detailTask.deadline }}</div>
          </div>
          <div class="detail-item" v-if="detailTask.original && detailTask.original.actual_end_time">
            <label>实际完成时间</label>
            <div class="value">{{ formatDateTime(detailTask.original.actual_end_time) }}</div>
          </div>
          <div class="detail-item" v-if="detailTask.note">
            <label>完成报告</label>
            <div class="value note-content">{{ detailTask.note }}</div>
          </div>
          <!-- 产线巡检工单的扩展字段 -->
          <div class="detail-item" v-if="detailTask.original && detailTask.original.extension_fields && getExtensionFields(detailTask.original.extension_fields).inspection_items">
            <label>巡检项目</label>
            <div class="value">{{ getExtensionFields(detailTask.original.extension_fields).inspection_items }}</div>
          </div>
          <div class="detail-item" v-if="detailTask.original && detailTask.original.extension_fields && getExtensionFields(detailTask.original.extension_fields).inspection_frequency">
            <label>巡检频率</label>
            <div class="value">{{ getExtensionFields(detailTask.original.extension_fields).inspection_frequency }}</div>
          </div>
          <div class="detail-item" v-if="detailTask.original && detailTask.original.extension_fields && getExtensionFields(detailTask.original.extension_fields).inspection_standard">
            <label>巡检标准</label>
            <div class="value">{{ getExtensionFields(detailTask.original.extension_fields).inspection_standard }}</div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="showDetailModal = false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SafetyNav from '@/components/SafetyNav.vue'

export default {
  name: 'SafetyInspection',
  components: {
    SafetyNav
  },
  data() {
    return {
      filterStatus: 'all',
      tasks: [],
      loading: false,
      error: null,
      // 用户名缓存
      usernameCache: {},
      // 完成巡检模态框
      showCompleteModal: false,
      selectedTask: {},
      completionNote: '',
      // 查看详情模态框
      showDetailModal: false,
      detailTask: {}
    }
  },
  created() {
    this.fetchWorkorders();
  },
  computed: {
    filteredTasks() {
      if (this.filterStatus === 'all') return this.tasks
      return this.tasks.filter(task => task.status === this.filterStatus)
    }
  },
  methods: {
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

        // 获取安全员组的产线巡检工单
        const response = await fetch(`/api/workorders/safety-inspection-workorders?group_id=${groupId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取工单失败: ${response.status}`);
        }

        const data = await response.json();
        console.log('安全员产线巡检工单数据:', data);

        if (data.success) {
          this.tasks = this.formatWorkorders(data.data || []);
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
            statusText = '待巡检';
            status = 'pending';
            break;

          case '已完成':
          case 'completed':
            statusText = '已完成';
            status = 'completed';
            break;

          case '已接受':
          case 'accepted':
            statusText = '巡检中';
            status = 'processing';
            break;

          case '已取消':
          case 'cancelled':
            statusText = '已取消';
            status = 'cancelled';
            break;
        }

        return {
          id: wo.workorder_number,
          name: wo.task_type,
          area: wo.production_line,
          time: this.formatDateTime(wo.created_at),
          deadline: this.formatDateTime(wo.deadline),
          status: status,
          statusText: statusText,
          description: wo.task_details,
          creator: wo.creator,
          creator_name: wo.creator_name || wo.creator,
          foreman: wo.foreman,
          foreman_name: wo.foreman_name || wo.foreman,
          team_members: wo.team_members,
          team_member_name: wo.team_member_name || wo.team_members,
          note: wo.note || '',
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

    addInspection() {
      console.log('新建巡检任务');
      alert('新建巡检功能开发中');
    },

    startInspection(task) {
      console.log('开始巡检:', task);

      // 更新工单状态为已接受
      this.updateWorkOrderStatus(task.id, '已接受');
    },

    completeInspection(task) {
      console.log('完成巡检:', task);

      // 显示完成巡检模态框
      this.selectedTask = task;
      this.completionNote = '';
      this.showCompleteModal = true;
    },

    // 提交完成报告
    submitCompletion() {
      if (!this.completionNote.trim()) {
        alert('请填写完成报告');
        return;
      }

      // 更新工单状态为已完成，并传递完成报告
      this.updateWorkOrderStatus(this.selectedTask.id, '已完成', this.completionNote);

      // 关闭模态框
      this.showCompleteModal = false;
    },

    viewTaskDetail(task) {
      console.log('查看工单详情:', task);
      // 设置详情任务并显示模态框
      this.detailTask = { ...task };
      this.showDetailModal = true;
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
    async updateWorkOrderStatus(workorderNumber, newStatus, note = '') {
      try {
        // 准备更新数据
        const updateData = {
          status: newStatus
        };

        // 如果有完成报告，添加到更新数据中
        if (note) {
          updateData.note = note;
        }

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
          alert('工单状态更新成功');
        } else {
          alert(`更新失败: ${data.error || '未知错误'}`);
        }
      } catch (error) {
        console.error('更新工单状态出错:', error);
        alert(`更新工单状态出错: ${error.message}`);
      }
    }
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

.inspection {
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

.task-filter {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.filter-select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.add-btn {
  padding: 8px 16px;
  background: #4CAF50;
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

.task-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.task-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.task-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  align-items: center;
}

.task-id {
  font-size: 14px;
  color: #757575;
}

.task-title h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.task-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.task-status.pending {
  background: #fff3e0;
  color: #ff9800;
}

.task-status.processing {
  background: #e3f2fd;
  color: #2196F3;
}

.task-status.completed {
  background: #e8f5e9;
  color: #4CAF50;
}

.task-status.cancelled, .status-tag.cancelled {
  background: #f5f5f5;
  color: #757575;
}

.status-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  display: inline-block;
}

.note-content {
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

.task-info {
  color: #666;
  font-size: 14px;
  margin-bottom: 15px;
}

.task-info p {
  margin: 8px 0;
}

.task-dates {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 12px;
  color: #757575;
}

.task-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.detail-btn {
  padding: 8px 16px;
  background: #9e9e9e;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.start-btn {
  padding: 8px 16px;
  background: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.complete-btn {
  padding: 8px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
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
