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
        <!-- 添加工单按钮 -->
        <div class="action-bar">
          <button class="add-btn" @click="showNewWorkOrderModal = true">
            <i class="plus-icon">+</i> 新建工单
          </button>
        </div>
        <!-- 工单列表 -->
        <div class="workorder-list">
          <div class="workorder-item" v-for="(item, index) in workorders" :key="index">
            <div class="workorder-header">
              <span class="workorder-number">{{ item.number }}</span>
              <span class="workorder-status" :class="item.status">{{ item.statusText }}</span>
            </div>
            <div class="workorder-body">
              <p class="workorder-desc">{{ item.description }}</p>
              <div class="workorder-meta">
                <span>负责人：{{ item.owner }}</span>
                <span>截止时间：{{ item.deadline }}</span>
              </div>
            </div>
            <div class="workorder-footer">
              <button class="detail-btn" @click="showWorkOrderDetail(item)">查看详情</button>
              <button class="action-btn assign" @click="assignTask(item)">安排员工</button>
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
                <option v-for="emp in employees" :key="emp.id" :value="emp.name">
                  {{ emp.name }} ({{ emp.skillLevel }})
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>设备编号</label>
              <input type="text" v-model="newWorkOrder.extension_fields.device_id" class="form-input" placeholder="请输入设备编号">
            </div>
          </div>

          <!-- 设备维护的字段 -->
          <div v-if="newWorkOrder.task_type === 'maintenance'" class="extension-fields">
            <div class="form-group">
              <label>负责组员</label>
              <select v-model="newWorkOrder.team_members" class="form-input">
                <option value="">请选择组员</option>
                <option v-for="emp in employees" :key="emp.id" :value="emp.name">
                  {{ emp.name }} ({{ emp.skillLevel }})
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>设备编号</label>
              <input type="text" v-model="newWorkOrder.extension_fields.device_id" class="form-input" placeholder="请输入设备编号">
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
                <option v-for="emp in employees" :key="emp.id" :value="emp.name">
                  {{ emp.name }} ({{ emp.skillLevel }})
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
            <div class="value">{{ selectedWorkOrder.type }}</div>
          </div>
          <div class="detail-item">
            <label>任务描述</label>
            <div class="value description">{{ selectedWorkOrder.description }}</div>
          </div>
          <div class="detail-item">
            <label>发出人</label>
            <div class="value">{{ selectedWorkOrder.creator }}</div>
          </div>
          <div class="detail-item">
            <label>负责工长</label>
            <div class="value">{{ selectedWorkOrder.foreman }}</div>
          </div>
          <div class="detail-item">
            <label>负责班组</label>
            <div class="value">{{ selectedWorkOrder.team }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkOrder.team_members">
            <label>负责组员</label>
            <div class="value">{{ selectedWorkOrder.team_members }}</div>
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
          <div class="detail-item" v-if="selectedWorkOrder.extension_fields && Object.keys(selectedWorkOrder.extension_fields).length > 0">
            <label>扩展信息</label>
            <div class="value">
              <div v-for="(value, key) in selectedWorkOrder.extension_fields" :key="key" class="extension-field">
                <span class="extension-key">{{ key }}:</span>
                <span class="extension-value">{{ value }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="showWorkOrderDetailModal = false">关闭</button>
          <button class="btn submit" @click="updateWorkOrder" v-if="selectedWorkOrder.status === 'pending'">
            开始处理
          </button>
          <button class="btn assign" @click="assignTask(selectedWorkOrder)" v-if="selectedWorkOrder.status === 'processing'">
            安排员工
          </button>
        </div>
      </div>
    </div>



    <!-- 安排工作模态框 -->
    <div class="modal" v-if="showAssignTask">
      <div class="modal-content">
        <div class="modal-header">
          <h3>安排工作</h3>
          <span class="close-btn" @click="closeAssignTask">&times;</span>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>工单</label>
            <input type="text" :value="selectedWorkOrder.number + ' - ' + selectedWorkOrder.description" class="form-input" disabled>
          </div>
          <div class="form-group">
            <label>产线</label>
            <select v-model="taskForm.lineId" class="form-input" @change="filterEmployeesByLine">
              <option value="">请选择产线</option>
              <option v-for="line in assignedLines" :key="line.id" :value="line.id">
                {{ line.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>员工</label>
            <select v-model="taskForm.employeeId" class="form-input">
              <option value="">请选择员工</option>
              <option v-for="emp in filteredEmployeesForTask" :key="emp.id" :value="emp.id">
                {{ emp.name }} ({{ emp.id }}) - {{ emp.statusText }} - {{ emp.skillLevel }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>工作类型</label>
            <select v-model="taskForm.type" class="form-input">
              <option value="">请选择工作类型</option>
              <option value="production">生产任务</option>
              <option value="maintenance">设备维护</option>
              <option value="quality">质量检查</option>
            </select>
          </div>
          <div class="form-group">
            <label>任务描述</label>
            <textarea v-model="taskForm.description" class="form-input" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>开始时间</label>
            <input type="datetime-local" v-model="taskForm.startTime" class="form-input">
          </div>
          <div class="form-group">
            <label>结束时间</label>
            <input type="datetime-local" v-model="taskForm.endTime" class="form-input">
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeAssignTask">取消</button>
          <button class="btn submit" @click="submitTask">确认</button>
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

      // 员工列表
      employees: [
        {
          id: 'W001',
          name: '张三',
          line_id: '1',
          phone: '13800138001',
          status: 'active',
          statusText: '在岗',
          skillLevel: '高级'
        },
        {
          id: 'W002',
          name: '李四',
          line_id: '1',
          phone: '13800138002',
          status: 'leave',
          statusText: '请假',
          skillLevel: '中级'
        },
        {
          id: 'W003',
          name: '王五',
          line_id: '2',
          phone: '13800138003',
          status: 'task',
          statusText: '任务中',
          skillLevel: '高级'
        },
        {
          id: 'W004',
          name: '赵六',
          line_id: '2',
          phone: '13800138004',
          status: 'active',
          statusText: '在岗',
          skillLevel: '初级'
        }
      ],
      showNewWorkOrderModal: false,
      showWorkOrderDetailModal: false,
      showAssignTask: false,
      selectedWorkOrder: {},
      selectedEmployee: {},
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
      taskForm: {
        lineId: '',
        employeeId: '',
        type: '',
        description: '',
        startTime: '',
        endTime: ''
      }
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
    }
  },
  computed: {
    // 根据选择的产线筛选员工
    filteredEmployeesForTask() {
      if (!this.taskForm.lineId) {
        return this.employees;
      }
      return this.employees.filter(emp => emp.line_id === this.taskForm.lineId);
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
        const response = await fetch(`/api/foreman/assigned-lines?employee_id=${this.currentForeman.employee_id}`, {
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

          // 如果没有产线数据，添加测试数据
          if (this.assignedLines.length === 0) {
            this.assignedLines = [
              { id: 'line1', name: '一号生产线' },
              { id: 'line2', name: '二号生产线' },
              { id: 'line3', name: '三号生产线' }
            ];
          }
        } else {
          console.error('获取产线列表失败:', data.error || '未知错误');
          // 添加测试数据
          this.assignedLines = [
            { id: 'line1', name: '一号生产线' },
            { id: 'line2', name: '二号生产线' },
            { id: 'line3', name: '三号生产线' }
          ];
        }
      } catch (error) {
        console.error('请求产线列表出错:', error);
        // 添加测试数据
        this.assignedLines = [
          { id: 'line1', name: '一号生产线' },
          { id: 'line2', name: '二号生产线' },
          { id: 'line3', name: '三号生产线' }
        ];
      }
    },

    // 获取工长组的工单列表
    async fetchWorkOrders() {
      try {
        if (!this.currentForeman || !this.currentForeman.group_id) {
          console.log('当前工长组号未知，无法获取工单信息');
          return;
        }

        console.log('开始获取工单数据,工长组号:', this.currentForeman.group_id);
        const response = await fetch(`/api/workorders/foreman-workorders?group_id=${this.currentForeman.group_id}`, {
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
              progress: 0                         // 默认进度
            };

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
            this.$message.warning('请输入设备编号');
            return;
          }
          if (!this.newWorkOrder.extension_fields.discovery_time) {
            this.$message.warning('请选择发现时间');
            return;
          }
        } else if (this.newWorkOrder.task_type === 'schedule') {
          if (!this.newWorkOrder.extension_fields.device_id) {
            this.$message.warning('请输入设备编号');
            return;
          }
        }

        // 准备工单数据
        // 先添加人工输入的字段
        const workorderData = {
          task_type: this.newWorkOrder.task_type,
          task_details: this.newWorkOrder.task_details,
          start_time: this.newWorkOrder.start_time,
          deadline: this.newWorkOrder.deadline,
          production_line: this.newWorkOrder.production_line,
          team_members: this.newWorkOrder.team_members,
          extension_fields: {}
        };

        // 添加自动生成的字段
        workorderData.creator = this.currentForeman.username;
        workorderData.foreman = this.currentForeman.username;
        workorderData.team = this.currentForeman.group_id;
        workorderData.status = '未接受';

        // 根据任务类型设置扩展字段
        if (this.newWorkOrder.task_type === 'maintenance') {
          // 设备维护类型
          workorderData.extension_fields = {
            device_id: this.newWorkOrder.extension_fields.device_id || '',
            discovery_time: this.newWorkOrder.extension_fields.discovery_time || new Date().toISOString()
          };
        } else if (this.newWorkOrder.task_type === 'inspection') {
          // 产线巡检类型
          workorderData.extension_fields = {};
        } else if (this.newWorkOrder.task_type === 'schedule') {
          // 排班任务类型
          workorderData.extension_fields = {
            device_id: this.newWorkOrder.extension_fields.device_id || ''
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
    // 安排工作
    assignTask(workorder) {
      this.selectedWorkOrder = { ...workorder };
      this.showAssignTask = true;

      // 初始化任务表单，可以预填工单的一些信息
      this.taskForm = {
        lineId: '',
        employeeId: '',
        type: '',
        description: workorder.description,
        startTime: '',
        endTime: ''
      };
    },

    // 根据产线筛选员工
    filterEmployeesByLine() {
      // 重置员工选择
      this.taskForm.employeeId = '';
    },

    // 关闭安排工作
    closeAssignTask() {
      this.showAssignTask = false;
      this.taskForm = {
        lineId: '',
        employeeId: '',
        type: '',
        description: '',
        startTime: '',
        endTime: ''
      };
    },

    // 提交工作安排
    async submitTask() {
      try {
        // 验证表单
        if (!this.taskForm.lineId) {
          this.$message.warning('请选择产线');
          return;
        }
        if (!this.taskForm.employeeId) {
          this.$message.warning('请选择员工');
          return;
        }

        // 获取选中的员工
        const employee = this.employees.find(emp => emp.id === this.taskForm.employeeId);
        if (!employee) {
          this.$message.warning('员工不存在');
          return;
        }

        // 准备更新数据
        const updateData = {
          status: 'processing',
          team_members: employee.name,
          production_line: this.taskForm.lineId
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
          this.$message.success('任务分配成功');

          // 记录日志
          console.log('安排工作成功:', {
            workorder: this.selectedWorkOrder,
            employee: employee,
            task: this.taskForm
          });
        } else {
          this.$message.error(data.error || '任务分配失败');
        }
      } catch (error) {
        console.error('分配任务出错:', error);
        this.$message.error('任务分配失败');
      }
      this.closeAssignTask();
    }
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



.action-btn.assign {
  background-color: #e8f5e9;
  color: #4CAF50;
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
  line-height: 1.5;
  white-space: pre-wrap;
}

.status-tag {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 13px;
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
</style>
