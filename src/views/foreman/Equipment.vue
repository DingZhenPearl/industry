<template>
  <div class="equipment">
    <header class="header">
      <h1>设备与产线</h1>
    </header>
    <EquipmentGantt class="equipment-gantt-section" />
    
    <div class="content">
      <div class="authority-notice">
        <i class="info-icon"></i>
        <span>您有权管理 <strong>{{ assignedLines.length }}</strong> 条产线</span>
      </div>
      
      <!-- 产线状态卡片 -->
      <div class="line-cards">
        <div class="line-card" v-for="line in assignedLines" :key="line.id">
          <div class="line-header">
            <h3>{{ line.name }}</h3>
            <span :class="['status-tag', line.status]">{{ line.statusText }}</span>
          </div>
          <div class="line-body">
            <div class="stat-item">
              <span class="label">设备运行</span>
              <span class="value">{{ line.runningDevices }}/{{ line.totalDevices }}</span>
            </div>
            <div class="stat-item">
              <span class="label">产能利用率</span>
              <span class="value">{{ line.utilization }}%</span>
            </div>
          </div>
          <div class="line-actions">
            <button class="action-btn" @click="manageDevices(line)">管理设备</button>
            <button class="action-btn" @click="scheduleMaintenace(line)">排程维护</button>
          </div>
        </div>
      </div>

      <!-- 设备列表 -->
      <div class="equipment-section">
        <div class="section-header">
          <h2>设备列表</h2>
          <div class="filter-bar">
            <select v-model="filterLine" class="filter-select">
              <option value="">全部产线</option>
              <option v-for="line in assignedLines" :key="line.id" :value="line.name">
                {{ line.name }}
              </option>
            </select>
            <select v-model="filterStatus" class="filter-select">
              <option value="">全部状态</option>
              <option value="running">运行中</option>
              <option value="warning">异常</option>
              <option value="stopped">已停机</option>
            </select>
          </div>
        </div>

        <div class="equipment-list">
          <div class="equipment-item" v-for="device in filteredDevices" :key="device.id">
            <div class="device-header">
              <span class="device-name">{{ device.name }}</span>
              <span :class="['device-status', device.status]">{{ device.statusText }}</span>
            </div>
            <div class="device-info">
              <div class="info-row">
                <span>所属产线：{{ device.productionLine }}</span>
                <span>运行时长：{{ device.runtime }}h</span>
              </div>
              <div class="info-row">
                <span>负责人：{{ device.manager }}</span>
                <span>上次维护：{{ device.lastMaintenance }}</span>
              </div>
            </div>
            <div class="device-actions">
              <button class="action-btn" @click="viewDeviceDetail(device)">查看详情</button>
              <button class="action-btn" @click="reportIssue(device)" v-if="device.status !== 'stopped'">上报故障</button>
              <button class="action-btn primary" @click="startMaintenance(device)" v-if="device.status === 'warning'">开始维护</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 维护排程模态框 -->
      <div class="modal" v-if="showMaintenanceModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>设备维护排程</h3>
            <span class="close-btn" @click="showMaintenanceModal = false">&times;</span>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>产线</label>
              <div class="value">{{ selectedLine.name }}</div>
            </div>
            <div class="form-group">
              <label>维护时间</label>
              <input type="datetime-local" v-model="maintenanceForm.time" class="form-input">
            </div>
            <div class="form-group">
              <label>维护工程师</label>
              <select v-model="maintenanceForm.engineer" class="form-input">
                <option value="">请选择工程师</option>
                <option value="张工">张工</option>
                <option value="李工">李工</option>
                <option value="王工">王工</option>
              </select>
            </div>
            <div class="form-group">
              <label>维护类型</label>
              <select v-model="maintenanceForm.type" class="form-input">
                <option value="">请选择维护类型</option>
                <option value="regular">定期保养</option>
                <option value="repair">故障修复</option>
                <option value="update">设备升级</option>
              </select>
            </div>
            <div class="form-group">
              <label>备注</label>
              <textarea v-model="maintenanceForm.notes" class="form-input" rows="3"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn cancel" @click="showMaintenanceModal = false">取消</button>
            <button class="btn submit" @click="submitMaintenance">提交</button>
          </div>
        </div>
      </div>
    </div>

    <ForemanNav />
  </div>
</template>

<script>
import ForemanNav from '@/components/ForemanNav.vue'
import EquipmentGantt from './EquipmentGantt.vue'

export default {
  components: {
    ForemanNav,
    EquipmentGantt
  },
  name: 'ForemanEquipment',
  data() {
    return {
      filterLine: '',
      filterStatus: '',
      showMaintenanceModal: false,
      selectedLine: {},
      maintenanceForm: {
        time: '',
        engineer: '',
        type: '',
        notes: ''
      },
      // 工长被分配的产线
      assignedLines: [
        {
          id: 1,
          name: '车身冲压生产线',
          status: 'running',
          statusText: '运行中',
          runningDevices: 12,
          totalDevices: 15,
          utilization: 88,
          assignedTo: 1 // 分配给当前工长的ID
        },
        {
          id: 2,
          name: '车身焊接生产线',
          status: 'warning',
          statusText: '预警',
          runningDevices: 8,
          totalDevices: 10,
          utilization: 75,
          assignedTo: 1 // 分配给当前工长的ID
        },
        {
          id: 3,
          name: '底盘装配生产线',
          status: 'running',
          statusText: '运行中',
          runningDevices: 9,
          totalDevices: 12,
          utilization: 82,
          assignedTo: 1 // 分配给当前工长的ID
        }
      ],
      // 所有设备列表
      devices: [
        {
          id: 1,
          name: '车身冲压机R-2023',
          productionLine: '车身冲压生产线',
          status: 'running',
          statusText: '运行中',
          runtime: 126.5,
          manager: '张工',
          lastMaintenance: '2023-07-01'
        },
        {
          id: 2,
          name: '钢板输送系统S-101',
          productionLine: '车身冲压生产线',
          status: 'running',
          statusText: '运行中',
          runtime: 130.2,
          manager: '李工',
          lastMaintenance: '2023-07-03'
        },
        {
          id: 3,
          name: '模具更换机械臂M-305',
          productionLine: '车身冲压生产线',
          status: 'warning',
          statusText: '预警',
          runtime: 85.5,
          manager: '王工',
          lastMaintenance: '2023-07-05'
        },
        {
          id: 4,
          name: '焊接机器人W-501',
          productionLine: '车身焊接生产线',
          status: 'warning',
          statusText: '预警',
          runtime: 95.2,
          manager: '赵工',
          lastMaintenance: '2023-07-02'
        },
        {
          id: 5,
          name: '激光焊接系统L-202',
          productionLine: '车身焊接生产线',
          status: 'running',
          statusText: '运行中',
          runtime: 110.5,
          manager: '钱工',
          lastMaintenance: '2023-07-04'
        },
        {
          id: 6,
          name: '底盘组装机A-601',
          productionLine: '底盘装配生产线',
          status: 'running',
          statusText: '运行中',
          runtime: 78.5,
          manager: '孙工',
          lastMaintenance: '2023-07-06'
        },
        {
          id: 7,
          name: '悬挂系统安装设备S-702',
          productionLine: '底盘装配生产线',
          status: 'stopped',
          statusText: '已停机',
          runtime: 45.5,
          manager: '周工',
          lastMaintenance: '2023-07-03'
        }
      ]
    }
  },
  computed: {
    // 工长只能看到自己负责的产线设备
    filteredDevices() {
      // 获取分配给当前工长的产线名称列表
      const assignedLineNames = this.assignedLines.map(line => line.name);
      
      return this.devices.filter(device => {
        // 首先检查设备是否属于工长负责的产线
        const belongsToAssignedLine = assignedLineNames.includes(device.productionLine);
        if (!belongsToAssignedLine) return false;
        
        // 然后应用筛选条件
        const lineMatch = !this.filterLine || device.productionLine === this.filterLine;
        const statusMatch = !this.filterStatus || device.status === this.filterStatus;
        return lineMatch && statusMatch;
      });
    }
  },
  methods: {
    manageDevices(line) {
      console.log('管理产线设备:', line);
      this.filterLine = line.name;
    },
    scheduleMaintenace(line) {
      this.selectedLine = line;
      this.showMaintenanceModal = true;
    },
    viewDeviceDetail(device) {
      console.log('查看设备详情:', device);
    },
    reportIssue(device) {
      console.log('上报设备故障:', device);
    },
    startMaintenance(device) {
      console.log('开始维护设备:', device);
    },
    submitMaintenance() {
      console.log('提交维护排程:', {
        line: this.selectedLine,
        ...this.maintenanceForm
      });
      this.showMaintenanceModal = false;
      // 重置表单
      this.maintenanceForm = {
        time: '',
        engineer: '',
        type: '',
        notes: ''
      };
    }
  }
}
</script>

<style scoped>
.equipment {
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

.line-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.line-card {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.line-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.status-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-tag.running {
  background: #e8f5e9;
  color: #4CAF50;
}

.status-tag.warning {
  background: #fff3e0;
  color: #ff9800;
}

.status-tag.stopped {
  background: #ffebee;
  color: #f44336;
}

.line-body {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.stat-item {
  text-align: center;
}

.stat-item .label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.stat-item .value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.equipment-section {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.section-header {
  margin-bottom: 15px;
}

.section-header h2 {
  margin: 0 0 10px 0;
  font-size: 18px;
}

.filter-bar {
  display: flex;
  gap: 10px;
}

.filter-select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 150px;
}

.equipment-list {
  display: grid;
  gap: 15px;
}

.equipment-item {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
}

.device-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.device-name {
  font-weight: bold;
  font-size: 16px;
}

.device-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.device-status.running {
  background: #e8f5e9;
  color: #4CAF50;
}

.device-status.warning {
  background: #fff3e0;
  color: #ff9800;
}

.device-status.stopped {
  background: #ffebee;
  color: #f44336;
}

.device-info {
  color: #666;
  font-size: 14px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.authority-notice {
  background: #e3f2fd;
  color: #2196F3;
  padding: 10px 15px;
  border-radius: 8px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.info-icon {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-color: #2196F3;
  mask-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" /></svg>');
  mask-repeat: no-repeat;
  mask-position: center;
}

.line-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  background: #e3f2fd;
  color: #2196F3;
  cursor: pointer;
}

.action-btn.primary {
  background: #2196F3;
  color: white;
}

.device-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
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
  color: #666;
}

.form-group .value {
  font-weight: bold;
}

.form-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
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
  background: #4CAF50;
  color: white;
}
</style>
