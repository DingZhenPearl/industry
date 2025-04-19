<template>
  <div class="production-line-detail">
    <ForemanNav />
    <header class="header">
      <div class="header-left">
        <button class="back-btn" @click="$router.go(-1)">&larr; 返回</button>
        <h1>{{ productionLine.name }} - 详细信息</h1>
      </div>
      <div class="header-right">
        <span :class="['status-tag', productionLine.status]">{{ productionLine.statusText }}</span>
      </div>
    </header>

    <div class="content">
      <!-- 使用产线详情组件 -->
      <production-line-detail-component
        :production-line="productionLine"
        :line-history="lineHistory"
        :loading="loading"
        :error="error"
        :auto-refresh-enabled="autoRefresh"
        :refresh-rate="refreshRate"
        @retry="fetchProductionLineDetail"
        @refresh-data="fetchLatestLineData"
        @fetch-history="fetchLineHistory"
      >
        <!-- 自定义操作按钮 -->
        <template v-slot:actions>
          <button class="action-btn" @click="scheduleMaintenace" v-if="productionLine && productionLine.status !== 'stopped'">排程维护</button>
          <button class="action-btn" @click="viewDevices">查看设备</button>
          <button class="action-btn" @click="viewWorkOrders">相关工单</button>
        </template>
      </production-line-detail-component>

      <!-- 产线设备列表 -->
      <div class="devices-section">
        <div class="section-header">
          <h2>产线设备</h2>
        </div>
        <div class="devices-list" v-if="!error && devices.length > 0">
          <div class="device-item" v-for="device in devices" :key="device.id">
            <div class="device-header">
              <span class="device-name">{{ device.name }}</span>
              <span :class="['device-status', device.status]">{{ device.statusText }}</span>
            </div>
            <div class="device-info">
              <div class="info-row">
                <span>设备编号：{{ device.id }}</span>
                <span>运行时长：{{ device.runtime }}h</span>
              </div>
              <div class="info-row">
                <span>负责人：{{ device.worker_name || '未分配' }}</span>
                <span>上次维护：{{ device.last_maintenance || '无记录' }}</span>
              </div>
            </div>
            <div class="device-actions">
              <button class="action-btn" @click="viewDeviceDetail(device)">详情</button>
              <button v-if="device.status === 'warning'" class="action-btn warning" @click="assignMaintenance(device)">维护</button>
            </div>
          </div>
        </div>
        <div class="empty-state" v-else-if="!error && devices.length === 0">
          <div class="empty-icon">🔍</div>
          <p>该产线暂无设备</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ForemanNav from '@/components/ForemanNav.vue'
import ProductionLineDetailComponent from '@/components/ProductionLineDetailComponent.vue'

export default {
  name: 'ForemanProductionLineDetail',
  components: {
    ForemanNav,
    ProductionLineDetailComponent
  },
  data() {
    return {
      productionLine: {
        id: 0,
        name: '加载中...',
        status: '',
        statusText: '加载中',
        utilization: 0,
        output: 0,
        target: 0,
        runtime: 0,
        manager: ''
      },
      devices: [],
      loading: false, // 设置为false，不显示加载界面
      error: null,

      // 图表相关数据
      lineHistory: [],
      historyLimit: '10',

      // 自动刷新相关
      autoRefresh: true,
      refreshInterval: null,
      refreshRate: 10000, // 10秒更新一次
      lastUpdateTime: '',

      // 当前工长信息
      currentForeman: null
    }
  },
  created() {
    // 获取当前工长信息
    this.getCurrentForeman();

    // 获取产线ID并加载数据
    const lineId = this.$route.params.id;
    if (lineId) {
      // 先获取产线详情，然后获取历史数据
      this.fetchProductionLineDetail(lineId).then(() => {
        this.fetchLineHistory(this.historyLimit);
      });
    }
  },
  mounted() {
    // 如果启用了自动刷新，则启动
    if (this.autoRefresh) {
      this.startAutoRefresh();
    }
  },
  beforeDestroy() {
    // 清除定时器
    this.stopAutoRefresh();
  },
  methods: {
    // 获取当前工长信息
    getCurrentForeman() {
      const userInfoStr = localStorage.getItem('userInfo');
      if (userInfoStr) {
        this.currentForeman = JSON.parse(userInfoStr);
        console.log('当前工长信息:', this.currentForeman);
      } else {
        console.error('未找到工长信息');
      }
    },

    // 获取产线详情
    async fetchProductionLineDetail(lineId) {
      // 不设置loading状态，避免显示加载界面
      // this.loading = true;
      this.error = null;

      try {
        // 从后端获取产线详情
        console.log('获取产线ID:', lineId, '的详情');

        const response = await fetch(`/api/production_line/detail?line_id=${lineId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取产线详情失败: ${response.status}`);
        }

        const result = await response.json();
        console.log('产线详情数据:', result);

        if (result.success && result.data) {
          // 处理产线数据
          const lineData = result.data.line;

          // 检查是否是当前工长负责的产线
          if (this.currentForeman && lineData.foreman_id !== this.currentForeman.employee_id) {
            this.error = '您没有权限查看此产线详情';
            return Promise.reject(new Error('无权限查看此产线'));
          }

          // 根据状态设置状态文本
          let statusText = '未知';
          let status = '';

          if (lineData.status === '正常') {
            statusText = '运行中';
            status = 'running';
          } else if (lineData.status === '异常') {
            statusText = '异常';
            status = 'warning';
          } else if (lineData.status === '停机') {
            statusText = '已停机';
            status = 'stopped';
          }

          // 计算产能利用率
          let utilization = 0;
          if (lineData.theoretical_capacity && lineData.theoretical_capacity > 0 && lineData.real_time_capacity) {
            utilization = Math.round((lineData.real_time_capacity / lineData.theoretical_capacity) * 100);
          }

          this.productionLine = {
            id: lineData.id,
            name: lineData.line_name,
            status: status,
            statusText: statusText,
            utilization: utilization,
            output: lineData.real_time_capacity || 0,
            target: lineData.theoretical_capacity || 0,
            runtime: lineData.runtime_hours || 0,
            manager: lineData.foreman_name || '未分配'
          };

          // 处理设备数据
          if (result.data.equipment) {
            this.devices = result.data.equipment.map(device => {
              // 根据设备状态设置状态文本和样式
              let deviceStatus = 'normal';
              let deviceStatusText = '正常';

              if (device.status === '故障') {
                deviceStatus = 'error';
                deviceStatusText = '故障';
              } else if (device.status === '预警') {
                deviceStatus = 'warning';
                deviceStatusText = '预警';
              } else if (device.status === '停机') {
                deviceStatus = 'stopped';
                deviceStatusText = '已停机';
              }

              return {
                id: device.id,
                name: device.equipment_name,
                status: deviceStatus,
                statusText: deviceStatusText,
                runtime: device.runtime_hours || 0,
                worker_name: device.worker_name,
                last_maintenance: device.last_maintenance_time ? new Date(device.last_maintenance_time).toLocaleDateString() : '无记录'
              };
            });
          }

          this.lastUpdateTime = new Date().toLocaleTimeString();
        } else {
          throw new Error(result.error || '获取产线详情失败');
        }
      } catch (error) {
        console.error('获取产线详情出错:', error);
        this.error = `获取产线详情失败: ${error.message}`;
      }

      return Promise.resolve();
    },

    // 获取产线历史数据
    async fetchLineHistory(limit = 10) {
      if (!this.productionLine || !this.productionLine.id) return;

      console.log('开始获取产线历史数据，条数限制:', limit);
      // 不设置loading状态，避免显示加载界面
      // this.loading = true;

      try {
        const response = await fetch(`/api/production_line/status-history?line_id=${this.productionLine.id}&limit=${limit}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取产线历史数据失败: ${response.status}`);
        }

        const result = await response.json();
        console.log('产线历史数据:', result);

        if (result.success && result.data) {
          // 保持历史数据，将新数据合并到现有数据中
          if (this.lineHistory.length > 0) {
            // 获取最新的数据点
            const latestData = result.data[result.data.length - 1];
            // 检查是否已存在该数据点
            const existingIndex = this.lineHistory.findIndex(item =>
              item.collection_time === latestData.collection_time);

            if (existingIndex === -1) {
              // 如果是新数据点，添加到历史数据中
              this.lineHistory.push(latestData);
              // 保持数组长度不超过限制
              if (this.lineHistory.length > limit) {
                this.lineHistory.shift(); // 移除最早的数据点
              }
            }
          } else {
            // 如果没有历史数据，直接设置
            this.lineHistory = result.data;
          }

          this.lastUpdateTime = new Date().toLocaleTimeString();
        } else {
          console.error('获取产线历史数据失败:', result.error);
        }
      } catch (error) {
        console.error('获取产线历史数据出错:', error);
      }
      // 不需要设置loading状态
      // finally {
      //   this.loading = false;
      // }
    },

    // 获取最新产线数据
    async fetchLatestLineData() {
      if (!this.productionLine || !this.productionLine.id) return;

      console.log('获取最新产线数据');

      try {
        // 获取产线最新状态，但不显示加载界面
        const response = await fetch(`/api/production_line/detail?line_id=${this.productionLine.id}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取产线详情失败: ${response.status}`);
        }

        const result = await response.json();

        if (result.success && result.data) {
          // 处理产线数据
          const lineData = result.data.line;

          // 根据状态设置状态文本
          let statusText = '未知';
          let status = '';

          if (lineData.status === '正常') {
            statusText = '运行中';
            status = 'running';
          } else if (lineData.status === '异常') {
            statusText = '异常';
            status = 'warning';
          } else if (lineData.status === '停机') {
            statusText = '已停机';
            status = 'stopped';
          }

          // 计算产能利用率
          let utilization = 0;
          if (lineData.theoretical_capacity && lineData.theoretical_capacity > 0 && lineData.real_time_capacity) {
            utilization = Math.round((lineData.real_time_capacity / lineData.theoretical_capacity) * 100);
          }

          // 更新产线数据，保持ID和名称不变
          this.productionLine = {
            ...this.productionLine,
            status: status,
            statusText: statusText,
            utilization: utilization,
            output: lineData.real_time_capacity || 0,
            target: lineData.theoretical_capacity || 0,
            runtime: lineData.runtime_hours || 0,
            manager: lineData.foreman_name || '未分配'
          };

          // 处理设备数据
          if (result.data.equipment) {
            this.devices = result.data.equipment.map(device => {
              // 根据设备状态设置状态文本和样式
              let deviceStatus = 'normal';
              let deviceStatusText = '正常';

              if (device.status === '故障') {
                deviceStatus = 'error';
                deviceStatusText = '故障';
              } else if (device.status === '预警') {
                deviceStatus = 'warning';
                deviceStatusText = '预警';
              } else if (device.status === '停机') {
                deviceStatus = 'stopped';
                deviceStatusText = '已停机';
              }

              return {
                id: device.id,
                name: device.equipment_name,
                status: deviceStatus,
                statusText: deviceStatusText,
                runtime: device.runtime_hours || 0,
                worker_name: device.worker_name,
                last_maintenance: device.last_maintenance_time ? new Date(device.last_maintenance_time).toLocaleDateString() : '无记录'
              };
            });
          }
        }

        // 获取最新历史数据点
        if (this.lineHistory && this.lineHistory.length > 0) {
          await this.fetchLineHistory(this.historyLimit);
        }

        this.lastUpdateTime = new Date().toLocaleTimeString();
      } catch (error) {
        console.error('获取最新产线数据出错:', error);
      }
    },

    // 开始自动刷新
    startAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
      }

      this.refreshInterval = setInterval(() => {
        this.fetchLatestLineData();
      }, this.refreshRate);
    },

    // 停止自动刷新
    stopAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
        this.refreshInterval = null;
      }
    },

    // 查看设备详情
    viewDeviceDetail(device) {
      this.$router.push(`/foreman/equipment-detail/${device.id}`);
    },

    // 查看产线所有设备
    viewDevices() {
      this.$router.push({
        path: '/foreman/equipment',
        query: { line: this.productionLine.id }
      });
    },

    // 查看相关工单
    viewWorkOrders() {
      this.$router.push({
        path: '/foreman/workorder',
        query: { line: this.productionLine.id }
      });
    },

    // 排程维护
    scheduleMaintenace() {
      // 这里可以添加排程维护的逻辑
      alert('排程维护功能待实现');
    },

    // 分配维护任务
    assignMaintenance(device) {
      // 这里可以添加分配维护任务的逻辑
      alert(`为设备 ${device.name} 分配维护任务`);
    }
  }
}
</script>

<style scoped>
.production-line-detail {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f7fa;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-left {
  display: flex;
  align-items: center;
}

.back-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  margin-right: 15px;
  color: #333;
}

.header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.status-tag {
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
}

.status-tag.running {
  background-color: #e6f7ff;
  color: #1890ff;
}

.status-tag.warning {
  background-color: #fff7e6;
  color: #fa8c16;
}

.status-tag.stopped {
  background-color: #f5f5f5;
  color: #8c8c8c;
}

.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.devices-section {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  margin-top: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.devices-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
}

.device-item {
  background-color: #f9f9f9;
  border-radius: 6px;
  padding: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.device-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.device-name {
  font-weight: 500;
  font-size: 16px;
}

.device-status {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.device-status.normal {
  background-color: #f6ffed;
  color: #52c41a;
}

.device-status.warning {
  background-color: #fff7e6;
  color: #fa8c16;
}

.device-status.error {
  background-color: #fff1f0;
  color: #f5222d;
}

.device-status.stopped {
  background-color: #f5f5f5;
  color: #8c8c8c;
}

.device-info {
  margin-bottom: 10px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 14px;
  color: #666;
}

.device-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.action-btn {
  padding: 5px 12px;
  border: none;
  border-radius: 4px;
  background-color: #1890ff;
  color: white;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.action-btn:hover {
  background-color: #40a9ff;
}

.action-btn.warning {
  background-color: #fa8c16;
}

.action-btn.warning:hover {
  background-color: #ffa940;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  color: #8c8c8c;
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 10px;
}
</style>
