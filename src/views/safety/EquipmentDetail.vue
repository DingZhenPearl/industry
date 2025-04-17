<template>
  <div class="equipment-detail">
    <header class="header">
      <div class="header-content">
        <button class="back-btn" @click="goBack">
          <i class="back-icon"></i>
          返回
        </button>
        <h1>设备安全详情</h1>
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
          <button class="action-btn" @click="startInspection">开始巡检</button>
          <button class="action-btn warning" @click="createSafetyAlert" v-if="formattedEquipment && formattedEquipment.status === 'warning'">创建预警</button>
          <button class="action-btn" @click="viewSafetyRecords">安全记录</button>
        </template>

        <!-- 额外内容 - 安全风险评估 -->
        <template v-slot:extra-content>
          <div class="safety-assessment">
            <h3>安全风险评估</h3>
            <div class="risk-indicators">
              <div class="risk-indicator" :class="{ warning: safetyData.temperature > 80 }">
                <div class="indicator-label">温度风险</div>
                <div class="indicator-value">{{ safetyData.temperature }}°C</div>
                <div class="indicator-bar">
                  <div class="indicator-fill" :style="{ width: `${Math.min(safetyData.temperature / 100 * 100, 100)}%` }"></div>
                </div>
              </div>
              <div class="risk-indicator" :class="{ warning: safetyData.noise > 85 }">
                <div class="indicator-label">噪音风险</div>
                <div class="indicator-value">{{ safetyData.noise }}dB</div>
                <div class="indicator-bar">
                  <div class="indicator-fill" :style="{ width: `${Math.min(safetyData.noise / 100 * 100, 100)}%` }"></div>
                </div>
              </div>
              <div class="risk-indicator" :class="{ warning: safetyData.vibration > 8 }">
                <div class="indicator-label">振动风险</div>
                <div class="indicator-value">{{ safetyData.vibration }}mm/s</div>
                <div class="indicator-bar">
                  <div class="indicator-fill" :style="{ width: `${Math.min(safetyData.vibration / 10 * 100, 100)}%` }"></div>
                </div>
              </div>
              <div class="risk-indicator" :class="{ warning: safetyData.pressure > 8 }">
                <div class="indicator-label">压力风险</div>
                <div class="indicator-value">{{ safetyData.pressure }}MPa</div>
                <div class="indicator-bar">
                  <div class="indicator-fill" :style="{ width: `${Math.min(safetyData.pressure / 10 * 100, 100)}%` }"></div>
                </div>
              </div>
            </div>
            <div class="safety-recommendations">
              <h4>安全建议</h4>
              <ul>
                <li v-if="safetyData.temperature > 80">温度过高，建议检查冷却系统</li>
                <li v-if="safetyData.noise > 85">噪音超标，建议佩戴防护耳罩并检查设备</li>
                <li v-if="safetyData.vibration > 8">振动异常，建议检查设备固定和平衡</li>
                <li v-if="safetyData.pressure > 8">压力过高，建议检查压力阀和管道</li>
                <li v-if="safetyData.temperature <= 80 && safetyData.noise <= 85 && safetyData.vibration <= 8 && safetyData.pressure <= 8">设备各项指标正常，请继续保持定期检查</li>
              </ul>
            </div>
          </div>

          <!-- 最近巡检记录 -->
          <div class="inspection-history">
            <h3>最近巡检记录</h3>
            <div class="inspection-list" v-if="inspectionRecords.length > 0">
              <div class="inspection-item" v-for="record in inspectionRecords" :key="record.id">
                <div class="inspection-header">
                  <span class="inspection-date">{{ record.date }}</span>
                  <span :class="['inspection-result', record.result]">{{ record.resultText }}</span>
                </div>
                <div class="inspection-body">
                  <p class="inspection-desc">{{ record.description }}</p>
                  <p class="inspection-inspector">检查人: {{ record.inspector }}</p>
                </div>
              </div>
            </div>
            <div class="empty-inspection" v-else>
              <p>暂无巡检记录</p>
            </div>
          </div>
        </template>
      </equipment-detail-component>

      <!-- 创建安全预警弹窗 -->
      <div class="modal" v-if="showAlertModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>创建安全预警</h3>
            <button class="close-btn" @click="showAlertModal = false">&times;</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>风险等级</label>
              <select v-model="alertForm.level" class="form-control">
                <option value="low">低风险</option>
                <option value="medium">中风险</option>
                <option value="high">高风险</option>
              </select>
            </div>
            <div class="form-group">
              <label>风险描述</label>
              <textarea v-model="alertForm.description" class="form-control" rows="3"></textarea>
            </div>
            <div class="form-group">
              <label>建议措施</label>
              <textarea v-model="alertForm.recommendation" class="form-control" rows="3"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="cancel-btn" @click="showAlertModal = false">取消</button>
            <button class="confirm-btn" @click="confirmAlert">确认</button>
          </div>
        </div>
      </div>
    </div>

    <SafetyNav />
  </div>
</template>

<script>
import SafetyNav from '@/components/SafetyNav.vue'
import EquipmentDetailComponent from '@/components/EquipmentDetailComponent.vue'

export default {
  components: {
    SafetyNav,
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
      showAlertModal: false,
      alertForm: {
        level: 'medium',
        description: '',
        recommendation: ''
      },
      safetyData: {
        temperature: 0,
        noise: 0,
        vibration: 0,
        pressure: 0
      },
      inspectionRecords: []
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

    // 获取巡检记录
    this.fetchInspectionRecords()

    // 打印自动刷新设置
    console.log('安全员设备详情页面初始化，自动刷新:', this.autoRefresh, '刷新间隔:', this.refreshRate)
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

            // 更新安全数据
            this.updateSafetyData(deviceData.sensor_data);
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

    // 更新安全数据
    updateSafetyData(sensorData) {
      if (!sensorData) return;

      this.safetyData = {
        temperature: sensorData.temperature || 0,
        noise: sensorData.noise || 0,
        vibration: sensorData.vibration || 0,
        pressure: sensorData.pressure || 0
      };
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

            // 更新安全数据
            this.updateSafetyData(latestData.sensor_data);
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

    // 获取巡检记录
    async fetchInspectionRecords() {
      if (!this.equipment || !this.equipment.id) return;

      try {
        // 模拟获取巡检记录的API调用
        // 实际项目中应该调用后端API
        setTimeout(() => {
          this.inspectionRecords = [
            {
              id: 1,
              date: '2023-07-18',
              result: 'pass',
              resultText: '通过',
              description: '设备运行正常，各项指标在安全范围内',
              inspector: '王安全'
            },
            {
              id: 2,
              date: '2023-07-10',
              result: 'warning',
              resultText: '警告',
              description: '设备温度偏高，建议检查冷却系统',
              inspector: '李安全'
            }
          ];
        }, 500);
      } catch (error) {
        console.error('获取巡检记录出错:', error);
      }
    },

    // 开始巡检
    startInspection() {
      // 跳转到巡检页面并传递设备ID
      this.$router.push({
        path: '/safety/inspection',
        query: { equipment_id: this.equipment.id }
      });
    },

    // 创建安全预警
    createSafetyAlert() {
      // 设置默认描述
      this.alertForm.description = `${this.equipment.name}在${this.equipment.lineName || this.equipment.location}的参数异常，存在安全风险`;

      // 根据安全数据设置建议措施
      let recommendations = [];
      if (this.safetyData.temperature > 80) recommendations.push('检查冷却系统');
      if (this.safetyData.noise > 85) recommendations.push('佩戴防护耳罩并检查设备');
      if (this.safetyData.vibration > 8) recommendations.push('检查设备固定和平衡');
      if (this.safetyData.pressure > 8) recommendations.push('检查压力阀和管道');

      this.alertForm.recommendation = recommendations.join('；');

      this.showAlertModal = true;
    },

    // 确认创建预警
    async confirmAlert() {
      try {
        // 模拟API调用
        console.log('创建安全预警:', this.alertForm);

        // 创建预警
        const alertData = {
          equipment_id: this.equipment.id,
          equipment_name: this.equipment.name,
          production_line: this.equipment.lineName || this.equipment.location,
          level: this.alertForm.level,
          description: this.alertForm.description,
          recommendation: this.alertForm.recommendation
        };

        // 实际项目中应该调用后端API
        console.log('创建安全预警:', alertData);

        alert('安全预警创建成功！');
        this.showAlertModal = false;
      } catch (error) {
        console.error('创建安全预警出错:', error);
        alert('创建安全预警失败，请重试');
      }
    },

    // 查看安全记录
    viewSafetyRecords() {
      // 跳转到安全记录页面并传递设备ID
      this.$router.push({
        path: '/safety/statistics',
        query: { equipment_id: this.equipment.id }
      });
    },

    // 返回上一页
    goBack() {
      this.$router.push('/safety/monitor');
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

.safety-assessment {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-top: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.safety-assessment h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
}

.risk-indicators {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 15px;
}

.risk-indicator {
  background: #f5f5f5;
  border-radius: 4px;
  padding: 10px;
}

.risk-indicator.warning {
  background: #fff3e0;
}

.indicator-label {
  font-weight: bold;
  margin-bottom: 5px;
}

.indicator-value {
  font-size: 18px;
  margin-bottom: 5px;
}

.indicator-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.indicator-fill {
  height: 100%;
  background: #4CAF50;
  border-radius: 4px;
}

.risk-indicator.warning .indicator-fill {
  background: #FF9800;
}

.safety-recommendations {
  background: #f5f5f5;
  border-radius: 4px;
  padding: 10px;
  margin-top: 15px;
}

.safety-recommendations h4 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 14px;
}

.safety-recommendations ul {
  margin: 0;
  padding-left: 20px;
}

.safety-recommendations li {
  margin-bottom: 5px;
}

.inspection-history {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-top: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.inspection-history h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
}

.inspection-list {
  max-height: 300px;
  overflow-y: auto;
}

.inspection-item {
  border-bottom: 1px solid #eee;
  padding: 10px 0;
}

.inspection-item:last-child {
  border-bottom: none;
}

.inspection-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.inspection-date {
  font-weight: bold;
}

.inspection-result {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.inspection-result.pass {
  background: #e8f5e9;
  color: #4CAF50;
}

.inspection-result.warning {
  background: #fff3e0;
  color: #FF9800;
}

.inspection-result.fail {
  background: #ffebee;
  color: #F44336;
}

.inspection-desc {
  margin: 5px 0;
  color: #333;
}

.inspection-inspector {
  margin: 5px 0;
  color: #666;
  font-size: 14px;
}

.empty-inspection {
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

.action-btn.warning {
  color: #FF9800;
}

.action-btn.disabled {
  background: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}
</style>
