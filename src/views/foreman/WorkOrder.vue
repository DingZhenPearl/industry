<template>
  <div class="workorder">
    <header class="header">
      <div class="tab-header">
        <div class="tab-item active">
          工单管理
        </div>
      </div>
    </header>

    <div class="content">
      <!-- 工单管理内容 -->
      <div class="workorder-content">
        <!-- 筛选和操作区 -->
        <div class="filter-bar">
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

          <!-- 工单类型筛选 -->
          <div class="filter-item">
            <label for="type-filter">工单类型</label>
            <select id="type-filter" v-model="filterType" class="filter-select" @change="onFilterTypeChange">
              <option value="all">全部类型</option>
              <option value="schedule">排班任务</option>
              <option value="maintenance">设备维护</option>
              <option value="inspection">产线巡检</option>
            </select>
          </div>

          <!-- 工单状态筛选 -->
          <div class="filter-item">
            <label for="status-filter">工单状态</label>
            <select id="status-filter" v-model="filterStatus" class="filter-select">
              <option value="all">全部状态</option>
              <option value="pending">待处理</option>
              <option value="processing">处理中</option>
              <option value="completed">已完成</option>
            </select>
          </div>

          <!-- 关键词搜索 -->
          <div class="filter-item search">
            <input
              type="text"
              v-model="searchKeyword"
              placeholder="搜索工单编号或描述"
              class="search-input"
            >
            <button class="search-btn" @click="searchWorkorders">搜索</button>
          </div>

          <!-- 刷新按钮 -->
          <button class="refresh-btn" @click="fetchWorkOrders">
            <i class="refresh-icon">&#8635;</i> 刷新
          </button>
        </div>

        <!-- 添加工单按钮 -->
        <div class="action-bar">
          <button class="add-btn" @click="showNewWorkOrderModal = true">
            <i class="plus-icon">+</i> 新建工单
          </button>
        </div>
        <!-- 工单列表 -->
        <div class="workorder-list">
          <!-- 加载中提示 -->
          <div class="loading-container" v-if="loading">
            <div class="loading-spinner"></div>
            <div class="loading-text">正在加载工单数据...</div>
          </div>

          <!-- 无数据提示 -->
          <div class="empty-container" v-else-if="filteredWorkorders.length === 0">
            <div class="empty-icon">&#x1F4C4;</div>
            <div class="empty-text">没有找到符合条件的工单</div>
          </div>

          <!-- 工单列表内容 -->
          <div class="workorder-item" v-for="(item, index) in filteredWorkorders" :key="index">
            <div class="workorder-header">
              <span class="workorder-number">{{ item.number }}</span>
              <span class="workorder-status" :class="item.status">{{ item.statusText }}</span>
              <span class="workorder-type">类型：{{ getTypeText(item.type || item.task_type) }}</span>
              <span class="emergency-badge" v-if="item.extension_fields && item.extension_fields.is_emergency">⚡ 紧急</span>
            </div>
            <div class="workorder-body">
              <p class="workorder-desc">{{ item.description }}</p>
              <div class="workorder-meta">
                <span>负责组员：{{ item.team_members ? (item.team_member_name || item.team_members) : '未分配' }}</span>
                <span>截止时间：{{ formatDateTime(item.deadline) }}</span>
              </div>
            </div>
            <div class="workorder-footer">
              <button class="detail-btn" @click="showWorkOrderDetail(item)">查看详情</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建工单模态框 -->
    <div class="modal" v-if="showNewWorkOrderModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>新建工单</h3>
          <span class="close-btn" @click="showNewWorkOrderModal = false">&times;</span>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>任务类型</label>
            <select v-model="newWorkOrder.task_type" class="form-input" required>
              <option value="schedule">排班任务</option>
              <option value="maintenance">设备维护</option>
              <option value="inspection">产线巡检</option>
            </select>
          </div>
          <div class="form-group">
            <label>任务详情</label>
            <textarea v-model="newWorkOrder.task_details" class="form-input" rows="3" placeholder="请输入任务详细内容" required></textarea>
          </div>
          <div class="form-group">
            <label>开始时间</label>
            <input type="datetime-local" v-model="newWorkOrder.start_time" class="form-input" required>
          </div>
          <div class="form-group">
            <label>截止时间</label>
            <input type="datetime-local" v-model="newWorkOrder.deadline" class="form-input" required>
          </div>
          <div class="form-group">
            <label>产线信息</label>
            <select v-model="newWorkOrder.production_line" class="form-input" required>
              <option value="">请选择产线</option>
              <option v-for="line in assignedLines" :key="line.id" :value="line.id">
                {{ line.name }}
              </option>
            </select>
          </div>
          <!-- 根据任务类型显示不同的扩展字段 -->
          <!-- 排班任务的字段 -->
          <div v-if="newWorkOrder.task_type === 'schedule'" class="extension-fields">
            <div class="form-group">
              <label>负责组员</label>
              <select v-model="newWorkOrder.team_members" class="form-input">
                <option value="">请选择组员</option>
                <option v-for="emp in employees" :key="emp.id" :value="emp.id">
                  {{ emp.name }} ({{ emp.id }}) - {{ emp.skillLevel }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>设备选择</label>
              <select v-model="newWorkOrder.extension_fields.device_id" class="form-input">
                <option value="">请选择设备</option>
                <option v-for="device in filteredEquipments" :key="device.id" :value="device.code">
                  {{ device.name }} ({{ device.code }})
                </option>
              </select>
            </div>
          </div>

          <!-- 设备维护的字段 -->
          <div v-if="newWorkOrder.task_type === 'maintenance'" class="extension-fields">
            <div class="form-group">
              <label>负责组员</label>
              <select v-model="newWorkOrder.team_members" class="form-input">
                <option value="">请选择组员</option>
                <option v-for="emp in employees" :key="emp.id" :value="emp.id">
                  {{ emp.name }} ({{ emp.id }}) - {{ emp.skillLevel }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>设备选择</label>
              <select v-model="newWorkOrder.extension_fields.device_id" class="form-input">
                <option value="">请选择设备</option>
                <option v-for="device in filteredEquipments" :key="device.id" :value="device.code">
                  {{ device.name }} ({{ device.code }})
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>发现时间</label>
              <input type="datetime-local" v-model="newWorkOrder.extension_fields.discovery_time" class="form-input">
            </div>
          </div>

          <!-- 产线巡检的字段 -->
          <div v-if="newWorkOrder.task_type === 'inspection'" class="extension-fields">
            <div class="form-group">
              <label>负责组员</label>
              <select v-model="newWorkOrder.team_members" class="form-input">
                <option value="">请选择组员</option>
                <option v-for="emp in employees" :key="emp.id" :value="emp.id">
                  {{ emp.name }} ({{ emp.id }}) - {{ emp.skillLevel }}
                </option>
              </select>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="showNewWorkOrderModal = false">取消</button>
          <button class="btn submit" @click="createWorkOrder">确认</button>
        </div>
      </div>
    </div>

    <!-- 工单详情模态框 -->
    <div class="modal" v-if="showWorkOrderDetailModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>工单详情</h3>
          <span class="close-btn" @click="showWorkOrderDetailModal = false">&times;</span>
        </div>
        <div class="modal-body">
          <div class="detail-item">
            <label>工单编号</label>
            <div class="value">{{ selectedWorkOrder.number }}</div>
          </div>
          <div class="detail-item">
            <label>工单状态</label>
            <div class="value">
              <span class="status-tag" :class="selectedWorkOrder.status">
                {{ selectedWorkOrder.statusText }}
              </span>
            </div>
          </div>
          <div class="detail-item">
            <label>任务类型</label>
            <div class="value">
              <span class="type-tag">{{ getTypeText(selectedWorkOrder.type || selectedWorkOrder.task_type) }}</span>
              <span class="emergency-badge" v-if="selectedWorkOrder.extension_fields && selectedWorkOrder.extension_fields.is_emergency">⚡ 紧急</span>
            </div>
          </div>
          <div class="detail-item">
            <label>任务描述</label>
            <div class="value description">{{ selectedWorkOrder.description }}</div>
          </div>
          <div class="detail-item">
            <label>发出人</label>
            <div class="value">{{ selectedWorkOrder.creator_name || selectedWorkOrder.creator }} ({{ selectedWorkOrder.creator }})</div>
          </div>
          <div class="detail-item">
            <label>负责工长</label>
            <div class="value">{{ selectedWorkOrder.foreman_name || selectedWorkOrder.foreman }} ({{ selectedWorkOrder.foreman }})</div>
          </div>
          <div class="detail-item">
            <label>负责班组</label>
            <div class="value">{{ selectedWorkOrder.team }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkOrder.team_members">
            <label>负责组员</label>
            <div class="value">{{ selectedWorkOrder.team_member_name || selectedWorkOrder.team_members }} ({{ selectedWorkOrder.team_members }})</div>
          </div>
          <div class="detail-item">
            <label>产线信息</label>
            <div class="value">{{ selectedWorkOrder.production_line }}</div>
          </div>
          <div class="detail-item">
            <label>开始时间</label>
            <div class="value">{{ formatDateTime(selectedWorkOrder.start_time) }}</div>
          </div>
          <div class="detail-item">
            <label>截止时间</label>
            <div class="value">{{ formatDateTime(selectedWorkOrder.deadline) }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkOrder.actual_end_time">
            <label>实际结束时间</label>
            <div class="value">{{ formatDateTime(selectedWorkOrder.actual_end_time) }}</div>
          </div>
          <div class="detail-item">
            <label>创建时间</label>
            <div class="value">{{ formatDateTime(selectedWorkOrder.created_at) }}</div>
          </div>
          <div class="detail-item">
            <label>更新时间</label>
            <div class="value">{{ formatDateTime(selectedWorkOrder.updated_at) }}</div>
          </div>
          <!-- 扩展字段显示 -->
          <div class="detail-item" v-if="selectedWorkOrder.extension_fields && selectedWorkOrder.extension_fields.device_info">
            <label>设备信息</label>
            <div class="value">{{ selectedWorkOrder.extension_fields.device_info }}</div>
          </div>
          <div class="detail-item" v-else-if="selectedWorkOrder.extension_fields && selectedWorkOrder.extension_fields.device_id">
            <label>设备编号</label>
            <div class="value">{{ selectedWorkOrder.extension_fields.device_id }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkOrder.extension_fields && selectedWorkOrder.extension_fields.discovery_time">
            <label>发现时间</label>
            <div class="value">{{ formatDateTime(selectedWorkOrder.extension_fields.discovery_time) }}</div>
          </div>
          <!-- 工单完成报告 -->
          <div class="detail-item" v-if="selectedWorkOrder.note">
            <label>完成报告</label>
            <div class="value note-content">{{ selectedWorkOrder.note }}</div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="showWorkOrderDetailModal = false">关闭</button>
          <button class="btn submit" @click="updateWorkOrder" v-if="selectedWorkOrder.status === 'pending'">
            开始处理
          </button>
          <button class="btn delete" @click="confirmDeleteWorkOrder(selectedWorkOrder)">
            删除工单
          </button>
        </div>
      </div>
    </div>



    <!-- 确认删除工单模态框 -->
    <div class="modal" v-if="showDeleteConfirmModal">
      <div class="modal-content confirm-modal">
        <div class="modal-header">
          <h3>确认删除</h3>
          <span class="close-btn" @click="showDeleteConfirmModal = false">&times;</span>
        </div>
        <div class="modal-body">
          <p class="confirm-message">您确定要删除工单 <strong>{{ workOrderToDelete.number }}</strong> 吗？</p>
          <p class="warning-message">此操作不可恢复，请谨慎操作。</p>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="showDeleteConfirmModal = false">取消</button>
          <button class="btn delete confirm" @click="deleteWorkOrder">确认删除</button>
        </div>
      </div>
    </div>



    <ForemanNav />
  </div>
</template>

<script>
import ForemanNav from '@/components/ForemanNav.vue'

// 使用Vue实例的$message方法，不需要单独导入Message

export default {
  name: 'WorkOrder',
  components: {
    ForemanNav
  },
  data() {
    return {
      // 工长被分配的产线
      assignedLines: [],
      workorders: [],

      // 筛选相关
      filterType: 'all',
      filterStatus: 'all',
      searchKeyword: '',
      loading: false,
      // 工单日期筛选
      showAllWorkorders: false,

      // 员工列表
      employees: [],
      // 设备列表
      equipments: [],
      // 按产线分组的设备列表
      equipmentsByLine: {},
      // 用户名缓存
      usernameCache: {},
      showNewWorkOrderModal: false,
      showWorkOrderDetailModal: false,
      showDeleteConfirmModal: false,
      selectedWorkOrder: {},
      workOrderToDelete: {},
      newWorkOrder: {
        task_type: 'schedule', // 默认选择排班任务
        task_details: '',
        start_time: '',
        deadline: '',
        production_line: '',
        team_members: '',
        extension_fields: {
          device_id: ''
        }
      },

    }
  },
  created() {
    // 获取当前工长信息
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
    this.currentForeman = userInfo;

    // 不需要在这里初始化自动生成的字段，在提交时会自动添加

    // 加载工单数据
    this.fetchWorkOrders();

    // 加载工长的产线信息
    this.fetchAssignedLines();

    // 加载团队成员信息
    this.fetchTeamMembers();

    // 加载设备信息
    this.fetchEquipments();

    // 加载用户名缓存
    this.fetchUsernames();
  },
  watch: {
    // 监听任务类型变化，动态更新扩展字段
    'newWorkOrder.task_type': function(newType) {
      // 根据任务类型初始化不同的扩展字段
      if (newType === 'schedule') {
        this.newWorkOrder.extension_fields = {
          device_id: ''
        };
      } else if (newType === 'maintenance') {
        this.newWorkOrder.extension_fields = {
          device_id: '',
          discovery_time: new Date().toISOString().slice(0, 16) // 格式化为日期时间输入框支持的格式
        };
      } else if (newType === 'inspection') {
        this.newWorkOrder.extension_fields = {};
      }

      // 重置负责组员
      this.newWorkOrder.team_members = '';
    },

    // 监听产线变化，重置设备选择
    'newWorkOrder.production_line': function(newLineId) {
      // 重置设备选择
      if (this.newWorkOrder.extension_fields) {
        this.newWorkOrder.extension_fields.device_id = '';
      }

      console.log('产线已更改为:', newLineId);
      console.log('可用设备:', this.filteredEquipments);
    }
  },
  computed: {
    // 根据选择的产线筛选设备
    filteredEquipments() {
      if (!this.newWorkOrder.production_line) {
        return [];
      }
      return this.equipmentsByLine[this.newWorkOrder.production_line] || [];
    },

    // 筛选后的工单列表
    filteredWorkorders() {
      return this.workorders.filter(workorder => {
        // 类型筛选
        // 添加调试信息
        console.log('筛选工单类型:', this.filterType, '工单:', workorder.number, '工单类型:', workorder.task_type, workorder.type);

        const typeMatch = this.filterType === 'all' ||
          (workorder.task_type === this.filterType) ||
          (workorder.type === this.filterType) ||
          // 处理中文类型名称的情况
          (this.filterType === 'schedule' && (workorder.task_type === '排班任务' || workorder.type === '排班任务')) ||
          (this.filterType === 'maintenance' && (workorder.task_type === '设备维护' || workorder.type === '设备维护')) ||
          (this.filterType === 'inspection' && (workorder.task_type === '产线巡检' || workorder.type === '产线巡检'));

        // 状态筛选
        let statusMatch = this.filterStatus === 'all';

        if (this.filterStatus === 'pending') {
          statusMatch = workorder.status === 'pending' || workorder.status === '未接受';
        } else if (this.filterStatus === 'processing') {
          statusMatch = workorder.status === 'processing' || workorder.status === '处理中' || workorder.status === '已接受';
        } else if (this.filterStatus === 'completed') {
          statusMatch = workorder.status === 'completed' || workorder.status === '已完成';
        }

        // 关键词搜索
        const keyword = this.searchKeyword.toLowerCase();
        const keywordMatch = !keyword ||
          (workorder.number && workorder.number.toLowerCase().includes(keyword)) ||
          (workorder.description && workorder.description.toLowerCase().includes(keyword)) ||
          (workorder.task_details && workorder.task_details.toLowerCase().includes(keyword));

        return typeMatch && statusMatch && keywordMatch;
      });
    },
  },
  methods: {
    // 获取工长的产线信息
    async fetchAssignedLines() {
      try {
        if (!this.currentForeman || !this.currentForeman.employee_id) {
          console.log('当前工长工号未知，无法获取产线信息');
          return;
        }

        console.log('开始获取工长产线信息,工长工号:', this.currentForeman.employee_id);
        const response = await fetch(`/api/users/foreman/assigned-lines?employee_id=${this.currentForeman.employee_id}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('产线数据:', data);

        if (data.success && Array.isArray(data.data)) {
          this.assignedLines = data.data.map(line => ({
            id: line.id,
            name: line.line_name
          }));

          // 如果没有产线数据，显示提示信息
          if (this.assignedLines.length === 0) {
            console.warn('未找到分配给当前工长的产线');
          }
        } else {
          console.error('获取产线列表失败:', data.error || '未知错误');
          // 显示错误提示
          this.$message.error('获取产线列表失败');
          this.assignedLines = [];
        }
      } catch (error) {
        console.error('请求产线列表出错:', error);
        // 显示错误提示
        this.$message.error('请求产线列表出错');
        this.assignedLines = [];
      }
    },

    // 获取团队成员信息
    async fetchTeamMembers() {
      try {
        if (!this.currentForeman || !this.currentForeman.group_id) {
          console.log('当前工长组号未知，无法获取团队成员信息');
          return;
        }

        console.log('开始获取团队成员数据,工长组号:', this.currentForeman.group_id);
        const response = await fetch(`/api/users/foreman/team-members?group_id=${this.currentForeman.group_id}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('团队成员数据:', data);

        if (data.success && Array.isArray(data.data)) {
          // 处理团队成员数据
          this.employees = data.data.map(emp => ({
            id: emp.id, // 工号
            name: emp.name,
            line_id: emp.line_id || '',
            status: emp.status || 'active',
            statusText: emp.statusText || '在岗',
            skillLevel: emp.skillLevel || '初级'
          }));
        } else {
          console.error('获取团队成员失败:', data.error || '未知错误');
          // 显示错误提示
          this.$message.error('获取团队成员失败');
          this.employees = [];
        }
      } catch (error) {
        console.error('请求团队成员出错:', error);
        // 显示错误提示
        this.$message.error('请求团队成员出错');
        this.employees = [];
      }
    },

    // 获取设备信息
    async fetchEquipments() {
      try {
        console.log('开始获取设备数据');
        const response = await fetch('/api/equipment/list', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('设备数据:', data);

        if (data.success && Array.isArray(data.data)) {
          // 处理设备数据
          this.equipments = data.data.map(device => ({
            id: device.id,
            name: device.equipment_name,
            code: device.equipment_code,
            line_id: device.line_id,
            status: device.status || '正常'
          }));

          // 按产线分组设备
          this.equipmentsByLine = {};
          this.equipments.forEach(device => {
            if (!this.equipmentsByLine[device.line_id]) {
              this.equipmentsByLine[device.line_id] = [];
            }
            this.equipmentsByLine[device.line_id].push(device);
          });

          console.log('按产线分组的设备:', this.equipmentsByLine);
        } else {
          console.error('获取设备列表失败:', data.error || '未知错误');
          // 显示错误提示
          this.$message.error('获取设备列表失败');
          this.equipments = [];
          this.equipmentsByLine = {};
        }
      } catch (error) {
        console.error('请求设备列表出错:', error);
        // 显示错误提示
        this.$message.error('请求设备列表出错');
        this.equipments = [];
        this.equipmentsByLine = {};
      }
    },

    // 切换工单日期筛选
    toggleWorkorderDateFilter(showAll) {
      if (this.showAllWorkorders !== showAll) {
        this.showAllWorkorders = showAll;
        this.fetchWorkOrders();
      }
    },

    // 获取工长组的工单列表
    async fetchWorkOrders() {
      try {
        if (!this.currentForeman || !this.currentForeman.group_id) {
          console.log('当前工长组号未知，无法获取工单信息');
          return;
        }

        // 设置加载状态
        this.loading = true;

        // 重置筛选条件
        this.filterType = 'all';
        this.filterStatus = 'all';
        this.searchKeyword = '';

        console.log('开始获取工单数据,工长组号:', this.currentForeman.group_id, '显示全部:', this.showAllWorkorders);
        const url = `/api/workorders/foreman-workorders?group_id=${this.currentForeman.group_id}${this.showAllWorkorders ? '&showAll=true' : ''}`;
        const response = await fetch(url, {
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
            // 将数据库中的字段直接映射到前端对象
            const wo = {
              ...workorder,
              number: workorder.workorder_number,  // 为了兼容前端显示
              statusText: this.getStatusText(workorder.status),
              description: workorder.task_details, // 为了兼容前端显示
              type: workorder.task_type,          // 为了兼容前端显示
              owner: workorder.creator,           // 为了兼容前端显示
              note: workorder.note,               // 完成报告
              progress: 0,                        // 默认进度
              // 使用后端返回的用户名
              creator_name: workorder.creator_name,
              team_member_name: workorder.team_member_name,
              foreman_name: workorder.foreman_name
            };

            // 确保 task_type 字段存在且与 type 一致
            if (!wo.task_type && wo.type) {
              wo.task_type = wo.type;
            } else if (!wo.type && wo.task_type) {
              wo.type = wo.task_type;
            }

            // 输出工单类型信息，帮助调试
            console.log(`工单 ${wo.number} 类型信息: task_type=${wo.task_type}, type=${wo.type}`);

            // 如果扩展字段是字符串，尝试解析为JSON对象
            if (typeof workorder.extension_fields === 'string') {
              try {
                wo.extension_fields = JSON.parse(workorder.extension_fields);
              } catch (e) {
                console.error('解析扩展字段失败:', e);
                wo.extension_fields = {};
              }
            }

            return wo;
          });
        } else {
          console.error('获取工单列表失败:', data.error || '未知错误');
          this.$message.error('获取工单列表失败');
        }
      } catch (error) {
        console.error('请求工单列表出错:', error);
        this.$message.error('获取工单列表失败');
      } finally {
        // 无论成功失败，都关闭加载状态
        this.loading = false;
      }
    },

    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },

    // 格式化日期时间
    formatDateTime(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleString();
    },

    // 获取状态显示文本
    getStatusText(status) {
      const statusMap = {
        '未接受': '待处理',
        '进行中': '进行中',
        '已完成': '已完成',
        '已取消': '已取消',
        'pending': '待处理',
        'processing': '进行中',
        'completed': '已完成',
        'cancelled': '已取消'
      };
      return statusMap[status] || '未知状态';
    },

    // 获取任务类型显示文本
    getTypeText(type) {
      const typeMap = {
        'schedule': '排班任务',
        'maintenance': '设备维修',
        'inspection': '产线巡检'
      };
      return typeMap[type] || type || '未知类型';
    },

    // 根据设备ID获取设备信息
    getDeviceInfo(deviceId) {
      if (!deviceId) {
        return { name: '', fullInfo: '' };
      }

      // 从所有设备中查找匹配的设备
      const device = this.equipments.find(d => d.code === deviceId);

      if (!device) {
        return { name: '', fullInfo: deviceId };
      }

      // 返回设备名称和完整信息
      return {
        name: device.name,
        fullInfo: `${device.name} (${device.code})`
      };
    },

    // 获取工号对应的用户名
    async fetchUsernames() {
      try {
        // 收集所有需要查询的工号
        const employeeIds = new Set();

        console.log('当前工单数据:', this.workorders);

        this.workorders.forEach(workorder => {
          if (workorder.creator) {
            employeeIds.add(workorder.creator);
            console.log('添加creator:', workorder.creator);
          }
          if (workorder.foreman) {
            employeeIds.add(workorder.foreman);
            console.log('添加foreman:', workorder.foreman);
          }
          if (workorder.team_members) {
            // 如果是多个组员，可能是逗号分隔的字符串
            const members = workorder.team_members.split(',');
            members.forEach(member => {
              if (member.trim()) {
                employeeIds.add(member.trim());
                console.log('添加team_member:', member.trim());
              }
            });
          }
          if (workorder.owner) {
            employeeIds.add(workorder.owner);
            console.log('添加owner:', workorder.owner);
          }
        });

        console.log('收集到的所有工号:', Array.from(employeeIds));

        // 过滤掉已经缓存的工号
        const idsToFetch = Array.from(employeeIds).filter(id => !this.usernameCache[id]);

        if (idsToFetch.length === 0) {
          console.log('所有用户名已缓存');
          return;
        }

        console.log('需要查询的工号:', idsToFetch);

        // 批量查询用户名
        // 改为使用单个查询的方式，避免批量查询的问题
        console.log('开始逐个查询用户名');

        // 先从员工列表中查找
        const foundInEmployees = {};
        idsToFetch.forEach(id => {
          const employee = this.employees.find(emp => emp.id === id);
          if (employee && employee.name) {
            foundInEmployees[id] = employee.name;
          }
        });

        // 更新已找到的用户名
        Object.keys(foundInEmployees).forEach(id => {
          this.$set(this.usernameCache, id, foundInEmployees[id]);
        });

        // 过滤出员工列表中没有的工号
        const remainingIds = idsToFetch.filter(id => !foundInEmployees[id]);

        if (remainingIds.length === 0) {
          console.log('所有用户名已从员工列表中找到');
          return;
        }

        // 逐个查询剩余的工号
        for (const id of remainingIds) {
          await this.fetchSingleUsername(id);
        }

        // 打印最终结果
        console.log('所有用户名查询完成，缓存:', this.usernameCache);

        // 模拟数据作为返回结果
        const data = {
          success: true,
          data: this.usernameCache
        };
        console.log('用户名数据:', data);

        if (data.success && data.data) {
          // 逐个更新缓存，使用Vue的$set确保响应式更新
          Object.keys(data.data).forEach(id => {
            if (data.data[id]) {
              this.$set(this.usernameCache, id, data.data[id]);
            }
          });

          console.log('更新后的用户名缓存:', this.usernameCache);
        } else {
          console.error('获取用户名失败:', data.error || '未知错误');
        }
      } catch (error) {
        console.error('请求用户名出错:', error);
      }
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

      // 直接从当前员工列表中查找
      const employee = this.employees.find(emp => emp.id === employeeId);
      if (employee && employee.name) {
        console.log(`从员工列表中找到工号 ${employeeId} 的用户名:`, employee.name);
        this.$set(this.usernameCache, employeeId, employee.name);
        return;
      }

      // 如果员工列表中没有，直接使用工号作为用户名
      this.$set(this.usernameCache, employeeId, employeeId);
      console.log(`已将工号 ${employeeId} 缓存为用户名`);
      return;

      // 以下代码暂时不执行，等后端问题解决后再恢复
      /*
      try {
        // 如果员工列表中没有，则调用API
        const response = await fetch(`/api/users/username/${employeeId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

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

    // 批量获取用户名
    async fetchBatchUsernames(employeeIds) {
      if (!employeeIds || employeeIds.length === 0) return;

      console.log(`批量获取${employeeIds.length}个工号的用户名`);

      // 先从员工列表中查找
      const foundInEmployees = {};
      employeeIds.forEach(id => {
        const employee = this.employees.find(emp => emp.id === id);
        if (employee && employee.name) {
          foundInEmployees[id] = employee.name;
        }
      });

      // 更新已找到的用户名
      Object.keys(foundInEmployees).forEach(id => {
        this.$set(this.usernameCache, id, foundInEmployees[id]);
      });

      // 对于员工列表中没有的工号，直接使用工号作为用户名
      const remainingIds = employeeIds.filter(id => !foundInEmployees[id]);
      remainingIds.forEach(id => {
        this.$set(this.usernameCache, id, id);
      });

      console.log('更新后的用户名缓存:', this.usernameCache);

      // 以下代码暂时不执行，等后端问题解决后再恢复
      /*
      try {
        const response = await fetch('/api/users/usernames', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({ employee_ids: employeeIds })
        });

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
            employeeIds.forEach(id => {
              this.$set(this.usernameCache, id, id);
            });
            return;
          }

          const data = JSON.parse(responseText);
          console.log('批量获取用户名响应:', data);

          if (data.success && data.data) {
            // 更新缓存
            Object.entries(data.data).forEach(([employeeId, username]) => {
              if (username) {
                this.$set(this.usernameCache, employeeId, username);
              } else {
                this.$set(this.usernameCache, employeeId, employeeId);
              }
            });
            console.log('更新后的用户名缓存:', this.usernameCache);
          }
        } catch (parseError) {
          console.error('解析用户名响应失败:', parseError);
          console.error('响应内容:', responseText);
          // 如果解析失败，将所有工号对应的用户名设置为工号本身
          employeeIds.forEach(id => {
            this.$set(this.usernameCache, id, id);
          });
        }
      } catch (error) {
        console.error('批量获取用户名失败:', error);
        // 如果批量获取失败，将所有工号对应的用户名设置为工号本身
        employeeIds.forEach(id => {
          this.$set(this.usernameCache, id, id);
        });
      }
      */
    },

    async createWorkOrder() {
      try {
        // 验证表单
        if (!this.newWorkOrder.task_type) {
          this.$message.warning('请选择任务类型');
          return;
        }
        if (!this.newWorkOrder.task_details) {
          this.$message.warning('请输入任务详情');
          return;
        }
        if (!this.newWorkOrder.start_time) {
          this.$message.warning('请选择开始时间');
          return;
        }
        if (!this.newWorkOrder.deadline) {
          this.$message.warning('请选择截止时间');
          return;
        }
        if (!this.newWorkOrder.production_line) {
          this.$message.warning('请选择产线');
          return;
        }

        if (!this.newWorkOrder.team_members) {
          this.$message.warning('请选择负责组员');
          return;
        }

        // 根据任务类型验证特定字段
        if (this.newWorkOrder.task_type === 'maintenance') {
          if (!this.newWorkOrder.extension_fields.device_id) {
            this.$message.warning('请选择设备');
            return;
          }
          if (!this.newWorkOrder.extension_fields.discovery_time) {
            this.$message.warning('请选择发现时间');
            return;
          }
        } else if (this.newWorkOrder.task_type === 'schedule') {
          if (!this.newWorkOrder.extension_fields.device_id) {
            this.$message.warning('请选择设备');
            return;
          }
        }

        // 准备工单数据
        // 先添加人工输入的字段
        const workorderData = {
          task_type: this.getTypeText(this.newWorkOrder.task_type), // 存储中文任务类型
          task_details: this.newWorkOrder.task_details,
          start_time: this.newWorkOrder.start_time,
          deadline: this.newWorkOrder.deadline,
          production_line: this.newWorkOrder.production_line,
          team_members: this.newWorkOrder.team_members,
          extension_fields: {}
        };

        // 添加自动生成的字段
        workorderData.creator = this.currentForeman.employee_id; // 使用工号而非用户名
        workorderData.foreman = this.currentForeman.employee_id; // 使用工号而非用户名
        workorderData.team = this.currentForeman.group_id;
        workorderData.status = '未接受';

        // 根据任务类型设置扩展字段
        if (this.newWorkOrder.task_type === 'maintenance') {
          // 设备维护类型
          // 获取设备信息
          const deviceInfo = this.getDeviceInfo(this.newWorkOrder.extension_fields.device_id);
          workorderData.extension_fields = {
            device_id: this.newWorkOrder.extension_fields.device_id || '',
            device_name: deviceInfo.name || '',  // 存储设备名称
            device_info: deviceInfo.fullInfo || '', // 存储完整设备信息
            discovery_time: this.newWorkOrder.extension_fields.discovery_time || new Date().toISOString()
          };
        } else if (this.newWorkOrder.task_type === 'inspection') {
          // 产线巡检类型
          workorderData.extension_fields = {};
        } else if (this.newWorkOrder.task_type === 'schedule') {
          // 排班任务类型
          // 获取设备信息
          const deviceInfo = this.getDeviceInfo(this.newWorkOrder.extension_fields.device_id);
          workorderData.extension_fields = {
            device_id: this.newWorkOrder.extension_fields.device_id || '',
            device_name: deviceInfo.name || '',  // 存储设备名称
            device_info: deviceInfo.fullInfo || '' // 存储完整设备信息
          };
        }

        // 发送请求创建工单
        const response = await fetch('/api/workorders/create-workorder', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(workorderData)
        });

        const data = await response.json();

        if (data.success) {
          // 重新获取工单列表
          this.fetchWorkOrders();
          this.resetNewWorkOrder();
          this.$message.success('工单创建成功');
          this.showNewWorkOrderModal = false;
        } else {
          this.$message.error(data.error || '工单创建失败');
        }
      } catch (error) {
        console.error('创建工单出错:', error);
        this.$message.error('创建工单失败');
      }
    },

    resetNewWorkOrder() {
      // 只保留需要人工输入的字段，其他字段在提交时自动生成
      this.newWorkOrder = {
        task_type: 'schedule', // 默认选择排班任务
        task_details: '',
        start_time: '',
        deadline: '',
        production_line: '',
        team_members: '',
        extension_fields: {}
      };

      // 根据任务类型初始化不同的扩展字段
      if (this.newWorkOrder.task_type === 'schedule') {
        this.newWorkOrder.extension_fields = {
          device_id: ''
        };
      } else if (this.newWorkOrder.task_type === 'maintenance') {
        this.newWorkOrder.extension_fields = {
          device_id: '',
          discovery_time: new Date().toISOString().slice(0, 16) // 格式化为日期时间输入框支持的格式
        };
      } else if (this.newWorkOrder.task_type === 'inspection') {
        this.newWorkOrder.extension_fields = {};
      }
    },

    showWorkOrderDetail(workorder) {
      this.selectedWorkOrder = { ...workorder };
      this.showWorkOrderDetailModal = true;

      // 获取工单相关人员的用户名
      if (workorder.creator && !this.usernameCache[workorder.creator]) {
        this.fetchSingleUsername(workorder.creator);
      }
      if (workorder.foreman && !this.usernameCache[workorder.foreman]) {
        this.fetchSingleUsername(workorder.foreman);
      }
      if (workorder.team_members) {
        const members = workorder.team_members.split(',');
        members.forEach(member => {
          if (member.trim() && !this.usernameCache[member.trim()]) {
            this.fetchSingleUsername(member.trim());
          }
        });
      }
    },
    async updateWorkOrder() {
      try {
        // 准备更新数据
        let newStatus = this.selectedWorkOrder.status;

        if(this.selectedWorkOrder.status === 'pending' || this.selectedWorkOrder.status === '未接受') {
          newStatus = 'processing';
        }

        const updateData = {
          status: newStatus
        };

        // 发送请求更新工单
        const response = await fetch('/api/workorders/update-workorder', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            workorder_number: this.selectedWorkOrder.number,
            update_data: updateData
          })
        });

        const data = await response.json();

        if (data.success) {
          // 重新获取工单列表
          this.fetchWorkOrders();
          this.$message.success('工单更新成功');
        } else {
          this.$message.error(data.error || '工单更新失败');
        }
      } catch (error) {
        console.error('更新工单出错:', error);
        this.$message.error('更新工单失败');
      }
      this.showWorkOrderDetailModal = false;
    },


    // 确认删除工单
    confirmDeleteWorkOrder(workorder) {
      this.workOrderToDelete = { ...workorder };
      this.showDeleteConfirmModal = true;
      this.showWorkOrderDetailModal = false; // 关闭详情模态框
    },

    // 工单类型筛选变化处理
    onFilterTypeChange() {
      console.log('工单类型筛选已更改为:', this.filterType);

      // 输出所有工单的类型信息，帮助调试
      this.workorders.forEach(workorder => {
        const isMatch = this.filterType === 'all' ||
          (workorder.task_type === this.filterType) ||
          (workorder.type === this.filterType) ||
          (this.filterType === 'schedule' && (workorder.task_type === '排班任务' || workorder.type === '排班任务')) ||
          (this.filterType === 'maintenance' && (workorder.task_type === '设备维护' || workorder.type === '设备维护')) ||
          (this.filterType === 'inspection' && (workorder.task_type === '产线巡检' || workorder.type === '产线巡检'));

        console.log(`工单 ${workorder.number} 类型信息: task_type=${workorder.task_type}, type=${workorder.type}, 是否匹配=${isMatch}`);
      });

      // 输出筛选后的工单数量
      console.log('筛选后的工单数量:', this.filteredWorkorders.length);
    },

    // 搜索工单
    searchWorkorders() {
      console.log('搜索关键词:', this.searchKeyword);
      console.log('当前筛选条件 - 类型:', this.filterType, '状态:', this.filterStatus);
      console.log('筛选后的工单数量:', this.filteredWorkorders.length);

      // 输出所有工单的类型信息，帮助调试
      this.workorders.forEach(workorder => {
        console.log(`工单 ${workorder.number} 类型信息: task_type=${workorder.task_type}, type=${workorder.type}`);
      });

      // 不需要额外的操作，因为我们已经在 filteredWorkorders 计算属性中处理了搜索逻辑
    },

    // 删除工单
    async deleteWorkOrder() {
      try {
        const workorderNumber = this.workOrderToDelete.number;

        if (!workorderNumber) {
          this.$message.error('工单编号不能为空');
          return;
        }

        const response = await fetch(`/api/workorders/delete-workorder/${workorderNumber}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        const data = await response.json();

        if (data.success) {
          this.$message.success('工单删除成功');
          // 重新获取工单列表
          this.fetchWorkOrders();
        } else {
          this.$message.error(data.error || '删除工单失败');
        }
      } catch (error) {
        console.error('删除工单出错:', error);
        this.$message.error('删除工单失败');
      }

      // 关闭确认对话框
      this.showDeleteConfirmModal = false;
    },


  }
}
</script>

<style scoped>
.workorder {
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

.task-create-form {
  display: flex;
  flex-direction: column;
  background-color: #fff;
  min-height: calc(100vh - 60px);
}

.tab-header {
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.tab-item {
  padding: 10px 20px;
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

.submit-btn {
  background: #4285F4;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 4px;
  width: 100%;
  font-size: 16px;
  cursor: pointer;
  text-align: center;
}

.workorder-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.filter-item {
  display: flex;
  flex-direction: column;
  min-width: 150px;
}

.filter-item label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
}

.filter-item.search {
  flex-grow: 1;
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  gap: 10px;
}

.search-input {
  flex-grow: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.search-btn {
  padding: 8px 16px;
  background: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.refresh-btn {
  padding: 8px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.refresh-icon {
  font-size: 16px;
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
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
  flex-wrap: wrap;
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

.workorder-status.pending {
  background-color: #fff3e0;
  color: #ff9800;
}

.workorder-status.processing {
  background-color: #e3f2fd;
  color: #2196F3;
}

.workorder-type {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  background-color: #f1f8e9;
  color: #689f38;
  margin-left: 10px;
}

.workorder-body {
  color: #666;
}

.workorder-desc {
  margin: 0 0 10px 0;
}

.workorder-meta {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #999;
}

.workorder-footer {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

.detail-btn {
  padding: 6px 12px;
  background: #f5f5f5;
  border: none;
  border-radius: 4px;
  color: #666;
  cursor: pointer;
}

.detail-btn:hover {
  background: #e0e0e0;
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

.btn.delete {
  background-color: #ffebee;
  color: #f44336;
}

.btn.delete.confirm {
  background-color: #f44336;
  color: white;
}

.confirm-modal {
  max-width: 400px;
}

.confirm-message {
  font-size: 16px;
  margin-bottom: 10px;
}

.warning-message {
  color: #f44336;
  font-size: 14px;
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

.detail-item .value.description, .detail-item .value.note-content {
  line-height: 1.5;
  white-space: pre-wrap;
  background-color: #f9f9f9;
  padding: 10px;
  border-radius: 4px;
  border-left: 3px solid #ddd;
}

.status-tag, .type-tag {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 13px;
}

.type-tag {
  background-color: #f1f8e9;
  color: #689f38;
}

.status-tag.pending {
  background-color: #fff3e0;
  color: #ff9800;
}

.status-tag.processing {
  background-color: #e3f2fd;
  color: #2196F3;
}

.progress-bar {
  height: 8px;
  background: #f5f5f5;
  border-radius: 4px;
  margin-right: 10px;
  flex: 1;
}

.progress {
  height: 100%;
  background: #4CAF50;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.detail-item .value {
  display: flex;
  align-items: center;
}

.progress-text {
  min-width: 45px;
  text-align: right;
  color: #666;
  font-size: 13px;
}

.action-btn {
  border: none;
  border-radius: 4px;
  padding: 5px 10px;
  margin-right: 5px;
  cursor: pointer;
  font-size: 0.8em;
}

.action-btn.view {
  background-color: #e3f2fd;
  color: #2196F3;
}

.action-btn.assign {
  background-color: #e8f5e9;
  color: #4CAF50;
}

.btn.assign {
  background-color: #4CAF50;
  color: white;
}

/* 加载和空数据状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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

.loading-text {
  color: #666;
  font-size: 16px;
}

.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  color: #ccc;
  margin-bottom: 15px;
}

.empty-text {
  color: #666;
  font-size: 16px;
}

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
  margin-right: 15px;
}

.date-filter {
  display: flex;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #ddd;
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
</style>
