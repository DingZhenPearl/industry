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

        <!-- 加载中提示 -->
        <div class="loading-container" v-if="loading.productionLines">
          <div class="loading-spinner"></div>
          <div class="loading-text">正在加载产线数据...</div>
        </div>

        <!-- 错误提示 -->
        <div class="error-container" v-if="error.productionLines">
          <div class="error-message">加载产线数据出错: {{ error.productionLines }}</div>
          <button class="retry-btn" @click="fetchProductionLines">重试</button>
        </div>

        <div class="line-list" v-if="!loading.productionLines && !error.productionLines && productionLines.length > 0">
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
                  <span v-if="line.foreman && line.foreman.name">
                    {{ line.foreman.name }}
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

        <!-- 加载中提示 -->
        <div class="loading-container" v-if="loading.equipments">
          <div class="loading-spinner"></div>
          <div class="loading-text">正在加载设备数据...</div>
        </div>

        <!-- 错误提示 -->
        <div class="error-container" v-if="error.equipments">
          <div class="error-message">加载设备数据出错: {{ error.equipments }}</div>
          <button class="retry-btn" @click="fetchEquipments">重试</button>
        </div>

        <div class="equipment-table" v-if="!loading.equipments && !error.equipments && equipments.length > 0">
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
      equipments: [],
      // 错误和加载状态
      loading: {
        productionLines: false,
        equipments: false,
        foremen: false
      },
      error: {
        productionLines: null,
        equipments: null,
        foremen: null
      }
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
    this.fetchForemen();
  },
  methods: {
    // 获取产线数据
    async fetchProductionLines() {
      this.loading.productionLines = true;
      this.error.productionLines = null;

      try {
        console.log('开始获取产线数据');
        const response = await fetch('/api/production_line/with-foremen', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error('响应状态错误:', response.status, errorText);
          throw new Error(`获取产线数据失败: ${response.status}`);
        }

        // 先获取响应文本，然后尝试解析为JSON
        const responseText = await response.text();
        console.log('原始响应文本:', responseText);

        let result;
        try {
          result = JSON.parse(responseText);
          console.log('产线数据返回结果:', result);
        } catch (jsonError) {
          console.error('JSON解析错误:', jsonError);
          console.error('收到的响应不是有效的JSON:', responseText.substring(0, 100) + '...');
          throw new Error(`响应数据格式错误: ${jsonError.message}`);
        }

        if (result.success && result.data) {
          // 处理产线数据
          this.productionLines = result.data.map(line => {
            console.log('处理产线数据:', line);

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

            // 确保产线名称字段存在
            const lineName = line.line_name || line.name || '未知产线';

            // 处理工长信息
            let foreman = null;
            if (line.foreman) {
              foreman = line.foreman;
            } else if (line.foreman_id) {
              // 如果只有工长ID，则创建一个简单的工长对象
              foreman = {
                id: line.foreman_id,
                name: line.foreman_name || line.foreman_id
              };
            }

            return {
              id: line.id,
              name: lineName,
              status: status,
              statusText: statusText,
              utilization: utilization,
              output: Math.round(line.real_time_capacity || 0),
              target: line.theoretical_capacity || 1000,
              runtime: line.runtime_hours || 0,
              equipment_list: line.equipment_list || [],
              foreman: foreman
            };
          });

          console.log('处理后的产线数据:', this.productionLines);

          // 更新状态卡片的数据
          this.updateStatusCards();
        } else {
          console.error('获取产线数据失败:', result.error || '未知错误');
        }
      } catch (error) {
        console.error('获取产线数据出错:', error);
        this.error.productionLines = error.message || '获取产线数据出错';
        this.productionLines = []; // 清空产线数据
        alert(`获取产线数据出错: ${error.message}`);
      } finally {
        this.loading.productionLines = false;
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
      console.log('分配管理工长到产线:', line);
      console.log('当前可用的工长列表:', this.foremen);
      this.selectedLine = line;
      this.showAssignModal = true;
      // 确保工长列表已加载
      if (!this.foremen || this.foremen.length === 0) {
        this.fetchForemen();
      }
    },
    viewDetails(line) {
      console.log('查看详情:', line);
      // 跳转到产线详情页面
      this.$router.push(`/supervisor/production-line-detail/${line.id}`);
    },
    async confirmAssign() {
      console.log(`将${this.selectedLine.name}分配给ID为${this.selectedManager}的工长管理`);

      try {
        // 调用API分配工长到产线
        const response = await fetch('/api/production_line/assign-foreman', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            line_id: this.selectedLine.id,
            foreman_id: this.selectedManager
          })
        });

        // 先获取响应文本，然后尝试解析为JSON
        const responseText = await response.text();
        console.log('原始响应文本:', responseText);

        let result;
        try {
          result = JSON.parse(responseText);
          console.log('分配工长返回结果:', result);
        } catch (jsonError) {
          console.error('JSON解析错误:', jsonError);
          console.error('收到的响应不是有效的JSON:', responseText.substring(0, 100) + '...');
          alert(`分配失败: 响应数据格式错误`);
          return;
        }

        if (result.success) {
          alert('工长分配成功！');
          // 重新加载产线数据
          this.fetchProductionLines();
        } else {
          alert(`分配失败: ${result.error || '未知错误'}`);
        }
      } catch (error) {
        console.error('分配工长时出错:', error);
        alert('分配失败，请重试');
      }

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
    },

    // 获取工长列表
    async fetchForemen() {
      this.loading.foremen = true;
      this.error.foremen = null;

      try {
        console.log('开始获取工长列表');
        const response = await fetch('/api/users/foremen', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error('响应状态错误:', response.status, errorText);
          throw new Error(`获取工长列表失败: ${response.status}`);
        }

        // 先获取响应文本，然后尝试解析为JSON
        const responseText = await response.text();
        console.log('原始响应文本:', responseText);

        let result;
        try {
          result = JSON.parse(responseText);
          console.log('工长列表返回数据:', result);
        } catch (jsonError) {
          console.error('JSON解析错误:', jsonError);
          console.error('收到的响应不是有效的JSON:', responseText.substring(0, 100) + '...');
          throw new Error(`响应数据格式错误: ${jsonError.message}`);
        }

        if (result.success && result.data) {
          this.foremen = result.data.map(foreman => ({
            id: foreman.id,  // 这里的id是employee_id
            name: foreman.name
          }));
          console.log('处理后的工长列表:', this.foremen);
        } else {
          console.error('获取工长列表失败:', result.error);
        }
      } catch (error) {
        console.error('获取工长列表出错:', error);
        this.error.foremen = error.message || '获取工长列表出错';
        this.foremen = []; // 清空工长列表
      } finally {
        this.loading.foremen = false;
      }
    },

    // 获取设备数据
    async fetchEquipments() {
      this.loading.equipments = true;
      this.error.equipments = null;

      try {
        console.log('开始获取设备数据');

        // 确保先获取产线数据
        if (this.productionLines.length === 0) {
          await this.fetchProductionLines();
        }

        // 从后端获取设备数据
        console.log('从后端获取设备数据');
        const response = await fetch('/api/equipment/with-status', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error('响应状态错误:', response.status, errorText);
          throw new Error(`获取设备数据失败: ${response.status}`);
        }

        // 先获取响应文本，然后尝试解析为JSON
        const responseText = await response.text();
        console.log('原始响应文本:', responseText);

        let result;
        try {
          result = JSON.parse(responseText);
          console.log('设备数据返回结果:', result);
        } catch (jsonError) {
          console.error('JSON解析错误:', jsonError);
          console.error('收到的响应不是有效的JSON:', responseText.substring(0, 100) + '...');
          throw new Error(`响应数据格式错误: ${jsonError.message}`);
        }

        // 从后端获取用户数据
        console.log('从后端获取用户数据');
        let users = [];
        try {
          const usersResponse = await fetch('/api/users', {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          });

          if (usersResponse.ok) {
            const usersResult = await usersResponse.json();
            console.log('用户数据返回结果:', usersResult);
            if (usersResult.success && usersResult.data) {
              users = usersResult.data;
              console.log('处理后的用户数据:', users);
            }
          } else {
            console.error('获取用户数据失败:', usersResponse.statusText);
          }
        } catch (error) {
          console.error('获取用户数据出错:', error);
          // 继续处理设备数据，不让用户数据错误影响整体功能
        }

        if (result.success && result.data) {
          // 处理设备数据
          this.equipments = result.data.map(device => {
            // 获取设备状态
            let status = 'running';
            if (device.status === '故障') status = 'stopped';
            else if (device.fault_probability > 0.3) status = 'warning';

            // 获取设备状态文本
            let statusText = '运行中';
            if (status === 'warning') statusText = '异常';
            else if (status === 'stopped') statusText = '已停机';

            // 获取设备类型
            let type = 'production';
            let typeText = '生产设备';
            if (device.equipment_type && device.equipment_type.includes('检测')) {
              type = 'inspection';
              typeText = '检测设备';
            } else if (device.equipment_type && device.equipment_type.includes('辅助')) {
              type = 'auxiliary';
              typeText = '辅助设备';
            }

            // 获取产线名称 - 从产线数组中查找匹配的产线
            let productionLine = '未知产线';
            console.log('设备的产线 ID:', device.line_id);
            console.log('可用的产线列表:', this.productionLines);

            // 注意：设备的line_id是字符串，而产线的id可能是数字
            const matchedLine = this.productionLines.find(line => {
              return String(line.id) === String(device.line_id);
            });

            if (matchedLine) {
              console.log('找到匹配的产线:', matchedLine);
              productionLine = matchedLine.name || matchedLine.line_name;
            } else {
              console.log('未找到匹配的产线');
            }

            // 获取负责人名称 - 从用户数组中查找匹配的用户
            let manager = '未分配';
            if (device.worker_id) {
              console.log('设备的负责人 ID:', device.worker_id);
              console.log('可用的用户列表:', users);

              // 注意：设备的worker_id对应用户的id字段
              const matchedUser = users.find(user => {
                return String(user.id) === String(device.worker_id);
              });

              if (matchedUser) {
                console.log('找到匹配的用户:', matchedUser);
                manager = matchedUser.name || matchedUser.username || device.worker_id;
              } else {
                console.log('未找到匹配的用户');
                manager = device.worker_id; // 如果找不到用户，则显示工号
              }
            }

            return {
              id: device.id,
              name: device.equipment_name,
              code: device.equipment_code,
              type: type,
              typeText: typeText,
              productionLine: productionLine,
              status: status,
              statusText: statusText,
              runtime: device.runtime_hours || 0,
              manager: manager,
              lastMaintenance: device.updated_at ? new Date(device.updated_at).toISOString().split('T')[0] : '未知',
              sensorData: device.sensor_data || {},
              faultProbability: device.fault_probability || 0
            };
          });

          console.log('处理后的设备数据:', this.equipments);
        } else {
          console.error('获取设备数据失败:', result.error || '未知错误');
        }
      } catch (error) {
        console.error('获取设备数据出错:', error);
        this.error.equipments = error.message || '获取设备数据出错';
        this.equipments = []; // 清空设备数据
      } finally {
        this.loading.equipments = false;
      }
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

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  background-color: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #2196F3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: #666;
  font-size: 16px;
}

.error-container {
  background-color: #ffebee;
  border: 1px solid #ffcdd2;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  text-align: center;
}

.error-message {
  color: #d32f2f;
  margin-bottom: 15px;
  font-size: 16px;
}

.retry-btn {
  padding: 8px 16px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.retry-btn:hover {
  background: #d32f2f;
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
