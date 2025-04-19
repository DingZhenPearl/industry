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
            <button class="action-btn" @click="viewLineDetail(line)">查看详情</button>
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
      assignedLines: [],
      // 所有设备列表
      devices: [],
      // 当前工长信息
      currentForeman: null,
      // 加载状态
      loading: {
        lines: false,
        devices: false
      },
      // 产线和设备的映射关系
      lineNameMap: {}
    }
  },
  created() {
    // 获取当前工长信息
    this.getCurrentForeman();
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
    // 获取当前工长信息
    getCurrentForeman() {
      const userInfoStr = localStorage.getItem('userInfo');
      if (userInfoStr) {
        this.currentForeman = JSON.parse(userInfoStr);
        console.log('当前工长信息:', this.currentForeman);
        // 获取工长负责的产线
        this.fetchAssignedLines();
      } else {
        console.error('未找到工长信息');
      }
    },

    // 获取工长负责的产线
    async fetchAssignedLines() {
      try {
        this.loading.lines = true;
        if (!this.currentForeman || !this.currentForeman.employee_id) {
          console.log('当前工长工号未知，无法获取产线信息');
          return;
        }

        console.log('开始获取产线数据,工长工号:', this.currentForeman.employee_id);
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

        if (data.success && data.data) {
          // 处理产线数据
          this.assignedLines = data.data.map(line => {
            // 创建产线名称映射
            this.lineNameMap[line.id] = line.line_name;

            return {
              id: line.id,
              name: line.line_name,
              status: this.getStatusFromRunningStatus(line.running_status),
              statusText: this.getStatusTextFromRunningStatus(line.running_status),
              totalDevices: 0, // 将在获取设备后更新
              runningDevices: 0, // 将在获取设备后更新
              utilization: line.real_time_capacity ?
                Math.round((line.real_time_capacity / line.theoretical_capacity) * 100) : 0,
              assignedTo: line.foreman_id
            };
          });

          // 获取设备数据
          this.fetchEquipmentWithStatus();
        } else {
          console.error('获取产线数据失败:', data.error || '未知错误');
        }
      } catch (error) {
        console.error('获取产线数据出错:', error);
      } finally {
        this.loading.lines = false;
      }
    },

    // 获取设备及其状态
    async fetchEquipmentWithStatus() {
      try {
        this.loading.devices = true;
        console.log('开始获取设备数据');

        const response = await fetch('/api/equipment/with-status', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('设备数据:', data);

        // 检查设备数据中是否包含 line_name 字段
        if (data.success && data.data && data.data.length > 0) {
          console.log('第一个设备的产线信息:', {
            equipment_id: data.data[0].id,
            equipment_name: data.data[0].equipment_name,
            line_id: data.data[0].line_id,
            line_name: data.data[0].line_name
          });
        }

        if (data.success && data.data) {
          // 处理设备数据
          this.devices = data.data.map(device => {
            // 获取设备状态
            const status = this.getDeviceStatus(device);

            // 更新产线的设备统计
            this.updateLineDeviceStats(device.line_id, status);

            return {
              id: device.id,
              name: device.equipment_name,
              code: device.equipment_code,
              productionLine: device.line_name || this.lineNameMap[device.line_id] || '未知产线',
              status: status,
              statusText: this.getDeviceStatusText(status),
              runtime: device.runtime_hours || 0,
              manager: device.worker_id || '未分配',
              lastMaintenance: this.formatDate(device.updated_at),
              sensorData: device.sensor_data || {},
              faultProbability: device.fault_probability || 0
            };
          });
        } else {
          console.error('获取设备数据失败:', data.error || '未知错误');
        }
      } catch (error) {
        console.error('获取设备数据出错:', error);
      } finally {
        this.loading.devices = false;
      }
    },

    // 更新产线的设备统计
    updateLineDeviceStats(lineId, deviceStatus) {
      const line = this.assignedLines.find(line => line.id === lineId);
      if (line) {
        line.totalDevices++;
        if (deviceStatus === 'running') {
          line.runningDevices++;
        }
      }
    },

    // 根据设备数据判断状态
    getDeviceStatus(device) {
      if (device.status === '故障') return 'stopped';
      if (device.fault_probability > 0.3) return 'warning';
      return 'running';
    },

    // 获取设备状态文本
    getDeviceStatusText(status) {
      switch (status) {
        case 'running': return '运行中';
        case 'warning': return '预警';
        case 'stopped': return '已停机';
        default: return '未知';
      }
    },

    // 根据产线运行状态获取状态
    getStatusFromRunningStatus(runningStatus) {
      switch (runningStatus) {
        case '运行中': return 'running';
        case '故障': return 'stopped';
        case '维护中': return 'warning';
        default: return 'running';
      }
    },

    // 根据产线运行状态获取状态文本
    getStatusTextFromRunningStatus(runningStatus) {
      return runningStatus || '运行中';
    },

    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return '未知';
      const date = new Date(dateString);
      return date.toISOString().split('T')[0];
    },

    // 查看产线详情
    viewLineDetail(line) {
      console.log('查看产线详情:', line);
      // 跳转到产线详情页面
      this.$router.push(`/foreman/production-line-detail/${line.id}`);
    },

    // 管理产线设备
    manageDevices(line) {
      console.log('管理产线设备:', line);
      this.filterLine = line.name;
    },

    // 排程维护
    scheduleMaintenace(line) {
      this.selectedLine = line;
      this.showMaintenanceModal = true;
    },

    // 查看设备详情
    viewDeviceDetail(device) {
      console.log('查看设备详情:', device);
      // 跳转到设备详情页面
      this.$router.push(`/foreman/equipment-detail/${device.id}`);
    },

    // 上报故障
    reportIssue(device) {
      console.log('上报设备故障:', device);
    },

    // 开始维护
    startMaintenance(device) {
      console.log('开始维护设备:', device);
    },

    // 提交维护排程
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
