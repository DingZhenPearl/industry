<template>
  <div class="my-workorders">
    <header class="header">
      <h1>我的工单</h1>
    </header>

    <div class="content">
      <!-- 工单筛选区域 -->
      <div class="filter-section">
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

        <div class="filter-bar">
          <div class="filter-item">
            <label class="filter-label">状态</label>
            <select v-model="workorderFilter.status" class="filter-select">
              <option value="all">全部工单</option>
              <option value="pending">待接收</option>
              <option value="accepted">已接收</option>
              <option value="completed">已完成</option>
            </select>
          </div>
          <div class="filter-item">
            <label class="filter-label">类型</label>
            <select v-model="workorderFilter.type" class="filter-select">
              <option value="all">全部类型</option>
              <option value="schedule">排班任务</option>
              <option value="maintenance">设备维护</option>
              <option value="inspection">产线巡检</option>
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
        <div class="workorder-card accepted">
          <div class="card-icon">⚙️</div>
          <div class="card-content">
            <h3>已接收工单</h3>
            <div class="count">{{ acceptedWorkordersCount }}</div>
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
        <div class="workorder-item" v-for="workorder in filteredWorkorders" :key="workorder.id" :class="workorder.displayStatus">
          <div class="workorder-header">
            <div class="workorder-left">
              <span class="workorder-type-icon" :class="workorder.type === '排班任务' ? 'schedule' :
                                                      workorder.type === '设备维护' ? 'maintenance' :
                                                      workorder.type === '产线巡检' ? 'inspection' : 'schedule'"></span>
              <span class="workorder-number">{{ workorder.number }}</span>
              <span class="emergency-badge" v-if="workorder.extension_fields && workorder.extension_fields.is_emergency">⚡ 紧急</span>
            </div>
            <span class="workorder-status" :class="workorder.displayStatus">{{ workorder.statusText }}</span>
          </div>
          <div class="workorder-body">
            <h3 class="workorder-title">{{ workorder.type }}</h3>
            <p class="workorder-desc">{{ workorder.description }}</p>
            <div class="workorder-meta">
              <div class="meta-item">
                <i class="meta-icon person"></i>
                <span>{{ workorder.assignedByName || workorder.assignedBy }}</span>
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
              v-if="workorder.displayStatus === 'pending'"
              @click="acceptWorkorder(workorder)"
            >接收工单</button>
            <button
              class="action-btn complete"
              v-if="workorder.displayStatus === 'accepted'"
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
            <div class="overview-status" :class="selectedWorkorder.displayStatus">{{ selectedWorkorder.statusText }}</div>
          </div>
          <div class="overview-type">
            {{ selectedWorkorder.type }}
            <span class="emergency-badge" v-if="selectedWorkorder.extension_fields && selectedWorkorder.extension_fields.is_emergency">⚡ 紧急</span>
          </div>
          <div class="overview-progress">
            <div class="progress-bar">
              <div
                class="progress"
                :style="{ width: (selectedWorkorder.progress || 0) + '%' }"
                :class="selectedWorkorder.displayStatus"
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
              <div class="detail-item" v-if="selectedWorkorder.displayStatus === 'completed'">
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
                <div class="value">{{ selectedWorkorder.assignedByName || selectedWorkorder.assignedBy }} ({{ selectedWorkorder.assignedBy }})</div>
              </div>
            </div>
          </div>

          <div class="detail-item" v-if="selectedWorkorder.displayStatus === 'accepted' || selectedWorkorder.displayStatus === 'completed'">
            <label>任务备注</label>
            <div class="value" v-if="selectedWorkorder.displayStatus === 'completed'">
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
            v-if="selectedWorkorder.displayStatus === 'pending'"
            @click="acceptWorkorder(selectedWorkorder)"
          >接收工单</button>

          <button
            class="btn complete"
            v-if="selectedWorkorder.displayStatus === 'accepted'"
            @click="completeWorkorder(selectedWorkorder)"
          >完成工单</button>
        </div>
      </div>
    </div>

    <!-- 完成工单备注模态框 -->
    <div class="modal" v-if="showCompleteNoteModal">
      <div class="modal-content note-modal">
        <div class="modal-header">
          <h3>完成工单</h3>
          <span class="close-btn" @click="showCompleteNoteModal = false">&times;</span>
        </div>
        <div class="modal-body">
          <div class="workorder-info">
            <div class="workorder-number">{{ workorderToComplete.number }}</div>
            <div class="workorder-desc">{{ workorderToComplete.description }}</div>
          </div>
          <div class="form-group">
            <label>完成报告</label>
            <textarea
              v-model="completeNote"
              class="form-input"
              rows="5"
              placeholder="请输入工单完成报告，详细描述工作内容和结果"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="showCompleteNoteModal = false">取消</button>
          <button class="btn complete" @click="submitCompleteWorkorder">提交并完成</button>
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
      // 工单日期筛选
      showAllWorkorders: false,

      // 模态框控制
      showWorkorderDetailModal: false,
      selectedWorkorder: {},
      taskNote: '',

      // 完成工单备注模态框
      showCompleteNoteModal: false,
      workorderToComplete: {},
      completeNote: '',

      // 工单列表数据
      workorders: [],
      responsibleWorkorders: [],
      submittedWorkorders: [],

      // 用户名缓存
      usernameCache: {}
    }
  },
  computed: {
    // 筛选后的工单列表
    filteredWorkorders() {
      return this.workorders.filter(workorder => {
        // 按状态筛选
        const statusMatch = this.workorderFilter.status === 'all' || workorder.displayStatus === this.workorderFilter.status;

        // 按类型筛选
        const typeMatch = this.workorderFilter.type === 'all' || workorder.type.includes(this.workorderFilter.type === 'schedule' ? '排班任务' :
                                                              this.workorderFilter.type === 'maintenance' ? '设备维护' :
                                                              this.workorderFilter.type === 'inspection' ? '产线巡检' : '');

        // 按关键词搜索
        const keywordMatch = !this.searchKeyword ||
                            workorder.number.toLowerCase().includes(this.searchKeyword.toLowerCase()) ||
                            workorder.description.toLowerCase().includes(this.searchKeyword.toLowerCase());

        return statusMatch && typeMatch && keywordMatch;
      });
    },

    // 待接收工单数量
    pendingWorkordersCount() {
      return this.workorders.filter(workorder => workorder.displayStatus === 'pending').length;
    },

    // 已接收工单数量
    acceptedWorkordersCount() {
      return this.workorders.filter(workorder => workorder.displayStatus === 'accepted').length;
    },

    // 已完成工单数量
    completedWorkordersCount() {
      return this.workorders.filter(workorder => workorder.displayStatus === 'completed').length;
    }
  },
  created() {
    // 检查用户信息
    const employeeId = this.getCurrentEmployeeId();
    if (!employeeId) {
      console.error('未找到用户工号信息');
      alert('无法获取您的工号信息，请重新登录');
      this.$router.push('/login');
      return;
    }

    // 页面创建时加载数据
    this.fetchWorkorders();
  },
  methods: {
    // 获取当前登录用户的工号
    getCurrentEmployeeId() {
      const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
      return userInfo.employee_id;
    },

    // 切换工单日期筛选
    toggleWorkorderDateFilter(showAll) {
      if (this.showAllWorkorders !== showAll) {
        this.showAllWorkorders = showAll;
        this.fetchWorkorders();
      }
    },

    // 从后端获取工单数据
    async fetchWorkorders() {
      try {
        // 获取当前登录用户的工号
        const employeeId = this.getCurrentEmployeeId();

        if (!employeeId) {
          console.error('未找到用户工号信息');
          alert('无法获取您的工号信息，请重新登录');
          // 重定向到登录页面
          this.$router.push('/login');
          return;
        }

        // 获取负责的工单
        const showAllParam = this.showAllWorkorders ? '&showAll=true' : '';
        const responsibleResponse = await fetch(`/api/workorders/worker-responsible-workorders?employee_id=${employeeId}${showAllParam}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!responsibleResponse.ok) {
          throw new Error(`获取负责工单失败: ${responsibleResponse.status}`);
        }

        const responsibleData = await responsibleResponse.json();
        console.log('负责工单数据:', responsibleData);

        if (responsibleData.success) {
          this.responsibleWorkorders = this.formatWorkorders(responsibleData.data || []);
        }

        // 获取提交的工单
        const submittedResponse = await fetch(`/api/workorders/worker-submitted-workorders?employee_id=${employeeId}${showAllParam}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!submittedResponse.ok) {
          throw new Error(`获取提交工单失败: ${submittedResponse.status}`);
        }

        const submittedData = await submittedResponse.json();
        console.log('提交工单数据:', submittedData);

        if (submittedData.success) {
          this.submittedWorkorders = this.formatWorkorders(submittedData.data || []);
        }

        // 合并工单列表，去除重复和自己上报的设备维护工单
        const allWorkorders = [...this.responsibleWorkorders];

        this.submittedWorkorders.forEach(submitted => {
          // 检查是否已存在于负责工单中
          const exists = allWorkorders.some(wo => wo.number === submitted.number);
          // 检查是否是设备维护工单
          const isMaintenanceWorkorder = submitted.type === '设备维护' || submitted.task_type === '设备维护';

          // 只添加非设备维护类型的自己上报的工单
          if (!exists && !isMaintenanceWorkorder) {
            allWorkorders.push(submitted);
          }
        });

        this.workorders = allWorkorders;
      } catch (error) {
        console.error('获取工单数据出错:', error);
      }
    },

    // 格式化工单数据
    formatWorkorders(workorders) {
      return workorders.map(wo => {
        // 根据状态设置状态文本
        let statusText = '未知';
        let progress = 0;
        let displayStatus = wo.status; // 用于前端显示的状态

        switch(wo.status) {
          case '未接受':
          case 'pending':
            statusText = '待接收';
            progress = 0;
            displayStatus = 'pending';
            wo.status = '未接受'; // 统一使用中文状态
            break;

          case '已完成':
          case 'completed':
            statusText = '已完成';
            progress = 100;
            displayStatus = 'completed';
            wo.status = '已完成'; // 统一使用中文状态
            break;
          case '已接受':
          case 'accepted':
            statusText = '已接收';
            progress = 10;
            displayStatus = 'accepted';
            wo.status = '已接受'; // 统一使用中文状态
            break;
          case '已取消':
          case 'cancelled':
            statusText = '已取消';
            progress = 0;
            displayStatus = 'cancelled';
            wo.status = '已取消'; // 统一使用中文状态
            break;
        }

        // 使用后端返回的用户名，不再需要获取用户名

        return {
          ...wo,
          statusText,
          progress,
          displayStatus, // 用于前端显示的状态类名
          id: wo.workorder_number || wo.number, // 确保有ID字段
          number: wo.workorder_number || wo.number,
          type: wo.task_type || wo.type,
          description: wo.task_details || wo.description,
          productionLine: wo.production_line || wo.productionLine,
          assignedBy: wo.foreman || wo.assignedBy,
          assignedByName: wo.foreman_name || wo.assignedBy, // 使用后端返回的用户名
          creatorName: wo.creator_name || wo.creator, // 使用后端返回的用户名
          teamMemberName: wo.team_member_name || wo.team_members, // 使用后端返回的用户名
          assignTime: wo.created_at || wo.assignTime,
          deadline: wo.deadline,
          startTime: wo.start_time || wo.startTime,
          completedTime: wo.actual_end_time || wo.completedTime,
          note: wo.note || ''
        };
      });
    },

    // 根据工号获取用户名
    getUsernameById(employeeId) {
      if (!employeeId) return '未知';

      // 打印调试信息
      console.log(`获取工号 ${employeeId} 的用户名, 缓存中的值:`, this.usernameCache[employeeId]);

      // 如果缓存中有该工号对应的用户名，则返回用户名
      if (this.usernameCache[employeeId]) {
        return this.usernameCache[employeeId];
      }

      // 如果缓存中没有该工号对应的用户名，则尝试获取
      // 异步获取用户名，但先返回工号作为默认值
      this.$nextTick(() => {
        this.fetchSingleUsername(employeeId);
      });

      // 返回工号作为默认值
      return employeeId;
    },

    // 获取单个工号的用户名
    async fetchSingleUsername(employeeId) {
      if (!employeeId) return;
      if (this.usernameCache[employeeId]) {
        console.log(`使用缓存中的用户名: ${employeeId} -> ${this.usernameCache[employeeId]}`);
        return;
      }

      // 直接使用工号作为用户名，避免调用API
      this.$set(this.usernameCache, employeeId, employeeId);
      console.log(`已将工号 ${employeeId} 缓存为用户名`);
      return;

      // 以下代码暂时不执行，等后端问题解决后再恢复
      /*
      try {
        console.log(`开始获取工号 ${employeeId} 的用户名`);
        console.log('当前认证令牌:', localStorage.getItem('token'));

        // 调用API获取用户名
        const response = await fetch(`/api/users/username/${employeeId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        console.log(`响应状态: ${response.status} ${response.statusText}`);
        console.log('响应头部:', response.headers);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        // 尝试解析响应内容
        let responseText;
        try {
          responseText = await response.text();

          // 检查是否是HTML响应
          if (responseText.trim().startsWith('<!doctype') || responseText.trim().startsWith('<html')) {
            console.error(`服务器返回了HTML而不是JSON，可能是认证问题`);
            this.$set(this.usernameCache, employeeId, employeeId);
            return;
          }

          const data = JSON.parse(responseText);
          console.log(`工号 ${employeeId} 的用户名数据:`, data);

          if (data.success && data.username) {
            // 更新缓存
            this.$set(this.usernameCache, employeeId, data.username);
            console.log('更新后的用户名缓存:', this.usernameCache);
          } else {
            // 如果没有找到用户名，使用工号作为用户名
            this.$set(this.usernameCache, employeeId, employeeId);
          }
        } catch (parseError) {
          console.error(`解析工号 ${employeeId} 的用户名响应失败:`, parseError);
          console.error('响应内容:', responseText);
          // 如果解析失败，使用工号作为用户名
          this.$set(this.usernameCache, employeeId, employeeId);
        }
      } catch (error) {
        console.error(`获取工号 ${employeeId} 的用户名失败:`, error);
        // 如果失败，使用工号作为用户名
        this.$set(this.usernameCache, employeeId, employeeId);
      }
      */
    },

    // 查看工单详情
    viewWorkorderDetail(workorder) {
      this.selectedWorkorder = { ...workorder };
      this.taskNote = workorder.note || '';
      this.showWorkorderDetailModal = true;
    },

    // 接收工单
    async acceptWorkorder(workorder) {
      try {
        // 获取当前登录用户的工号
        const employeeId = this.getCurrentEmployeeId();

        if (!employeeId) {
          alert('无法获取您的工号信息，请重新登录');
          this.$router.push('/login');
          return;
        }

        // 准备更新数据
        const updateData = {
          status: '已接受', // 使用中文状态
          team_members: employeeId
        };

        // 发送请求更新工单
        const response = await fetch('/api/workorders/update-workorder', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            workorder_number: workorder.number,
            update_data: updateData
          })
        });

        const data = await response.json();

        if (data.success) {
          // 更新本地工单状态
          const index = this.workorders.findIndex(w => w.number === workorder.number);
          if (index !== -1) {
            this.workorders[index].status = '已接受'; // 使用中文状态
            this.workorders[index].displayStatus = 'accepted'; // 前端显示状态仍然使用英文
            this.workorders[index].statusText = '已接收';
            this.workorders[index].progress = 10;
          }

          // 如果是在详情页操作，同步更新选中的工单
          if (this.selectedWorkorder.number === workorder.number) {
            this.selectedWorkorder.status = '已接受'; // 使用中文状态
            this.selectedWorkorder.displayStatus = 'accepted'; // 前端显示状态仍然使用英文
            this.selectedWorkorder.statusText = '已接收';
            this.selectedWorkorder.progress = 10;
          }

          // 提示用户
          alert('已成功接收工单');

          // 如果是在详情页操作，关闭详情页
          if (this.showWorkorderDetailModal) {
            this.showWorkorderDetailModal = false;
          }
        } else {
          alert(`接收工单失败: ${data.error || '未知错误'}`);
        }
      } catch (error) {
        console.error('接收工单出错:', error);
        alert('接收工单失败，请重试');
      }
    },

    // 完成工单
    completeWorkorder(workorder) {
      // 如果是从详情页完成，直接使用详情页的备注
      if (this.showWorkorderDetailModal) {
        // 验证是否填写了备注
        if (!this.taskNote.trim()) {
          alert('请填写工单执行备注');
          return;
        }

        // 使用详情页的备注完成工单
        this.doCompleteWorkorder(workorder, this.taskNote);
      } else {
        // 如果是从列表页完成，显示备注填写模态框
        this.workorderToComplete = { ...workorder };
        this.completeNote = '';
        this.showCompleteNoteModal = true;
      }
    },

    // 提交完成工单
    submitCompleteWorkorder() {
      // 验证是否填写了备注
      if (!this.completeNote.trim()) {
        alert('请填写工单完成报告');
        return;
      }

      // 完成工单
      this.doCompleteWorkorder(this.workorderToComplete, this.completeNote);

      // 关闭模态框
      this.showCompleteNoteModal = false;
    },

    // 执行完成工单的操作
    async doCompleteWorkorder(workorder, note) {

      try {
        const now = new Date();

        // 获取当前登录用户的工号
        const employeeId = this.getCurrentEmployeeId();

        if (!employeeId) {
          alert('无法获取您的工号信息，请重新登录');
          this.$router.push('/login');
          return;
        }

        // 格式化日期时间为MySQL兼容格式
        const formatDate = (date) => {
          return date.getFullYear() + '-' +
                 String(date.getMonth() + 1).padStart(2, '0') + '-' +
                 String(date.getDate()).padStart(2, '0') + ' ' +
                 String(date.getHours()).padStart(2, '0') + ':' +
                 String(date.getMinutes()).padStart(2, '0') + ':' +
                 String(date.getSeconds()).padStart(2, '0');
        };

        // 准备更新数据
        const updateData = {
          status: '已完成', // 使用中文状态
          start_time: formatDate(now), // 设置开始时间为当前时间
          actual_end_time: formatDate(now),
          team_members: employeeId, // 确保记录负责人
          note: note
        };

        // 发送请求更新工单
        const response = await fetch('/api/workorders/update-workorder', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            workorder_number: workorder.number,
            update_data: updateData
          })
        });

        const data = await response.json();

        if (data.success) {
          // 更新本地工单状态
          const index = this.workorders.findIndex(w => w.number === workorder.number);
          if (index !== -1) {
            this.workorders[index].status = '已完成'; // 使用中文状态
            this.workorders[index].displayStatus = 'completed'; // 前端显示状态仍然使用英文
            this.workorders[index].statusText = '已完成';
            this.workorders[index].startTime = now.toLocaleString();
            this.workorders[index].completedTime = now.toLocaleString();
            this.workorders[index].note = this.taskNote; // 添加备注
          }

          // 如果是在详情页操作，同步更新选中的工单
          if (this.selectedWorkorder.number === workorder.number) {
            this.selectedWorkorder.status = '已完成'; // 使用中文状态
            this.selectedWorkorder.displayStatus = 'completed'; // 前端显示状态仍然使用英文
            this.selectedWorkorder.statusText = '已完成';
            this.selectedWorkorder.startTime = now.toLocaleString();
            this.selectedWorkorder.completedTime = now.toLocaleString();
            this.selectedWorkorder.note = this.taskNote;
          }

          // 提示用户
          alert('工单已完成');

          // 如果是在详情页操作，关闭详情页
          if (this.showWorkorderDetailModal) {
            this.showWorkorderDetailModal = false;
          }
        } else {
          alert(`完成工单失败: ${data.error || '未知错误'}`);
        }
      } catch (error) {
        console.error('完成工单出错:', error);
        alert('完成工单失败，请重试');
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

.workorder-card.accepted .count {
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

.workorder-type-icon.schedule {
  background-color: #e3f2fd;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='%232196F3' d='M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z'/%3E%3C/svg%3E");
}

.workorder-type-icon.maintenance {
  background-color: #e8f5e9;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='%234CAF50' d='M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z'/%3E%3C/svg%3E");
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

/* 完成工单备注模态框样式 */
.note-modal {
  max-width: 500px;
}

.workorder-info {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.workorder-number {
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 8px;
  color: #333;
}

.workorder-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
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
