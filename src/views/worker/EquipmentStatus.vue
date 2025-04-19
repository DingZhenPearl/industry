<template>
  <div class="equipment-status">
    <header class="header">
      <h1>设备状态</h1>
    </header>

    <div class="content">
      <!-- 设备选择器，当有多个设备时显示 -->
      <div class="device-selector" v-if="!loading && !error && myDevices.length > 1">
        <label for="device-select">选择设备：</label>
        <select id="device-select" v-model="selectedDeviceId" @change="onDeviceChange" class="device-select">
          <option v-for="device in myDevices" :key="device.id" :value="device.id">
            {{ device.name }} ({{ device.code }})
          </option>
        </select>
      </div>

      <!-- 无设备提示 -->
      <div class="empty-container" v-if="!loading && !error && myDevices.length === 0">
        <div class="empty-icon">🛠️</div>
        <p>您当前没有负责的设备</p>
      </div>

      <!-- 使用设备详情组件 -->
      <equipment-detail-component
        v-if="myDevices.length > 0"
        :equipment="currentDevice"
        :device-history="deviceHistory"
        :loading="loading"
        :error="error"
        :auto-refresh-enabled="autoRefresh"
        :refresh-rate="refreshRate"
        :show-status-control="true"
        @retry="fetchMyDevices"
        @refresh-data="fetchLatestDeviceData"
        @fetch-history="fetchDeviceHistory"
        @status-change="updateEquipmentStatus"
      >
        <!-- 自定义操作按钮 -->
        <template v-slot:actions>
          <button
            class="action-btn"
            :class="{ disabled: currentDevice && currentDevice.status === 'stopped' }"
            @click="checkParameters"
          >参数检查</button>
          <button
            class="action-btn"
            :class="{ disabled: currentDevice && currentDevice.status === 'stopped' }"
            @click="reportIssue"
          >故障上报</button>
          <button
            class="action-btn"
            @click="viewManual"
          >操作手册</button>
          <button
            class="action-btn refresh"
            @click="refreshDeviceData"
          >刷新数据</button>
        </template>

        <!-- 运行日志 -->
        <template v-slot:extra-content>
          <div class="operation-log">
            <h3>运行日志</h3>
            <div class="log-list">
              <div class="log-item" v-for="log in operationLogs" :key="log.time">
                <span class="log-time">{{ log.time }}</span>
                <span class="log-content">{{ log.content }}</span>
              </div>
            </div>
          </div>
        </template>
      </equipment-detail-component>
    </div>

    <WorkerNav />
  </div>
</template>

<script>
import WorkerNav from '@/components/WorkerNav.vue'
import EquipmentDetailComponent from '@/components/EquipmentDetailComponent.vue'

export default {
  name: 'EquipmentStatus',
  components: {
    WorkerNav,
    EquipmentDetailComponent
  },
  data() {
    return {
      loading: false,
      error: null,
      myDevices: [],
      selectedDeviceId: null,
      currentUserInfo: {},
      deviceHistory: [],
      autoRefresh: true,
      refreshRate: 10000, // 10秒更新一次
      operationLogs: [
        { time: '2023-07-10 10:30', content: '完成设备检查' },
        { time: '2023-07-10 09:15', content: '设备启动运行' },
        { time: '2023-07-10 09:00', content: '设备维护' },
        { time: '2023-07-10 08:30', content: '参数调整' }
      ]
    }
  },
  computed: {
    // 当前选中的设备
    currentDevice() {
      if (!this.myDevices.length) return null;
      if (!this.selectedDeviceId) return this.myDevices[0];
      return this.myDevices.find(device => device.id === this.selectedDeviceId) || this.myDevices[0];
    }
  },
  created() {
    // 获取当前用户信息
    this.getCurrentUserInfo();
    // 获取工人负责的设备
    this.fetchMyDevices();

    // 打印自动刷新设置
    console.log('工人设备详情页面初始化，自动刷新:', this.autoRefresh, '刷新间隔:', this.refreshRate);
  },
  mounted() {
    // 组件内部会处理自动刷新
  },
  beforeDestroy() {
    // 组件内部会处理清理工作
  },
  watch: {
    currentDevice(newDevice) {
      if (newDevice) {
        this.fetchDeviceHistory();
      }
    }
  },
  methods: {
    // 获取当前用户信息
    getCurrentUserInfo() {
      const userInfoStr = localStorage.getItem('userInfo');
      if (userInfoStr) {
        try {
          this.currentUserInfo = JSON.parse(userInfoStr);
        } catch (error) {
          console.error('解析用户信息失败:', error);
          this.currentUserInfo = {};
        }
      }
    },

    // 获取工人负责的设备
    async fetchMyDevices() {
      this.loading = true;
      this.error = null;

      try {
        // 获取当前登录用户的工号
        const employeeId = this.currentUserInfo.employee_id;

        if (!employeeId) {
          this.error = '无法获取您的工号信息，请重新登录';
          return;
        }

        // 获取工人所在组的设备信息
        const groupId = this.currentUserInfo.group_id;
        const response = await fetch(`/api/equipment/with-status?group_id=${groupId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取设备信息失败: ${response.status}`);
        }

        const result = await response.json();
        console.log('设备信息:', result);

        if (result.success && result.data) {
          // 过滤出工人负责的设备
          this.myDevices = result.data
            .filter(device => device.worker_id === employeeId)
            .map(device => {
              // 获取设备状态
              let status = 'running';
              // 保存原始数据库状态值供状态修改使用
              let dbStatus = device.status || '正常';

              if (device.status === '故障') {
                status = 'stopped';
                dbStatus = '故障';
              } else if (device.status === '停机') {
                status = 'stopped';
                dbStatus = '停机';
              } else if (device.status === '维修中') {
                status = 'stopped';
                dbStatus = '维修中';
              } else if (device.status === '预警' || device.fault_probability > 0.3) {
                status = 'warning';
                dbStatus = '预警';
              } else if (device.status === '正常') {
                dbStatus = '正常';
              }

              // 获取设备状态文本
              let statusText = '运行中';
              if (status === 'warning') statusText = '预警';
              else if (status === 'stopped') {
                if (dbStatus === '故障') statusText = '故障';
                else if (dbStatus === '维修中') statusText = '维修中';
                else statusText = '已停机';
              }

              // 创建设备对象
              const deviceObj = {
                id: device.id,
                name: device.equipment_name,
                code: device.equipment_code,
                line_id: device.line_id,
                productionLine: device.line_name || '未知产线',
                status: status,
                statusText: statusText,
                dbStatus: dbStatus, // 原始数据库状态值
                runtime: device.runtime_hours || 0,
                faultProbability: device.fault_probability || 0,
                sensorData: device.sensor_data || {}
              };

              console.log('设备产线名称:', device.line_name);

              return deviceObj;
            });

          // 如果有设备，选中第一个
          if (this.myDevices.length > 0) {
            this.selectedDeviceId = this.myDevices[0].id;
          }
        } else {
          this.error = result.error || '获取设备信息失败';
        }
      } catch (error) {
        console.error('获取设备信息出错:', error);
        this.error = error.message || '获取设备信息出错';
      } finally {
        this.loading = false;
      }
    },

    // 刷新设备数据
    refreshDeviceData() {
      this.fetchMyDevices();
      // 刷新图表数据
      if (this.currentDevice) {
        this.fetchDeviceHistory();
      }
    },

    // 获取最新的设备数据并更新图表
    async fetchLatestDeviceData() {
      if (!this.currentDevice) return;

      try {
        // 获取最新的一条记录
        const response = await fetch(`/api/equipment/status-history?equipment_id=${this.currentDevice.id}&limit=1`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取设备最新数据失败: ${response.status}`);
        }

        const result = await response.json();

        if (result.success && result.data && result.data.length > 0) {
          const latestData = result.data[0];

          // 处理sensor_data字段，确保是对象
          if (latestData.sensor_data && typeof latestData.sensor_data === 'string') {
            try {
              latestData.sensor_data = JSON.parse(latestData.sensor_data);
            } catch (e) {
              console.error('解析sensor_data失败:', e);
              latestData.sensor_data = {};
            }
          }

          // 检查是否是新数据
          const isNewData = this.deviceHistory.length === 0 ||
                           new Date(latestData.collection_time) > new Date(this.deviceHistory[this.deviceHistory.length - 1].collection_time);

          if (isNewData) {
            console.log('检测到新数据，添加到历史数据中');
            // 添加新数据到历史数据中
            this.deviceHistory.push(latestData);

            // 如果历史数据超过限制，删除最早的数据
            if (this.deviceHistory.length > parseInt(this.historyLimit || 10)) {
              this.deviceHistory.shift();
            }

            // 对数据进行排序，确保按时间正序排列
            this.deviceHistory.sort((a, b) => new Date(a.collection_time) - new Date(b.collection_time));

            // 创建一个新数组，触发Vue的响应式更新
            this.deviceHistory = [...this.deviceHistory];

            // 图表将自动更新，因为我们修改了 deviceHistory

            // 更新当前设备的传感器数据
            if (this.currentDevice && latestData.sensor_data) {
              this.currentDevice.sensorData = latestData.sensor_data;
              this.currentDevice.faultProbability = latestData.fault_probability || 0;
              this.currentDevice.runtime = latestData.runtime_hours || 0;

              // 更新设备状态
              let status = 'running';
              if (latestData.fault_probability > 0.3) status = 'warning';
              this.currentDevice.status = status;

              let statusText = '运行中';
              if (status === 'warning') statusText = '预警';
              this.currentDevice.statusText = statusText;
            }
          }
        }
      } catch (error) {
        console.error('获取设备最新数据出错:', error);
      }
    },

    // 设备选择变更
    onDeviceChange() {
      console.log('选中设备:', this.selectedDeviceId);
      this.fetchDeviceHistory();
    },

    // 获取设备历史数据
    async fetchDeviceHistory(limit = 10) {
      if (!this.currentDevice) return;

      try {
        const response = await fetch(`/api/equipment/status-history?equipment_id=${this.currentDevice.id}&limit=${limit}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取设备历史数据失败: ${response.status}`);
        }

        const result = await response.json();
        console.log('设备历史数据:', result);

        if (result.success && result.data) {
          // 将数据按时间正序排列
          this.deviceHistory = result.data
            .sort((a, b) => new Date(a.collection_time) - new Date(b.collection_time))
            .map(item => {
              // 处理sensor_data字段，确保是对象
              if (item.sensor_data && typeof item.sensor_data === 'string') {
                try {
                  item.sensor_data = JSON.parse(item.sensor_data);
                } catch (e) {
                  console.error('解析sensor_data失败:', e);
                  item.sensor_data = {};
                }
              }
              return item;
            });
        } else {
          console.error('获取设备历史数据失败:', result.error || '未知错误');
        }
      } catch (error) {
        console.error('获取设备历史数据出错:', error);
      }
    },

    // 检查参数
    checkParameters() {
      if (!this.currentDevice || this.currentDevice.status === 'stopped') return;
      console.log('检查设备参数');
    },

    // 故障上报
    reportIssue() {
      if (!this.currentDevice || this.currentDevice.status === 'stopped') return;
      this.$router.push('/worker/issues');
    },

    // 查看操作手册
    viewManual() {
      console.log('查看设备操作手册');
    },

    // 更新设备状态
    async updateEquipmentStatus(data) {
      try {
        console.log(`更新设备 ${data.equipmentId} 状态为: ${data.newStatus}`);

        // 准备状态数据
        const equipmentData = {
          status: data.newStatus
        };

        // 调用API更新设备状态
        const response = await fetch('/api/equipment/update', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            equipment_id: data.equipmentId,
            equipment_data: equipmentData
          })
        });

        const result = await response.json();

        if (result.success) {
          // 更新成功，刷新设备数据
          await this.fetchMyDevices();

          // 直接更新当前设备的状态显示，确保界面立即反映变化
          if (this.currentDevice && this.currentDevice.id === data.equipmentId) {
            // 更新状态文本和样式类
            if (data.newStatus === '停机') {
              this.currentDevice.status = 'stopped';
              this.currentDevice.statusText = '已停机';
              this.currentDevice.dbStatus = '停机';
            } else if (data.newStatus === '正常') {
              this.currentDevice.status = 'running';
              this.currentDevice.statusText = '运行中';
              this.currentDevice.dbStatus = '正常';
            }
          }

          alert(`设备状态已更新为 ${data.newStatus}`);
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
.equipment-status {
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

.assigned-device {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.device-header {
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

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  color: #666;
  font-size: 14px;
}

.parameter-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.parameter-item {
  text-align: center;
}

.parameter-item .label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.parameter-item .value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.parameter-item .value.warning {
  color: #ff9800;
}

.action-group {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 15px;
}

.action-btn.refresh {
  background: #e3f2fd;
  color: #2196F3;
}

.device-selector {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
}

.device-selector label {
  margin-right: 10px;
  font-weight: bold;
}

.device-select {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.loading-container, .error-container, .empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  background: white;
  border-radius: 8px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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

.error-message {
  color: #f44336;
  margin-bottom: 15px;
}

.retry-btn {
  background-color: #f44336;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
  color: #ddd;
}

.action-btn {
  padding: 12px;
  border: none;
  border-radius: 8px;
  background: white;
  color: #2196F3;
  font-size: 14px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.action-btn.disabled {
  background: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}



.operation-log {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.operation-log h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
}

.log-list {
  max-height: 200px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
  font-size: 14px;
}

.log-item:last-child {
  border-bottom: none;
}

.log-time {
  color: #999;
  margin-right: 15px;
  flex-shrink: 0;
}

.log-content {
  color: #666;
}
</style>
