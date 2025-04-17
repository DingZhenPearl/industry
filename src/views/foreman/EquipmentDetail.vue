<template>
  <div class="equipment-detail">
    <header class="header">
      <div class="header-content">
        <button class="back-btn" @click="goBack">
          <i class="back-icon"></i>
          返回
        </button>
        <h1>设备详情</h1>
      </div>
    </header>

    <div class="content">
      <!-- 使用设备详情组件 -->
      <equipment-detail-component
        :equipment="formattedEquipment"
        :device-history="deviceHistory"
        :loading="loading"
        :error="error"
        :auto-refresh-enabled="autoRefresh"
        :refresh-rate="refreshRate"
        @retry="fetchEquipmentDetail"
        @refresh-data="fetchLatestDeviceData"
        @fetch-history="fetchDeviceHistory"
      >
        <!-- 自定义操作按钮 -->
        <template v-slot:actions>
          <button class="action-btn" @click="scheduleMaintenace" v-if="formattedEquipment && formattedEquipment.status !== 'stopped'">排程维护</button>
          <button class="action-btn" @click="assignWorker" v-if="formattedEquipment">分配工人</button>
          <button class="action-btn" @click="viewWorkOrders" v-if="formattedEquipment">相关工单</button>
        </template>

        <!-- 额外内容 - 设备维护记录 -->
        <template v-slot:extra-content>
          <div class="maintenance-history">
            <h3>维护记录</h3>
            <div class="maintenance-list" v-if="maintenanceRecords.length > 0">
              <div class="maintenance-item" v-for="record in maintenanceRecords" :key="record.id">
                <div class="maintenance-header">
                  <span class="maintenance-type">{{ record.type }}</span>
                  <span class="maintenance-date">{{ record.date }}</span>
                </div>
                <div class="maintenance-body">
                  <p class="maintenance-desc">{{ record.description }}</p>
                  <p class="maintenance-worker">执行人: {{ record.worker }}</p>
                </div>
              </div>
            </div>
            <div class="empty-maintenance" v-else>
              <p>暂无维护记录</p>
            </div>
          </div>
        </template>
      </equipment-detail-component>

      <!-- 排程维护弹窗 -->
      <div class="modal" v-if="showMaintenanceModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>排程设备维护</h3>
            <button class="close-btn" @click="showMaintenanceModal = false">&times;</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>维护时间</label>
              <input type="datetime-local" v-model="maintenanceForm.time" class="form-control">
            </div>
            <div class="form-group">
              <label>维护类型</label>
              <select v-model="maintenanceForm.type" class="form-control">
                <option value="routine">例行维护</option>
                <option value="repair">故障修复</option>
                <option value="upgrade">设备升级</option>
              </select>
            </div>
            <div class="form-group">
              <label>负责工人</label>
              <select v-model="maintenanceForm.worker" class="form-control">
                <option v-for="worker in teamMembers" :key="worker.id" :value="worker.id">
                  {{ worker.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>备注</label>
              <textarea v-model="maintenanceForm.notes" class="form-control" rows="3"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="cancel-btn" @click="showMaintenanceModal = false">取消</button>
            <button class="confirm-btn" @click="confirmMaintenance">确认</button>
          </div>
        </div>
      </div>

      <!-- 分配工人弹窗 -->
      <div class="modal" v-if="showAssignModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>分配负责工人</h3>
            <button class="close-btn" @click="showAssignModal = false">&times;</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>选择工人</label>
              <select v-model="selectedWorker" class="form-control">
                <option value="">请选择工人</option>
                <option v-for="worker in teamMembers" :key="worker.id" :value="worker.id">
                  {{ worker.name }}
                </option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button class="cancel-btn" @click="showAssignModal = false">取消</button>
            <button class="confirm-btn" @click="confirmAssign">确认</button>
          </div>
        </div>
      </div>
    </div>

    <ForemanNav />
  </div>
</template>

<script>
import ForemanNav from '@/components/ForemanNav.vue'
import EquipmentDetailComponent from '@/components/EquipmentDetailComponent.vue'

export default {
  components: {
    ForemanNav,
    EquipmentDetailComponent
  },
  data() {
    return {
      equipment: {
        id: '',
        name: '',
        line_id: '',
        location: '',
        lineName: '',
        sensorId: '',
        description: '',
        status: 'normal',
        statusText: '正常'
      },
      sensors: [],
      currentSensor: null,
      deviceHistory: [],
      loading: false,
      error: null,
      autoRefresh: true,
      refreshRate: 10000, // 10秒更新一次
      showMaintenanceModal: false,
      showAssignModal: false,
      maintenanceForm: {
        time: '',
        type: 'routine',
        worker: '',
        notes: ''
      },
      selectedWorker: '',
      teamMembers: [],
      maintenanceRecords: []
    }
  },
  computed: {
    // 格式化设备数据以适应组件
    formattedEquipment() {
      if (!this.equipment) return null;

      // 构建传感器数据对象
      const sensorData = {};
      if (this.sensors && this.sensors.length > 0) {
        this.sensors.forEach(sensor => {
          // 从传感器名称反向查找键名
          const key = this.getSensorKeyByLabel(sensor.name);
          if (key) {
            sensorData[key] = sensor.value;
          }
        });
      }

      return {
        id: this.equipment.id,
        name: this.equipment.name,
        code: this.equipment.sensorId,
        productionLine: this.equipment.lineName || this.equipment.location,
        status: this.equipment.status,
        statusText: this.equipment.statusText,
        runtime: 0, // 默认值
        sensorData: sensorData
      };
    }
  },
  created() {
    // 获取路由参数中的设备ID
    const equipmentId = this.$route.params.id
    this.equipment.id = equipmentId

    // 获取设备详情
    this.fetchEquipmentDetail(equipmentId)

    // 获取团队成员
    this.fetchTeamMembers()

    // 获取维护记录
    this.fetchMaintenanceRecords()

    // 打印自动刷新设置
    console.log('工长设备详情页面初始化，自动刷新:', this.autoRefresh, '刷新间隔:', this.refreshRate)
  },
  methods: {
    async fetchEquipmentDetail(id) {
      this.loading = true;
      this.error = null;

      try {
        // 从后端获取设备详情
        console.log('获取设备ID:', id, '的详情')

        const response = await fetch(`/api/equipment/with-status?equipment_id=${id}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取设备详情失败: ${response.status}`);
        }

        const result = await response.json();
        console.log('设备详情数据:', result);

        if (result.success && result.data && result.data.length > 0) {
          const deviceData = result.data[0];

          // 处理sensor_data字段，确保是对象
          if (deviceData.sensor_data && typeof deviceData.sensor_data === 'string') {
            try {
              deviceData.sensor_data = JSON.parse(deviceData.sensor_data);
            } catch (e) {
              console.error('解析sensor_data失败:', e);
              deviceData.sensor_data = {};
            }
          }

          // 更新设备数据
          this.equipment = {
            id: deviceData.id,
            name: deviceData.equipment_name,
            line_id: deviceData.line_id,
            location: deviceData.line_name || '未知产线',
            lineName: deviceData.line_name || '未知产线',
            sensorId: deviceData.equipment_code,
            description: deviceData.description || '暂无详细信息',
            status: deviceData.status === '故障' ? 'error' :
                   deviceData.fault_probability > 0.3 ? 'warning' : 'normal',
            statusText: deviceData.status === '故障' ? '故障' :
                       deviceData.fault_probability > 0.3 ? '预警' : '正常'
          };

          console.log('设备产线名称:', deviceData.line_name);

          // 更新传感器数据
          if (deviceData.sensor_data) {
            this.sensors = [];
            for (const [key, value] of Object.entries(deviceData.sensor_data)) {
              const unit = this.getSensorUnit(key);
              this.sensors.push({
                name: this.getSensorLabel(key),
                value: value,
                unit: unit
              });
            }

            if (this.sensors.length > 0) {
              this.currentSensor = this.sensors[0];
            }
          }

          // 获取设备历史数据
          this.fetchDeviceHistory();
        } else {
          this.error = result.error || '未找到设备数据';
        }
      } catch (error) {
        console.error('获取设备详情出错:', error);
        this.error = error.message || '获取设备详情出错';
      } finally {
        this.loading = false;
      }
    },

    // 获取设备历史数据
    async fetchDeviceHistory(limit = 10) {
      if (!this.equipment || !this.equipment.id) return;

      try {
        const response = await fetch(`/api/equipment/status-history?equipment_id=${this.equipment.id}&limit=${limit}`, {
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

    // 获取最新设备数据
    async fetchLatestDeviceData() {
      if (!this.equipment || !this.equipment.id) return;

      try {
        // 获取最新的一条记录
        const response = await fetch(`/api/equipment/status-history?equipment_id=${this.equipment.id}&limit=1`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取设备最新数据失败: ${response.status}`);
        }

        const result = await response.json();
        console.log('获取到最新设备数据:', result);

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
            if (this.deviceHistory.length > 10) {
              this.deviceHistory.shift();
            }

            // 对数据进行排序，确保按时间正序排列
            this.deviceHistory.sort((a, b) => new Date(a.collection_time) - new Date(b.collection_time));

            // 创建一个新数组，触发Vue的响应式更新
            this.deviceHistory = [...this.deviceHistory];
          }

          // 更新传感器数据
          if (latestData.sensor_data) {
            this.sensors = [];
            for (const [key, value] of Object.entries(latestData.sensor_data)) {
              const unit = this.getSensorUnit(key);
              this.sensors.push({
                name: this.getSensorLabel(key),
                value: value,
                unit: unit
              });
            }

            if (this.sensors.length > 0 && this.currentSensor) {
              // 更新当前选中的传感器数据
              const sensorName = this.currentSensor.name;
              const updatedSensor = this.sensors.find(s => s.name === sensorName);
              if (updatedSensor) {
                this.currentSensor = updatedSensor;
              } else {
                this.currentSensor = this.sensors[0];
              }
            }
          }

          // 更新设备状态
          this.equipment.status = latestData.status === '故障' ? 'error' :
                                 latestData.fault_probability > 0.3 ? 'warning' : 'normal';
          this.equipment.statusText = latestData.status === '故障' ? '故障' :
                                     latestData.fault_probability > 0.3 ? '预警' : '正常';
        }
      } catch (error) {
        console.error('获取设备最新数据出错:', error);
      }
    },

    // 获取团队成员
    async fetchTeamMembers() {
      try {
        // 获取当前登录用户的组号
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
        const groupId = userInfo.group_id;

        if (!groupId) {
          console.error('未找到组号信息');
          return;
        }

        const response = await fetch(`/api/foreman/team-members?group_id=${groupId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取团队成员失败: ${response.status}`);
        }

        const result = await response.json();
        console.log('团队成员数据:', result);

        if (result.success && result.data) {
          // 过滤出工人角色的成员
          this.teamMembers = result.data
            .filter(member => member.role === 'member')
            .map(member => ({
              id: member.employee_id,
              name: member.username
            }));
        }
      } catch (error) {
        console.error('获取团队成员出错:', error);
      }
    },

    // 获取维护记录
    async fetchMaintenanceRecords() {
      if (!this.equipment || !this.equipment.id) return;

      try {
        // 模拟获取维护记录的API调用
        // 实际项目中应该调用后端API
        setTimeout(() => {
          this.maintenanceRecords = [
            {
              id: 1,
              type: '例行维护',
              date: '2023-07-15',
              description: '更换传感器，清理设备表面',
              worker: '张工'
            },
            {
              id: 2,
              type: '故障修复',
              date: '2023-06-20',
              description: '修复电机故障，更换轴承',
              worker: '李工'
            }
          ];
        }, 500);
      } catch (error) {
        console.error('获取维护记录出错:', error);
      }
    },

    // 排程维护
    scheduleMaintenace() {
      // 设置默认时间为明天同一时间
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      this.maintenanceForm.time = tomorrow.toISOString().slice(0, 16);

      this.showMaintenanceModal = true;
    },

    // 确认维护
    async confirmMaintenance() {
      try {
        // 模拟API调用
        console.log('排程维护:', this.maintenanceForm);

        // 创建工单
        const workOrderData = {
          equipment_id: this.equipment.id,
          equipment_name: this.equipment.name,
          scheduled_time: this.maintenanceForm.time,
          type: '设备维护',
          worker_id: this.maintenanceForm.worker,
          description: this.maintenanceForm.notes,
          maintenance_type: this.maintenanceForm.type
        };

        // 实际项目中应该调用后端API
        console.log('创建维护工单:', workOrderData);

        alert('维护排程成功！');
        this.showMaintenanceModal = false;
      } catch (error) {
        console.error('排程维护出错:', error);
        alert('排程维护失败，请重试');
      }
    },

    // 分配工人
    assignWorker() {
      this.showAssignModal = true;
    },

    // 确认分配
    async confirmAssign() {
      if (!this.selectedWorker) {
        alert('请选择工人');
        return;
      }

      try {
        // 模拟API调用
        console.log('分配工人:', this.selectedWorker, '到设备:', this.equipment.id);

        // 实际项目中应该调用后端API
        const response = await fetch('/api/equipment/assign-worker', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            equipment_id: this.equipment.id,
            worker_id: this.selectedWorker
          })
        });

        if (response.ok) {
          alert('工人分配成功！');
          this.showAssignModal = false;
        } else {
          alert('工人分配失败，请重试');
        }
      } catch (error) {
        console.error('分配工人出错:', error);
        alert('分配工人失败，请重试');
      }
    },

    // 查看相关工单
    viewWorkOrders() {
      // 跳转到工单页面并传递设备ID
      this.$router.push({
        path: '/foreman/workorder',
        query: { equipment_id: this.equipment.id }
      });
    },

    // 返回上一页
    goBack() {
      this.$router.push('/foreman/equipment');
    },

    // 获取传感器标签
    getSensorLabel(key) {
      const labelMap = {
        'temperature': '温度',
        'pressure': '压力',
        'speed': '转速',
        'vibration': '振动',
        'noise': '噪音',
        'humidity': '湿度',
        'voltage': '电压',
        'current': '电流'
      };
      return labelMap[key] || key;
    },

    // 根据标签获取传感器键名
    getSensorKeyByLabel(label) {
      const keyMap = {
        '温度': 'temperature',
        '压力': 'pressure',
        '转速': 'speed',
        '振动': 'vibration',
        '噪音': 'noise',
        '湿度': 'humidity',
        '电压': 'voltage',
        '电流': 'current'
      };
      return keyMap[label] || null;
    },

    // 获取传感器单位
    getSensorUnit(key) {
      const unitMap = {
        'temperature': '°C',
        'pressure': 'MPa',
        'speed': 'rpm',
        'vibration': 'mm/s',
        'noise': 'dB',
        'humidity': '%',
        'voltage': 'V',
        'current': 'A'
      };
      return unitMap[key] || '';
    }
  }
}
</script>

<style scoped>
.equipment-detail {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding-bottom: 60px;
}

.header {
  background-color: #2196F3;
  color: white;
  padding: 15px;
}

.header-content {
  display: flex;
  align-items: center;
}

.back-btn {
  display: flex;
  align-items: center;
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  margin-right: 15px;
  padding: 5px;
}

.back-icon {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-top: 2px solid white;
  border-left: 2px solid white;
  transform: rotate(-45deg);
  margin-right: 5px;
}

.content {
  flex: 1;
  padding: 15px;
}

.maintenance-history {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-top: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.maintenance-history h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
}

.maintenance-list {
  max-height: 300px;
  overflow-y: auto;
}

.maintenance-item {
  border-bottom: 1px solid #eee;
  padding: 10px 0;
}

.maintenance-item:last-child {
  border-bottom: none;
}

.maintenance-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.maintenance-type {
  font-weight: bold;
  color: #2196F3;
}

.maintenance-date {
  color: #666;
  font-size: 14px;
}

.maintenance-desc {
  margin: 5px 0;
  color: #333;
}

.maintenance-worker {
  margin: 5px 0;
  color: #666;
  font-size: 14px;
}

.empty-maintenance {
  text-align: center;
  padding: 20px;
  color: #999;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.5);
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
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-body {
  padding: 15px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-control {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.modal-footer {
  padding: 15px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.cancel-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  color: #333;
  cursor: pointer;
}

.confirm-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background-color: #2196F3;
  color: white;
  cursor: pointer;
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
</style>
