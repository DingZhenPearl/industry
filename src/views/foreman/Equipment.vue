<template>
  <div class="equipment">
    <header class="header">
      <h1>设备与产线</h1>
    </header>

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
              <div class="status-control">
                <span :class="['device-status', device.status]">{{ device.statusText }}</span>
                <div class="status-buttons">
                  <button
                    class="status-btn"
                    :class="{ 'active': device.dbStatus === '正常' }"
                    @click="setDeviceStatus(device, '正常')"
                    :disabled="device.dbStatus === '故障' || device.dbStatus === '维修中'"
                  >正常</button>
                  <button
                    class="status-btn"
                    :class="{ 'active': device.dbStatus === '停机' }"
                    @click="setDeviceStatus(device, '停机')"
                  >停机</button>
                </div>
                <span class="status-note" v-if="device.dbStatus === '故障' || device.dbStatus === '维修中' || device.dbStatus === '预警'">
                  {{ getDeviceStatusNote(device) }}
                </span>
              </div>
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
            </div>
          </div>
        </div>
      </div>


    </div>

    <ForemanNav />
  </div>
</template>

<script>
import ForemanNav from '@/components/ForemanNav.vue'

export default {
  components: {
    ForemanNav
  },
  name: 'ForemanEquipment',
  data() {
    return {
      filterLine: '',
      filterStatus: '',
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

        // 调试日志，查看设备列表数据
        if (data.success && data.data && data.data.length > 0) {
          const firstLine = data.data[0];
          console.log('第一个产线数据:', firstLine);
          console.log('产线设备列表存在吗?', 'equipment_list' in firstLine);
          if ('equipment_list' in firstLine) {
            console.log('产线设备列表类型:', typeof firstLine.equipment_list);
            console.log('产线设备列表内容:', firstLine.equipment_list);
            if (Array.isArray(firstLine.equipment_list)) {
              console.log('设备列表长度:', firstLine.equipment_list.length);
              if (firstLine.equipment_list.length > 0) {
                console.log('第一个设备数据:', firstLine.equipment_list[0]);
              }
            }
          }
        }

        if (data.success && data.data) {
          // 处理产线数据
          this.assignedLines = data.data.map(line => {
            // 创建产线名称映射
            this.lineNameMap[line.id] = line.line_name;

            // 获取产线状态
            const status = this.getStatusFromRunningStatus(line.running_status || line.status);
            const statusText = this.getStatusTextFromRunningStatus(line.running_status || line.status);

            // 计算产能利用率
            let utilization = 0;
            if (line.real_time_capacity && line.theoretical_capacity && line.theoretical_capacity > 0) {
              utilization = Math.round((line.real_time_capacity / line.theoretical_capacity) * 100);
            }

            // 获取设备总数和运行设备数
            let totalDevices = 0;
            let runningDevices = 0;

            // 如果后端返回了设备列表，直接使用
            if (line.equipment_list && Array.isArray(line.equipment_list)) {
              totalDevices = line.equipment_list.length;
              runningDevices = line.equipment_list.filter(eq => {
                // 检查设备状态
                const status = eq.status || eq.running_status;
                return status === '正常' || status === '运行中';
              }).length;

              console.log(`产线 ${line.line_name} 设备总数: ${totalDevices}, 运行设备数: ${runningDevices}`);
            }

            return {
              id: line.id,
              name: line.line_name,
              status: status,
              statusText: statusText,
              totalDevices: totalDevices,
              runningDevices: runningDevices,
              utilization: utilization,
              assignedTo: line.foreman_id,
              // 保存原始数据，以便后续使用
              rawData: line
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
            // 保存原始数据库状态值供状态修改使用
            const dbStatus = device.status || '正常';

            // 更新产线的设备统计
            // 将产线ID转换为字符串，确保类型匹配
            const lineId = device.line_id;
            console.log(`设备 ${device.equipment_name} (设备ID: ${device.id}) 属于产线ID: ${lineId}, 状态: ${status}`);
            this.updateLineDeviceStats(lineId, status);

            return {
              id: device.id,
              name: device.equipment_name,
              code: device.equipment_code,
              productionLine: device.line_name || this.lineNameMap[device.line_id] || '未知产线',
              status: status,
              statusText: this.getDeviceStatusText(status),
              dbStatus: dbStatus, // 原始数据库状态值
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
      // 将lineId转换为字符串，确保类型匹配
      const lineIdStr = String(lineId);
      const line = this.assignedLines.find(line => String(line.id) === lineIdStr);

      // 只在产线卡片没有设备数据时才更新
      if (line) {
        // 检查是否有设备列表数据
        const hasEquipmentList = line.rawData &&
                                line.rawData.equipment_list &&
                                Array.isArray(line.rawData.equipment_list) &&
                                line.rawData.equipment_list.length > 0;

        if (!hasEquipmentList) {
          console.log(`更新产线 ${line.name} (产线ID: ${lineIdStr}) 的设备统计，设备状态: ${deviceStatus}`);
          line.totalDevices++;
          if (deviceStatus === 'running') {
            line.runningDevices++;
          }
          console.log(`更新后的设备统计: 总数=${line.totalDevices}, 运行数=${line.runningDevices}`);
        }
      } else {
        console.log(`未找到产线ID: ${lineIdStr} 的产线数据`);
      }
    },

    // 根据设备数据判断状态
    getDeviceStatus(device) {
      if (device.status === '故障') return 'stopped';
      if (device.status === '预警') return 'warning';
      if (device.status === '停机') return 'stopped';
      if (device.status === '维修中') return 'warning';
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
      if (!runningStatus) return 'running';

      switch (runningStatus) {
        case '运行中':
        case '正常':
          return 'running';
        case '故障':
        case '停机':
          return 'stopped';
        case '维修中':
        case '预警':
          return 'warning';
        default:
          return 'running';
      }
    },

    // 根据产线运行状态获取状态文本
    getStatusTextFromRunningStatus(runningStatus) {
      if (!runningStatus) return '运行中';

      switch (runningStatus) {
        case '运行中':
        case '正常':
          return '运行中';
        case '故障':
          return '故障';
        case '停机':
          return '已停机';
        case '维修中':
          return '维修中';
        case '预警':
          return '预警';
        default:
          return runningStatus;
      }
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
      // 使用导航辅助函数跳转到产线详情页面
      import('@/utils/navigationHelper').then(({ navigateWithUid }) => {
        navigateWithUid(this.$router, `/foreman/production-line-detail/${line.id}`);
      });
    },

    // 管理产线设备
    manageDevices(line) {
      console.log('管理产线设备:', line);
      this.filterLine = line.name;
    },



    // 查看设备详情
    viewDeviceDetail(device) {
      console.log('查看设备详情:', device);
      // 使用导航辅助函数跳转到设备详情页面
      import('@/utils/navigationHelper').then(({ navigateWithUid }) => {
        navigateWithUid(this.$router, `/foreman/equipment-detail/${device.id}`);
      });
    },

    // 上报故障
    reportIssue(device) {
      console.log('上报设备故障:', device);
    },



    // 设置设备状态
    async setDeviceStatus(device, status) {
      // 检查当前状态是否允许修改
      if (device.dbStatus === '故障' || device.dbStatus === '维修中') {
        alert(`无法将设备状态修改为 ${status}，当前状态不允许手动设置。`);
        return;
      }

      // 如果当前状态是预警，只能改为停机
      if (device.dbStatus === '预警' && status !== '停机') {
        alert('预警状态下只能将设备设置为停机状态。');
        return;
      }

      // 设置新状态
      device.dbStatus = status;

      // 调用更新方法
      this.updateDeviceStatus(device);
    },

    // 获取设备状态说明
    getDeviceStatusNote(device) {
      if (device.dbStatus === '故障') {
        return '故障状态由系统自动检测，无法手动修改';
      } else if (device.dbStatus === '预警') {
        return '预警状态由系统自动检测，可停机处理';
      } else if (device.dbStatus === '维修中') {
        return '维修中状态由安全员设置，无法手动修改';
      }
      return '';
    },

    // 更新设备状态
    async updateDeviceStatus(device) {
      try {
        console.log(`更新设备 ${device.id} 状态为: ${device.dbStatus}`);

        // 准备状态数据
        const equipmentData = {
          status: device.dbStatus
        };

        // 调用API更新设备状态
        const response = await fetch('/api/equipment/update', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            equipment_id: device.id,
            equipment_data: equipmentData
          })
        });

        const result = await response.json();

        if (result.success) {
          // 更新成功，刷新设备数据
          await this.fetchEquipmentWithStatus();

          // 直接更新当前设备的状态显示，确保界面立即反映变化
          const updatedDevice = this.devices.find(d => d.id === device.id);
          if (updatedDevice) {
            // 更新状态文本和样式类
            if (device.dbStatus === '停机') {
              updatedDevice.status = 'stopped';
              updatedDevice.statusText = '已停机';
            } else if (device.dbStatus === '正常') {
              updatedDevice.status = 'running';
              updatedDevice.statusText = '运行中';
            }
          }

          alert(`设备 ${device.name} 状态已更新为 ${device.dbStatus}`);
        } else {
          alert(`更新设备状态失败: ${result.error || '未知错误'}`);
        }
      } catch (error) {
        console.error('更新设备状态出错:', error);
        alert(`更新设备状态出错: ${error.message || '未知错误'}`);
      }
    },


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

/* 状态控制样式 */
.status-control {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.status-buttons {
  display: flex;
  gap: 8px;
}

.status-btn {
  padding: 4px 10px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background-color: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.status-btn:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.status-btn.active {
  background-color: #1890ff;
  border-color: #1890ff;
  color: white;
}

.status-btn:disabled {
  background-color: #f5f5f5;
  border-color: #d9d9d9;
  color: #bfbfbf;
  cursor: not-allowed;
}

.status-note {
  font-size: 12px;
  color: #ff9800;
  margin-left: 8px;
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
