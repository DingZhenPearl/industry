<template>
  <div class="team">
    <header class="header">
      <h1>团队管理</h1>
    </header>

    <div class="content">
      <!-- 产线员工概览卡片 -->
      <div class="authority-notice">
        <i class="info-icon"></i>
        <span>您有权管理 <strong>{{ assignedLines.length }}</strong> 条产线上的员工</span>
      </div>

      <!-- 产线员工统计卡片 -->
      <div class="department-cards">
        <div class="dept-card" v-for="line in assignedLines" :key="line.id">
          <div class="dept-header">
            <h3>{{ line.name || line.line_name || `产线${line.id}` }}</h3>
            <span class="member-count">{{ getLineWorkerCount(line.id) }}人</span>
          </div>
          <div class="dept-stats">
            <div class="stat-item">
              <span class="label">在岗率</span>
              <span class="value">{{ getLineActiveRate(line.id) }}%</span>
            </div>
          </div>
          <div class="dept-actions">
            <button class="action-btn" @click="viewLineDetail(line)">查看产线详情</button>
          </div>
        </div>
      </div>

      <!-- 员工列表 -->
      <div class="employee-section">
        <div class="section-header">
          <h3>员工管理</h3>
          <div class="header-actions">

            <button class="view-btn" @click="showLeaveManagement = true">
              <i class="calendar-icon"></i> 请假管理
            </button>
          </div>
        </div>

        <div class="filter-bar">
          <select v-model="filterLine" class="filter-select">
            <option value="">全部产线</option>
            <option v-for="line in assignedLines" :key="line.id" :value="line.id">
              {{ line.name || line.line_name || `产线${line.id}` }}
            </option>
          </select>
          <select v-model="filterStatus" class="filter-select">
            <option value="">全部状态</option>
            <option value="在岗">在岗</option>
            <option value="离岗">离岗</option>
            <option value="请假">请假</option>
          </select>
          <input
            type="text"
            v-model="searchKeyword"
            class="search-input"
            placeholder="搜索员工姓名"
          >
        </div>

        <div class="employee-list">
          <table>
            <thead>
              <tr>
                <th>工号</th>
                <th>姓名</th>
                <th>分组号</th>
                <th>负责产线</th>
                <th>负责设备</th>
                <th>联系方式</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="emp in filteredEmployees" :key="emp.id" :class="{ 'current-foreman': emp.id === currentForeman.id }">
                <td>{{ emp.id }}</td>
                <td>{{ emp.name }}</td>
                <td>{{ emp.group_id || '未分组' }}</td>
                <td>
                  <!-- 工长显示自己的产线，工人和安全员显示和工长相同的产线 -->
                  <span v-if="emp.role === 'foreman' && emp.assigned_lines && emp.assigned_lines.length">
                    {{ emp.assigned_lines.map(line => line.name).join(', ') }}
                  </span>
                  <span v-else-if="emp.role === 'member' || emp.role === 'safety_officer'">
                    {{ getForemanLines() }}
                  </span>
                  <span v-else>无</span>
                </td>
                <td>
                  <!-- 工长显示无，工人显示分配的设备 -->
                  <span v-if="emp.role === 'member' && emp.assigned_equipment && emp.assigned_equipment.length">
                    {{ emp.assigned_equipment.map(eq => eq.name).join(', ') }}
                  </span>
                  <span v-else>无</span>
                </td>
                <td>{{ emp.phone }}</td>
                <td>
                  <span :class="['status-tag', getStatusClass(emp.status)]">
                    {{ emp.status || '未知' }}
                  </span>
                </td>
                <td>
                  <button class="action-btn view" @click="viewEmployeeDetail(emp)">详情</button>
                  <button class="action-btn assign" v-if="emp.role === 'member'" @click="showAssignDeviceModal(emp)">分配设备</button>
                  <button class="action-btn assign" v-if="emp.role === 'member'" @click="showAssignLineModal(emp)">分配产线</button>
                  <button class="action-btn status" @click="showUpdateStatusModal(emp)">修改状态</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 员工详情模态框 -->
    <div class="modal" v-if="showEmployeeDetail">
      <div class="modal-content">
        <div class="modal-header">
          <h3>员工详情</h3>
          <span class="close-btn" @click="closeEmployeeDetail">&times;</span>
        </div>
        <div class="modal-body">
          <div class="detail-item">
            <label>工号</label>
            <div class="value">{{ selectedEmployee.id }}</div>
          </div>
          <div class="detail-item">
            <label>姓名</label>
            <div class="value">{{ selectedEmployee.name }}</div>
          </div>
          <div class="detail-item">
            <label>角色</label>
            <div class="value">{{ getRoleName(selectedEmployee.role) }}</div>
          </div>
          <div class="detail-item">
            <label>分组号</label>
            <div class="value">{{ selectedEmployee.group_id || '未分组' }}</div>
          </div>
          <div class="detail-item">
            <label>负责产线</label>
            <div class="value">
              <span v-if="selectedEmployee.role === 'foreman' && selectedEmployee.assigned_lines && selectedEmployee.assigned_lines.length">
                {{ selectedEmployee.assigned_lines.map(line => line.name).join(', ') }}
              </span>
              <span v-else-if="selectedEmployee.role === 'member' || selectedEmployee.role === 'safety_officer'">
                {{ getForemanLines() }}
              </span>
              <span v-else>无</span>
            </div>
          </div>
          <div class="detail-item">
            <label>负责设备</label>
            <div class="value">
              <span v-if="selectedEmployee.role === 'member' && selectedEmployee.assigned_equipment && selectedEmployee.assigned_equipment.length">
                {{ selectedEmployee.assigned_equipment.map(eq => eq.name).join(', ') }}
              </span>
              <span v-else>无</span>
            </div>
          </div>
          <div class="detail-item">
            <label>联系方式</label>
            <div class="value">{{ selectedEmployee.phone }}</div>
          </div>
          <div class="detail-item">
            <label>状态</label>
            <div class="value">
              <span :class="['status-tag', getStatusClass(selectedEmployee.status)]">
                {{ selectedEmployee.status || '未知' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>



    <!-- 请假管理模态框 -->
    <div class="modal" v-if="showLeaveManagement">
      <div class="modal-content leave-modal-content">
        <div class="modal-header">
          <h3>请假管理</h3>
          <span class="close-btn" @click="showLeaveManagement = false">&times;</span>
        </div>
        <div class="modal-body">
          <div class="tabs">
            <div
              class="tab"
              :class="{ active: activeLeaveTab === 'pending' }"
              @click="activeLeaveTab = 'pending'"
            >
              待审批申请
            </div>
            <div
              class="tab"
              :class="{ active: activeLeaveTab === 'history' }"
              @click="activeLeaveTab = 'history'"
            >
              历史记录
            </div>
          </div>

          <!-- 待审批申请列表 -->
          <div v-if="activeLeaveTab === 'pending'" class="tab-content">
            <PendingLeaveList
              :approver-id="currentForeman.id"
              :group-id="currentForeman.group_id"
              ref="pendingLeaveList"
              @leave-approved="handleLeaveApproved"
              @leave-rejected="handleLeaveRejected"
            />
          </div>

          <!-- 历史记录列表 -->
          <div v-if="activeLeaveTab === 'history'" class="tab-content">
            <div class="leave-list">
              <div class="leave-item" v-for="(leave, index) in leaveRequests" :key="index">
                <div class="leave-header">
                  <span class="employee-name">{{ leave.employeeName }}</span>
                  <span :class="['status-tag', leave.status]">{{ leave.statusText }}</span>
                </div>
                <div class="leave-details">
                  <div class="leave-type">{{ leave.type }}</div>
                  <div class="leave-period">{{ leave.startDate }} 至 {{ leave.endDate }}</div>
                  <div class="leave-reason">
                    <div class="reason-label">请假原因：</div>
                    <div class="reason-content">{{ leave.reason }}</div>
                  </div>
                  <div class="approval-info">
                    <div class="approval-time">审批时间：{{ leave.approvalTime }}</div>
                    <div class="approver-info" v-if="leave.approverName">审批人：{{ leave.approverName }} ({{ leave.approverRole ? getRoleName(leave.approverRole) : '未知' }})</div>
                    <div class="approval-notes" v-if="leave.notes">备注：{{ leave.notes }}</div>
                  </div>
                </div>
              </div>

              <div v-if="leaveRequests.length === 0" class="empty-state">
                暂无历史记录
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>



    <!-- 修改状态模态框 -->
    <div class="modal" v-if="showUpdateStatus">
      <div class="modal-content">
        <div class="modal-header">
          <h3>修改员工状态</h3>
          <span class="close-btn" @click="showUpdateStatus = false">&times;</span>
        </div>
        <div class="modal-body">
          <div class="employee-info">
            <div class="info-item">
              <label>工号：</label>
              <span>{{ selectedEmployee.id }}</span>
            </div>
            <div class="info-item">
              <label>姓名：</label>
              <span>{{ selectedEmployee.name }}</span>
            </div>
            <div class="info-item">
              <label>当前状态：</label>
              <span class="status-tag" :class="getStatusClass(selectedEmployee.status)">
                {{ selectedEmployee.status || '未知' }}
              </span>
            </div>
          </div>

          <div class="form-group">
            <label>新状态：</label>
            <select v-model="newStatus" class="form-control">
              <option value="">请选择新状态</option>
              <option value="在岗">在岗</option>
              <option value="请假">请假</option>
              <option value="离岗">离岗</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showUpdateStatus = false">取消</button>
          <button
            class="confirm-btn"
            :disabled="!newStatus || statusUpdateLoading"
            @click="updateEmployeeStatus"
          >
            {{ statusUpdateLoading ? '更新中...' : '确认更新' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 分配设备模态框 -->
    <div class="modal" v-if="showAssignDevice">
      <div class="modal-content">
        <div class="modal-header">
          <h3>分配设备给 {{ selectedWorker.name }}</h3>
          <span class="close-btn" @click="showAssignDevice = false">&times;</span>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>选择设备</label>
            <select v-model="selectedDeviceId" class="form-control">
              <option value="">请选择设备</option>
              <option v-for="device in availableDevices" :key="device.id" :value="device.id">
                {{ device.equipment_name }} ({{ device.equipment_code || '无编号' }})
              </option>
            </select>
          </div>
          <div class="device-info" v-if="selectedDeviceId && getSelectedDevice()">
            <h4>设备信息</h4>
            <div class="info-item">
              <label>设备名称：</label>
              <span>{{ getSelectedDevice().equipment_name }}</span>
            </div>
            <div class="info-item">
              <label>设备编号：</label>
              <span>{{ getSelectedDevice().equipment_code || '无编号' }}</span>
            </div>
            <div class="info-item">
              <label>所属产线：</label>
              <span>{{ getSelectedDevice().line_name || '未知产线' }}</span>
            </div>
            <div class="info-item">
              <label>当前状态：</label>
              <span :class="['status-tag', getDeviceStatusClass(getSelectedDevice().status)]">{{ getSelectedDevice().status }}</span>
            </div>
            <div class="info-item" v-if="getSelectedDevice().worker_id">
              <label>当前负责人：</label>
              <span>{{ getDeviceWorkerName(getSelectedDevice().worker_id) }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showAssignDevice = false">取消</button>
          <button class="confirm-btn" @click="confirmAssignDevice">确认分配</button>
        </div>
      </div>
    </div>

    <!-- 分配产线模态框 -->
    <div class="modal" v-if="showAssignLine">
      <div class="modal-content">
        <div class="modal-header">
          <h3>分配产线给 {{ selectedWorker.name }}</h3>
          <span class="close-btn" @click="showAssignLine = false">&times;</span>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>选择产线</label>
            <select v-model="selectedLineId" class="form-control">
              <option value="">请选择产线</option>
              <option v-for="line in assignedLines" :key="line.id" :value="line.id">
                {{ line.name }}
              </option>
            </select>
          </div>
          <div class="line-info" v-if="selectedLineId && getSelectedLine()">
            <h4>产线信息</h4>
            <div class="info-item">
              <label>产线名称：</label>
              <span>{{ getSelectedLine().name }}</span>
            </div>
            <div class="info-item">
              <label>产线 ID：</label>
              <span>{{ getSelectedLine().id }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showAssignLine = false">取消</button>
          <button class="confirm-btn" @click="confirmAssignLine">确认分配</button>
        </div>
      </div>
    </div>

    <!-- 根据用户角色显示不同的导航栏 -->
    <ForemanNav v-if="currentForeman && currentForeman.role === 'foreman'" />
    <SafetyNav v-else-if="currentForeman && currentForeman.role === 'safety_officer'" />
  </div>
</template>

<script>
import ForemanNav from '@/components/ForemanNav.vue'
import SafetyNav from '@/components/SafetyNav.vue'
import PendingLeaveList from '@/components/PendingLeaveList.vue'

export default {
  name: 'TeamManagement',
  components: {
    ForemanNav,
    SafetyNav,
    PendingLeaveList
  },
  data() {
    return {
      // 工长被分配的产线
      assignedLines: [


      ],
      employees: [], // 清空本地数据
      leaveRequests: [

      ],
      filterLine: '',
      filterStatus: '',
      searchKeyword: '',
      showEmployeeDetail: false,
      showLeaveManagement: false,
      showStatusManagement: false,
      showAssignDevice: false,
      showAssignLine: false,
      showUpdateStatus: false,
      selectedEmployee: {},
      selectedWorker: {},
      selectedDeviceId: '',
      selectedLineId: '',
      availableDevices: [],
      currentForeman: null, // 存储当前工长信息
      newStatus: '',
      statusUpdateLoading: false,
      activeLeaveTab: 'pending' // 请假管理模态框的激活标签
    }
  },
  async created() {
    // 获取当前工长信息,并打印完整的用户信息用于调试
    const userInfoStr = localStorage.getItem('userInfo') || '{}';
    console.log('localStorage中的userInfo:', userInfoStr);

    const userInfo = JSON.parse(userInfoStr);
    console.log('解析后的用户信息:', userInfo);

    this.currentForeman = {
      id: userInfo.employee_id,
      employee_id: userInfo.employee_id, // 添加employee_id字段
      name: userInfo.username,
      role: userInfo.role,
      group_id: userInfo.group_id || 99
    };

    console.log('当前工长信息:', this.currentForeman);

    await this.fetchAssignedLines(); // 先获取产线信息
    await this.fetchEmployees();

    // 获取已处理的请假记录
    await this.fetchProcessedLeaveRequests();
  },
  computed: {
    filteredEmployees() {
      if (!this.currentForeman || !this.currentForeman.group_id) {
        console.log('当前工长组号未知');
        return [];
      }

      return this.employees.filter(emp => {
        // 首先检查组号是否匹配
        const groupMatch = Number(emp.group_id) === Number(this.currentForeman.group_id);
        if (!groupMatch) {
          console.log(`组号不匹配: ${emp.name}, 组号:${emp.group_id} vs ${this.currentForeman.group_id}`);
          return false;
        }

        // 然后应用其他筛选条件
        const lineMatch = !this.filterLine || (emp.assigned_lines && emp.assigned_lines.some(line => line.id === this.filterLine));
        const statusMatch = !this.filterStatus || emp.status === this.filterStatus;
        const searchMatch = !this.searchKeyword ||
          emp.name.includes(this.searchKeyword) ||
          emp.id.includes(this.searchKeyword);

        return lineMatch && statusMatch && searchMatch;
      });
    },

    // 修改产线员工数量统计方法
    getLineWorkerCount() {
      return (lineId) => {
        // 转换lineId为字符串，确保类型匹配
        const lineIdStr = String(lineId);

        // 详细调试日志
        console.log(`计算产线 ${lineIdStr} 的员工数量`);
        console.log(`当前员工总数: ${this.employees.length}`);

        // 查看产线信息
        const line = this.assignedLines.find(l => String(l.id) === lineIdStr);
        console.log(`产线信息:`, line);

        // 获取产线负责工长的分组号
        const lineManagerGroupId = this.getLineManagerGroupId(lineIdStr);
        console.log(`产线 ${lineIdStr} 的负责工长分组号: ${lineManagerGroupId}`);

        // 如果没有找到工长分组号，使用当前工长的分组号
        const groupId = lineManagerGroupId || this.currentForeman.group_id;
        console.log(`使用分组号: ${groupId} 来查询产线员工`);

        // 筛选该产线的员工
        const lineWorkers = this.employees.filter(emp => {
          // 检查员工是否负责该产线（通过assigned_lines字段）
          const isResponsibleForLine = emp.assigned_lines &&
            Array.isArray(emp.assigned_lines) &&
            emp.assigned_lines.some(assignedLine => String(assignedLine.id) === lineIdStr);

          // 检查员工是否属于该产线（通过line_id字段）
          const isAssignedToLine = emp.line_id && String(emp.line_id) === lineIdStr;

          // 检查员工组号是否与产线负责工长的组号匹配
          const groupMatch = String(emp.group_id) === String(groupId);

          // 员工属于该产线的条件：
          // 1. 员工的assigned_lines包含该产线，或
          // 2. 员工的line_id字段等于该产线ID，或
          // 3. 员工是该产线的负责工长，或
          // 4. 员工是工人（member角色）且属于该产线负责工长的组，或
          // 5. 员工是安全员（safety_officer角色）且属于该产线负责工长的组
          const isLineManager = line && line.foreman_id && String(emp.id) === String(line.foreman_id);
          const isWorkerInGroup = emp.role === 'member' && groupMatch;
          const isSafetyOfficerInGroup = emp.role === 'safety_officer' && groupMatch;

          const isRelatedToLine = isResponsibleForLine || isAssignedToLine || isLineManager || isWorkerInGroup || isSafetyOfficerInGroup;

          // 详细调试日志
          console.log(`员工 ${emp.name} (工号: ${emp.id}, 角色: ${emp.role}):`);
          console.log(`  - 通过assigned_lines关联: ${isResponsibleForLine}`);
          console.log(`  - 通过line_id关联: ${isAssignedToLine}`);
          console.log(`  - 是产线负责工长: ${isLineManager}`);
          console.log(`  - 是工长组内工人: ${isWorkerInGroup}`);
          console.log(`  - 是工长组内安全员: ${isSafetyOfficerInGroup}`);
          console.log(`  - 组号匹配: ${groupMatch} (员工组号: ${emp.group_id}, 产线工长组号: ${groupId})`);
          console.log(`  - 最终结果: ${isRelatedToLine}`);

          return isRelatedToLine;
        });

        console.log(`产线 ${lineIdStr} 的员工数量: ${lineWorkers.length}`);
        lineWorkers.forEach(worker => {
          console.log(`- 员工: ${worker.name}, 状态: ${worker.status}, 角色: ${worker.role}, 组号: ${worker.group_id}`);
        });

        return lineWorkers.length;
      };
    },

    // 修改产线在岗率统计方法
    getLineActiveRate() {
      return (lineId) => {
        // 转换lineId为字符串，确保类型匹配
        const lineIdStr = String(lineId);

        // 详细调试日志
        console.log(`计算产线 ${lineIdStr} 的在岗率`);
        console.log(`当前员工总数: ${this.employees.length}`);

        // 查看产线信息
        const line = this.assignedLines.find(l => String(l.id) === lineIdStr);
        console.log(`产线信息:`, line);

        // 获取产线负责工长的分组号
        const lineManagerGroupId = this.getLineManagerGroupId(lineIdStr);
        console.log(`产线 ${lineIdStr} 的负责工长分组号: ${lineManagerGroupId}`);

        // 如果没有找到工长分组号，使用当前工长的分组号
        const groupId = lineManagerGroupId || this.currentForeman.group_id;
        console.log(`使用分组号: ${groupId} 来查询产线员工`);

        // 筛选该产线的员工
        const lineWorkers = this.employees.filter(emp => {
          // 检查员工是否负责该产线（通过assigned_lines字段）
          const isResponsibleForLine = emp.assigned_lines &&
            Array.isArray(emp.assigned_lines) &&
            emp.assigned_lines.some(assignedLine => String(assignedLine.id) === lineIdStr);

          // 检查员工是否属于该产线（通过line_id字段）
          const isAssignedToLine = emp.line_id && String(emp.line_id) === lineIdStr;

          // 检查员工组号是否与产线负责工长的组号匹配
          const groupMatch = String(emp.group_id) === String(groupId);

          // 员工是否是该产线的负责工长
          const isLineManager = line && line.foreman_id && String(emp.id) === String(line.foreman_id);

          // 员工是否是工人角色且属于该产线负责工长的组
          const isWorkerInGroup = emp.role === 'member' && groupMatch;

          // 员工是否是安全员角色且属于该产线负责工长的组
          const isSafetyOfficerInGroup = emp.role === 'safety_officer' && groupMatch;

          // 员工属于该产线的条件：
          // 1. 员工的assigned_lines包含该产线，或
          // 2. 员工的line_id字段等于该产线ID，或
          // 3. 员工是该产线的负责工长，或
          // 4. 员工是工人（member角色）且属于该产线负责工长的组，或
          // 5. 员工是安全员（safety_officer角色）且属于该产线负责工长的组
          const isRelatedToLine = isResponsibleForLine || isAssignedToLine || isLineManager || isWorkerInGroup || isSafetyOfficerInGroup;

          // 详细调试日志
          console.log(`员工 ${emp.name} (工号: ${emp.id}, 角色: ${emp.role}):`);
          console.log(`  - 通过assigned_lines关联: ${isResponsibleForLine}`);
          console.log(`  - 通过line_id关联: ${isAssignedToLine}`);
          console.log(`  - 是产线负责工长: ${isLineManager}`);
          console.log(`  - 是工长组内工人: ${isWorkerInGroup}`);
          console.log(`  - 是工长组内安全员: ${isSafetyOfficerInGroup}`);
          console.log(`  - 组号匹配: ${groupMatch} (员工组号: ${emp.group_id}, 产线工长组号: ${groupId})`);
          console.log(`  - 最终结果: ${isRelatedToLine}`);

          return isRelatedToLine;
        });

        console.log(`产线 ${lineIdStr} 的员工数量: ${lineWorkers.length}`);
        lineWorkers.forEach(worker => {
          console.log(`- 员工: ${worker.name}, 状态: ${worker.status}, 角色: ${worker.role}, 组号: ${worker.group_id}`);
        });

        if (lineWorkers.length === 0) return 0;

        // 考虑中文和英文状态值
        const activeWorkers = lineWorkers.filter(emp => {
          // 在岗状态可能是中文或英文
          const isActive = emp.status === '在岗' || emp.status === 'active' || emp.status === 'task';
          console.log(`员工 ${emp.name} 状态: ${emp.status}, 是否在岗: ${isActive}`);
          return isActive;
        });

        // 计算在岗率
        const activeRate = Math.round((activeWorkers.length / lineWorkers.length) * 100);
        console.log(`产线 ${lineIdStr} 的在岗率: ${activeRate}%, 在岗人数: ${activeWorkers.length}, 总人数: ${lineWorkers.length}`);
        return activeRate;
      };
    },


  },
  methods: {
    // 获取分配给当前工长的产线信息
    async fetchAssignedLines() {
      try {
        if (!this.currentForeman || !this.currentForeman.id) {
          console.log('当前工长工号未知，无法获取产线信息');
          return;
        }

        const foremanId = this.currentForeman.id;
        console.log('开始获取产线数据,工长工号:', foremanId);
        const response = await fetch(`/api/foreman/assigned-lines?employee_id=${foremanId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('产线返回数据:', data);

        if (data.success && Array.isArray(data.data)) {
          console.log('原始产线数据:');
          data.data.forEach(line => {
            console.log(`产线 ID: ${line.id}, 名称: ${line.name}, 类型: ${typeof line.id}`);
          });

          this.assignedLines = data.data.map(line => ({
            ...line, // 保持原始数据格式
            name: line.line_name || line.name || `产线${line.id}`, // 确保有name字段
            foreman_id: line.foreman_id || null // 确保有foreman_id字段
          }));

          console.log('处理后的产线数据:');
          this.assignedLines.forEach(line => {
            console.log(`产线 ID: ${line.id}, 名称: ${line.name}, 类型: ${typeof line.id}`);
          });
        } else {
          throw new Error(data.error || '产线数据格式错误');
        }
      } catch (error) {
        console.error('获取产线列表出错:', error);
      }
    },

    async fetchEmployees() {
      try {
        console.log('开始获取员工数据,工长组号:', this.currentForeman.group_id);
        const response = await fetch(`/api/foreman/team-members?group_id=${this.currentForeman.group_id}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('原始返回数据:', data);

        if (data.success && Array.isArray(data.data)) {
          // 打印原始员工数据中的line_id字段
          console.log('员工原始数据中的line_id字段:');
          data.data.forEach(emp => {
            console.log(`员工 ${emp.name} 的line_id: ${emp.line_id}, 类型: ${typeof emp.line_id}`);
          });

          // 处理员工数据,只保留后端提供的字段
          this.employees = data.data.map(emp => {
            // 打印员工原始状态
            console.log(`员工 ${emp.name} 原始状态: ${emp.status}`);

            return {
              ...emp,
              // 保留原始状态，不设置默认值
              assigned_lines: emp.assigned_lines || [],
              assigned_equipment: emp.assigned_equipment || []
            };
          });

          // 打印处理后的员工状态
          console.log('处理后的员工状态:');
          this.employees.forEach(emp => {
            console.log(`员工 ${emp.name} 状态: ${emp.status}`);
          });

          // 打印处理后的员工数据
          console.log('处理后的员工数据:');
          this.employees.forEach(emp => {
            console.log(`员工 ${emp.name} 的line_id: ${emp.line_id}, 类型: ${typeof emp.line_id}`);
          });
        } else {
          throw new Error(data.error || '数据格式错误');
        }
      } catch (error) {
        console.error('获取员工列表出错:', error);
      }
    },

    // 获取角色名称显示
    getRoleName(role) {
      const roleMap = {
        'supervisor': '厂长',
        'foreman': '工长',
        'member': '产线工人',
        'safety_officer': '安全员'
      };
      return roleMap[role] || role;
    },

    // 获取状态显示文本
    getStatusText(emp) {
      // 如果是安全员
      if (emp.role === 'safety_officer') {
        return '安全员';
      }

      // 如果是工长
      if (emp.role === 'foreman') {
        // 如果是当前工长
        if (emp.id === this.currentForeman.id) {
          return '当前工长';
        }
        return '同组工长';
      }

      const statusMap = {
        'active': '在岗',
        'leave': '请假',
        'task': '任务中',
        'off': '离岗'
      };
      return statusMap[emp.status] || '未知';
    },

    // 获取工长的产线名称列表，用于显示工人的产线
    getForemanLines() {
      // 找到当前工长
      const foreman = this.employees.find(emp =>
        emp.role === 'foreman' && emp.group_id === this.currentForeman.group_id
      );

      if (foreman && foreman.assigned_lines && foreman.assigned_lines.length > 0) {
        return foreman.assigned_lines.map(line => line.name).join(', ');
      }
      return '无';
    },

    // 获取产线负责工长的分组号
    getLineManagerGroupId(lineId) {
      // 转换lineId为字符串，确保类型匹配
      const lineIdStr = String(lineId);

      // 查找产线信息
      const line = this.assignedLines.find(l => String(l.id) === lineIdStr);
      if (!line) {
        console.log(`未找到产线 ${lineIdStr} 的信息`);
        return null;
      }

      // 获取产线的负责工长ID
      const foremanId = line.foreman_id;
      if (!foremanId) {
        console.log(`产线 ${lineIdStr} 没有指定负责工长`);
        return null;
      }

      // 查找工长信息
      const foreman = this.employees.find(emp =>
        emp.role === 'foreman' && String(emp.id) === String(foremanId)
      );

      if (!foreman) {
        console.log(`未找到工长 ${foremanId} 的信息`);
        return null;
      }

      console.log(`产线 ${lineIdStr} 的负责工长 ${foreman.name} 的分组号: ${foreman.group_id}`);
      return foreman.group_id;
    },

    // 查看产线详情
    viewLineDetail(line) {
      console.log('查看产线详情:', line);
      // 跳转到产线详情页面
      this.$router.push(`/foreman/production-line-detail/${line.id}`);
    },

    // 查看员工详情
    viewEmployeeDetail(employee) {
      this.selectedEmployee = { ...employee };
      this.showEmployeeDetail = true;
    },

    // 关闭员工详情
    closeEmployeeDetail() {
      this.showEmployeeDetail = false;
      this.selectedEmployee = {};
    },

    // 批准请假
    approveLeave(index) {
      this.leaveRequests[index].status = 'approved';
      this.leaveRequests[index].statusText = '已批准';

      // 更新员工状态
      const employeeId = this.leaveRequests[index].employeeId;
      const empIndex = this.employees.findIndex(emp => emp.id === employeeId);
      if (empIndex !== -1) {
        this.employees[empIndex].status = 'leave';
        this.employees[empIndex].statusText = '请假';
      }
    },

    // 拒绝请假
    rejectLeave(index) {
      this.leaveRequests[index].status = 'rejected';
      this.leaveRequests[index].statusText = '已拒绝';
    },

    // 显示分配设备模态框
    async showAssignDeviceModal(worker) {
      this.selectedWorker = worker;
      this.selectedDeviceId = '';
      this.showAssignDevice = true;

      // 获取可分配的设备列表
      await this.fetchAvailableDevices();
    },

    // 显示分配产线模态框
    showAssignLineModal(worker) {
      this.selectedWorker = worker;
      this.selectedLineId = '';
      this.showAssignLine = true;
    },

    // 获取可分配的设备列表
    async fetchAvailableDevices() {
      try {
        // 获取当前工长的组号和工号
        const groupId = this.currentForeman.group_id;
        const foremanId = this.currentForeman.id; // 使用id代替employee_id

        console.log('当前工长信息:', {
          id: this.currentForeman.id,
          name: this.currentForeman.name,
          employee_id: this.currentForeman.employee_id,
          group_id: groupId
        });

        if (!groupId) {
          console.error('未找到组号信息');
          return;
        }

        if (!foremanId) {
          console.error('未找到工长工号信息');
          return;
        }

        // 使用正确的API获取工长负责的产线
        const linesResponse = await fetch(`/api/foreman/assigned-lines?employee_id=${foremanId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!linesResponse.ok) {
          throw new Error(`获取产线列表失败: ${linesResponse.status}`);
        }

        const linesResult = await linesResponse.json();
        console.log('产线列表数据:', linesResult);

        if (!linesResult.success || !linesResult.data || linesResult.data.length === 0) {
          console.warn('没有找到工长负责的产线');
          this.availableDevices = [];
          return;
        }

        // 获取这些产线上的设备
        const lineIds = linesResult.data.map(line => line.id);
        console.log('产线 ID 列表:', lineIds);

        // 直接获取组号对应的所有设备
        const equipmentResponse = await fetch(`/api/equipment/with-status?group_id=${groupId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!equipmentResponse.ok) {
          throw new Error(`获取设备列表失败: ${equipmentResponse.status}`);
        }

        const equipmentResult = await equipmentResponse.json();
        console.log('设备列表数据:', equipmentResult);

        if (!equipmentResult.success || !equipmentResult.data) {
          console.warn('没有找到设备数据');
          this.availableDevices = [];
          return;
        }

        // 过滤出属于工长负责产线的设备
        const lineIdSet = new Set(lineIds.map(id => id.toString()));
        const filteredDevices = equipmentResult.data.filter(device => {
          // 确保类型一致性
          const deviceLineId = device.line_id ? device.line_id.toString() : '';
          return lineIdSet.has(deviceLineId);
        });

        console.log('过滤后的设备数据:', filteredDevices);
        this.availableDevices = filteredDevices;

        if (filteredDevices.length === 0) {
          console.warn('没有找到可分配的设备');
        }
      } catch (error) {
        console.error('获取设备列表出错:', error);
        alert('获取设备列表失败，请重试');
      }
    },

    // 获取选中的设备
    getSelectedDevice() {
      return this.availableDevices.find(device => device.id === this.selectedDeviceId);
    },

    // 获取选中的产线
    getSelectedLine() {
      return this.assignedLines.find(line => String(line.id) === String(this.selectedLineId));
    },

    // 获取设备状态类名
    getDeviceStatusClass(status) {
      if (status === '故障') return 'error';
      if (status === '预警') return 'warning';
      if (status === '停机') return 'stopped';
      if (status === '维修中') return 'warning';
      return 'normal';
    },

    // 获取设备负责人名称
    getDeviceWorkerName(workerId) {
      if (!workerId) return '无';
      const worker = this.employees.find(emp => emp.id === workerId);
      return worker ? worker.name : '未知';
    },

    // 获取状态类名
    getStatusClass(status) {
      // 打印状态值以便调试
      console.log(`获取状态类名，状态值: ${status}, 类型: ${typeof status}`);

      // 处理中文状态
      if (status === '在岗') return 'status-active';
      if (status === '请假') return 'status-leave';
      if (status === '离岗') return 'status-off';

      // 处理英文状态
      if (status === 'active' || status === 'task') return 'status-active';
      if (status === 'leave') return 'status-leave';
      if (status === 'off') return 'status-off';

      // 如果状态为空或未知，返回空字符串
      return '';
    },



    // 显示修改状态模态框
    showUpdateStatusModal(employee) {
      this.selectedEmployee = { ...employee };
      this.newStatus = '';
      this.showUpdateStatus = true;
    },

    // 更新员工状态
    async updateEmployeeStatus() {
      if (!this.newStatus || this.statusUpdateLoading) return;

      this.statusUpdateLoading = true;

      try {
        const response = await fetch('/api/attendance/update-status', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            employee_id: this.selectedEmployee.id,
            status: this.newStatus
          })
        });

        const result = await response.json();

        if (result.success) {
          alert('员工状态更新成功');
          this.showUpdateStatus = false;

          // 更新本地数据
          const index = this.employees.findIndex(emp => emp.id === this.selectedEmployee.id);
          if (index !== -1) {
            this.$set(this.employees[index], 'status', this.newStatus);
          }

          // 刷新员工列表
          await this.fetchEmployees();
        } else {
          alert(`更新员工状态失败: ${result.error}`);
        }
      } catch (error) {
        console.error('更新员工状态出错:', error);
        alert('更新员工状态失败，请重试');
      } finally {
        this.statusUpdateLoading = false;
      }
    },

    // 确认分配设备
    async confirmAssignDevice() {
      if (!this.selectedDeviceId) {
        alert('请选择设备');
        return;
      }

      try {
        // 调用API分配设备
        const response = await fetch('/api/equipment/assign-worker', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            equipment_id: this.selectedDeviceId,
            worker_id: this.selectedWorker.id
          })
        });

        const result = await response.json();

        if (result.success) {
          alert('设备分配成功！');
          this.showAssignDevice = false;

          // 重新获取员工数据
          await this.fetchEmployees();
        } else {
          alert(`分配失败: ${result.error || '未知错误'}`);
        }
      } catch (error) {
        console.error('分配设备出错:', error);
        alert('分配设备失败，请重试');
      }
    },

    // 确认分配产线
    async confirmAssignLine() {
      if (!this.selectedLineId) {
        alert('请选择产线');
        return;
      }

      try {
        // 获取员工当前的产线关联
        const currentLines = this.selectedWorker.assigned_lines || [];

        // 检查是否已经关联了该产线
        const alreadyAssigned = currentLines.some(line => String(line.id) === String(this.selectedLineId));

        if (alreadyAssigned) {
          alert('该员工已经关联了该产线');
          return;
        }

        // 获取选中的产线
        const selectedLine = this.getSelectedLine();

        if (!selectedLine) {
          alert('无法获取产线信息');
          return;
        }

        // 手动关联员工与产线
        // 在实际项目中，这里应该调用后端API
        // 这里我们只是在前端模拟关联

        // 添加新的产线关联
        const newAssignedLines = [...currentLines, {
          id: selectedLine.id,
          name: selectedLine.name
        }];

        // 更新员工数据
        const index = this.employees.findIndex(emp => emp.id === this.selectedWorker.id);
        if (index !== -1) {
          // 更新员工的产线关联
          this.$set(this.employees[index], 'assigned_lines', newAssignedLines);

          // 打印调试信息
          console.log(`已将产线 ${selectedLine.name} (ID: ${selectedLine.id}) 分配给员工 ${this.selectedWorker.name}`);
          console.log('更新后的员工产线关联:', newAssignedLines);

          alert('产线分配成功！');
          this.showAssignLine = false;
        } else {
          alert('找不到员工数据，无法更新');
        }
      } catch (error) {
        console.error('分配产线出错:', error);
        alert('分配产线失败，请重试');
      }
    },

    // 员工状态更新后的处理
    handleStatusUpdated() {
      // 刷新员工列表
      this.fetchEmployees();
    },

    // 处理请假审批通过
    async handleLeaveApproved(leaveRequest) {
      // 将审批通过的请假添加到历史记录
      this.leaveRequests.unshift({
        employeeId: leaveRequest.employee_id,
        employeeName: leaveRequest.employee_name,
        type: leaveRequest.leave_type,
        startDate: leaveRequest.start_date,
        endDate: leaveRequest.end_date,
        reason: leaveRequest.reason,
        status: 'approved',
        statusText: '已批准',
        approvalTime: new Date().toLocaleString()
      });

      // 刷新员工列表
      await this.fetchEmployees();

      // 刷新请假历史记录
      await this.fetchProcessedLeaveRequests();
    },

    // 处理请假审批拒绝
    async handleLeaveRejected(leaveRequest) {
      // 将审批拒绝的请假添加到历史记录
      this.leaveRequests.unshift({
        employeeId: leaveRequest.employee_id,
        employeeName: leaveRequest.employee_name,
        type: leaveRequest.leave_type,
        startDate: leaveRequest.start_date,
        endDate: leaveRequest.end_date,
        reason: leaveRequest.reason,
        status: 'rejected',
        statusText: '已拒绝',
        approvalTime: new Date().toLocaleString()
      });

      // 刷新请假历史记录
      await this.fetchProcessedLeaveRequests();
    },

    // 获取已处理的请假记录
    async fetchProcessedLeaveRequests() {
      try {
        if (!this.currentForeman || !this.currentForeman.group_id) {
          console.log('当前工长组号未知，无法获取请假记录');
          return;
        }

        const response = await fetch(`/api/attendance/processed-leaves?group_id=${this.currentForeman.group_id}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        const result = await response.json();

        if (result.success && Array.isArray(result.data)) {
          console.log('获取到的请假记录:', result.data);

          // 将后端返回的数据转换为前端需要的格式
          this.leaveRequests = result.data.map(leave => ({
            id: leave.id,
            employeeId: leave.employee_id,
            employeeName: leave.employee_name,
            type: leave.leave_type,
            startDate: leave.start_date,
            endDate: leave.end_date,
            reason: leave.reason,
            status: leave.status === '已批准' ? 'approved' : 'rejected',
            statusText: leave.status,
            approvalTime: leave.approval_time,
            approverName: leave.approver_name,
            approverRole: leave.approver_role,
            notes: leave.approval_notes
          }));
        } else {
          console.error('获取已处理请假记录失败:', result.error || '未知错误');
        }
      } catch (error) {
        console.error('获取已处理请假记录出错:', error);
      }
    }
  }
}
</script>

<style scoped>
.team {
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
  background-color: #f4f4f4;
}

.authority-notice {
  background-color: #e3f2fd;
  border-left: 4px solid #2196F3;
  padding: 10px 15px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  border-radius: 4px;
}

.info-icon {
  width: 20px;
  height: 20px;
  background-color: #2196F3;
  border-radius: 50%;
  margin-right: 10px;
  position: relative;
}

.info-icon::after {
  content: 'i';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-style: italic;
  font-weight: bold;
}

.department-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.dept-card {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dept-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.dept-header h3 {
  margin: 0;
  font-size: 1.1em;
}

.member-count {
  background-color: #e3f2fd;
  color: #2196F3;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.9em;
}

.dept-stats {
  display: flex;
  justify-content: space-between;
}

.dept-actions {
  display: flex;
  justify-content: center;
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.label {
  font-size: 0.8em;
  color: #666;
  margin-bottom: 5px;
}

.value {
  font-weight: bold;
  color: #333;
}

.employee-section {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h3 {
  margin: 0;
}

.view-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.calendar-icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  margin-right: 5px;
  position: relative;
}

.calendar-icon::before {
  content: '📅';
}

.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.filter-select, .search-input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  flex: 1;
}

.employee-list table {
  width: 100%;
  border-collapse: collapse;
}

.employee-list th, .employee-list td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.employee-list th {
  background-color: #f9f9f9;
  font-weight: 600;
}

.status-tag {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.8em;
}

.status-tag.status-active {
  background-color: #e8f5e9;
  color: #4CAF50;
}

.status-tag.status-leave {
  background-color: #fff8e1;
  color: #FFC107;
}

.status-tag.status-off {
  background-color: #f5f5f5;
  color: #666;
}

.status-tag.pending {
  background-color: #f5f5f5;
  color: #9e9e9e;
}

.status-tag.approved {
  background-color: #e8f5e9;
  color: #4CAF50;
}

.status-tag.rejected {
  background-color: #ffebee;
  color: #f44336;
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

.action-btn.status {
  background-color: #e3f2fd;
  color: #2196F3;
}

.action-btn.approve {
  background-color: #e8f5e9;
  color: #4CAF50;
}

.action-btn.reject {
  background-color: #ffebee;
  color: #f44336;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
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
}

.close-btn {
  font-size: 1.5em;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 15px;
}

.modal-footer {
  padding: 15px;
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
  font-weight: 600;
}

.form-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn.cancel {
  background-color: #f5f5f5;
  color: #333;
}

.btn.submit {
  background-color: #2196F3;
  color: white;
}

.detail-item {
  margin-bottom: 15px;
}

.detail-item label {
  display: block;
  font-size: 0.9em;
  color: #666;
  margin-bottom: 5px;
}

.detail-item .value {
  font-weight: 500;
}

.leave-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.leave-item {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
}

.leave-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

/* 当前工长行样式 */
.current-foreman {
  background-color: rgba(33, 150, 243, 0.1);
  font-weight: bold;
}

.current-foreman td {
  position: relative;
}

.current-foreman td:first-child::before {
  content: '(您)';
  color: #2196F3;
  font-size: 0.8em;
  margin-right: 5px;
}

.employee-name {
  font-weight: bold;
}

.leave-details {
  margin-bottom: 15px;
}

.leave-type {
  font-weight: 500;
  margin-bottom: 5px;
}

.leave-period {
  color: #666;
  margin-bottom: 5px;
}

.leave-reason {
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
  margin-bottom: 10px;
}

.reason-label {
  font-weight: 500;
  margin-bottom: 5px;
  color: #555;
}

.reason-content {
  white-space: pre-line;
}

.approval-info {
  padding: 10px;
  background-color: #f0f8ff;
  border-radius: 4px;
  font-size: 14px;
  color: #555;
}

.approval-time, .approver-info {
  margin-bottom: 5px;
}

.approval-notes {
  font-style: italic;
  color: #666;
}

.leave-actions {
  display: flex;
  gap: 10px;
}

/* 设备信息样式 */
.device-info {
  margin-top: 15px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #eee;
}

.device-info h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
}

.info-item {
  display: flex;
  margin-bottom: 8px;
}

.info-item label {
  font-weight: 600;
  width: 100px;
  flex-shrink: 0;
}

.info-item span {
  flex: 1;
}

.leave-modal-content {
  max-width: 800px;
  width: 95%;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #eee;
  margin-bottom: 15px;
}

.tab {
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.tab.active {
  border-bottom-color: #2196F3;
  color: #2196F3;
  font-weight: 500;
}

.tab-content {
  padding: 10px 0;
}

.empty-state {
  padding: 30px 0;
  text-align: center;
  color: #999;
}

.form-control {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 10px;
}

.confirm-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 15px;
  cursor: pointer;
}

.cancel-btn {
  background-color: #f5f5f5;
  color: #333;
  border: none;
  border-radius: 4px;
  padding: 8px 15px;
  cursor: pointer;
}

/* 状态管理模态框样式 */
.status-modal-content {
  max-width: 800px;
  width: 95%;
}

.status-icon::before {
  content: '📈';
}

.header-actions {
  display: flex;
  gap: 10px;
}
</style>
