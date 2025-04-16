<template>
  <div class="safety-monitor">
    <header class="header">
      <h1>安全监控</h1>
    </header>

    <div class="content">
      <div class="monitor-cards">
        <div class="monitor-card">
          <h3>今日安全状况</h3>
          <div class="status good">良好</div>
        </div>

        <div class="monitor-card">
          <h3>预警数量</h3>
          <div class="count">2</div>
        </div>

        <div class="monitor-card">
          <h3>待处理隐患</h3>
          <div class="count">1</div>
        </div>
      </div>

      <div class="monitor-list">
        <h3>实时监控</h3>

        <!-- 加载中提示 -->
        <div class="loading-container" v-if="loading.productionLines">
          <div class="loading-spinner"></div>
          <p>正在加载产线数据...</p>
        </div>

        <!-- 错误提示 -->
        <div class="error-container" v-if="error.productionLines">
          <p class="error-message">{{ error.productionLines }}</p>
          <button class="retry-btn" @click="fetchProductionLines">重试</button>
        </div>

        <!-- 空数据提示 -->
        <div class="empty-container" v-if="!loading.productionLines && !error.productionLines && monitorItems.length === 0">
          <p>没有找到产线数据</p>
        </div>

        <!-- 监控列表 -->
        <div v-if="!loading.productionLines && !error.productionLines && monitorItems.length > 0">
          <div class="list-item" v-for="(item, index) in monitorItems" :key="index">
            <div class="area-info">
              <div class="area-name">{{ item.area }}</div>
              <div class="area-status" :class="item.status">{{ item.statusText }}</div>
            </div>
            <div class="detail">{{ item.detail }}</div>
          </div>
        </div>
      </div>

      <!-- 增加产线安全状态监控 -->
      <div class="production-lines">
        <h3 class="section-title">产线安全状态</h3>

        <!-- 加载中提示 -->
        <div class="loading-container" v-if="loading.productionLines">
          <div class="loading-spinner"></div>
          <p>正在加载产线数据...</p>
        </div>

        <!-- 错误提示 -->
        <div class="error-container" v-if="error.productionLines">
          <p class="error-message">{{ error.productionLines }}</p>
          <button class="retry-btn" @click="fetchProductionLines">重试</button>
        </div>

        <!-- 空数据提示 -->
        <div class="empty-container" v-if="!loading.productionLines && !error.productionLines && productionLines.length === 0">
          <p>没有找到产线数据</p>
        </div>

        <!-- 产线列表 -->
        <div class="line-list" v-if="!loading.productionLines && !error.productionLines && productionLines.length > 0">
          <div class="line-item" v-for="line in productionLines" :key="line.id">
            <div class="line-header">
              <span class="line-name">{{ line.name }}</span>
              <span class="line-status" :class="line.status">{{ line.statusText }}</span>
            </div>
            <div class="line-body">
              <div class="metric-item">
                <span class="label">噪音水平</span>
                <span class="value" :class="{ warning: line.noise > 85 }">
                  {{ line.noise }}dB
                </span>
              </div>
              <div class="metric-item">
                <span class="label">环境温度</span>
                <span class="value" :class="{ warning: line.temperature > 35 }">
                  {{ line.temperature }}°C
                </span>
              </div>
              <div class="metric-item">
                <span class="label">空气质量</span>
                <span class="value" :class="{ warning: line.airQuality === 'poor' }">
                  {{ line.airQualityText }}
                </span>
              </div>
            </div>
            <div class="action-bar">
              <button class="action-btn" @click="startInspection(line)">开始巡检</button>
              <button class="action-btn" @click="viewHistory(line)">历史记录</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 安全隐患列表 -->
      <div class="hazard-list">
        <h3 class="section-title">安全隐患</h3>
        <div class="hazard-item" v-for="hazard in hazards" :key="hazard.id">
          <div class="hazard-header">
            <span class="hazard-type">{{ hazard.type }}</span>
            <span class="hazard-level" :class="hazard.level">{{ hazard.levelText }}</span>
          </div>
          <div class="hazard-content">
            <p>{{ hazard.description }}</p>
            <div class="hazard-info">
              <span>位置：{{ hazard.location }}</span>
              <span>发现时间：{{ hazard.time }}</span>
            </div>
          </div>
          <div class="hazard-actions">
            <button class="handle-btn" @click="handleHazard(hazard)">处理</button>
            <button class="detail-btn" @click="viewHazardDetail(hazard)">详情</button>
          </div>
        </div>
      </div>

      <!-- 新增设备安全监控模块 -->
      <div class="equipment-safety">
        <h3 class="section-title">设备安全状态监控</h3>

        <!-- 加载中提示 -->
        <div class="loading-container" v-if="loading.equipments">
          <div class="loading-spinner"></div>
          <p>正在加载设备数据...</p>
        </div>

        <!-- 错误提示 -->
        <div class="error-container" v-if="error.equipments">
          <p class="error-message">{{ error.equipments }}</p>
          <button class="retry-btn" @click="fetchEquipments">重试</button>
        </div>

        <!-- 空数据提示 -->
        <div class="empty-container" v-if="!loading.equipments && !error.equipments && equipments.length === 0">
          <p>没有找到设备数据</p>
        </div>

        <!-- 设备列表 -->
        <div v-if="!loading.equipments && !error.equipments && equipments.length > 0">
          <div class="filter-bar">
            <select v-model="equipmentFilter.line" class="filter-select">
              <option value="">全部产线</option>
              <option v-for="line in productionLines" :key="line.id" :value="line.id">
                {{ line.name }}
              </option>
            </select>
            <select v-model="equipmentFilter.risk" class="filter-select">
              <option value="">全部风险等级</option>
              <option value="high">高风险</option>
              <option value="medium">中风险</option>
              <option value="low">低风险</option>
            </select>
            <button class="refresh-btn" @click="fetchEquipments">刷新</button>
          </div>

          <div class="equipment-table">
            <table>
              <thead>
                <tr>
                  <th>设备名称</th>
                  <th>所属产线</th>
                  <th>风险等级</th>
                  <th>安全参数</th>
                  <th>最后检查</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="device in filteredEquipments" :key="device.id">
                  <td>{{ device.name }}</td>
                  <td>{{ device.productionLine }}</td>
                  <td>
                    <span :class="['risk-level', device.riskLevel]">{{ device.riskLevelText }}</span>
                  </td>
                  <td>
                    <div class="safety-params">
                      <span :class="{ warning: device.temperature > 80 }">温度: {{ device.temperature }}°C</span>
                      <span :class="{ warning: device.noise > 85 }">噪音: {{ device.noise }}dB</span>
                    </div>
                  </td>
                  <td>{{ device.lastCheck }}</td>
                  <td>
                    <button class="action-btn" @click="startInspectionForDevice(device)">开始巡检</button>
                    <button class="action-btn warning" v-if="device.riskLevel === 'high'" @click="createSafetyAlert(device)">安全预警</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- 巡检任务模态框 -->
    <div class="modal" v-if="showInspectionModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>巡检任务</h3>
          <span class="close-btn" @click="showInspectionModal = false">&times;</span>
        </div>
        <div class="modal-body">
          <div class="checklist">
            <div class="check-item" v-for="item in inspectionItems" :key="item.id">
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  v-model="item.checked"
                  :disabled="item.status === 'passed'"
                >
                <span class="item-text">{{ item.content }}</span>
              </label>
              <span class="check-status" :class="item.status">
                {{ item.statusText }}
              </span>
            </div>
          </div>
          <div class="form-group">
            <label>备注</label>
            <textarea
              v-model="inspectionNote"
              class="form-input"
              rows="3"
              placeholder="请输入巡检备注"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="showInspectionModal = false">取消</button>
          <button class="btn submit" @click="submitInspection">提交</button>
        </div>
      </div>
    </div>

    <SafetyNav />
  </div>
</template>

<script>
import SafetyNav from '@/components/SafetyNav.vue'

export default {
  name: 'SafetyMonitor',
  components: {
    SafetyNav
  },
  data() {
    return {
      monitorItems: [],
      loading: {
        productionLines: false,
        equipments: false
      },
      error: {
        productionLines: null,
        equipments: null
      },
      // 原始模拟数据
      /*
      monitorItems: [
        {
          area: '车身冲压生产线',
          status: 'normal',
          statusText: '正常',
          detail: '设备运行正常，无安全隐患'
        },
        {
          area: '车身焊接生产线',
          status: 'warning',
          statusText: '预警',
          detail: '检测到焊接机器人异常振动，建议检查'
        },
        {
          area: '底盘装配生产线',
          status: 'normal',
          statusText: '正常',
          detail: '设备运行正常，无安全隐患'
        },
        {
          area: '电池组装生产线',
          status: 'warning',
          statusText: '预警',
          detail: '电池测试区温度偏高，需要检查散热系统'
        }
      ],
      */
      productionLines: [],
      // 原始模拟数据
      /*
      productionLines: [
        {
          id: 1,
          name: '车身冲压生产线',
          status: 'normal',
          statusText: '正常',
          noise: 82,
          temperature: 28,
          airQuality: 'good',
          airQualityText: '良好'
        },
        {
          id: 2,
          name: '车身焊接生产线',
          status: 'warning',
          statusText: '预警',
          noise: 88,
          temperature: 37,
          airQuality: 'poor',
          airQualityText: '较差'
        },
        {
          id: 3,
          name: '底盘装配生产线',
          status: 'normal',
          statusText: '正常',
          noise: 75,
          temperature: 26,
          airQuality: 'good',
          airQualityText: '良好'
        },
        {
          id: 4,
          name: '电池组装生产线',
          status: 'warning',
          statusText: '预警',
          noise: 72,
          temperature: 42,
          airQuality: 'medium',
          airQualityText: '一般'
        }
      ],
      */
      hazards: [
        {
          id: 1,
          type: '设备隐患',
          level: 'high',
          levelText: '高危',
          description: '车身焊接生产线焊接机器人温度异常，存在安全隐患',
          location: '车身焊接生产线',
          time: '2023-07-10 10:30'
        },
        {
          id: 2,
          type: '环境隐患',
          level: 'medium',
          levelText: '中危',
          description: '电池组装生产线通风系统效率下降，可能影响空气质量',
          location: '电池组装生产线',
          time: '2023-07-10 11:15'
        }
      ],
      showInspectionModal: false,
      inspectionItems: [
        {
          id: 1,
          content: '检查安全防护装置是否完好',
          status: 'pending',
          statusText: '待检查',
          checked: false
        },
        {
          id: 2,
          content: '检查消防设施是否正常',
          status: 'pending',
          statusText: '待检查',
          checked: false
        }
      ],
      inspectionNote: '',

      // 新增设备安全监控相关数据
      equipmentFilter: {
        line: '',
        risk: ''
      },
      equipments: [],
      // 原始模拟数据
      /*
      equipments: [
        {
          id: 1,
          name: '车身冲压机R-2023',
          productionLine: '车身冲压生产线',
          riskLevel: 'medium',
          riskLevelText: '中风险',
          temperature: 85,
          noise: 82,
          safetyStatus: 'normal',
          lastCheck: '2023-07-05'
        },
        {
          id: 2,
          name: '钢板输送系统S-101',
          productionLine: '车身冲压生产线',
          riskLevel: 'low',
          riskLevelText: '低风险',
          temperature: 65,
          noise: 75,
          safetyStatus: 'normal',
          lastCheck: '2023-07-06'
        },
        {
          id: 3,
          name: '焊接机器人W-501',
          productionLine: '车身焊接生产线',
          riskLevel: 'high',
          riskLevelText: '高风险',
          temperature: 92,
          noise: 88,
          safetyStatus: 'warning',
          lastCheck: '2023-07-03'
        },
        {
          id: 4,
          name: '激光焊接系统L-202',
          productionLine: '车身焊接生产线',
          riskLevel: 'medium',
          riskLevelText: '中风险',
          temperature: 78,
          noise: 80,
          safetyStatus: 'normal',
          lastCheck: '2023-07-04'
        },
        {
          id: 5,
          name: '底盘组装机A-601',
          productionLine: '底盘装配生产线',
          riskLevel: 'low',
          riskLevelText: '低风险',
          temperature: 65,
          noise: 72,
          safetyStatus: 'normal',
          lastCheck: '2023-07-07'
        },
        {
          id: 6,
          name: '电池测试设备B-301',
          productionLine: '电池组装生产线',
          riskLevel: 'high',
          riskLevelText: '高风险',
          temperature: 90,
          noise: 70,
          safetyStatus: 'warning',
          lastCheck: '2023-07-02'
        },
        {
          id: 7,
          name: '电芯配对系统C-405',
          productionLine: '电池组装生产线',
          riskLevel: 'low',
          riskLevelText: '低风险',
          temperature: 65,
          noise: 72,
          safetyStatus: 'normal',
          lastCheck: '2023-07-08'
        },
        {
          id: 8,
          name: '动力总成测试台D-501',
          productionLine: '动力总成生产线',
          riskLevel: 'low',
          riskLevelText: '低风险',
          temperature: 60,
          noise: 75,
          safetyStatus: 'normal',
          lastCheck: '2023-07-04'
        }
      ]
      */
    }
  },
  computed: {
    // 根据筛选条件过滤设备
    filteredEquipments() {
      return this.equipments.filter(equipment => {
        // 按产线筛选
        const lineMatch = !this.equipmentFilter.line ||
          equipment.productionLine.includes(this.productionLines.find(l => l.id === this.equipmentFilter.line)?.name || '');

        // 按风险等级筛选
        const riskMatch = !this.equipmentFilter.risk ||
          equipment.riskLevel === this.equipmentFilter.risk;

        return lineMatch && riskMatch;
      });
    }
  },
  created() {
    this.fetchProductionLines();
    this.fetchEquipments();
  },
  methods: {
    startInspection(line) {
      this.selectedLine = line;
      this.showInspectionModal = true;
    },
    viewHistory(line) {
      console.log('查看历史记录:', line);
    },
    handleHazard(hazard) {
      console.log('处理安全隐患:', hazard);
    },
    viewHazardDetail(hazard) {
      console.log('查看隐患详情:', hazard);
    },
    submitInspection() {
      console.log('提交巡检结果');
      this.showInspectionModal = false;
    },

    // 对特定设备开始巡检
    startInspectionForDevice(device) {
      console.log('对设备开始安全巡检:', device);
      // 这里可以直接打开巡检表单或跳转到巡检页面
      this.$router.push('/safety/inspection');
    },

    // 创建安全预警
    createSafetyAlert(device) {
      console.log('为设备创建安全预警:', device);
      const newHazard = {
        id: this.hazards.length + 1,
        type: '设备安全隐患',
        level: 'high',
        levelText: '高危',
        description: `${device.name}在${device.productionLine}的温度异常，存在安全风险`,
        location: device.productionLine,
        time: new Date().toLocaleString()
      };

      this.hazards.push(newHazard);
      alert('已创建安全预警并添加到隐患列表');
    },

    // 从后端获取产线数据
    async fetchProductionLines() {
      this.loading.productionLines = true;
      this.error.productionLines = null;

      try {
        // 获取当前登录用户的组号
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
        const groupId = userInfo.group_id;

        if (!groupId) {
          console.error('未找到组号信息');
          this.error.productionLines = '无法获取您的组号信息，请重新登录';
          return;
        }

        console.log('尝试获取组号为', groupId, '的产线数据');

        // 获取安全员组的产线信息
        const url = `/api/production_line/with-status?group_id=${groupId}`;
        console.log('请求URL:', url);

        const response = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error('响应状态错误:', response.status, errorText);
          throw new Error(`获取产线数据失败: ${response.status}`);
        }

        const responseText = await response.text();
        console.log('原始响应文本:', responseText);

        try {
          const data = JSON.parse(responseText);
          console.log('安全员组的产线数据:', data);

          if (data.success) {
            // 格式化产线数据
            this.productionLines = this.formatProductionLines(data.data || []);
            // 更新监控项目
            this.updateMonitorItems();
          } else {
            this.error.productionLines = data.error || '获取产线数据失败';
          }
        } catch (jsonError) {
          console.error('JSON解析错误:', jsonError);
          this.error.productionLines = `响应数据格式错误: ${jsonError.message}`;
        }
      } catch (error) {
        console.error('获取产线数据出错:', error);
        this.error.productionLines = error.message || '获取产线数据出错';
      } finally {
        this.loading.productionLines = false;
      }
    },

    // 格式化产线数据
    formatProductionLines(lines) {
      return lines.map(line => {
        // 根据状态设置状态文本和颜色
        let status = 'normal';
        let statusText = '正常';

        if (line.status === '故障' || line.status === 'fault') {
          status = 'warning';
          statusText = '预警';
        }

        // 解析传感器数据
        let noise = 0;
        let temperature = 0;
        let airQuality = 'good';
        let airQualityText = '良好';

        try {
          // 如果有实时状态数据
          if (line.latest_status) {
            // 尝试解析JSON数据
            const sensorData = typeof line.latest_status.sensor_data === 'string'
              ? JSON.parse(line.latest_status.sensor_data)
              : line.latest_status.sensor_data || {};

            noise = sensorData.noise || 0;
            temperature = sensorData.temperature || 0;

            // 根据空气质量值设置文本
            if (sensorData.air_quality) {
              airQuality = sensorData.air_quality;

              if (airQuality === 'poor') {
                airQualityText = '较差';
              } else if (airQuality === 'medium') {
                airQualityText = '一般';
              } else {
                airQualityText = '良好';
              }
            }
          }
        } catch (e) {
          console.error('解析传感器数据失败:', e);
        }

        return {
          id: line.id,
          name: line.line_name,
          status: status,
          statusText: statusText,
          noise: noise,
          temperature: temperature,
          airQuality: airQuality,
          airQualityText: airQualityText,
          // 保存原始数据
          original: line
        };
      });
    },

    // 更新监控项目
    updateMonitorItems() {
      this.monitorItems = this.productionLines.map(line => ({
        area: line.name,
        status: line.status,
        statusText: line.statusText,
        detail: line.status === 'warning'
          ? `${line.name}存在异常情况，请检查`
          : '设备运行正常，无安全隐患'
      }));
    },

    // 从后端获取设备数据
    async fetchEquipments() {
      this.loading.equipments = true;
      this.error.equipments = null;

      try {
        // 获取当前登录用户的组号
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
        const groupId = userInfo.group_id;

        if (!groupId) {
          console.error('未找到组号信息');
          this.error.equipments = '无法获取您的组号信息，请重新登录';
          return;
        }

        console.log('尝试获取组号为', groupId, '的设备数据');

        // 获取设备信息
        const url = `/api/equipment/with-status?group_id=${groupId}`;
        console.log('请求URL:', url);

        const response = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error('响应状态错误:', response.status, errorText);
          throw new Error(`获取设备数据失败: ${response.status}`);
        }

        const responseText = await response.text();
        console.log('原始响应文本:', responseText);

        try {
          const data = JSON.parse(responseText);
          console.log('安全员组的设备数据:', data);

          if (data.success) {
            // 格式化设备数据
            this.equipments = this.formatEquipments(data.data || []);
          } else {
            this.error.equipments = data.error || '获取设备数据失败';
          }
        } catch (jsonError) {
          console.error('JSON解析错误:', jsonError);
          this.error.equipments = `响应数据格式错误: ${jsonError.message}`;
        }
      } catch (error) {
        console.error('获取设备数据出错:', error);
        this.error.equipments = error.message || '获取设备数据出错';
      } finally {
        this.loading.equipments = false;
      }
    },

    // 格式化设备数据
    formatEquipments(equipments) {
      return equipments.map(equipment => {
        // 获取关联的产线名称
        const productionLine = this.productionLines.find(line => line.id === equipment.line_id)?.name || '未知产线';

        // 解析传感器数据
        let temperature = 0;
        let noise = 0;
        let riskLevel = 'low';
        let riskLevelText = '低风险';

        try {
          // 如果有实时状态数据
          if (equipment.latest_status) {
            // 尝试解析JSON数据
            const sensorData = typeof equipment.latest_status.sensor_data === 'string'
              ? JSON.parse(equipment.latest_status.sensor_data)
              : equipment.latest_status.sensor_data || {};

            temperature = sensorData.temperature || 0;
            noise = sensorData.noise || 0;

            // 根据故障概率设置风险等级
            const faultProbability = equipment.latest_status.fault_probability || 0;

            if (faultProbability > 0.7) {
              riskLevel = 'high';
              riskLevelText = '高风险';
            } else if (faultProbability > 0.3) {
              riskLevel = 'medium';
              riskLevelText = '中风险';
            } else {
              riskLevel = 'low';
              riskLevelText = '低风险';
            }
          }
        } catch (e) {
          console.error('解析传感器数据失败:', e);
        }

        // 设置安全状态
        let safetyStatus = 'normal';
        if (riskLevel === 'high' || temperature > 85) {
          safetyStatus = 'warning';
        }

        // 格式化最后检查时间
        const lastCheck = equipment.latest_status?.collection_time
          ? new Date(equipment.latest_status.collection_time).toLocaleDateString()
          : '未知';

        return {
          id: equipment.id,
          name: equipment.equipment_name,
          productionLine: productionLine,
          riskLevel: riskLevel,
          riskLevelText: riskLevelText,
          temperature: temperature,
          noise: noise,
          safetyStatus: safetyStatus,
          lastCheck: lastCheck,
          // 保存原始数据
          original: equipment
        };
      });
    }
  }
}
</script>

<style scoped>
.safety-monitor {
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

.monitor-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.monitor-card {
  background: white;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.monitor-card h3 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
}

.status {
  font-size: 18px;
  font-weight: bold;
}

.status.good {
  color: #4CAF50;
}

.count {
  font-size: 24px;
  font-weight: bold;
  color: #2196F3;
}

.monitor-list {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.list-item {
  border-bottom: 1px solid #eee;
  padding: 15px 0;
}

.list-item:last-child {
  border-bottom: none;
}

.area-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.area-name {
  font-weight: bold;
}

.area-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.area-status.normal {
  background: #e8f5e9;
  color: #4CAF50;
}

.area-status.warning {
  background: #fff3e0;
  color: #ff9800;
}

.detail {
  color: #666;
  font-size: 14px;
}

.production-lines {
  margin-top: 20px;
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
}

.line-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.line-body {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.metric-item {
  text-align: center;
}

.metric-item .label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.metric-item .value {
  font-size: 18px;
  font-weight: bold;
  color: #4CAF50;
}

.metric-item .value.warning {
  color: #ff9800;
}

.action-bar {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 15px;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  background: #e3f2fd;
  color: #2196F3;
  cursor: pointer;
}

.hazard-list {
  margin-top: 20px;
}

.hazard-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.hazard-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.hazard-type {
  font-weight: bold;
}

.hazard-level {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.hazard-level.high {
  background: #ffebee;
  color: #f44336;
}

.hazard-level.medium {
  background: #fff3e0;
  color: #ff9800;
}

.hazard-level.low {
  background: #e8f5e9;
  color: #4CAF50;
}

.hazard-info {
  display: flex;
  justify-content: space-between;
  color: #666;
  font-size: 14px;
  margin-top: 10px;
}

.hazard-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 15px;
}

.handle-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  background: #2196F3;
  color: white;
  cursor: pointer;
}

.detail-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  background: #f5f5f5;
  color: #666;
  cursor: pointer;
}

.checklist {
  margin-bottom: 20px;
}

.check-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.check-status {
  font-size: 12px;
}

.check-status.passed {
  color: #4CAF50;
}

.check-status.pending {
  color: #666;
}

/* 新增设备安全监控样式 */
.equipment-safety {
  margin-top: 20px;
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.equipment-table {
  overflow-x: auto;
  margin-top: 15px;
}

.equipment-table table {
  width: 100%;
  border-collapse: collapse;
}

.equipment-table th,
.equipment-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.equipment-table th {
  background: #f5f5f5;
  font-weight: bold;
  color: #333;
}

.risk-level {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.risk-level.high {
  background: #ffebee;
  color: #f44336;
}

.risk-level.medium {
  background: #fff3e0;
  color: #ff9800;
}

.risk-level.low {
  background: #e8f5e9;
  color: #4CAF50;
}

.safety-params {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.safety-params span {
  font-size: 13px;
}

.safety-params span.warning {
  color: #f44336;
  font-weight: bold;
}

.filter-bar {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.filter-select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  flex: 1;
}

.action-btn.warning {
  background: #ffebee;
  color: #f44336;
}
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  background-color: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 15px;
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

.error-container {
  background-color: #ffebee;
  border: 1px solid #ffcdd2;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  text-align: center;
}

.error-message {
  color: #d32f2f;
  margin-bottom: 10px;
}

.retry-btn {
  padding: 8px 16px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.empty-container {
  text-align: center;
  padding: 30px;
  color: #757575;
  background-color: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 15px;
}

.refresh-btn {
  padding: 8px 16px;
  background: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
