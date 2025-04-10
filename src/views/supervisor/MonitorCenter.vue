<template>
  <div class="monitor-center">
    <header class="header">
      <h1>监控中心</h1>
    </header>

    <div class="content">
      <!-- 增加实时监控卡片 -->
      <div class="status-cards">
        <div class="status-card running">
          <h3>运行产线</h3>
          <div class="count">8</div>
          <div class="status-detail">正常运行中</div>
        </div>
        <div class="status-card warning">
          <h3>预警设备</h3>
          <div class="count">2</div>
          <div class="status-detail">需要维护</div>
        </div>
        <div class="status-card stopped">
          <h3>停机产线</h3>
          <div class="count">1</div>
          <div class="status-detail">故障处理中</div>
        </div>
      </div>

      <div class="monitor-stats">
        <div class="stat-item">
          <span class="stat-label">设备运行率</span>
          <span class="stat-value">95%</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">生产完成率</span>
          <span class="stat-value">87%</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">任务达成率</span>
          <span class="stat-value">92%</span>
        </div>
      </div>

      <!-- 增加产线状态列表 -->
      <div class="production-lines">
        <div class="section-header">
          <h3 class="section-title">产线运行状态</h3>
          <button class="config-btn" @click="showConfigModal = true">
            <i class="settings-icon"></i> 产线配置
          </button>
        </div>

        <div class="line-list">
          <div class="line-item" v-for="line in productionLines" :key="line.id">
            <div class="line-header">
              <span class="line-name">{{ line.name }}</span>
              <span class="line-status" :class="line.status">{{ line.statusText }}</span>
            </div>
            <div class="line-details">
              <div class="detail-item">
                <span class="label">产能利用率</span>
                <span class="value">{{ line.utilization }}%</span>
              </div>
              <div class="detail-item">
                <span class="label">当前产量</span>
                <span class="value">{{ line.output }}/{{ line.target }}</span>
              </div>
              <div class="detail-item">
                <span class="label">运行时长</span>
                <span class="value">{{ line.runtime }}h</span>
              </div>
              <div class="detail-item">
                <span class="label">负责工长</span>
                <span class="value">
                  <span v-if="line.foremen && line.foremen.length > 0">
                    <span v-for="(foreman, index) in line.foremen" :key="foreman.id">
                      {{ foreman.name }}<span v-if="index < line.foremen.length - 1">, </span>
                    </span>
                  </span>
                  <span v-else>未分配</span>
                </span>
              </div>
            </div>
            <div class="line-actions">
              <button class="action-btn" @click="assignManager(line)">分配管理</button>
              <button class="action-btn" @click="viewDetails(line)">查看详情</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 新增全厂设备监控模块 -->
      <div class="equipment-monitor">
        <div class="section-header">
          <h3 class="section-title">全厂设备状态</h3>
          <div class="filter-bar">
            <select v-model="equipmentFilter.line" class="filter-select">
              <option value="">全部产线</option>
              <option v-for="line in productionLines" :key="line.id" :value="line.id">
                {{ line.name }}
              </option>
            </select>
            <select v-model="equipmentFilter.status" class="filter-select">
              <option value="">全部状态</option>
              <option value="running">运行中</option>
              <option value="warning">异常</option>
              <option value="stopped">已停机</option>
            </select>
            <select v-model="equipmentFilter.type" class="filter-select">
              <option value="">全部类型</option>
              <option value="production">生产设备</option>
              <option value="inspection">检测设备</option>
              <option value="auxiliary">辅助设备</option>
            </select>
          </div>
        </div>

        <div class="equipment-stats">
          <div class="stat-box">
            <span class="stat-label">设备总数</span>
            <span class="stat-value">{{ equipmentStats.total }}</span>
          </div>
          <div class="stat-box running">
            <span class="stat-label">运行中</span>
            <span class="stat-value">{{ equipmentStats.running }}</span>
          </div>
          <div class="stat-box warning">
            <span class="stat-label">异常</span>
            <span class="stat-value">{{ equipmentStats.warning }}</span>
          </div>
          <div class="stat-box stopped">
            <span class="stat-label">已停机</span>
            <span class="stat-value">{{ equipmentStats.stopped }}</span>
          </div>
        </div>

        <div class="equipment-table">
          <table>
            <thead>
              <tr>
                <th>设备名称</th>
                <th>设备类型</th>
                <th>所属产线</th>
                <th>负责人</th>
                <th>运行状态</th>
                <th>运行时长(h)</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="device in filteredEquipments" :key="device.id">
                <td>{{ device.name }}</td>
                <td>{{ device.typeText }}</td>
                <td>{{ device.productionLine }}</td>
                <td>{{ device.manager }}</td>
                <td>
                  <span :class="['status-tag', device.status]">{{ device.statusText }}</span>
                </td>
                <td>{{ device.runtime }}</td>
                <td>
                  <button class="op-btn" @click="viewDeviceDetail(device)">查看</button>
                  <button class="op-btn warning" v-if="device.status === 'warning'" @click="assignMaintenance(device)">维护</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 产线配置模态框 -->
      <div class="modal" v-if="showConfigModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>产线配置</h3>
            <span class="close-btn" @click="showConfigModal = false">&times;</span>
          </div>
          <div class="modal-body">
            <div class="config-list">
              <div class="config-item" v-for="line in productionLines" :key="line.id">
                <span class="line-name">{{ line.name }}</span>
                <div class="config-actions">
                  <button class="btn" @click="editLine(line)">编辑</button>
                  <button class="btn danger" @click="deleteLine(line)">停用</button>
                </div>
              </div>
            </div>
            <button class="btn primary add-line" @click="addNewLine">新增产线</button>
          </div>
        </div>
      </div>

      <!-- 分配管理模态框 -->
      <div class="modal" v-if="showAssignModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>分配产线管理</h3>
            <span class="close-btn" @click="showAssignModal = false">&times;</span>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>产线名称</label>
              <div class="value">{{ selectedLine.name }}</div>
            </div>
            <div class="form-group">
              <label>选择管理工长</label>
              <select v-model="selectedManager" class="form-input">
                <option value="">请选择工长</option>
                <option v-for="manager in foremen" :key="manager.id" :value="manager.id">
                  {{ manager.name }}
                </option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn cancel" @click="showAssignModal = false">取消</button>
            <button class="btn submit" @click="confirmAssign">确定分配</button>
          </div>
        </div>
      </div>
    </div>

    <SupervisorNav />
  </div>
</template>

<script>
import SupervisorNav from '@/components/SupervisorNav.vue'

export default {
  name: 'MonitorCenter',
  components: {
    SupervisorNav
  },
  data() {
    return {
      productionLines: [],
      showConfigModal: false,
      showAssignModal: false,
      selectedLine: {},
      selectedManager: '',
      foremen: [],
      // 新增设备监控相关数据
      equipmentFilter: {
        line: '',
        status: '',
        type: ''
      },
      equipments: [
        {
          id: 1,
          name: '注塑机A-01',
          type: 'production',
          typeText: '生产设备',
          productionLine: '一号生产线',
          status: 'running',
          statusText: '运行中',
          runtime: 126.5,
          manager: '张工',
          lastMaintenance: '2023-07-01'
        },
        {
          id: 2,
          name: '压铸机B-02',
          type: 'production',
          typeText: '生产设备',
          productionLine: '二号生产线',
          status: 'warning',
          statusText: '异常',
          runtime: 85.2,
          manager: '李工',
          lastMaintenance: '2023-07-05'
        },
        {
          id: 3,
          name: '检测仪C-01',
          type: 'inspection',
          typeText: '检测设备',
          productionLine: '一号生产线',
          status: 'running',
          statusText: '运行中',
          runtime: 95.5,
          manager: '王工',
          lastMaintenance: '2023-07-03'
        },
        {
          id: 4,
          name: '打包机D-01',
          type: 'auxiliary',
          typeText: '辅助设备',
          productionLine: '三号生产线',
          status: 'stopped',
          statusText: '已停机',
          runtime: 45.5,
          manager: '刘工',
          lastMaintenance: '2023-07-02'
        }
      ]
    }
  },
  computed: {
    // 根据筛选条件过滤设备
    filteredEquipments() {
      return this.equipments.filter(equipment => {
        // 按产线筛选
        const lineMatch = !this.equipmentFilter.line ||
          equipment.productionLine.includes(this.productionLines.find(l => l.id === this.equipmentFilter.line)?.name || '');

        // 按状态筛选
        const statusMatch = !this.equipmentFilter.status ||
          equipment.status === this.equipmentFilter.status;

        // 按类型筛选
        const typeMatch = !this.equipmentFilter.type ||
          equipment.type === this.equipmentFilter.type;

        return lineMatch && statusMatch && typeMatch;
      });
    },

    // 设备状态统计
    equipmentStats() {
      const stats = {
        total: this.equipments.length,
        running: 0,
        warning: 0,
        stopped: 0
      };

      this.equipments.forEach(device => {
        stats[device.status]++;
      });

      return stats;
    }
  },
  created() {
    this.fetchProductionLines();
    this.fetchEquipments();
  },
  methods: {
    // 获取产线数据
    async fetchProductionLines() {
      try {
        const response = await fetch('/api/production-line/with-foremen');
        const result = await response.json();

        if (result.success && result.data) {
          // 处理产线数据
          this.productionLines = result.data.map(line => {
            // 根据实时产能和理论产能计算利用率
            const utilization = line.theoretical_capacity ?
              Math.round((line.real_time_capacity / line.theoretical_capacity) * 100) : 0;

            // 根据产线状态字段确定状态
            let status = 'running';
            let statusText = '运行中';

            // 根据数据库中的状态字段设置状态
            if (line.status === '维修中') {
              status = 'warning';
              statusText = '维修中';
            } else if (line.status === '停机') {
              status = 'stopped';
              statusText = '已停机';
            } else if (line.status === '故障') {
              status = 'stopped';
              statusText = '故障';
            } else if (line.status === '预警') {
              status = 'warning';
              statusText = '预警';
            }

            // 如果产线状态正常，但利用率过低，也显示为预警
            if (status === 'running' && utilization < 80) {
              status = 'warning';
              statusText = '产能过低';
            }

            // 如果产线状态正常，但利用率为0，显示为停机
            if (status === 'running' && utilization === 0) {
              status = 'stopped';
              statusText = '无产出';
            }

            return {
              id: line.id,
              name: line.line_name,
              status: status,
              statusText: statusText,
              utilization: utilization,
              output: Math.round(line.real_time_capacity || 0),
              target: line.theoretical_capacity || 1000,
              runtime: line.runtime_hours || 0,
              equipment_list: line.equipment_list || [],
              foremen: line.foremen || []
            };
          });

          // 更新状态卡片的数据
          this.updateStatusCards();
        } else {
          console.error('获取产线数据失败:', result.error);
        }
      } catch (error) {
        console.error('获取产线数据出错:', error);
      }
    },

    // 更新状态卡片数据
    updateStatusCards() {
      // 计算不同状态的产线数量
      const runningLines = this.productionLines.filter(line => line.status === 'running').length;
      const warningLines = this.productionLines.filter(line => line.status === 'warning').length;
      const stoppedLines = this.productionLines.filter(line => line.status === 'stopped').length;

      // 更新DOM元素
      const runningCard = document.querySelector('.status-card.running .count');
      const warningCard = document.querySelector('.status-card.warning .count');
      const stoppedCard = document.querySelector('.status-card.stopped .count');

      if (runningCard) runningCard.textContent = runningLines;
      if (warningCard) warningCard.textContent = warningLines;
      if (stoppedCard) stoppedCard.textContent = stoppedLines;
    },

    editLine(line) {
      console.log('编辑产线:', line);
      // 这里添加编辑产线的逻辑
    },
    deleteLine(line) {
      if(confirm(`确定要停用${line.name}吗？`)) {
        console.log('停用产线:', line);
        // 这里添加停用产线的逻辑
      }
    },
    addNewLine() {
      console.log('新增产线');
      // 这里添加新增产线的逻辑
    },
    assignManager(line) {
      this.selectedLine = line;
      this.showAssignModal = true;
    },
    viewDetails(line) {
      console.log('查看详情:', line);
      // 跳转到产线详情页面
      this.$router.push(`/supervisor/production-line-detail/${line.id}`);
    },
    confirmAssign() {
      console.log(`将${this.selectedLine.name}分配给ID为${this.selectedManager}的工长管理`);
      this.showAssignModal = false;
      this.selectedManager = '';
    },
    // 查看设备详情
    viewDeviceDetail(device) {
      console.log('查看设备详情:', device);
      // 跳转到设备详情页面
      this.$router.push(`/supervisor/equipment-detail/${device.id}`);
    },

    // 分配维护任务
    assignMaintenance(device) {
      console.log('分配设备维护任务:', device);
      // 这里可以增加设备维护任务分配的逻辑
    }
  }
}
</script>

<style scoped>
.monitor-center {
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

.monitor-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.stat-item {
  background: white;
  padding: 15px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #2196F3;
}

.monitor-chart {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.status-card {
  padding: 20px;
  border-radius: 8px;
  color: white;
  text-align: center;
}

.status-card.running {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
}

.status-card.warning {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
}

.status-card.stopped {
  background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
}

.status-card .count {
  font-size: 36px;
  font-weight: bold;
  margin: 10px 0;
}

.section-title {
  margin: 20px 0;
  font-size: 18px;
  color: #333;
}

.line-list {
  display: grid;
  gap: 15px;
}

.line-item {
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

.line-name {
  font-weight: bold;
  font-size: 16px;
}

.line-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
}

.line-status.running {
  background: #e8f5e9;
  color: #4CAF50;
}

.line-status.warning {
  background: #fff3e0;
  color: #ff9800;
}

.line-status.stopped {
  background: #ffebee;
  color: #f44336;
}

.line-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.detail-item {
  text-align: center;
}

.detail-item .label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.detail-item .value {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.config-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  background: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.settings-icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  background-color: white;
  mask-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" /></svg>');
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

.config-list {
  margin-bottom: 20px;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.config-item:last-child {
  border-bottom: none;
}

.line-name {
  font-weight: bold;
}

.config-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn.primary {
  background: #2196F3;
  color: white;
  width: 100%;
  padding: 10px;
  margin-top: 10px;
}

.btn.danger {
  background: #f44336;
  color: white;
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

.btn.cancel {
  background: #f5f5f5;
  color: #666;
}

.btn.submit {
  background: #4CAF50;
  color: white;
}

/* 设备监控样式 */
.equipment-monitor {
  margin-top: 20px;
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.equipment-stats {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.stat-box {
  flex: 1;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
  text-align: center;
}

.stat-box.running {
  background: #e8f5e9;
  color: #4CAF50;
}

.stat-box.warning {
  background: #fff3e0;
  color: #ff9800;
}

.stat-box.stopped {
  background: #ffebee;
  color: #f44336;
}

.stat-label {
  display: block;
  font-size: 14px;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
}

.equipment-table {
  overflow-x: auto;
}

.equipment-table table {
  width: 100%;
  border-collapse: collapse;
}

.equipment-table th,
.equipment-table td {
  text-align: left;
  padding: 12px;
  border-bottom: 1px solid #eee;
}

.equipment-table th {
  background: #f5f5f5;
  font-weight: bold;
}

.op-btn {
  padding: 4px 8px;
  margin-right: 5px;
  border: none;
  border-radius: 4px;
  background: #e3f2fd;
  color: #2196F3;
  cursor: pointer;
}

.op-btn.warning {
  background: #fff3e0;
  color: #ff9800;
}

.filter-bar {
  display: flex;
  gap: 10px;
}

.filter-select {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 120px;
}
</style>
