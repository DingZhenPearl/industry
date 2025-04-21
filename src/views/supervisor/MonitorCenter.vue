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


      <!-- 增加产线状态列表 -->
      <div class="production-lines">
        <div class="section-header">
          <h3 class="section-title">产线运行状态</h3>
          <div class="header-actions">
            <div class="refresh-control">
              <span class="last-update" v-if="lastUpdateTime">上次更新: {{ lastUpdateTime }}</span>
              <button class="refresh-btn" :class="{ 'auto-refresh': autoRefresh }" @click="toggleAutoRefresh">
                {{ autoRefresh ? '自动刷新中' : '自动刷新' }}
              </button>
              <button class="refresh-btn" @click="fetchProductionLines">
                <i class="refresh-icon"></i> 刷新
              </button>
            </div>
            <button class="config-btn" @click="showConfigModal = true">
              <i class="settings-icon"></i> 产线配置
            </button>
          </div>
        </div>

        <!-- 错误提示 -->
        <div class="error-container" v-if="error.productionLines">
          <div class="error-message">加载产线数据出错: {{ error.productionLines }}</div>
          <button class="retry-btn" @click="fetchProductionLines">重试</button>
        </div>

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
                </div>
                <span class="status-note" v-if="line.dbStatus === '故障' || line.dbStatus === '维修中' || line.dbStatus === '预警'">
                  {{ getStatusNote(line) }}
                </span>
              </div>
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
          <div class="header-actions">
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
            <button class="config-btn" @click="showEquipmentConfigModal = true">
              <i class="config-icon"></i> 设备配置
            </button>
            <button class="config-btn" @click="showAddEquipmentModal = true">
              <i class="add-icon"></i> 新增设备
            </button>
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

        <!-- 错误提示 -->
        <div class="error-container" v-if="error.equipments">
          <div class="error-message">加载设备数据出错: {{ error.equipments }}</div>
          <button class="retry-btn" @click="fetchEquipments">重试</button>
        </div>

        <div class="equipment-table" v-if="!error.equipments && equipments.length > 0">
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
                  <div class="status-control">
                    <span :class="['status-tag', device.status]">{{ device.statusText }}</span>
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
                </td>
                <td>{{ device.runtime }}</td>
                <td>
                  <button class="op-btn" @click="viewDeviceDetail(device)">查看</button>
                  <button class="op-btn warning" v-if="device.status === 'warning'" @click="assignMaintenance(device)">维护</button>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- 分页控件 -->
          <div class="pagination-controls" v-if="filteredTotal > pagination.pageSize">
            <button
              class="pagination-btn"
              :disabled="pagination.currentPage === 1"
              @click="changePage(pagination.currentPage - 1)">
              上一页
            </button>
            <span class="pagination-info">
              {{ pagination.currentPage }} / {{ totalPages }} (共{{ filteredTotal }}条)
            </span>
            <button
              class="pagination-btn"
              :disabled="pagination.currentPage === totalPages"
              @click="changePage(pagination.currentPage + 1)">
              下一页
            </button>
          </div>
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
                  <button class="btn" @click="editProductionLine(line)">编辑</button>
                  <button class="btn danger" @click="deleteLine(line)">删除</button>
                </div>
              </div>
            </div>
            <button class="btn primary add-line" @click="showAddLineModal = true">新增产线</button>
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

      <!-- 新增产线模态框 -->
      <div class="modal" v-if="showAddLineModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>新增产线</h3>
            <span class="close-btn" @click="showAddLineModal = false">&times;</span>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>产线名称</label>
              <input type="text" v-model="newLine.name" class="form-input" placeholder="请输入产线名称">
            </div>
            <div class="form-group">
              <label>理论产能</label>
              <input type="number" v-model="newLine.theoretical_capacity" class="form-input" placeholder="请输入理论产能">
            </div>
            <div class="form-group">
              <label>选择管理工长</label>
              <select v-model="newLine.foreman_id" class="form-input">
                <option value="">请选择工长</option>
                <option v-for="manager in foremen" :key="manager.id" :value="manager.id">
                  {{ manager.name }}
                </option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn cancel" @click="showAddLineModal = false">取消</button>
            <button class="btn submit" @click="confirmAddLine">确定添加</button>
          </div>
        </div>
      </div>

      <!-- 编辑产线模态框 -->
      <div class="modal" v-if="showEditLineModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>编辑产线</h3>
            <span class="close-btn" @click="showEditLineModal = false">&times;</span>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>产线名称</label>
              <input type="text" v-model="editLine.name" class="form-input" placeholder="请输入产线名称">
            </div>
            <div class="form-group">
              <label>理论产能</label>
              <input type="number" v-model="editLine.theoretical_capacity" class="form-input" placeholder="请输入理论产能">
            </div>
            <div class="form-group">
              <label>选择管理工长</label>
              <select v-model="editLine.foreman_id" class="form-input">
                <option value="">请选择工长</option>
                <option v-for="manager in foremen" :key="manager.id" :value="manager.id">
                  {{ manager.name }}
                </option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn cancel" @click="showEditLineModal = false">取消</button>
            <button class="btn submit" @click="confirmEditLine">确定修改</button>
          </div>
        </div>
      </div>

      <!-- 设备配置模态框 -->
      <div class="modal" v-if="showEquipmentConfigModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>设备配置</h3>
            <span class="close-btn" @click="showEquipmentConfigModal = false">&times;</span>
          </div>
          <div class="modal-body">
            <div class="config-list">
              <div class="config-item" v-for="device in equipments" :key="device.id">
                <span class="device-name">{{ device.name }}</span>
                <div class="config-actions">
                  <button class="btn" @click="viewDeviceDetail(device)">查看</button>
                  <button class="btn" @click="editDevice(device)">编辑</button>
                  <button class="btn danger" @click="deleteDevice(device)">删除</button>
                </div>
              </div>
            </div>
            <button class="btn primary add-device" @click="showAddEquipmentModal = true">新增设备</button>
          </div>
        </div>
      </div>

      <!-- 编辑设备模态框 -->
      <div class="modal" v-if="showEditEquipmentModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>编辑设备</h3>
            <span class="close-btn" @click="showEditEquipmentModal = false">&times;</span>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>设备名称</label>
              <input type="text" v-model="editEquipment.name" class="form-input" placeholder="请输入设备名称">
            </div>
            <div class="form-group">
              <label>设备编码</label>
              <input type="text" v-model="editEquipment.code" class="form-input" placeholder="请输入设备编码">
            </div>
            <div class="form-group">
              <label>设备类型</label>
              <select v-model="editEquipment.type" class="form-input">
                <option value="生产设备">生产设备</option>
                <option value="检测设备">检测设备</option>
                <option value="辅助设备">辅助设备</option>
              </select>
            </div>
            <div class="form-group">
              <label>所属产线</label>
              <select v-model="editEquipment.line_id" class="form-input">
                <option value="">请选择产线</option>
                <option v-for="line in productionLines" :key="line.id" :value="line.id">
                  {{ line.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>设备位置</label>
              <input type="text" v-model="editEquipment.location" class="form-input" placeholder="请输入设备位置">
            </div>
            <div class="form-group">
              <label>设备描述</label>
              <textarea v-model="editEquipment.description" class="form-input" rows="3" placeholder="请输入设备描述"></textarea>
            </div>

            <div class="form-group">
              <label>传感器项目</label>
              <div class="sensor-projects-container">
                <h4>基本参数</h4>
                <div class="sensor-projects-group">
                  <div class="sensor-project-item">
                    <input type="checkbox" id="edit_temperature" v-model="editEquipment.sensorProjects.temperature">
                    <label for="edit_temperature">温度</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="edit_pressure" v-model="editEquipment.sensorProjects.pressure">
                    <label for="edit_pressure">压力</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="edit_vibration" v-model="editEquipment.sensorProjects.vibration">
                    <label for="edit_vibration">振动</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="edit_speed" v-model="editEquipment.sensorProjects.speed">
                    <label for="edit_speed">转速</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="edit_noise" v-model="editEquipment.sensorProjects.noise">
                    <label for="edit_noise">噪音</label>
                  </div>
                </div>

                <h4>电气参数</h4>
                <div class="sensor-projects-group">
                  <div class="sensor-project-item">
                    <input type="checkbox" id="edit_voltage" v-model="editEquipment.sensorProjects.voltage">
                    <label for="edit_voltage">电压</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="edit_current" v-model="editEquipment.sensorProjects.current">
                    <label for="edit_current">电流</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="edit_power" v-model="editEquipment.sensorProjects.power">
                    <label for="edit_power">功率</label>
                  </div>
                </div>

                <h4>环境参数</h4>
                <div class="sensor-projects-group">
                  <div class="sensor-project-item">
                    <input type="checkbox" id="edit_humidity" v-model="editEquipment.sensorProjects.humidity">
                    <label for="edit_humidity">湿度</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="edit_air_pressure" v-model="editEquipment.sensorProjects.air_pressure">
                    <label for="edit_air_pressure">气压</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="edit_light_intensity" v-model="editEquipment.sensorProjects.light_intensity">
                    <label for="edit_light_intensity">光强</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="edit_radiation" v-model="editEquipment.sensorProjects.radiation">
                    <label for="edit_radiation">辐射</label>
                  </div>
                </div>

                <h4>液体参数</h4>
                <div class="sensor-projects-group">
                  <div class="sensor-project-item">
                    <input type="checkbox" id="edit_flow_rate" v-model="editEquipment.sensorProjects.flow_rate">
                    <label for="edit_flow_rate">流量</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="edit_liquid_level" v-model="editEquipment.sensorProjects.liquid_level">
                    <label for="edit_liquid_level">液位</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="edit_concentration" v-model="editEquipment.sensorProjects.concentration">
                    <label for="edit_concentration">浓度</label>
                  </div>
                </div>

                <h4>机械参数</h4>
                <div class="sensor-projects-group">
                  <div class="sensor-project-item">
                    <input type="checkbox" id="edit_torque" v-model="editEquipment.sensorProjects.torque">
                    <label for="edit_torque">扭矩</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="edit_displacement" v-model="editEquipment.sensorProjects.displacement">
                    <label for="edit_displacement">位移</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="edit_weight" v-model="editEquipment.sensorProjects.weight">
                    <label for="edit_weight">重量</label>
                  </div>
                </div>

                <h4>自定义传感器项目</h4>
                <div class="custom-sensor-projects">
                  <div class="custom-sensor-input">
                    <input type="text" v-model="customSensorKey" placeholder="项目英文名称（如custom_temp）" class="form-input">
                    <input type="text" v-model="customSensorValue" placeholder="项目中文名称（如自定义温度）" class="form-input">
                    <button class="btn add-sensor" @click="addCustomSensor">添加</button>
                  </div>
                  <div class="custom-sensors-list" v-if="Object.keys(customSensors).length > 0">
                    <div v-for="(value, key) in customSensors" :key="key" class="custom-sensor-item">
                      <span>{{ key }}: {{ value }}</span>
                      <button class="btn remove-sensor" @click="removeCustomSensor(key)">删除</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn cancel" @click="showEditEquipmentModal = false">取消</button>
            <button class="btn submit" @click="confirmEditEquipment">保存</button>
          </div>
        </div>
      </div>

      <!-- 新增设备模态框 -->
      <div class="modal" v-if="showAddEquipmentModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>新增设备</h3>
            <span class="close-btn" @click="showAddEquipmentModal = false">&times;</span>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>设备名称</label>
              <input type="text" v-model="newEquipment.name" class="form-input" placeholder="请输入设备名称">
            </div>
            <div class="form-group">
              <label>设备编码</label>
              <input type="text" v-model="newEquipment.code" class="form-input" placeholder="请输入设备编码">
            </div>
            <div class="form-group">
              <label>设备类型</label>
              <select v-model="newEquipment.type" class="form-input">
                <option value="生产设备">生产设备</option>
                <option value="检测设备">检测设备</option>
                <option value="辅助设备">辅助设备</option>
              </select>
            </div>
            <div class="form-group">
              <label>所属产线</label>
              <select v-model="newEquipment.line_id" class="form-input">
                <option value="">请选择产线</option>
                <option v-for="line in productionLines" :key="line.id" :value="line.id">
                  {{ line.name }}
                </option>
              </select>
            </div>


            <div class="form-group">
              <label>传感器项目</label>
              <div class="sensor-projects-container">
                <h4>基本参数</h4>
                <div class="sensor-projects-group">
                  <div class="sensor-project-item">
                    <input type="checkbox" id="temperature" v-model="newEquipment.sensorProjects.temperature">
                    <label for="temperature">温度</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="pressure" v-model="newEquipment.sensorProjects.pressure">
                    <label for="pressure">压力</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="vibration" v-model="newEquipment.sensorProjects.vibration">
                    <label for="vibration">振动</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="speed" v-model="newEquipment.sensorProjects.speed">
                    <label for="speed">转速</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="noise" v-model="newEquipment.sensorProjects.noise">
                    <label for="noise">噪音</label>
                  </div>
                </div>

                <h4>电气参数</h4>
                <div class="sensor-projects-group">
                  <div class="sensor-project-item">
                    <input type="checkbox" id="voltage" v-model="newEquipment.sensorProjects.voltage">
                    <label for="voltage">电压</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="current" v-model="newEquipment.sensorProjects.current">
                    <label for="current">电流</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="power" v-model="newEquipment.sensorProjects.power">
                    <label for="power">功率</label>
                  </div>
                </div>

                <h4>环境参数</h4>
                <div class="sensor-projects-group">
                  <div class="sensor-project-item">
                    <input type="checkbox" id="humidity" v-model="newEquipment.sensorProjects.humidity">
                    <label for="humidity">湿度</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="air_pressure" v-model="newEquipment.sensorProjects.air_pressure">
                    <label for="air_pressure">气压</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="light_intensity" v-model="newEquipment.sensorProjects.light_intensity">
                    <label for="light_intensity">光强</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="radiation" v-model="newEquipment.sensorProjects.radiation">
                    <label for="radiation">辐射</label>
                  </div>
                </div>

                <h4>液体参数</h4>
                <div class="sensor-projects-group">
                  <div class="sensor-project-item">
                    <input type="checkbox" id="flow_rate" v-model="newEquipment.sensorProjects.flow_rate">
                    <label for="flow_rate">流量</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="liquid_level" v-model="newEquipment.sensorProjects.liquid_level">
                    <label for="liquid_level">液位</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="concentration" v-model="newEquipment.sensorProjects.concentration">
                    <label for="concentration">浓度</label>
                  </div>
                </div>

                <h4>机械参数</h4>
                <div class="sensor-projects-group">
                  <div class="sensor-project-item">
                    <input type="checkbox" id="torque" v-model="newEquipment.sensorProjects.torque">
                    <label for="torque">扭矩</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="displacement" v-model="newEquipment.sensorProjects.displacement">
                    <label for="displacement">位移</label>
                  </div>
                  <div class="sensor-project-item">
                    <input type="checkbox" id="weight" v-model="newEquipment.sensorProjects.weight">
                    <label for="weight">重量</label>
                  </div>
                </div>


                <h4>自定义传感器项目</h4>
                <div class="custom-sensor-projects">
                  <div class="custom-sensor-input">
                    <input type="text" v-model="customSensorKey" placeholder="项目英文名称（如custom_temp）" class="form-input">
                    <input type="text" v-model="customSensorValue" placeholder="项目中文名称（如自定义温度）" class="form-input">
                    <button class="btn add-sensor" @click="addCustomSensor">添加</button>
                  </div>
                  <div class="custom-sensors-list" v-if="Object.keys(customSensors).length > 0">
                    <div v-for="(value, key) in customSensors" :key="key" class="custom-sensor-item">
                      <span>{{ key }}: {{ value }}</span>
                      <button class="btn remove-sensor" @click="removeCustomSensor(key)">删除</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn cancel" @click="showAddEquipmentModal = false">取消</button>
            <button class="btn submit" @click="confirmAddEquipment">确定添加</button>
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
      // 自定义传感器项目
      customSensorKey: '',
      customSensorValue: '',
      customSensors: {},
      productionLines: [],
      showConfigModal: false,
      showEquipmentConfigModal: false,
      showAssignModal: false,
      showAddLineModal: false,
      showAddEquipmentModal: false,
      showEditEquipmentModal: false,
      showEditLineModal: false,
      selectedLine: {},
      selectedManager: '',
      foremen: [],
      workers: [],
      // 新增产线相关数据
      newLine: {
        name: '',
        theoretical_capacity: 1000,
        foreman_id: ''
      },
      // 编辑产线相关数据
      editLine: {
        id: '',
        name: '',
        theoretical_capacity: 1000,
        foreman_id: ''
      },
      // 编辑设备相关数据
      editEquipment: {
        id: '',
        name: '',
        code: '',
        type: '',
        line_id: '',
        location: '',
        description: '',
        sensorProjects: {
          temperature: false,
          pressure: false,
          vibration: false,
          speed: false,
          voltage: false,
          current: false,
          power: false,
          noise: false,
          humidity: false,
          flow_rate: false,
          liquid_level: false,
          air_pressure: false,
          torque: false,
          displacement: false,
          weight: false,
          concentration: false,
          light_intensity: false,
          radiation: false,
          runtime: false,
          output: false
        }
      },
      // 新增设备相关数据
      newEquipment: {
        name: '',
        code: '',
        type: '生产设备',
        line_id: '',
        sensorProjects: {
          temperature: true,
          pressure: false,
          vibration: false,
          speed: false,
          voltage: false,
          current: false,
          power: false,
          noise: false,
          humidity: false,
          flow_rate: false,
          liquid_level: false,
          air_pressure: false,
          torque: false,
          displacement: false,
          weight: false,
          concentration: false,
          light_intensity: false,
          radiation: false,
          runtime: false,
          output: false
        }
      },
      // 设备监控相关数据
      equipmentFilter: {
        line: '',
        status: '',
        type: ''
      },
      equipments: [],
      // 分页相关数据
      pagination: {
        currentPage: 1,
        pageSize: 10,
        total: 0
      },
      // 错误和加载状态
      loading: {
        productionLines: false,
        equipments: false,
        foremen: false,
        workers: false
      },
      error: {
        productionLines: null,
        equipments: null,
        foremen: null,
        workers: null
      },
      // 缓存数据
      cachedData: {
        equipments: null,
        timestamp: null
      },
      // 自动刷新相关
      autoRefresh: true,
      refreshInterval: null,
      refreshRate: 10000, // 10秒更新一次
      lastUpdateTime: ''
    }
  },
  computed: {
    // 根据筛选条件过滤设备
    filteredEquipments() {
      // 先过滤所有设备
      const filtered = this.equipments.filter(equipment => {
        // 按产线筛选
        const lineMatch = !this.equipmentFilter.line ||
          String(equipment.productionLine).includes(this.productionLines.find(l => l.id === this.equipmentFilter.line)?.name || '');

        // 按状态筛选
        const statusMatch = !this.equipmentFilter.status ||
          equipment.status === this.equipmentFilter.status;

        // 按类型筛选
        const typeMatch = !this.equipmentFilter.type ||
          equipment.type === this.equipmentFilter.type;

        return lineMatch && statusMatch && typeMatch;
      });

      // 计算分页起始和结束索引
      const start = (this.pagination.currentPage - 1) * this.pagination.pageSize;
      const end = start + this.pagination.pageSize;

      // 返回当前页的数据
      return filtered.slice(start, end);
    },

    // 过滤后的总数
    filteredTotal() {
      return this.equipments.filter(equipment => {
        const lineMatch = !this.equipmentFilter.line ||
          String(equipment.productionLine).includes(this.productionLines.find(l => l.id === this.equipmentFilter.line)?.name || '');
        const statusMatch = !this.equipmentFilter.status ||
          equipment.status === this.equipmentFilter.status;
        const typeMatch = !this.equipmentFilter.type ||
          equipment.type === this.equipmentFilter.type;
        return lineMatch && statusMatch && typeMatch;
      }).length;
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
    },

    // 计算总页数
    totalPages() {
      return Math.ceil(this.filteredTotal / this.pagination.pageSize);
    }
  },
  created() {
    this.fetchProductionLines();
    this.fetchEquipments();
    this.fetchForemen();
    this.fetchWorkers();

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
    // 获取产线数据
    // 开始自动刷新
    startAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
      }

      if (this.autoRefresh) {
        console.log('开始自动刷新，间隔:', this.refreshRate, '毫秒');
        this.refreshInterval = setInterval(() => {
          console.log('触发自动刷新事件');
          this.fetchProductionLines();
          this.fetchEquipments();
        }, this.refreshRate);
      }
    },

    // 停止自动刷新
    stopAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
        this.refreshInterval = null;
      }
    },

    // 切换自动刷新状态
    toggleAutoRefresh() {
      this.autoRefresh = !this.autoRefresh;
      if (this.autoRefresh) {
        this.startAutoRefresh();
      } else {
        this.stopAutoRefresh();
      }
    },

    async fetchProductionLines() {
      // 不设置loading状态，避免显示加载界面
      // this.loading.productionLines = true;
      this.error.productionLines = null;

      try {
        const response = await fetch('/api/production_line/with-foremen', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取产线数据失败: ${response.status}`);
        }

        const result = await response.json();

        if (result.success && result.data) {
          // 处理产线数据
          const updatedLines = result.data.map(line => {
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

            // 保存原始数据库状态值供下拉菜单使用

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
              dbStatus: line.status || '正常', // 原始数据库状态值
              utilization: utilization,
              output: Math.round(line.real_time_capacity || 0),
              target: line.theoretical_capacity || 1000,
              runtime: line.runtime_hours || 0,
              equipment_list: line.equipment_list || [],
              foreman: foreman
            };
          });

          // 更新产线数据
          this.productionLines = updatedLines;

          // 更新状态卡片的数据
          this.updateStatusCards();

          // 更新最后更新时间
          this.lastUpdateTime = new Date().toLocaleTimeString();
        } else {
          throw new Error(result.error || '未知错误');
        }
      } catch (error) {
        this.error.productionLines = error.message || '获取产线数据出错';
        // 只在没有产线数据时才清空
        if (this.productionLines.length === 0) {
          this.productionLines = [];
        }
      }
      // 不需要设置loading状态
      // finally {
      //   this.loading.productionLines = false;
      // }
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

    editProductionLine(line) {
      // 初始化编辑表单
      this.editLine = {
        id: line.id,
        name: line.name,
        theoretical_capacity: line.target || 1000,
        foreman_id: line.foreman ? line.foreman.id : ''
      };

      // 显示编辑模态框
      this.showEditLineModal = true;

      // 确保工长列表已加载
      if (!this.foremen || this.foremen.length === 0) {
        this.fetchForemen();
      }
    },

    // 确认编辑产线
    async confirmEditLine() {
      // 验证表单
      if (!this.editLine.name) {
        alert('请输入产线名称');
        return;
      }

      if (!this.editLine.theoretical_capacity || this.editLine.theoretical_capacity <= 0) {
        alert('请输入有效的理论产能');
        return;
      }

      try {
        // 准备产线数据
        const lineData = {
          line_name: this.editLine.name,
          theoretical_capacity: this.editLine.theoretical_capacity,
          foreman_id: this.editLine.foreman_id || null
        };

        // 调用API更新产线
        const response = await fetch('/api/production_line/update', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            line_id: this.editLine.id,
            line_data: lineData
          })
        });

        const result = await response.json();

        if (result.success) {
          alert('产线信息更新成功！');
          // 重新加载产线数据
          this.fetchProductionLines();
          // 关闭模态框
          this.showEditLineModal = false;
        } else {
          alert(`更新失败: ${result.error || '未知错误'}`);
        }
      } catch (error) {
        console.error('编辑产线出错:', error);
        alert(`编辑产线出错: ${error.message || '未知错误'}`);
      }
    },

    deleteLine(line) {
      if(confirm(`确定要删除产线 ${line.name} 吗？删除后无法恢复，且产线上不能有设备。`)) {
        this.deleteProductionLine(line);
      }
    },

    async deleteProductionLine(line) {
      try {
        // 调用API删除产线
        const response = await fetch(`/api/production_line/delete/${line.id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        const result = await response.json();

        if (result.success) {
          alert(`产线 ${line.name} 删除成功！`);
          // 重新加载产线数据
          this.fetchProductionLines();
        } else {
          alert(`删除失败: ${result.error || '未知错误'}`);
        }
      } catch (error) {
        console.error('删除产线出错:', error);
        alert(`删除产线出错: ${error.message || '未知错误'}`);
      }
    },

    // 编辑设备
    editDevice(device) {
      // 清空自定义传感器项目
      this.customSensors = {};
      this.customSensorKey = '';
      this.customSensorValue = '';

      // 初始化传感器项目
      const sensorProjects = {
        temperature: false,
        pressure: false,
        vibration: false,
        speed: false,
        voltage: false,
        current: false,
        power: false,
        noise: false,
        humidity: false,
        flow_rate: false,
        liquid_level: false,
        air_pressure: false,
        torque: false,
        displacement: false,
        weight: false,
        concentration: false,
        light_intensity: false,
        radiation: false,
        runtime: false,
        output: false
      };

      // 如果设备有传感器项目数据，则加载
      if (device.sensor_projects && typeof device.sensor_projects === 'object') {
        // 处理预设传感器项目
        const sensorNameMap = {
          '温度': 'temperature',
          '压力': 'pressure',
          '振动': 'vibration',
          '转速': 'speed',
          '电压': 'voltage',
          '电流': 'current',
          '功率': 'power',
          '噪音': 'noise',
          '湿度': 'humidity',
          '流量': 'flow_rate',
          '液位': 'liquid_level',
          '气压': 'air_pressure',
          '扭矩': 'torque',
          '位移': 'displacement',
          '重量': 'weight',
          '浓度': 'concentration',
          '光强': 'light_intensity',
          '辐射': 'radiation',
          '运行时间': 'runtime',
          '产量': 'output'
        };

        // 遍历设备的传感器项目
        for (const [key, value] of Object.entries(device.sensor_projects)) {
          // 检查是否是预设项目
          const englishKey = sensorNameMap[value];
          if (englishKey && Object.prototype.hasOwnProperty.call(sensorProjects, englishKey)) {
            // 设置预设项目为选中
            sensorProjects[englishKey] = true;
          } else {
            // 添加为自定义项目
            this.$set(this.customSensors, key, value);
          }
        }
      }

      // 初始化编辑表单
      this.editEquipment = {
        id: device.id,
        name: device.name,
        code: device.code || '',
        type: device.typeText || '生产设备',
        line_id: device.line_id || '',
        location: device.location || '',
        description: device.description || '',
        sensorProjects: sensorProjects
      };

      // 显示编辑模态框
      this.showEditEquipmentModal = true;
    },

    // 确认编辑设备
    async confirmEditEquipment() {
      try {
        // 验证表单
        if (!this.editEquipment.name) {
          alert('请输入设备名称');
          return;
        }

        if (!this.editEquipment.code) {
          alert('请输入设备编码');
          return;
        }

        if (!this.editEquipment.line_id) {
          alert('请选择所属产线');
          return;
        }

        // 处理传感器项目数据
        const sensorProjects = {};
        const sensorNameMap = {
          temperature: '温度',
          pressure: '压力',
          vibration: '振动',
          speed: '转速',
          voltage: '电压',
          current: '电流',
          power: '功率',
          noise: '噪音',
          humidity: '湿度',
          flow_rate: '流量',
          liquid_level: '液位',
          air_pressure: '气压',
          torque: '扭矩',
          displacement: '位移',
          weight: '重量',
          concentration: '浓度',
          light_intensity: '光强',
          radiation: '辐射',
          runtime: '运行时间',
          output: '产量'
        };

        // 处理预设传感器项目
        for (const [key, value] of Object.entries(this.editEquipment.sensorProjects)) {
          if (value && sensorNameMap[key]) {
            // 只保存选中的传感器项目
            sensorProjects[key] = sensorNameMap[key];
          }
        }

        // 处理自定义传感器项目
        for (const [key, value] of Object.entries(this.customSensors)) {
          sensorProjects[key] = value;
        }

        // 准备请求数据
        const equipmentData = {
          equipment_name: this.editEquipment.name,
          equipment_code: this.editEquipment.code,
          equipment_type: this.editEquipment.type,
          line_id: this.editEquipment.line_id,
          location: this.editEquipment.location || '',
          description: this.editEquipment.description || '',
          sensor_projects: sensorProjects // 添加传感器项目数据
        };

        // 发送请求
        const response = await fetch('/api/equipment/update', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            equipment_id: this.editEquipment.id,
            equipment_data: equipmentData
          })
        });

        const result = await response.json();

        if (result.success) {
          alert('设备信息更新成功！');
          // 重新加载设备数据
          this.fetchEquipments(true);
          // 关闭模态框
          this.showEditEquipmentModal = false;
        } else {
          alert(`更新失败: ${result.error || '未知错误'}`);
        }
      } catch (error) {
        console.error('编辑设备出错:', error);
        alert(`编辑设备出错: ${error.message || '未知错误'}`);
      }
    },

    deleteDevice(device) {
      if(confirm(`确定要删除设备 ${device.name} 吗？删除后无法恢复。`)) {
        this.deleteEquipment(device);
      }
    },

    async deleteEquipment(device) {
      try {
        // 调用API删除设备
        const response = await fetch(`/api/equipment/delete/${device.id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        const result = await response.json();

        if (result.success) {
          alert(`设备 ${device.name} 删除成功！`);
          // 重新加载设备数据
          this.fetchEquipments(true);
          // 关闭模态框
          this.showEquipmentConfigModal = false;
        } else {
          alert(`删除失败: ${result.error || '未知错误'}`);
        }
      } catch (error) {
        console.error('删除设备出错:', error);
        alert(`删除设备出错: ${error.message || '未知错误'}`);
      }
    },

    // 重置新增产线表单
    resetNewLineForm() {
      this.newLine = {
        name: '',
        theoretical_capacity: 1000,
        foreman_id: ''
      };
    },

    // 添加自定义传感器项目
    addCustomSensor() {
      if (!this.customSensorKey || !this.customSensorValue) {
        alert('请输入项目英文名称和中文名称');
        return;
      }

      // 检查英文名称格式
      if (!/^[a-z][a-z0-9_]*$/.test(this.customSensorKey)) {
        alert('项目英文名称必须以小写字母开头，只能包含小写字母、数字和下划线');
        return;
      }

      // 检查是否与预设项目重名
      const presetKeys = [
        'temperature', 'pressure', 'vibration', 'speed', 'voltage', 'current', 'power',
        'noise', 'humidity', 'flow_rate', 'liquid_level', 'air_pressure', 'torque',
        'displacement', 'weight', 'concentration', 'light_intensity', 'radiation',
        'runtime', 'output'
      ];

      if (presetKeys.includes(this.customSensorKey)) {
        alert('项目英文名称与预设项目重名，请使用其他名称');
        return;
      }

      // 检查是否与已添加的自定义项目重名
      if (this.customSensors[this.customSensorKey]) {
        alert('项目英文名称已存在，请使用其他名称');
        return;
      }

      // 添加自定义传感器项目
      this.$set(this.customSensors, this.customSensorKey, this.customSensorValue);

      // 清空输入框
      this.customSensorKey = '';
      this.customSensorValue = '';
    },

    // 删除自定义传感器项目
    removeCustomSensor(key) {
      this.$delete(this.customSensors, key);
    },

    // 重置新增设备表单
    resetNewEquipmentForm() {
      // 清空自定义传感器项目
      this.customSensors = {};
      this.customSensorKey = '';
      this.customSensorValue = '';

      this.newEquipment = {
        name: '',
        code: '',
        type: '生产设备',
        line_id: '',
        sensorProjects: {
          temperature: true,
          pressure: false,
          vibration: false,
          speed: false,
          voltage: false,
          current: false,
          power: false,
          noise: false,
          humidity: false,
          flow_rate: false,
          liquid_level: false,
          air_pressure: false,
          torque: false,
          displacement: false,
          weight: false,
          concentration: false,
          light_intensity: false,
          radiation: false,
          runtime: false,
          output: false
        }
      };
    },

    // 确认添加产线
    async confirmAddLine() {
      // 验证表单
      if (!this.newLine.name) {
        alert('请输入产线名称');
        return;
      }

      if (!this.newLine.theoretical_capacity || this.newLine.theoretical_capacity <= 0) {
        alert('请输入有效的理论产能');
        return;
      }

      try {
        // 准备产线数据
        const lineData = {
          line_name: this.newLine.name,
          theoretical_capacity: this.newLine.theoretical_capacity,
          foreman_id: this.newLine.foreman_id || null,
          status: '正常' // 默认状态为正常
        };

        // 调用API添加产线
        const response = await fetch('/api/production_line/add', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(lineData)
        });

        const result = await response.json();

        if (result.success) {
          alert('产线添加成功！');
          // 重新加载产线数据
          this.fetchProductionLines();
          // 重置表单并关闭模态框
          this.resetNewLineForm();
          this.showAddLineModal = false;
        } else {
          alert(`添加失败: ${result.error || '未知错误'}`);
        }
      } catch (error) {
        console.error('添加产线出错:', error);
        alert(`添加产线出错: ${error.message || '未知错误'}`);
      }
    },

    // 确认添加设备
    async confirmAddEquipment() {
      // 验证表单
      if (!this.newEquipment.name) {
        alert('请输入设备名称');
        return;
      }

      if (!this.newEquipment.code) {
        alert('请输入设备编码');
        return;
      }

      if (!this.newEquipment.line_id) {
        alert('请选择所属产线');
        return;
      }

      try {
        // 准备设备数据
        // 处理传感器项目数据
        const sensorProjects = {};
        const sensorNameMap = {
          temperature: '温度',
          pressure: '压力',
          vibration: '振动',
          speed: '转速',
          voltage: '电压',
          current: '电流',
          power: '功率',
          noise: '噪音',
          humidity: '湿度',
          flow_rate: '流量',
          liquid_level: '液位',
          air_pressure: '气压',
          torque: '扭矩',
          displacement: '位移',
          weight: '重量',
          concentration: '浓度',
          light_intensity: '光强',
          radiation: '辐射',
          runtime: '运行时间',
          output: '产量'
        };

        // 处理预设传感器项目
        for (const [key, value] of Object.entries(this.newEquipment.sensorProjects)) {
          if (value && sensorNameMap[key]) {
            // 只保存选中的传感器项目
            sensorProjects[key] = sensorNameMap[key];
          }
        }

        // 处理自定义传感器项目
        for (const [key, value] of Object.entries(this.customSensors)) {
          sensorProjects[key] = value;
        }

        const equipmentData = {
          equipment_name: this.newEquipment.name,
          equipment_code: this.newEquipment.code,
          equipment_type: this.newEquipment.type,
          line_id: this.newEquipment.line_id,
          status: '正常', // 默认状态为正常
          sensor_projects: sensorProjects // 添加传感器项目数据
        };

        // 调用API添加设备
        const response = await fetch('/api/equipment/add', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(equipmentData)
        });

        const result = await response.json();

        if (result.success) {
          alert('设备添加成功！');
          // 重新加载设备数据
          this.fetchEquipments(true);
          // 重置表单并关闭模态框
          this.resetNewEquipmentForm();
          this.showAddEquipmentModal = false;
        } else {
          alert(`添加失败: ${result.error || '未知错误'}`);
        }
      } catch (error) {
        console.error('添加设备出错:', error);
        alert(`添加设备出错: ${error.message || '未知错误'}`);
      }
    },
    assignManager(line) {
      this.selectedLine = line;
      this.showAssignModal = true;
      // 确保工长列表已加载
      if (!this.foremen || this.foremen.length === 0) {
        this.fetchForemen();
      }
    },
    viewDetails(line) {
      // 使用导航辅助函数跳转到产线详情页面
      import('@/utils/navigationHelper').then(({ navigateWithUid }) => {
        navigateWithUid(this.$router, `/supervisor/production-line-detail/${line.id}`);
      });
    },


    async confirmAssign() {
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

        const result = await response.json();

        if (result.success) {
          alert('工长分配成功！');
          // 重新加载产线数据
          this.fetchProductionLines();
        } else {
          alert(`分配失败: ${result.error || '未知错误'}`);
        }
      } catch (error) {
        alert('分配失败，请重试');
      }

      this.showAssignModal = false;
      this.selectedManager = '';
    },
    // 查看设备详情
    viewDeviceDetail(device) {
      // 使用导航辅助函数跳转到设备详情页面
      import('@/utils/navigationHelper').then(({ navigateWithUid }) => {
        navigateWithUid(this.$router, `/supervisor/equipment-detail/${device.id}`);
      });
    },

    // 更新产线状态
    async updateLineStatus(line) {
      try {

        console.log(`更新产线 ${line.id} 状态为: ${line.dbStatus}`);

        // 准备状态数据
        const lineData = {
          status: line.dbStatus
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
          alert(`产线 ${line.name} 状态已更新为 ${line.dbStatus}`);
        } else {
          alert(`更新产线状态失败: ${result.error || '未知错误'}`);
        }
      } catch (error) {
        console.error('更新产线状态出错:', error);
        alert(`更新产线状态出错: ${error.message || '未知错误'}`);
      }
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
          // 更新成功，强制刷新数据
          await this.fetchEquipments(true); // 使用forceRefresh参数强制刷新设备数据

          // 直接更新当前设备的状态显示，确保界面立即反映变化
          const updatedDevice = this.equipments.find(d => d.id === device.id);
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

    // 设置产线状态
    setLineStatus(line, status) {
      // 检查当前状态是否允许修改
      if (line.dbStatus === '故障' || line.dbStatus === '维修中') {
        alert(`无法将产线状态修改为 ${status}，当前状态不允许手动设置。`);
        return;
      }

      // 如果当前状态是预警，只能改为停机
      if (line.dbStatus === '预警' && status !== '停机') {
        alert('预警状态下只能将产线设置为停机状态。');
        return;
      }

      // 设置新状态
      line.dbStatus = status;

      // 调用更新方法
      this.updateLineStatus(line);
    },

    // 设置设备状态
    setDeviceStatus(device, status) {
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

    // 获取产线状态说明
    getStatusNote(line) {
      if (line.dbStatus === '故障') {
        return '故障状态由系统自动检测，无法手动修改';
      } else if (line.dbStatus === '预警') {
        return '预警状态由系统自动检测，可停机处理';
      } else if (line.dbStatus === '维修中') {
        return '维修中状态由安全员设置，无法手动修改';
      }
      return '';
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

    // 分配维护任务
    assignMaintenance(device) {
      // 这里可以增加设备维护任务分配的逻辑
      alert(`为设备 ${device.name} 分配维护任务`);
    },

    // 获取工长列表
    async fetchForemen() {
      this.loading.foremen = true;
      this.error.foremen = null;

      try {
        const response = await fetch('/api/users/foremen', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取工长列表失败: ${response.status}`);
        }

        const result = await response.json();

        if (result.success && result.data) {
          this.foremen = result.data.map(foreman => ({
            id: foreman.id,  // 这里的id是employee_id
            name: foreman.name
          }));
        } else {
          throw new Error(result.error || '获取工长列表失败');
        }
      } catch (error) {
        this.error.foremen = error.message || '获取工长列表出错';
        this.foremen = []; // 清空工长列表
      } finally {
        this.loading.foremen = false;
      }
    },

    // 获取工人列表
    async fetchWorkers() {
      this.loading.workers = true;
      this.error.workers = null;

      try {
        const response = await fetch('/api/users/workers', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取工人列表失败: ${response.status}`);
        }

        const result = await response.json();

        if (result.success && result.data) {
          this.workers = result.data.map(worker => ({
            id: worker.id,  // 这里的id是employee_id
            name: worker.name
          }));
        } else {
          throw new Error(result.error || '获取工人列表失败');
        }
      } catch (error) {
        this.error.workers = error.message || '获取工人列表出错';
        this.workers = []; // 清空工人列表
      } finally {
        this.loading.workers = false;
      }
    },

    // 获取设备数据
    async fetchEquipments(forceRefresh = false) {
      // 不设置loading状态，避免显示加载界面
      // this.loading.equipments = true;
      this.error.equipments = null;

      try {
        // 检查缓存是否有效（缓存时间30秒）
        const now = Date.now();
        if (!forceRefresh && this.cachedData.equipments && this.cachedData.timestamp &&
            (now - this.cachedData.timestamp < 30000)) {
          // 使用缓存数据，但不设置loading状态
          this.equipments = this.cachedData.equipments;
          return;
        }

        // 确保先获取产线数据
        if (this.productionLines.length === 0) {
          await this.fetchProductionLines();
        }

        // 并行获取设备数据和用户数据
        const [equipmentResponse, usersResponse] = await Promise.all([
          fetch('/api/equipment/with-status', {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          }),
          fetch('/api/users', {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          })
        ]);

        if (!equipmentResponse.ok) {
          throw new Error(`获取设备数据失败: ${equipmentResponse.status}`);
        }

        const result = await equipmentResponse.json();

        // 处理用户数据
        let users = [];
        if (usersResponse.ok) {
          const usersResult = await usersResponse.json();
          if (usersResult.success && usersResult.data) {
            users = usersResult.data;
          }
        }

        // 创建产线映射表，提高查询效率
        const lineMap = {};
        this.productionLines.forEach(line => {
          lineMap[line.id] = line.name || line.line_name;
        });

        // 创建用户映射表，提高查询效率
        const userMap = {};
        users.forEach(user => {
          userMap[user.id] = user.name || user.username;
        });

        if (result.success && result.data) {
          // 处理设备数据
          const processedEquipments = result.data.map(device => {
            // 获取设备状态
            let status = 'running';
            if (device.status === '故障') status = 'stopped';
            else if (device.status === '停机') status = 'stopped';
            else if (device.status === '维修中') status = 'warning';
            else if (device.status === '预警') status = 'warning';

            // 获取设备状态文本
            let statusText = '运行中';
            if (device.status === '预警') statusText = '预警';
            else if (device.status === '维修中') statusText = '维修中';
            else if (device.status === '故障') statusText = '故障';
            else if (device.status === '停机') statusText = '已停机';

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

            // 使用映射表获取产线名称
            const productionLine = lineMap[device.line_id] || '未知产线';

            // 使用映射表获取负责人名称
            const manager = device.worker_id ? (userMap[device.worker_id] || device.worker_id) : '未分配';

            return {
              id: device.id,
              name: device.equipment_name,
              code: device.equipment_code,
              type: type,
              typeText: typeText,
              productionLine: productionLine,
              status: status,
              statusText: statusText,
              dbStatus: device.status || '正常', // 原始数据库状态值
              runtime: device.runtime_hours || 0,
              manager: manager,
              lastMaintenance: device.updated_at ? new Date(device.updated_at).toISOString().split('T')[0] : '未知',
              sensorData: device.sensor_data || {},
              faultProbability: device.fault_probability || 0
            };
          });

          // 更新数据和缓存
          this.equipments = processedEquipments;
          this.cachedData.equipments = processedEquipments;
          this.cachedData.timestamp = now;

          // 重置分页到第一页
          this.pagination.currentPage = 1;
          this.pagination.total = processedEquipments.length;
        } else {
          throw new Error(result.error || '未知错误');
        }
      } catch (error) {
        this.error.equipments = error.message || '获取设备数据出错';
        // 只在没有设备数据时才清空
        if (this.equipments.length === 0) {
          this.equipments = [];
        }
      }
      // 不需要设置loading状态
      // finally {
      //   this.loading.equipments = false;
      // }
    },

    // 切换页面
    changePage(page) {
      if (page < 1 || page > this.totalPages) return;
      this.pagination.currentPage = page;
    }
  }
}
</script>

<style scoped>
/* 分页控件样式 */
.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  padding: 10px 0;
}

.pagination-btn {
  padding: 6px 12px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin: 0 5px;
}

.pagination-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.pagination-info {
  margin: 0 15px;
  font-size: 14px;
  color: #666;
}
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

.status-control {
  display: flex;
  align-items: center;
  gap: 10px;
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

.header-actions {
  display: flex;
  gap: 10px;
}

.refresh-control {
  display: flex;
  align-items: center;
  gap: 10px;
}

.last-update {
  font-size: 14px;
  color: #666;
}

.refresh-btn {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #f5f5f5;
  cursor: pointer;
  font-size: 14px;
}

.refresh-btn.auto-refresh {
  background-color: #e3f2fd;
  color: #2196F3;
  border-color: #2196F3;
}

.refresh-icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  margin-right: 5px;
  background-color: #666;
  mask-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>');
  mask-repeat: no-repeat;
  mask-position: center;
  mask-size: contain;
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

.settings-icon,
.config-icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  background-color: white;
  mask-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" /></svg>');
  mask-repeat: no-repeat;
  mask-position: center;
}

.add-icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  background-color: white;
  mask-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 3a1 1 0 00-1 1v5H4a1 1 0 100 2h5v5a1 1 0 102 0v-5h5a1 1 0 100-2h-5V4a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>');
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

.line-name,
.device-name {
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

.status-select {
  padding: 3px 6px;
  border-radius: 4px;
  border: 1px solid #d9d9d9;
  background-color: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.status-select:hover {
  border-color: #1890ff;
}

.status-note {
  font-size: 12px;
  color: #ff4d4f;
  margin-left: 10px;
  font-style: italic;
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

/* 设备状态标签样式 */
.status-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-tag.running {
  background-color: #e8f5e9;
  color: #4CAF50;
}

.status-tag.warning {
  background-color: #fff3e0;
  color: #ff9800;
}

.status-tag.stopped {
  background-color: #ffebee;
  color: #f44336;
}

/* 传感器项目选择区域样式 */
.sensor-projects-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 5px;
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
}

.sensor-projects-container h4 {
  margin: 10px 0 5px 0;
  font-size: 14px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}

.sensor-projects-group {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 10px;
}

.sensor-project-item {
  display: flex;
  align-items: center;
  gap: 5px;
  min-width: 100px;
}

.sensor-project-item input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.sensor-project-item label {
  cursor: pointer;
  font-size: 14px;
}

/* 自定义传感器项目样式 */
.custom-sensor-projects {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.custom-sensor-input {
  display: flex;
  gap: 10px;
  align-items: center;
}

.custom-sensor-input .form-input {
  flex: 1;
  height: 32px;
}

.custom-sensor-input .btn.add-sensor {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.custom-sensors-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 10px;
  padding: 10px;
  border: 1px dashed #ddd;
  border-radius: 4px;
}

.custom-sensor-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.custom-sensor-item .btn.remove-sensor {
  background-color: #f44336;
  color: white;
  border: none;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
}
</style>
