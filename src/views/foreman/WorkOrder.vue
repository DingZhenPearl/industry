<template>
  <div class="workorder">
    <header class="header">
      <div class="tab-header">
        <div 
          class="tab-item" 
          :class="{ active: currentTab === 'workorder' }" 
          @click="currentTab = 'workorder'"
        >
          工单管理
        </div>
        <div 
          class="tab-item" 
          :class="{ active: currentTab === 'schedule' }" 
          @click="currentTab = 'schedule'"
        >
          排班管理
        </div>
      </div>
    </header>
    
    <div class="content">
      <!-- 工单管理内容 -->
      <div v-if="currentTab === 'workorder'" class="workorder-content">
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

      <!-- 排班管理内容 -->
      <div v-else class="schedule-content">
        <!-- 添加新建排班按钮 -->
        <div class="action-bar">
          <button class="add-btn" @click="showNewScheduleModal = true">
            <i class="plus-icon">+</i> 新建排班
          </button>
        </div>
        <div class="schedule-list">
          <div class="schedule-item" v-for="(item, index) in schedules" :key="index">
            <div class="schedule-header">
              <span class="schedule-title">{{ item.title }}</span>
              <span class="schedule-time">{{ item.time }}</span>
            </div>
            <div class="schedule-members">
              <span v-for="(member, mIndex) in item.members" :key="mIndex">
                {{ member }}
              </span>
            </div>
            <div class="schedule-actions">
              <button class="action-btn assign" @click="assignEmployeeToSchedule(item)">
                安排员工
              </button>
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
            <select v-model="newWorkOrder.type" class="form-input">
              <option value="">请选择任务类型</option>
              <option value="schedule">排班任务</option>
              <option value="maintenance">设备维护</option>
              <option value="inspection">产线巡查</option>
            </select>
          </div>
          <div class="form-group">
            <label>任务详情</label>
            <textarea v-model="newWorkOrder.description" class="form-input" rows="3" placeholder="请输入任务详细内容"></textarea>
          </div>
          <div class="form-group">
            <label>开始时间</label>
            <input type="datetime-local" v-model="newWorkOrder.startTime" class="form-input">
          </div>
          <div class="form-group">
            <label>结束时间</label>
            <input type="datetime-local" v-model="newWorkOrder.endTime" class="form-input">
          </div>
          <div class="form-group">
            <label>巡检产线</label>
            <select v-model="newWorkOrder.productionLine" class="form-input">
              <option value="">请选择巡检产线</option>
              <option value="line1">一号生产线</option>
              <option value="line2">二号生产线</option>
              <option value="line3">三号生产线</option>
            </select>
          </div>
          <div class="form-group">
            <label>负责人</label>
            <input type="text" v-model="newWorkOrder.owner" class="form-input" placeholder="请输入负责人姓名">
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
            <div class="value">{{ selectedWorkOrder.type || '维护任务' }}</div>
          </div>
          <div class="detail-item">
            <label>任务描述</label>
            <div class="value description">{{ selectedWorkOrder.description }}</div>
          </div>
          <div class="detail-item">
            <label>负责人</label>
            <div class="value">{{ selectedWorkOrder.owner }}</div>
          </div>
          <div class="detail-item">
            <label>创建时间</label>
            <div class="value">{{ selectedWorkOrder.createTime || '2023-07-10 10:00' }}</div>
          </div>
          <div class="detail-item">
            <label>截止时间</label>
            <div class="value">{{ selectedWorkOrder.deadline }}</div>
          </div>
          <div class="detail-item">
            <label>执行进度</label>
            <div class="value">
              <div class="progress-bar">
                <div 
                  class="progress" 
                  :style="{ width: (selectedWorkOrder.progress || 0) + '%' }"
                ></div>
              </div>
              <span class="progress-text">{{ selectedWorkOrder.progress || 0 }}%</span>
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

    <!-- 新建排班模态框 -->
    <div class="modal" v-if="showNewScheduleModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>新建排班</h3>
          <span class="close-btn" @click="showNewScheduleModal = false">&times;</span>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>班次</label>
            <select v-model="newSchedule.shift" class="form-input">
              <option value="morning">早班(6:00-14:00)</option>
              <option value="middle">中班(14:00-22:00)</option>
              <option value="night">夜班(22:00-6:00)</option>
            </select>
          </div>
          <div class="form-group">
            <label>日期</label>
            <input type="date" v-model="newSchedule.date" class="form-input">
          </div>
          <div class="form-group">
            <label>排班人员</label>
            <div class="member-list">
              <input 
                type="text" 
                v-model="memberInput"
                class="form-input" 
                placeholder="输入员工姓名后回车添加"
                @keyup.enter="addMember"
              >
              <div class="member-tags">
                <span class="member-tag" v-for="(member, index) in newSchedule.members" :key="index">
                  {{ member }}
                  <i class="remove-icon" @click="removeMember(index)">×</i>
                </span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="showNewScheduleModal = false">取消</button>
          <button class="btn submit" @click="createSchedule">确认</button>
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

export default {
  name: 'WorkOrder',
  components: {
    ForemanNav
  },
  data() {
    return {
      currentTab: 'workorder',
      // 工长被分配的产线
      assignedLines: [
        {
          id: 1,
          name: '一号生产线',
          status: 'running',
          statusText: '运行中',
          runningDevices: 8,
          totalDevices: 10,
          utilization: 85,
          assignedTo: 1 // 分配给当前工长的ID
        },
        {
          id: 2,
          name: '二号生产线',
          status: 'warning',
          statusText: '预警',
          runningDevices: 6,
          totalDevices: 8,
          utilization: 75,
          assignedTo: 1 // 分配给当前工长的ID
        }
      ],
      workorders: [
        {
          number: 'WO2023001',
          status: 'pending',
          statusText: '待处理',
          description: '一号生产线设备维护',
          owner: '张工',
          deadline: '2023-07-30',
          type: '设备维护',
          progress: 0
        },
        {
          number: 'WO2023002',
          status: 'processing',
          statusText: '进行中',
          description: '二号生产线质量检查',
          owner: '李工',
          deadline: '2023-07-31',
          type: '质量检查',
          progress: 45
        }
      ],
      schedules: [
        {
          title: '早班',
          time: '06:00-14:00',
          members: ['张三', '李四', '王五']
        },
        {
          title: '中班',
          time: '14:00-22:00',
          members: ['赵六', '孙七', '周八']
        },
        {
          title: '夜班',
          time: '22:00-06:00',
          members: ['吴九', '郑十', '钱十一']
        }
      ],
      // 员工列表
      employees: [
        { 
          id: 'W001', 
          name: '张三', 
          lineId: 1,
          phone: '13800138001', 
          status: 'active', 
          statusText: '在岗',
          skillLevel: '高级'
        },
        { 
          id: 'W002', 
          name: '李四', 
          lineId: 1,
          phone: '13800138002', 
          status: 'leave', 
          statusText: '请假',
          skillLevel: '中级'
        },
        { 
          id: 'W003', 
          name: '王五', 
          lineId: 2,
          phone: '13800138003', 
          status: 'task', 
          statusText: '任务中',
          skillLevel: '高级'
        },
        { 
          id: 'W004', 
          name: '赵六', 
          lineId: 2,
          phone: '13800138004', 
          status: 'active', 
          statusText: '在岗',
          skillLevel: '初级'
        }
      ],
      showNewWorkOrderModal: false,
      showNewScheduleModal: false,
      showWorkOrderDetailModal: false,
      showAssignTask: false,
      selectedWorkOrder: {},
      selectedEmployee: {},
      newWorkOrder: {
        type: '',
        description: '',
        startTime: '',
        endTime: '',
        productionLine: '',
        owner: ''
      },
      newSchedule: {
        shift: 'morning',
        date: '',
        members: []
      },
      taskForm: {
        lineId: '',
        employeeId: '',
        type: '',
        description: '',
        startTime: '',
        endTime: ''
      },
      memberInput: ''
    }
  },
  computed: {
    // 根据选择的产线筛选员工
    filteredEmployeesForTask() {
      if (!this.taskForm.lineId) {
        return this.employees;
      }
      return this.employees.filter(emp => emp.lineId === parseInt(this.taskForm.lineId));
    },
  },
  methods: {
    createWorkOrder() {
      // 获取任务类型的显示文本
      const typeTextMap = {
        'schedule': '排班任务',
        'maintenance': '设备维护',
        'inspection': '产线巡查'
      };
      
      this.workorders.push({
        number: 'WO' + Date.now(),
        status: 'pending',
        statusText: '待处理',
        description: this.newWorkOrder.description,
        owner: this.newWorkOrder.owner,
        deadline: this.newWorkOrder.endTime,
        type: typeTextMap[this.newWorkOrder.type] || '未知类型'
      });
      
      this.resetNewWorkOrder();
      alert('任务创建成功');
      this.showNewWorkOrderModal = false;
    },
    createSchedule() {
      // 这里添加创建排班的逻辑
      this.schedules.push({
        title: this.getShiftTitle(this.newSchedule.shift),
        time: this.getShiftTime(this.newSchedule.shift),
        members: [...this.newSchedule.members]
      });
      this.showNewScheduleModal = false;
      this.resetNewSchedule();
    },
    resetNewWorkOrder() {
      this.newWorkOrder = {
        type: '',
        description: '',
        startTime: '',
        endTime: '',
        productionLine: '',
        owner: ''
      };
    },
    resetNewSchedule() {
      this.newSchedule = {
        shift: 'morning',
        date: '',
        members: []
      };
      this.memberInput = '';
    },
    addMember() {
      if (this.memberInput.trim() && !this.newSchedule.members.includes(this.memberInput.trim())) {
        this.newSchedule.members.push(this.memberInput.trim());
      }
      this.memberInput = '';
    },
    removeMember(index) {
      this.newSchedule.members.splice(index, 1);
    },
    getShiftTitle(shift) {
      const titles = {
        morning: '早班',
        middle: '中班',
        night: '夜班'
      };
      return titles[shift];
    },
    getShiftTime(shift) {
      const times = {
        morning: '06:00-14:00',
        middle: '14:00-22:00',
        night: '22:00-06:00'
      };
      return times[shift];
    },
    
    // 从排班管理页面安排员工
    assignEmployeeToSchedule(schedule) {
      // 创建一个临时工单对象
      const tempWorkOrder = {
        number: 'SCH' + Date.now(),
        status: 'pending',
        statusText: '待处理',
        description: `${schedule.title} (${schedule.time}) 排班任务`,
        owner: '当前工长',
        deadline: new Date().toISOString().split('T')[0]
      };
      
      // 调用安排员工方法
      this.assignTask(tempWorkOrder);
    },
    showWorkOrderDetail(workorder) {
      this.selectedWorkOrder = { ...workorder };
      this.showWorkOrderDetailModal = true;
    },
    updateWorkOrder() {
      if(this.selectedWorkOrder.status === 'pending') {
        this.selectedWorkOrder.status = 'processing';
        this.selectedWorkOrder.statusText = '进行中';
        
        // 更新列表中对应的工单状态
        const index = this.workorders.findIndex(w => w.number === this.selectedWorkOrder.number);
        if(index !== -1) {
          this.workorders[index] = { ...this.selectedWorkOrder };
        }
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
    submitTask() {
      // 验证表单
      if (!this.taskForm.lineId) {
        alert('请选择产线');
        return;
      }
      if (!this.taskForm.employeeId) {
        alert('请选择员工');
        return;
      }
      if (!this.taskForm.type) {
        alert('请选择工作类型');
        return;
      }
      if (!this.taskForm.startTime || !this.taskForm.endTime) {
        alert('请设置开始和结束时间');
        return;
      }
      
      // 获取选中的员工
      const employee = this.employees.find(emp => emp.id === this.taskForm.employeeId);
      if (!employee) {
        alert('员工不存在');
        return;
      }
      
      // 更新员工状态
      const empIndex = this.employees.findIndex(emp => emp.id === this.taskForm.employeeId);
      if (empIndex !== -1) {
        this.employees[empIndex].status = 'task';
        this.employees[empIndex].statusText = '任务中';
      }
      
      // 更新工单信息，可以添加分配的员工信息
      const workorderIndex = this.workorders.findIndex(w => w.number === this.selectedWorkOrder.number);
      if (workorderIndex !== -1) {
        this.workorders[workorderIndex].assignedEmployee = employee.name;
      }
      
      console.log('安排工作:', {
        workorder: this.selectedWorkOrder,
        employee: employee,
        task: this.taskForm
      });
      
      this.closeAssignTask();
      alert('工作安排已提交');
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

.schedule-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.schedule-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.schedule-title {
  font-weight: bold;
  color: #333;
}

.schedule-time {
  color: #666;
}

.schedule-members {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.schedule-members span {
  background-color: #e3f2fd;
  color: #2196F3;
  padding: 3px 8px;
  border-radius: 12px;
  margin-right: 5px;
  margin-bottom: 5px;
  font-size: 0.9em;
}

.schedule-actions {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
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

.member-list {
  margin-top: 10px;
}

.member-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.member-tag {
  background: #e3f2fd;
  color: #2196F3;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.remove-icon {
  cursor: pointer;
  font-size: 16px;
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
