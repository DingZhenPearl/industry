<template>
  <div class="safety-monitor">
    <header class="header">
      <h1>安全监控</h1>
    </header>

    <div class="content">
      <div class="monitor-cards">
        <div class="monitor-card">
          <h3>今日安全状况</h3>
          <div class="status" :class="safetyStatus.class">{{ safetyStatus.text }}</div>
        </div>
      </div>

      <div class="monitor-list">
        <h3>实时监控</h3>



        <!-- 错误提示 -->
        <div class="error-container" v-if="error.productionLines">
          <p class="error-message">{{ error.productionLines }}</p>
          <button class="retry-btn" @click="fetchProductionLines">重试</button>
        </div>

        <!-- 空数据提示 -->
        <div class="empty-container" v-if="!error.productionLines && monitorItems.length === 0">
          <p>没有找到产线数据</p>
        </div>

        <!-- 监控列表 -->
        <div v-if="!error.productionLines && monitorItems.length > 0">
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



        <!-- 错误提示 -->
        <div class="error-container" v-if="error.productionLines">
          <p class="error-message">{{ error.productionLines }}</p>
          <button class="retry-btn" @click="fetchProductionLines">重试</button>
        </div>

        <!-- 空数据提示 -->
        <div class="empty-container" v-if="!error.productionLines && productionLines.length === 0">
          <p>没有找到产线数据</p>
        </div>

        <!-- 产线列表 -->
        <div class="line-list" v-if="!error.productionLines && productionLines.length > 0">
          <div class="line-item" v-for="line in productionLines" :key="line.id">
            <div class="line-header">
              <span class="line-name">{{ line.name }}</span>
              <div class="status-control">
                <span class="line-status" :class="line.status">{{ line.statusText }}</span>
                <div class="status-buttons">
                  <button
                    class="status-btn"
                    :class="{ 'active': line.dbStatus === '正常' }"
                    @click="setLineStatus(line, '正常')"
                    :disabled="line.dbStatus === '故障' || line.dbStatus === '维修中'"
                  >正常</button>
                  <button
                    class="status-btn"
                    :class="{ 'active': line.dbStatus === '停机' }"
                    @click="setLineStatus(line, '停机')"
                  >停机</button>
                  <button
                    class="status-btn"
                    :class="{ 'active': line.dbStatus === '维修中' }"
                    @click="setLineStatus(line, '维修中')"
                  >维修中</button>
                </div>
                <span class="status-note" v-if="line.dbStatus === '故障' || line.dbStatus === '预警'">
                  {{ getStatusNote(line) }}
                </span>
              </div>
            </div>
            <div class="line-body">
              <div class="metric-item">
                <span class="label">噪音水平</span>
                <span class="value" :class="{ warning: typeof line.noise === 'number' && line.noise > 85 }">
                  {{ typeof line.noise === 'number' ? line.noise + 'dB' : line.noise }}
                </span>
              </div>
              <div class="metric-item">
                <span class="label">环境温度</span>
                <span class="value" :class="{ warning: typeof line.temperature === 'number' && line.temperature > 35 }">
                  {{ typeof line.temperature === 'number' ? line.temperature + '°C' : line.temperature }}
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
              <button class="action-btn" @click="viewLineDetail(line)">查看详情</button>
            </div>
          </div>
        </div>
      </div>



      <!-- 新增设备安全监控模块 -->
      <div class="equipment-safety">
        <h3 class="section-title">设备安全状态监控</h3>



        <!-- 错误提示 -->
        <div class="error-container" v-if="error.equipments">
          <p class="error-message">{{ error.equipments }}</p>
          <button class="retry-btn" @click="fetchEquipments">重试</button>
        </div>

        <!-- 空数据提示 -->
        <div class="empty-container" v-if="!error.equipments && equipments.length === 0">
          <p>没有找到设备数据</p>
        </div>

        <!-- 设备列表 -->
        <div v-if="!error.equipments && equipments.length > 0">
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
                    <div class="status-control">
                      <span :class="['status-tag', device.safetyStatus]">{{ device.statusText }}</span>
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
                        <button
                          class="status-btn"
                          :class="{ 'active': device.dbStatus === '维修中' }"
                          @click="setDeviceStatus(device, '维修中')"
                        >维修中</button>
                      </div>
                      <span class="status-note" v-if="device.dbStatus === '故障' || device.dbStatus === '预警'">
                        {{ getDeviceStatusNote(device) }}
                      </span>
                    </div>
                  </td>
                  <td>
                    <div class="safety-params">
                      <span :class="{ warning: typeof device.temperature === 'number' && device.temperature > 80 }">温度: {{ typeof device.temperature === 'number' ? device.temperature + '°C' : device.temperature }}</span>
                      <span :class="{ warning: typeof device.noise === 'number' && device.noise > 85 }">噪音: {{ typeof device.noise === 'number' ? device.noise + 'dB' : device.noise }}</span>
                    </div>
                  </td>
                  <td>{{ device.lastCheck }}</td>
                  <td>
                    <button class="op-btn" @click="viewDeviceDetail(device)">查看</button>
                    <button class="op-btn warning" v-if="device.safetyStatus === 'error'" @click="createMaintenanceOrder(device)">维修</button>
                    <button class="op-btn warning" v-else-if="device.safetyStatus === 'warning'" @click="createSafetyAlert(device)">预警</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
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
      error: {
        productionLines: null,
        equipments: null
      },
      safetyStatus: {
        text: '良好',
        class: 'good'
      },
      updateTimer: null,
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
    // 设置10秒自动刷新
    this.updateTimer = setInterval(() => {
      this.fetchProductionLines(false);
      this.fetchEquipments(false);
    }, 10000);
  },

  beforeDestroy() {
    // 组件销毁前清除定时器
    if (this.updateTimer) {
      clearInterval(this.updateTimer);
    }
  },
  methods: {
    // 查看产线详情
    viewLineDetail(line) {
      console.log('查看产线详情:', line);
      // 确保产线 ID 存在
      if (!line || !line.id) {
        console.error('产线 ID 不存在');
        alert('无法查看产线详情，产线 ID 不存在');
        return;
      }

      // 输出详细信息便于调试
      console.log('产线详细信息:', {
        id: line.id,
        name: line.name,
        original: line.original
      });

      // 使用导航辅助函数跳转到产线详情页面
      import('@/utils/navigationHelper').then(({ navigateWithUid }) => {
        navigateWithUid(this.$router, `/safety-officer/production-line-detail/${line.id}`);
      });
    },





    // 查看设备详情
    viewDeviceDetail(device) {
      console.log('查看设备详情:', device);
      // 使用导航辅助函数跳转到设备详情页面
      import('@/utils/navigationHelper').then(({ navigateWithUid }) => {
        navigateWithUid(this.$router, `/safety-officer/equipment-detail/${device.id}`);
      });
    },



    // 创建安全预警
    async createSafetyAlert(device) {
      console.log('为设备创建安全预警:', device);
      try {
        const hazardData = {
          type: '设备安全隐患',
          level: 'high',
          description: `${device.name}在${device.productionLine}的温度异常，存在安全风险`,
          location: device.productionLine,
          equipment_id: device.id
        };

        // 调用API创建安全隐患
        const response = await fetch('/api/safety/hazards', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(hazardData)
        });

        const result = await response.json();

        if (result.success) {
          alert('已创建安全预警');
        } else {
          alert(`创建安全预警失败: ${result.error || '未知错误'}`);
        }
      } catch (error) {
        console.error('创建安全预警出错:', error);
        alert(`创建安全预警出错: ${error.message || '未知错误'}`);
      }
    },

    // 创建维修工单
    createMaintenanceOrder(device) {
      console.log('创建维修工单:', device);

      // 使用导航辅助函数跳转到安全预警处理页面
      import('@/utils/navigationHelper').then(({ navigateWithUid }) => {
        navigateWithUid(this.$router, '/safety-officer/warnings', {
          device_id: device.id,
          type: 'maintenance'
        });
      });
    },



    // 从后端获取产线数据
    async fetchProductionLines(showError = true) {
      if (showError) {
        this.error.productionLines = null;
      }

      try {
        // 获取当前登录用户的组号
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
        const groupId = userInfo.group_id;

        if (!groupId) {
          if (showError) {
            this.error.productionLines = '无法获取您的组号信息，请重新登录';
          }
          return;
        }

        // 获取安全员组的产线信息
        const url = `/api/production_line/with-status?group_id=${groupId}`;

        const response = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          if (showError) {
            throw new Error(`获取产线数据失败: ${response.status}`);
          }
          return;
        }

        const data = await response.json();

        if (data.success) {
          // 格式化产线数据
          this.productionLines = this.formatProductionLines(data.data || []);
          // 更新监控项目
          this.updateMonitorItems();
          // 更新安全状况
          this.updateSafetyStatus();
        } else if (showError) {
          this.error.productionLines = data.error || '获取产线数据失败';
        }
      } catch (error) {
        if (showError) {
          this.error.productionLines = error.message || '获取产线数据出错';
        }
      }
    },

    // 格式化产线数据
    formatProductionLines(lines) {
      return lines.map(line => {
        // 根据状态设置状态文本和颜色
        let status = 'normal';
        let statusText = '正常';

        // 保存原始数据库状态值供下拉菜单使用
        const dbStatus = line.status || '正常';

        if (dbStatus === '故障' || dbStatus === 'fault') {
          status = 'error';
          statusText = '故障';
        } else if (dbStatus === '预警' || dbStatus === 'warning') {
          status = 'warning';
          statusText = '预警';
        } else if (dbStatus === '停机') {
          status = 'stopped';
          statusText = '已停机';
        } else if (dbStatus === '维修中') {
          status = 'warning';
          statusText = '维修中';
        }

        // 使用后端数据或显示未找到
        let noise = line.noise_level || '未找到';
        let temperature = line.temperature || '未找到';
        let airQuality = line.air_quality || 'unknown';
        let airQualityText = '未找到';

        // 根据空气质量设置文本
        if (airQuality === 'good') {
          airQualityText = '良好';
        } else if (airQuality === 'medium') {
          airQualityText = '一般';
        } else if (airQuality === 'poor') {
          airQualityText = '较差';
        }

        return {
          id: line.id,
          name: line.line_name,
          status: status,
          statusText: statusText,
          dbStatus: dbStatus, // 原始数据库状态值
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
      this.monitorItems = this.productionLines.map(line => {
        let detail = '设备运行正常，无安全隐患';

        if (line.status === 'error') {
          detail = `${line.name}存在故障，需要立即处理`;
        } else if (line.status === 'warning') {
          detail = `${line.name}存在异常情况，请检查`;
        }

        return {
          area: line.name,
          status: line.status,
          statusText: line.statusText,
          detail: detail
        };
      });
    },

    // 从后端获取设备数据
    async fetchEquipments(showError = true) {
      if (showError) {
        this.error.equipments = null;
      }

      try {
        // 获取当前登录用户的组号
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
        const groupId = userInfo.group_id;

        if (!groupId) {
          if (showError) {
            this.error.equipments = '无法获取您的组号信息，请重新登录';
          }
          return;
        }

        // 获取设备信息
        const url = `/api/equipment/with-status?group_id=${groupId}`;

        const response = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          if (showError) {
            throw new Error(`获取设备数据失败: ${response.status}`);
          }
          return;
        }

        const data = await response.json();

        if (data.success) {
          // 格式化设备数据
          this.equipments = this.formatEquipments(data.data || []);
          // 更新安全状况
          this.updateSafetyStatus();
        } else if (showError) {
          this.error.equipments = data.error || '获取设备数据失败';
        }
      } catch (error) {
        if (showError) {
          this.error.equipments = error.message || '获取设备数据出错';
        }
      }
    },

    // 获取状态提示
    getStatusNote(line) {
      if (line.dbStatus === '故障') {
        return '当前产线处于故障状态，需要维修后才能恢复正常';
      } else if (line.dbStatus === '预警') {
        return '产线存在异常，可以停机或进行维修';
      }
      return '';
    },

    // 获取设备状态提示
    getDeviceStatusNote(device) {
      if (device.dbStatus === '故障') {
        return '当前设备处于故障状态，需要维修后才能恢复正常';
      } else if (device.dbStatus === '预警') {
        return '设备存在异常，可以停机或进行维修';
      }
      return '';
    },

    // 设置产线状态
    async setLineStatus(line, status) {
      // 检查当前状态是否允许修改
      if (line.dbStatus === '故障' && status !== '维修中') {
        alert(`故障状态下只能将产线设置为维修中状态。`);
        return;
      }

      // 如果当前状态是预警，只能改为停机或维修中
      if (line.dbStatus === '预警' && status === '正常') {
        alert('预警状态下只能将产线设置为停机或维修中状态。');
        return;
      }

      try {
        console.log(`更新产线 ${line.id} 状态为: ${status}`);

        // 准备状态数据
        const lineData = {
          status: status
        };

        // 调用API更新产线状态
        const response = await fetch('/api/production_line/update', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            line_id: line.id,
            line_data: lineData
          })
        });

        const result = await response.json();

        if (result.success) {
          // 更新成功，强制刷新数据
          await this.fetchProductionLines();
          await this.fetchEquipments(true); // 使用forceRefresh参数强制刷新设备数据
          alert(`产线 ${line.name} 状态已更新为 ${status}`);
        } else {
          alert(`更新产线状态失败: ${result.error || '未知错误'}`);
        }
      } catch (error) {
        console.error('更新产线状态出错:', error);
        alert(`更新产线状态出错: ${error.message || '未知错误'}`);
      }
    },

    // 设置设备状态
    async setDeviceStatus(device, status) {
      // 检查当前状态是否允许修改
      if (device.dbStatus === '故障' && status !== '维修中') {
        alert(`故障状态下只能将设备设置为维修中状态。`);
        return;
      }

      // 如果当前状态是预警，只能改为停机或维修中
      if (device.dbStatus === '预警' && status === '正常') {
        alert('预警状态下只能将设备设置为停机或维修中状态。');
        return;
      }

      try {
        console.log(`更新设备 ${device.id} 状态为: ${status}`);

        // 准备状态数据
        const equipmentData = {
          status: status
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
          // 更新成功，强制刷新数据
          await this.fetchEquipments(true); // 使用forceRefresh参数强制刷新设备数据

          // 直接更新当前设备的状态显示，确保界面立即反映变化
          const updatedDevice = this.equipments.find(d => d.id === device.id);
          if (updatedDevice) {
            // 更新状态文本和样式类
            if (status === '停机') {
              updatedDevice.safetyStatus = 'stopped';
              updatedDevice.statusText = '已停机';
            } else if (status === '正常') {
              updatedDevice.safetyStatus = 'normal';
              updatedDevice.statusText = '正常';
            } else if (status === '维修中') {
              updatedDevice.safetyStatus = 'warning';
              updatedDevice.statusText = '维修中';
            }
          }

          alert(`设备 ${device.name} 状态已更新为 ${status}`);
        } else {
          alert(`更新设备状态失败: ${result.error || '未知错误'}`);
        }
      } catch (error) {
        console.error('更新设备状态出错:', error);
        alert(`更新设备状态出错: ${error.message || '未知错误'}`);
      }
    },

    // 更新安全状况
    updateSafetyStatus() {
      // 检查是否有数据
      if (this.productionLines.length === 0 && this.equipments.length === 0) {
        this.safetyStatus = {
          text: '无数据',
          class: 'unknown'
        };
        return;
      }

      // 检查是否有故障或预警状态的产线或设备
      const hasError = this.productionLines.some(line => line.status === 'error') ||
                      this.equipments.some(device => device.safetyStatus === 'error');

      const hasWarning = this.productionLines.some(line => line.status === 'warning') ||
                        this.equipments.some(device => device.safetyStatus === 'warning');

      if (hasError) {
        this.safetyStatus = {
          text: '异常',
          class: 'error'
        };
      } else if (hasWarning) {
        this.safetyStatus = {
          text: '预警',
          class: 'warning'
        };
      } else {
        this.safetyStatus = {
          text: '良好',
          class: 'good'
        };
      }
    },

    // 格式化设备数据
    formatEquipments(equipments) {
      return equipments.map(equipment => {
        // 获取关联的产线名称
        // 优先使用设备数据中的 line_name 字段
        const productionLine = equipment.line_name || this.productionLines.find(line => line.id === equipment.line_id)?.name || '未知产线';

        // 解析传感器数据
        let temperature = 0;
        let noise = 0;
        let riskLevel = 'low';
        let riskLevelText = '低风险';

        // 尝试解析传感器数据
        try {
          if (equipment.sensor_data) {
            // 尝试解析JSON数据
            const sensorData = typeof equipment.sensor_data === 'string'
              ? JSON.parse(equipment.sensor_data)
              : equipment.sensor_data || {};

            temperature = sensorData.temperature ? sensorData.temperature : '未找到';
            noise = sensorData.noise ? sensorData.noise : '未找到';
          }

          // 根据故障概率设置风险等级
          if (equipment.fault_probability) {
            const faultProbability = equipment.fault_probability;

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
          } else {
            riskLevel = 'unknown';
            riskLevelText = '未知';
          }
        } catch (e) {
          // 如果解析失败，显示未找到
          temperature = '未找到';
          noise = '未找到';
          riskLevel = 'unknown';
          riskLevelText = '未知';
        }

        // 设置安全状态
        let safetyStatus = 'normal';
        let statusText = '正常';

        // 保存原始数据库状态值供下拉菜单使用
        const dbStatus = equipment.status || '正常';

        // 检查设备状态
        if (dbStatus === '故障' || dbStatus === 'fault') {
          safetyStatus = 'error';
          statusText = '故障';
        } else if (dbStatus === '预警' || dbStatus === 'warning' || riskLevel === 'high' || temperature > 85) {
          safetyStatus = 'warning';
          statusText = '预警';
        } else if (dbStatus === '停机') {
          safetyStatus = 'stopped';
          statusText = '已停机';
        } else if (dbStatus === '维修中') {
          safetyStatus = 'warning';
          statusText = '维修中';
        }

        // 格式化最后检查时间
        const lastCheck = equipment.collection_time
          ? new Date(equipment.collection_time).toLocaleDateString()
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
          statusText: statusText,
          dbStatus: dbStatus, // 原始数据库状态值
          lastCheck: lastCheck,
          // 保存原始数据
          original: equipment
        };
      });
    },




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

.status.warning {
  color: #ff9800;
}

.status.error {
  color: #f44336;
}

.status.unknown {
  color: #9e9e9e;
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

.area-status.error {
  background: #ffebee;
  color: #f44336;
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

.line-status.normal {
  background: #e8f5e9;
  color: #4CAF50;
}

.line-status.warning {
  background: #fff3e0;
  color: #ff9800;
}

.line-status.error {
  background: #ffebee;
  color: #f44336;
}

.line-status.stopped {
  background: #ffebee;
  color: #f44336;
}

/* 状态控制样式 */
.status-control {
  display: flex;
  align-items: center;
}

.status-buttons {
  display: flex;
  gap: 8px;
  margin: 0 10px;
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
  color: #ff4d4f;
  margin-left: 10px;
  font-style: italic;
}

/* 设备状态标签样式 */
.status-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-tag.normal {
  background-color: #e8f5e9;
  color: #4CAF50;
}

.status-tag.warning {
  background-color: #fff3e0;
  color: #ff9800;
}

.status-tag.error {
  background-color: #ffebee;
  color: #f44336;
}

.status-tag.stopped {
  background-color: #ffebee;
  color: #f44336;
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
  background: #fff3e0;
  color: #ff9800;
}

.action-btn.error {
  background: #ffebee;
  color: #f44336;
}

.action-btn.status-btn {
  background: #e8eaf6;
  color: #3f51b5;
}

.status-tag {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-tag.normal {
  background: #e8f5e9;
  color: #4CAF50;
}

.status-tag.warning {
  background: #fff3e0;
  color: #ff9800;
}

.status-tag.error {
  background: #ffebee;
  color: #f44336;
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
.warning-list {
  margin-bottom: 15px;
}

.warning-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 15px;
}

.warning-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.warning-type {
  font-weight: bold;
  color: #f44336;
}

.warning-time {
  color: #666;
  font-size: 12px;
}

.warning-content p {
  margin: 5px 0;
}

.warning-location {
  color: #666;
  font-size: 14px;
  margin-top: 5px;
}

.warning-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background-color: #e0e0e0;
  color: #333;
}

.action-btn.primary {
  background-color: #2196F3;
  color: white;
}

/* 表单样式 */
.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

.form-group .value {
  padding: 8px 0;
}

.form-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-input:focus {
  border-color: #2196F3;
  outline: none;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}
</style>
