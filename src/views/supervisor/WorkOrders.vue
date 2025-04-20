<template>
  <div class="workorders">
    <header class="header">
      <h1>工单管理</h1>
    </header>

    <div class="content">
      <!-- 工单统计卡片 -->
      <div class="stat-cards">
        <div class="stat-card">
          <h3>待处理工单</h3>
          <div class="count pending">{{ pendingCount }}</div>
        </div>
        <div class="stat-card">
          <h3>处理中工单</h3>
          <div class="count processing">{{ processingCount }}</div>
        </div>
        <div class="stat-card">
          <h3>已完成工单</h3>
          <div class="count completed">{{ completedCount }}</div>
        </div>
      </div>

      <!-- 工单筛选区和操作区 -->
      <div class="filter-action-bar">
        <div class="filter-bar">
          <select v-model="filterType" class="filter-select">
            <option value="all">全部工单</option>
            <option value="设备维护">设备维护</option>
            <option value="产线巡检">产线巡检</option>
            <option value="排班任务">排班任务</option>
          </select>
          <select v-model="filterStatus" class="filter-select">
            <option value="all">全部状态</option>
            <option value="未接受">未接受</option>
            <option value="进行中">进行中</option>
            <option value="已完成">已完成</option>
            <option value="已取消">已取消</option>
          </select>
          <input
            type="text"
            v-model="searchKeyword"
            class="search-input"
            placeholder="搜索工单编号/提交人"
          >
        </div>
        <div class="action-buttons">
          <button class="create-btn" @click="showCreateWorkOrderModal = true">
            <i class="plus-icon">+</i> 创建工单
          </button>
          <button class="emergency-btn" @click="showEmergencyWorkOrderModal = true">
            <i class="emergency-icon">⚡</i> 发放紧急工单
          </button>
        </div>
      </div>

      <!-- 加载状态 -->
      <div class="loading-container" v-if="loading">
        <div class="loading-spinner"></div>
        <p>正在加载工单数据...</p>
      </div>

      <!-- 空数据提示 -->
      <div class="empty-container" v-else-if="workorders.length === 0">
        <p>暂无工单数据</p>
      </div>

      <!-- 工单列表 -->
      <div class="workorder-list" v-else>
        <div class="workorder-item" v-for="item in filteredWorkorders" :key="item.id">
          <div class="workorder-header">
            <span class="workorder-number">{{ item.number }}</span>
            <span :class="['workorder-status', item.status]">{{ item.status }}</span>
          </div>
          <div class="workorder-content">
            <h3>
              <span class="emergency-badge" v-if="item.extension_fields && item.extension_fields.is_emergency">⚡ 紧急</span>
              {{ item.title }}
            </h3>
            <p class="description">{{ item.description }}</p>
            <div class="workorder-info">
              <span>类型：{{ item.typeText }}</span>
              <span>位置：{{ item.location }}</span>
            </div>
            <div class="workorder-meta">
              <span>提交人：{{ item.submitter_name || item.submitter }} ({{ item.submitter }})</span>
              <span>提交时间：{{ item.submitTime }}</span>
            </div>
            <div class="workorder-handler" v-if="item.handler">
              <span>处理人：{{ item.handler_name || item.handler }} ({{ item.handler }})</span>
              <span>更新时间：{{ item.updateTime }}</span>
            </div>
            <div class="workorder-actions">
              <button class="detail-btn" @click="viewWorkOrderDetail(item)">查看详情</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <SupervisorNav />

    <!-- 工单详情模态框 -->
    <div class="modal" v-if="showDetailModal" @click.self="closeDetailModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>工单详情</h2>
          <button class="close-btn" @click="closeDetailModal">&times;</button>
        </div>
        <!-- 详情加载状态 -->
        <div class="modal-body loading-container" v-if="detailLoading">
          <div class="loading-spinner"></div>
          <p>正在加载工单详情...</p>
        </div>

        <!-- 详情内容 -->
        <div class="modal-body" v-else-if="selectedWorkOrder">
          <div class="detail-item">
            <label>工单编号</label>
            <div class="value">{{ selectedWorkOrder.number }}</div>
          </div>
          <div class="detail-item">
            <label>工单状态</label>
            <div class="value">
              <span class="status-tag" :class="selectedWorkOrder.status">
                {{ selectedWorkOrder.status }}
              </span>
            </div>
          </div>
          <div class="detail-item">
            <label>任务类型</label>
            <div class="value">{{ selectedWorkOrder.typeText }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkOrder.extension_fields && selectedWorkOrder.extension_fields.is_emergency">
            <label>紧急工单</label>
            <div class="value">
              <span class="emergency-badge">⚡ 紧急</span>
            </div>
          </div>
          <div class="detail-item">
            <label>任务描述</label>
            <div class="value description">{{ selectedWorkOrder.description }}</div>
          </div>
          <div class="detail-item">
            <label>产线信息</label>
            <div class="value">{{ selectedWorkOrder.location }}</div>
          </div>
          <div class="detail-item">
            <label>发出人</label>
            <div class="value">{{ selectedWorkOrder.creator_name || selectedWorkOrder.submitter }} ({{ selectedWorkOrder.submitter }})</div>
          </div>
          <div class="detail-item">
            <label>负责工长</label>
            <div class="value">{{ selectedWorkOrder.foreman ? (selectedWorkOrder.foreman_name || selectedWorkOrder.foreman) + ' (' + selectedWorkOrder.foreman + ')' : '未指定' }}</div>
          </div>
          <div class="detail-item">
            <label>负责班组</label>
            <div class="value">{{ selectedWorkOrder.team || '未指定' }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkOrder.handler">
            <label>负责组员</label>
            <div class="value">{{ selectedWorkOrder.team_member_name || selectedWorkOrder.handler }} ({{ selectedWorkOrder.handler }})</div>
          </div>
          <div class="detail-item">
            <label>创建时间</label>
            <div class="value">{{ selectedWorkOrder.submitTime }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkOrder.updateTime">
            <label>更新时间</label>
            <div class="value">{{ selectedWorkOrder.updateTime }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkOrder.startTime">
            <label>开始时间</label>
            <div class="value">{{ selectedWorkOrder.startTime }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkOrder.deadline">
            <label>截止时间</label>
            <div class="value">{{ selectedWorkOrder.deadline }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkOrder.actualEndTime">
            <label>实际结束时间</label>
            <div class="value">{{ selectedWorkOrder.actualEndTime }}</div>
          </div>

          <!-- 扩展字段显示 -->
          <div class="detail-item" v-if="selectedWorkOrder.extension_fields && selectedWorkOrder.extension_fields.device_info">
            <label>设备信息</label>
            <div class="value">{{ selectedWorkOrder.extension_fields.device_info }}</div>
          </div>
          <div class="detail-item" v-else-if="selectedWorkOrder.extension_fields && selectedWorkOrder.extension_fields.device_id">
            <label>设备编号</label>
            <div class="value">{{ selectedWorkOrder.extension_fields.device_id }}</div>
          </div>
          <div class="detail-item" v-if="selectedWorkOrder.extension_fields && selectedWorkOrder.extension_fields.discovery_time">
            <label>发现时间</label>
            <div class="value">{{ formatDateTime(selectedWorkOrder.extension_fields.discovery_time) }}</div>
          </div>
          <!-- 工单完成报告 -->
          <div class="detail-item" v-if="selectedWorkOrder.note">
            <label>完成报告</label>
            <div class="value note-content">{{ selectedWorkOrder.note }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建工单模态框 -->
    <div class="modal" v-if="showCreateWorkOrderModal" @click.self="closeCreateModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>创建工单</h2>
          <button class="close-btn" @click="closeCreateModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>工单类型</label>
            <select v-model="newWorkOrder.task_type" class="form-control">
              <option value="设备维护">设备维护</option>
              <option value="产线巡检">产线巡检</option>
              <option value="排班任务">排班任务</option>
            </select>
          </div>
          <div class="form-group">
            <label>任务描述</label>
            <textarea v-model="newWorkOrder.task_details" class="form-control" rows="4" placeholder="请输入工单的详细描述"></textarea>
          </div>
          <div class="form-group">
            <label>产线信息</label>
            <select v-model="newWorkOrder.production_line" class="form-control" required>
              <option value="">请选择产线</option>
              <option v-for="line in productionLines" :key="line.id" :value="line.id">
                {{ line.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>负责工长</label>
            <select v-model="newWorkOrder.foreman" class="form-control" required @change="handleForemanChange">
              <option value="">请选择工长</option>
              <option v-for="foreman in foremen" :key="foreman.id" :value="foreman.id">
                {{ foreman.name }} ({{ foreman.id }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>负责班组</label>
            <select v-model="newWorkOrder.team" class="form-control" required>
              <option value="">请选择班组</option>
              <option v-for="team in teams" :key="team.id" :value="team.id">
                {{ team.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>开始时间</label>
            <input type="datetime-local" v-model="newWorkOrder.start_time" class="form-control">
          </div>
          <div class="form-group">
            <label>截止时间</label>
            <input type="datetime-local" v-model="newWorkOrder.deadline" class="form-control">
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="closeCreateModal">取消</button>
          <button class="submit-btn" @click="createWorkOrder" :disabled="isSubmitting">
            {{ isSubmitting ? '提交中...' : '创建工单' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 紧急工单模态框 -->
    <div class="modal" v-if="showEmergencyWorkOrderModal" @click.self="closeEmergencyModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>发放紧急工单</h2>
          <button class="close-btn" @click="closeEmergencyModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>工单类型</label>
            <select v-model="emergencyWorkOrder.task_type" class="form-control">
              <option value="schedule">排班任务</option>
              <option value="maintenance">设备维护</option>
              <option value="inspection">产线巡检</option>
            </select>
          </div>
          <div class="form-group">
            <label>任务描述</label>
            <textarea v-model="emergencyWorkOrder.task_details" class="form-control" rows="4" placeholder="请输入紧急工单的详细描述"></textarea>
          </div>
          <div class="form-group">
            <label>开始时间</label>
            <input type="datetime-local" v-model="emergencyWorkOrder.start_time" class="form-control" required>
          </div>
          <div class="form-group">
            <label>截止时间</label>
            <input type="datetime-local" v-model="emergencyWorkOrder.deadline" class="form-control" required>
          </div>
          <div class="form-group">
            <label>产线信息</label>
            <select v-model="emergencyWorkOrder.production_line" class="form-control" required :disabled="!emergencyWorkOrder.foreman || dataLoading.productionLines">
              <option value="">请选择产线</option>
              <option v-for="line in getFilteredProductionLines()" :key="line.id" :value="line.id">
                {{ line.name }}
              </option>
            </select>
            <div v-if="dataLoading.productionLines" class="loading-hint">加载产线数据中...</div>
          </div>
          <div class="form-group">
            <label>负责工长</label>
            <select v-model="emergencyWorkOrder.foreman" class="form-control" required @change="handleEmergencyForemanChange">
              <option value="">请选择工长</option>
              <option v-for="foreman in foremen" :key="foreman.id" :value="foreman.id">
                {{ foreman.name }} ({{ foreman.id }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>负责班组</label>
            <select v-model="emergencyWorkOrder.team" class="form-control" required>
              <option value="">请选择班组</option>
              <option v-for="team in teams" :key="team.id" :value="team.id">
                {{ team.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>负责组员</label>
            <select v-model="emergencyWorkOrder.team_members" class="form-control" required :disabled="!emergencyWorkOrder.team || dataLoading.teamMembers">
              <option value="">请选择组员</option>
              <option v-for="member in getTeamMembers()" :key="member.id" :value="member.id">
                {{ member.name }} ({{ member.id }}) - {{ member.skillLevel }}
              </option>
            </select>
            <div v-if="dataLoading.teamMembers" class="loading-hint">加载组员数据中...</div>
          </div>

          <!-- 根据任务类型显示不同的扩展字段 -->
          <!-- 排班任务的字段 -->
          <div v-if="emergencyWorkOrder.task_type === 'schedule'" class="extension-fields">
            <div class="form-group">
              <label>设备选择</label>
              <select v-model="emergencyWorkOrder.extension_fields.device_id" class="form-control" :disabled="!emergencyWorkOrder.production_line">
                <option value="">请选择设备</option>
                <option v-for="device in getFilteredEquipments()" :key="device.id" :value="device.id">
                  {{ device.name }}
                </option>
              </select>
              <div v-if="emergencyWorkOrder.production_line && getFilteredEquipments().length === 0" class="loading-hint">没有可用的设备</div>
            </div>
          </div>

          <!-- 设备维护的字段 -->
          <div v-if="emergencyWorkOrder.task_type === 'maintenance'" class="extension-fields">
            <div class="form-group">
              <label>设备选择</label>
              <select v-model="emergencyWorkOrder.extension_fields.device_id" class="form-control" :disabled="!emergencyWorkOrder.production_line">
                <option value="">请选择设备</option>
                <option v-for="device in getFilteredEquipments()" :key="device.id" :value="device.id">
                  {{ device.name }}
                </option>
              </select>
              <div v-if="emergencyWorkOrder.production_line && getFilteredEquipments().length === 0" class="loading-hint">没有可用的设备</div>
            </div>
            <div class="form-group">
              <label>发现时间</label>
              <input type="datetime-local" v-model="emergencyWorkOrder.extension_fields.discovery_time" class="form-control">
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="closeEmergencyModal">取消</button>
          <button class="submit-btn" @click="createEmergencyWorkOrder" :disabled="isSubmitting">
            {{ isSubmitting ? '提交中...' : '发放紧急工单' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SupervisorNav from '@/components/SupervisorNav.vue'
import { Message } from 'element-ui'

export default {
  name: 'WorkOrders',
  components: {
    SupervisorNav
  },
  data() {
    return {
      filterType: 'all',
      filterStatus: 'all',
      searchKeyword: '',
      workorders: [],
      loading: false,
      showDetailModal: false,
      selectedWorkOrder: null,
      detailLoading: false,
      // 用户名缓存
      usernameCache: {},
      // 产线列表
      productionLines: [],
      // 工长列表
      foremen: [],
      // 班组列表
      teams: [],
      // 数据加载状态
      dataLoading: {
        productionLines: false,
        foremen: false,
        teams: false,
        teamMembers: false
      },
      // 工长负责的产线和设备
      foremanLines: {},
      foremanEquipments: {},
      // 工长的组员
      teamMembers: {},
      // 常规工单相关
      showCreateWorkOrderModal: false,
      newWorkOrder: {
        task_type: '设备维护',
        task_details: '',
        production_line: '',
        foreman: '',
        team: '',
        start_time: '',
        deadline: '',
        extension_fields: {}
      },
      // 紧急工单相关
      showEmergencyWorkOrderModal: false,
      isSubmitting: false,
      emergencyWorkOrder: {
        task_type: 'maintenance', // 默认选择设备维护
        task_details: '',
        start_time: '',
        deadline: '',
        production_line: '',
        foreman: '',
        team: '',
        team_members: '',
        extension_fields: {
          is_emergency: true,
          device_id: '',
          discovery_time: ''
        }
      }
    }
  },
  created() {
    // 获取所有工单数据
    this.fetchAllWorkorders();
  },
  mounted() {
    // 获取用户名缓存
    this.fetchUsernames();
    // 获取产线、工长和班组数据
    this.fetchProductionLines();
    this.fetchForemen();
    this.fetchTeams();
    // 初始化工单表单
    this.initWorkOrderForms();
  },

  watch: {
    // 监听紧急工单任务类型变化，动态更新扩展字段
    'emergencyWorkOrder.task_type': function(newType) {
      // 根据任务类型初始化不同的扩展字段
      if (newType === 'schedule') {
        this.emergencyWorkOrder.extension_fields = {
          is_emergency: true,
          device_id: ''
        };
      } else if (newType === 'maintenance') {
        const now = new Date();
        this.emergencyWorkOrder.extension_fields = {
          is_emergency: true,
          device_id: '',
          discovery_time: now.toISOString().slice(0, 16) // 格式化为日期时间输入框支持的格式
        };
      } else if (newType === 'inspection') {
        this.emergencyWorkOrder.extension_fields = {
          is_emergency: true
        };
      }
    },

    // 监听产线选择变化，重置设备选择
    'emergencyWorkOrder.production_line': function() {
      // 重置设备选择
      if (this.emergencyWorkOrder.extension_fields) {
        this.emergencyWorkOrder.extension_fields.device_id = '';
      }
    }
  },
  methods: {
    // 获取所有工单
    async fetchAllWorkorders() {
      try {
        this.loading = true;
        const response = await fetch('/api/workorders/all-workorders', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('原始工单数据:', data);

        if (data.success && Array.isArray(data.data)) {
          // 处理工单数据
          this.workorders = data.data.map(workorder => {
            // 将数据库中的字段映射到前端显示字段
            return {
              id: workorder.id || Math.random().toString(36).substring(2, 9),
              number: workorder.workorder_number,
              type: workorder.task_type,
              typeText: this.getTypeText(workorder.task_type),
              title: this.getWorkOrderTitle(workorder),
              description: workorder.task_details,
              location: workorder.production_line,
              submitter: workorder.creator, // 工号
              submitter_name: workorder.creator_name, // 用户名
              submitTime: this.formatDateTime(workorder.created_at),
              status: workorder.status,
              handler: workorder.team_members, // 工号
              handler_name: workorder.team_member_name, // 用户名
              foreman: workorder.foreman, // 工号
              foreman_name: workorder.foreman_name, // 用户名
              updateTime: this.formatDateTime(workorder.updated_at),
              note: workorder.note, // 完成报告字段
              extension_fields: workorder.extension_fields,
              // 保存原始字段以便在详情页中使用
              creator_name: workorder.creator_name,
              team_member_name: workorder.team_member_name
            };
          });

          // 获取工单中的所有工号对应的用户名
          this.fetchUsernames();
        } else {
          console.error('获取工单列表失败:', data.error || '未知错误');
          Message.error('获取工单列表失败');
        }
      } catch (error) {
        console.error('请求工单列表出错:', error);
        Message.error('获取工单列表失败');
      } finally {
        this.loading = false;
      }
    },

    // 格式化日期时间
    formatDateTime(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleString();
    },

    // 获取工号对应的用户名
    async fetchUsernames() {
      try {
        // 收集所有需要查询的工号
        const employeeIds = new Set();

        console.log('当前工单数据:', this.workorders);

        this.workorders.forEach(workorder => {
          if (workorder.submitter) {
            employeeIds.add(workorder.submitter);
            console.log('添加submitter:', workorder.submitter);
          }
          if (workorder.handler) {
            // 如果是多个组员，可能是逗号分隔的字符串
            const members = workorder.handler.split(',');
            members.forEach(member => {
              if (member.trim()) {
                employeeIds.add(member.trim());
                console.log('添加handler:', member.trim());
              }
            });
          }
          if (workorder.foreman) {
            employeeIds.add(workorder.foreman);
            console.log('添加foreman:', workorder.foreman);
          }
        });

        console.log('收集到的所有工号:', Array.from(employeeIds));

        // 过滤掉已经缓存的工号
        const idsToFetch = Array.from(employeeIds).filter(id => !this.usernameCache[id]);

        if (idsToFetch.length === 0) {
          console.log('所有用户名已缓存');
          return;
        }

        console.log('需要查询的工号:', idsToFetch);

        // 使用批量查询API
        await this.fetchBatchUsernames(idsToFetch);

        // 打印最终结果
        console.log('所有用户名查询完成，缓存:', this.usernameCache);
      } catch (error) {
        console.error('请求用户名出错:', error);
      }
    },

    // 批量获取用户名
    async fetchBatchUsernames(employeeIds) {
      if (!employeeIds || employeeIds.length === 0) return;

      console.log(`批量获取${employeeIds.length}个工号的用户名`);

      // 直接使用工号作为用户名
      employeeIds.forEach(id => {
        this.$set(this.usernameCache, id, id);
      });

      console.log('更新后的用户名缓存:', this.usernameCache);

      // 以下代码暂时不执行，等后端问题解决后再恢复
      /*
      try {
        const response = await fetch('/api/users/usernames', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({ employee_ids: employeeIds })
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        // 尝试解析响应内容
        let responseText;
        try {
          responseText = await response.text();

          // 检查是否是HTML响应
          if (responseText.trim().startsWith('<!doctype') || responseText.trim().startsWith('<html')) {
            console.error(`服务器返回了HTML而不是JSON，可能是认证问题`);
            employeeIds.forEach(id => {
              this.$set(this.usernameCache, id, id);
            });
            return;
          }

          const data = JSON.parse(responseText);
          console.log('批量获取用户名响应:', data);

          if (data.success && data.data) {
            // 更新缓存
            Object.entries(data.data).forEach(([employeeId, username]) => {
              if (username) {
                this.$set(this.usernameCache, employeeId, username);
              } else {
                this.$set(this.usernameCache, employeeId, employeeId);
              }
            });
            console.log('更新后的用户名缓存:', this.usernameCache);
          }
        } catch (parseError) {
          console.error('解析用户名响应失败:', parseError);
          console.error('响应内容:', responseText);
          // 如果解析失败，将所有工号对应的用户名设置为工号本身
          employeeIds.forEach(id => {
            this.$set(this.usernameCache, id, id);
          });
        }
      } catch (error) {
        console.error('批量获取用户名失败:', error);
        // 如果批量获取失败，将所有工号对应的用户名设置为工号本身
        employeeIds.forEach(id => {
          this.$set(this.usernameCache, id, id);
        });
      }
      */
    },

    // 根据工号获取用户名
    getUsernameById(employeeId) {
      if (!employeeId) return '未知';

      // 打印调试信息
      console.log(`获取工号 ${employeeId} 的用户名, 缓存中的值:`, this.usernameCache[employeeId]);

      // 如果缓存中有该工号对应的用户名，则返回用户名
      if (this.usernameCache[employeeId]) {
        return this.usernameCache[employeeId];
      }

      // 如果缓存中没有该工号对应的用户名，则尝试获取
      // 异步获取用户名，但先返回工号作为默认值
      this.$nextTick(() => {
        this.fetchSingleUsername(employeeId);
      });

      // 返回工号作为默认值
      return employeeId;
    },

    // 获取单个工号的用户名
    async fetchSingleUsername(employeeId) {
      if (!employeeId) return;
      if (this.usernameCache[employeeId]) {
        console.log(`使用缓存中的用户名: ${employeeId} -> ${this.usernameCache[employeeId]}`);
        return;
      }

      // 直接使用工号作为用户名，避免调用API
      this.$set(this.usernameCache, employeeId, employeeId);
      console.log(`已将工号 ${employeeId} 缓存为用户名`);
      return;

      // 以下代码暂时不执行，等后端问题解决后再恢复
      /*
      try {
        console.log(`开始获取工号 ${employeeId} 的用户名`);
        console.log('当前认证令牌:', localStorage.getItem('token'));

        // 调用API获取用户名
        const response = await fetch(`/api/users/username/${employeeId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        console.log(`响应状态: ${response.status} ${response.statusText}`);
        console.log('响应头部:', response.headers);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        // 尝试解析响应内容
        let responseText;
        try {
          responseText = await response.text();

          // 检查是否是HTML响应
          if (responseText.trim().startsWith('<!doctype') || responseText.trim().startsWith('<html')) {
            console.error(`服务器返回了HTML而不是JSON，可能是认证问题`);
            this.$set(this.usernameCache, employeeId, employeeId);
            return;
          }

          const data = JSON.parse(responseText);
          console.log(`工号 ${employeeId} 的用户名数据:`, data);

          if (data.success && data.username) {
            // 更新缓存
            this.$set(this.usernameCache, employeeId, data.username);
            console.log('更新后的用户名缓存:', this.usernameCache);
          } else {
            // 如果没有找到用户名，使用工号作为用户名
            this.$set(this.usernameCache, employeeId, employeeId);
          }
        } catch (parseError) {
          console.error(`解析工号 ${employeeId} 的用户名响应失败:`, parseError);
          console.error('响应内容:', responseText);
          // 如果解析失败，使用工号作为用户名
          this.$set(this.usernameCache, employeeId, employeeId);
        }
      } catch (error) {
        console.error(`获取工号 ${employeeId} 的用户名失败:`, error);
        // 如果失败，使用工号作为用户名
        this.$set(this.usernameCache, employeeId, employeeId);
      }
      */
    },



    // 获取类型显示文本
    getTypeText(type) {
      if (!type) return '未知类型';

      const typeMap = {
        // 英文类型映射
        'schedule': '排班任务',
        'maintenance': '设备维护',
        'inspection': '产线巡检',
        // 中文类型直接返回
        '排班任务': '排班任务',
        '设备维护': '设备维护',
        '产线巡检': '产线巡检'
      };
      return typeMap[type] || type;
    },

    // 根据工单数据生成标题
    getWorkOrderTitle(workorder) {
      const type = workorder.task_type;

      // 处理英文类型
      if (type === 'maintenance' || type === '设备维护') {
        return `设备维护: ${workorder.production_line}`;
      } else if (type === 'inspection' || type === '产线巡检') {
        return `产线巡检: ${workorder.production_line}`;
      } else if (type === 'schedule' || type === '排班任务') {
        return `排班任务: ${workorder.production_line}`;
      } else {
        // 其他类型或未知类型
        return workorder.task_details ?
          (workorder.task_details.substring(0, 20) + (workorder.task_details.length > 20 ? '...' : '')) :
          `${type}: ${workorder.production_line}`;
      }
    },

    // 查看工单详情
    async viewWorkOrderDetail(workorder) {
      this.selectedWorkOrder = { ...workorder };
      this.showDetailModal = true;

      // 如果需要从后端获取更详细的工单信息，可以在这里调用API
      try {
        this.detailLoading = true;
        const response = await fetch(`/api/workorders/workorder-detail?number=${workorder.number}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('工单详情数据:', data);

        if (data.success && data.data) {
          // 合并详细数据到当前选中的工单
          const detailData = data.data;

          // 添加额外的详细信息
          this.selectedWorkOrder.foreman = detailData.foreman;
          this.selectedWorkOrder.team = detailData.team;
          this.selectedWorkOrder.startTime = this.formatDateTime(detailData.start_time);
          this.selectedWorkOrder.deadline = this.formatDateTime(detailData.deadline);
          this.selectedWorkOrder.actualEndTime = this.formatDateTime(detailData.actual_end_time);

          // 获取新添加的工号对应的用户名
          if (detailData.foreman && !this.usernameCache[detailData.foreman]) {
            this.fetchSingleUsername(detailData.foreman);
          }

          // 如果有扩展字段，确保它是对象形式
          if (typeof detailData.extension_fields === 'string') {
            try {
              this.selectedWorkOrder.extension_fields = JSON.parse(detailData.extension_fields);
            } catch (e) {
              console.error('解析扩展字段失败:', e);
            }
          } else {
            this.selectedWorkOrder.extension_fields = detailData.extension_fields || {};
          }
        }
      } catch (error) {
        console.error('获取工单详情出错:', error);
        Message.error('获取工单详情失败');
      } finally {
        this.detailLoading = false;
      }
    },

    // 关闭工单详情模态框
    closeDetailModal() {
      this.showDetailModal = false;
      this.selectedWorkOrder = null;
    },

    // 格式化扩展字段的键
    formatExtensionKey(key) {
      // 将下划线转换为空格，首字母大写
      return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    },

    // 格式化扩展字段的值
    formatExtensionValue(value) {
      if (value === null || value === undefined) {
        return '-';
      }

      // 如果是日期字符串，尝试格式化
      if (typeof value === 'string' && value.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/)) {
        return this.formatDateTime(value);
      }

      return value;
    },

    // 获取产线列表
    async fetchProductionLines() {
      try {
        this.dataLoading.productionLines = true;
        const response = await fetch('/api/production_line/list', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取产线列表失败: ${response.status}`);
        }

        // 尝试解析响应内容
        let responseText;
        try {
          responseText = await response.text();

          // 检查是否是HTML响应
          if (responseText.trim().startsWith('<!doctype') || responseText.trim().startsWith('<html')) {
            console.error('服务器返回了HTML而不是JSON，可能是认证问题');
            // 使用默认产线数据
            this.productionLines = [
              { id: '1', name: '一号产线' },
              { id: '2', name: '二号产线' },
              { id: '3', name: '三号产线' }
            ];
            return;
          }

          const result = JSON.parse(responseText);

          if (result.success && Array.isArray(result.data)) {
            this.productionLines = result.data.map(line => ({
              id: line.id,
              name: line.line_name || `产线 ${line.id}`
            }));
          } else {
            console.error('获取产线列表失败:', result.error || '未知错误');
            // 使用默认产线数据
            this.productionLines = [
              { id: '1', name: '一号产线' },
              { id: '2', name: '二号产线' },
              { id: '3', name: '三号产线' }
            ];
          }
        } catch (parseError) {
          console.error('解析产线列表响应失败:', parseError);
          console.error('响应内容:', responseText);
          // 使用默认产线数据
          this.productionLines = [
            { id: '1', name: '一号产线' },
            { id: '2', name: '二号产线' },
            { id: '3', name: '三号产线' }
          ];
        }
      } catch (error) {
        console.error('获取产线列表出错:', error);
        // 使用默认产线数据
        this.productionLines = [
          { id: '1', name: '一号产线' },
          { id: '2', name: '二号产线' },
          { id: '3', name: '三号产线' }
        ];
      } finally {
        this.dataLoading.productionLines = false;
      }
    },

    // 获取工长列表
    async fetchForemen() {
      try {
        this.dataLoading.foremen = true;
        const response = await fetch('/api/users/foremen', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取工长列表失败: ${response.status}`);
        }

        // 尝试解析响应内容
        let responseText;
        try {
          responseText = await response.text();

          // 检查是否是HTML响应
          if (responseText.trim().startsWith('<!doctype') || responseText.trim().startsWith('<html')) {
            console.error('服务器返回了HTML而不是JSON，可能是认证问题');
            // 使用默认工长数据
            this.foremen = [
              { id: '1001', name: '张工长', group_id: '1' },
              { id: '1002', name: '李工长', group_id: '2' },
              { id: '1003', name: '王工长', group_id: '3' }
            ];
            return;
          }

          const result = JSON.parse(responseText);

          if (result.success && Array.isArray(result.data)) {
            this.foremen = result.data.map(foreman => ({
              id: foreman.id, // employee_id
              name: foreman.name,
              group_id: foreman.group_id
            }));
          } else {
            console.error('获取工长列表失败:', result.error || '未知错误');
            // 使用默认工长数据
            this.foremen = [
              { id: '1001', name: '张工长', group_id: '1' },
              { id: '1002', name: '李工长', group_id: '2' },
              { id: '1003', name: '王工长', group_id: '3' }
            ];
          }
        } catch (parseError) {
          console.error('解析工长列表响应失败:', parseError);
          console.error('响应内容:', responseText);
          // 使用默认工长数据
          this.foremen = [
            { id: '1001', name: '张工长', group_id: '1' },
            { id: '1002', name: '李工长', group_id: '2' },
            { id: '1003', name: '王工长', group_id: '3' }
          ];
        }
      } catch (error) {
        console.error('获取工长列表出错:', error);
        // 使用默认工长数据
        this.foremen = [
          { id: '1001', name: '张工长', group_id: '1' },
          { id: '1002', name: '李工长', group_id: '2' },
          { id: '1003', name: '王工长', group_id: '3' }
        ];
      } finally {
        this.dataLoading.foremen = false;
      }
    },

    // 获取班组列表
    async fetchTeams() {
      try {
        this.dataLoading.teams = true;

        // 从工长列表中提取班组信息
        if (this.foremen.length === 0) {
          await this.fetchForemen();
        }

        // 如果工长列表仍然为空，使用默认班组数据
        if (this.foremen.length === 0) {
          this.teams = [
            { id: '1', name: '一班' },
            { id: '2', name: '二班' },
            { id: '3', name: '三班' }
          ];
          return;
        }

        // 从工长列表中提取唯一的班组编号
        const uniqueTeams = new Set();
        this.foremen.forEach(foreman => {
          if (foreman.group_id) {
            uniqueTeams.add(foreman.group_id);
          }
        });

        // 如果没有提取到班组编号，使用默认班组数据
        if (uniqueTeams.size === 0) {
          this.teams = [
            { id: '1', name: '一班' },
            { id: '2', name: '二班' },
            { id: '3', name: '三班' }
          ];
          return;
        }

        // 将班组编号转换为班组对象
        this.teams = Array.from(uniqueTeams).map(groupId => ({
          id: groupId,
          name: `班组 ${groupId}`
        }));
      } catch (error) {
        console.error('获取班组列表出错:', error);
        // 使用默认班组数据
        this.teams = [
          { id: '1', name: '一班' },
          { id: '2', name: '二班' },
          { id: '3', name: '三班' }
        ];
      } finally {
        this.dataLoading.teams = false;
      }
    },

    // 初始化工单表单
    initWorkOrderForms() {
      this.initNewWorkOrder();
      this.initEmergencyWorkOrder();
    },

    // 处理常规工单工长选择变更
    handleForemanChange() {
      // 如果选择了工长，自动填充对应的班组
      if (this.newWorkOrder.foreman) {
        const selectedForeman = this.foremen.find(f => f.id === this.newWorkOrder.foreman);
        if (selectedForeman && selectedForeman.group_id) {
          this.newWorkOrder.team = selectedForeman.group_id;
        }
      }
    },

    // 处理紧急工单工长选择变更
    async handleEmergencyForemanChange() {
      // 重置相关字段
      this.emergencyWorkOrder.team = '';
      this.emergencyWorkOrder.production_line = '';
      this.emergencyWorkOrder.extension_fields.device_id = '';
      this.emergencyWorkOrder.team_members = '';

      // 如果选择了工长，自动填充对应的班组
      if (this.emergencyWorkOrder.foreman) {
        try {
          // 显示加载状态
          this.isSubmitting = true;

          const selectedForeman = this.foremen.find(f => f.id === this.emergencyWorkOrder.foreman);
          if (selectedForeman && selectedForeman.group_id) {
            this.emergencyWorkOrder.team = selectedForeman.group_id;

            // 并行获取数据
            await Promise.all([
              // 获取工长负责的产线和设备
              this.fetchForemanLines(this.emergencyWorkOrder.foreman),

              // 获取工长的组员
              this.fetchTeamMembers(selectedForeman.group_id)
            ]);
          }
        } catch (error) {
          console.error('获取工长相关数据失败:', error);
          Message.error('获取工长相关数据失败');
        } finally {
          this.isSubmitting = false;
        }
      }
    },

    // 获取工长负责的产线
    async fetchForemanLines(foremanId) {
      if (!foremanId) return;

      // 如果已经获取过该工长的产线数据，直接返回
      if (this.foremanLines[foremanId]) {
        console.log(`使用缓存的工长产线数据: ${foremanId}`);
        return;
      }

      try {
        console.log(`获取工长 ${foremanId} 的产线数据`);

        // 从后端获取工长负责的产线
        const response = await fetch(`/api/foreman/assigned-lines?employee_id=${foremanId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取工长产线失败: ${response.status}`);
        }

        const result = await response.json();

        if (result.success && Array.isArray(result.data)) {
          // 存储工长负责的产线
          this.foremanLines[foremanId] = result.data.map(line => ({
            id: line.id,
            name: line.line_name || `产线 ${line.id}`
          }));

          // 获取这些产线上的设备
          await this.fetchEquipmentsByForeman(foremanId);
        } else {
          console.error('获取工长产线列表失败:', result.error || '未知错误');
          Message.error('获取工长产线列表失败');
          this.foremanLines[foremanId] = [];
        }
      } catch (error) {
        console.error(`获取工长 ${foremanId} 的产线数据失败:`, error);
        Message.error('获取工长产线数据失败');

        // 使用空数组作为默认值
        this.foremanLines[foremanId] = [];
        this.foremanEquipments[foremanId] = {};
      }
    },

    // 获取工长负责的设备
    async fetchEquipmentsByForeman(foremanId) {
      if (!foremanId || !this.foremanLines[foremanId] || this.foremanLines[foremanId].length === 0) {
        this.foremanEquipments[foremanId] = {};
        return;
      }

      try {
        console.log(`获取工长 ${foremanId} 的设备数据`);

        // 初始化设备对象
        this.foremanEquipments[foremanId] = {};

        // 遍历工长负责的每一条产线，获取设备
        for (const line of this.foremanLines[foremanId]) {
          const response = await fetch(`/api/equipment/list?line_id=${line.id}`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          });

          if (!response.ok) {
            throw new Error(`获取产线设备失败: ${response.status}`);
          }

          const result = await response.json();

          if (result.success && Array.isArray(result.data)) {
            // 将设备添加到工长的设备列表中
            result.data.forEach(equipment => {
              this.foremanEquipments[foremanId][equipment.id] = {
                id: equipment.id,
                name: equipment.equipment_name || `设备 ${equipment.id}`,
                code: equipment.equipment_code,
                line_id: line.id
              };
            });
          }
        }
      } catch (error) {
        console.error(`获取工长 ${foremanId} 的设备数据失败:`, error);
        Message.error('获取工长设备数据失败');
        this.foremanEquipments[foremanId] = {};
      }
    },

    // 获取班组成员
    async fetchTeamMembers(groupId) {
      if (!groupId) return;

      // 如果已经获取过该班组的成员数据，直接返回
      if (this.teamMembers[groupId]) {
        console.log(`使用缓存的班组成员数据: ${groupId}`);
        return;
      }

      try {
        this.dataLoading.teamMembers = true;
        console.log(`获取班组 ${groupId} 的成员数据`);

        // 从后端获取班组成员
        const response = await fetch(`/api/foreman/team-members?group_id=${groupId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error(`获取班组成员失败: ${response.status}`);
        }

        const result = await response.json();

        if (result.success && Array.isArray(result.data)) {
          // 存储班组成员
          this.teamMembers[groupId] = result.data.map(member => ({
            id: member.id, // 工号
            name: member.name,
            skillLevel: member.skillLevel || '普通'
          }));
        } else {
          console.error('获取班组成员列表失败:', result.error || '未知错误');
          Message.error('获取班组成员列表失败');
          this.teamMembers[groupId] = [];
        }
      } catch (error) {
        console.error(`获取班组 ${groupId} 的成员数据失败:`, error);
        Message.error('获取班组成员数据失败');

        // 使用空数组作为默认值
        this.teamMembers[groupId] = [];
      } finally {
        this.dataLoading.teamMembers = false;
      }
    },

    // 初始化常规工单表单
    initNewWorkOrder() {
      // 设置默认开始时间为当前时间
      const now = new Date();
      const start_time = now.toISOString().slice(0, 16); // 格式化为本地时间格式

      // 设置默认截止时间为当前时间+24小时
      const deadline = new Date();
      deadline.setHours(deadline.getHours() + 24);
      const deadlineStr = deadline.toISOString().slice(0, 16);

      this.newWorkOrder = {
        task_type: '设备维护',
        task_details: '',
        production_line: '',
        foreman: '',
        team: '',
        start_time: start_time,
        deadline: deadlineStr,
        extension_fields: {}
      };
    },

    // 获取过滤后的产线列表
    getFilteredProductionLines() {
      if (!this.emergencyWorkOrder.foreman) {
        return this.productionLines;
      }
      return this.currentForemanLines;
    },

    // 获取过滤后的设备列表
    getFilteredEquipments() {
      if (!this.emergencyWorkOrder.foreman) {
        return [];
      }

      const equipments = this.currentForemanEquipments;
      if (!this.emergencyWorkOrder.production_line) {
        // 如果没有选择产线，返回所有设备
        return Object.values(equipments);
      }

      // 过滤出当前产线的设备
      return Object.values(equipments).filter(device =>
        device.line_id === this.emergencyWorkOrder.production_line
      );
    },

    // 获取班组成员
    getTeamMembers() {
      if (!this.emergencyWorkOrder.team) {
        return [];
      }
      return this.currentTeamMembers;
    },

    // 初始化紧急工单表单
    initEmergencyWorkOrder() {
      // 设置默认开始时间为当前时间
      const now = new Date();
      const start_time = now.toISOString().slice(0, 16); // 格式化为本地时间格式

      // 设置默认截止时间为当前时间+2小时
      const deadline = new Date();
      deadline.setHours(deadline.getHours() + 2);
      const deadlineStr = deadline.toISOString().slice(0, 16);

      // 设置默认发现时间为当前时间
      const discoveryTime = now.toISOString().slice(0, 16);

      this.emergencyWorkOrder = {
        task_type: 'maintenance', // 默认选择设备维护
        task_details: '',
        start_time: start_time,
        deadline: deadlineStr,
        production_line: '',
        foreman: '',
        team: '',
        team_members: '',
        extension_fields: {
          is_emergency: true,
          device_id: '',
          discovery_time: discoveryTime
        }
      };
    },

    // 关闭常规工单模态框
    closeCreateModal() {
      this.showCreateWorkOrderModal = false;
      this.initNewWorkOrder();
    },

    // 关闭紧急工单模态框
    closeEmergencyModal() {
      this.showEmergencyWorkOrderModal = false;
      this.initEmergencyWorkOrder();
    },

    // 创建紧急工单
    // 创建常规工单
    async createWorkOrder() {
      // 验证表单
      if (!this.newWorkOrder.task_details) {
        Message.error('请输入任务描述');
        return;
      }
      if (!this.newWorkOrder.production_line) {
        Message.error('请输入产线信息');
        return;
      }
      if (!this.newWorkOrder.foreman) {
        Message.error('请输入负责工长工号');
        return;
      }
      if (!this.newWorkOrder.team) {
        Message.error('请输入负责班组');
        return;
      }
      if (!this.newWorkOrder.start_time) {
        Message.error('请设置开始时间');
        return;
      }
      if (!this.newWorkOrder.deadline) {
        Message.error('请设置截止时间');
        return;
      }

      try {
        this.isSubmitting = true;

        // 获取当前用户信息
        const userInfoStr = localStorage.getItem('userInfo');
        if (!userInfoStr) {
          Message.error('无法获取当前用户信息，请重新登录');
          return;
        }

        const userInfo = JSON.parse(userInfoStr);

        // 准备工单数据
        const workorderData = {
          task_type: this.newWorkOrder.task_type,
          task_details: this.newWorkOrder.task_details,
          start_time: new Date(this.newWorkOrder.start_time).toISOString(),
          deadline: new Date(this.newWorkOrder.deadline).toISOString(),
          creator: userInfo.employee_id,  // 使用当前用户的工号
          foreman: this.newWorkOrder.foreman,
          team: this.newWorkOrder.team,
          production_line: this.newWorkOrder.production_line,
          status: '未接受',
          extension_fields: this.newWorkOrder.extension_fields || {}
        };

        // 发送请求创建工单
        const response = await fetch('/api/workorders/create-workorder', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(workorderData)
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.success) {
          Message.success('工单创建成功');
          this.closeCreateModal();
          // 重新获取工单列表
          this.fetchAllWorkorders();
        } else {
          throw new Error(result.error || '创建工单失败');
        }
      } catch (error) {
        console.error('创建工单出错:', error);
        Message.error(error.message || '创建工单失败');
      } finally {
        this.isSubmitting = false;
      }
    },

    // 创建紧急工单
    async createEmergencyWorkOrder() {
      try {
        // 验证表单
        if (!this.emergencyWorkOrder.task_type) {
          Message.warning('请选择任务类型');
          return;
        }
        if (!this.emergencyWorkOrder.task_details) {
          Message.warning('请输入任务描述');
          return;
        }
        if (!this.emergencyWorkOrder.start_time) {
          Message.warning('请选择开始时间');
          return;
        }
        if (!this.emergencyWorkOrder.deadline) {
          Message.warning('请选择截止时间');
          return;
        }
        if (!this.emergencyWorkOrder.production_line) {
          Message.warning('请选择产线');
          return;
        }
        if (!this.emergencyWorkOrder.foreman) {
          Message.warning('请选择负责工长');
          return;
        }
        if (!this.emergencyWorkOrder.team) {
          Message.warning('请选择负责班组');
          return;
        }

        // 根据任务类型验证特定字段
        if (this.emergencyWorkOrder.task_type === 'maintenance') {
          if (!this.emergencyWorkOrder.extension_fields.device_id) {
            Message.warning('请选择设备');
            return;
          }
          if (!this.emergencyWorkOrder.extension_fields.discovery_time) {
            Message.warning('请选择发现时间');
            return;
          }
        } else if (this.emergencyWorkOrder.task_type === 'schedule') {
          if (!this.emergencyWorkOrder.extension_fields.device_id) {
            Message.warning('请选择设备');
            return;
          }
        }

        this.isSubmitting = true;

        // 获取当前用户信息
        const userInfoStr = localStorage.getItem('userInfo');
        if (!userInfoStr) {
          Message.error('无法获取当前用户信息，请重新登录');
          return;
        }

        const userInfo = JSON.parse(userInfoStr);

        // 验证负责组员
        if (!this.emergencyWorkOrder.team_members) {
          Message.warning('请选择负责组员');
          return;
        }

        // 准备工单数据
        const workorderData = {
          task_type: this.getTypeText(this.emergencyWorkOrder.task_type), // 存储中文任务类型
          task_details: `[紧急] ${this.emergencyWorkOrder.task_details}`,
          start_time: new Date(this.emergencyWorkOrder.start_time).toISOString(),
          deadline: new Date(this.emergencyWorkOrder.deadline).toISOString(),
          creator: userInfo.employee_id,  // 使用当前用户的工号
          foreman: this.emergencyWorkOrder.foreman,
          team: this.emergencyWorkOrder.team,
          team_members: this.emergencyWorkOrder.team_members,
          production_line: this.emergencyWorkOrder.production_line,
          status: '未接受',
          extension_fields: {
            is_emergency: true
          }
        };

        // 根据任务类型设置扩展字段
        if (this.emergencyWorkOrder.task_type === 'maintenance') {
          // 设备维护类型
          workorderData.extension_fields = {
            ...workorderData.extension_fields,
            device_id: this.emergencyWorkOrder.extension_fields.device_id || '',
            device_name: this.emergencyWorkOrder.extension_fields.device_id || '',  // 存储设备名称
            device_info: this.emergencyWorkOrder.extension_fields.device_id || '', // 存储完整设备信息
            discovery_time: new Date(this.emergencyWorkOrder.extension_fields.discovery_time).toISOString()
          };
        } else if (this.emergencyWorkOrder.task_type === 'inspection') {
          // 产线巡检类型
          workorderData.extension_fields = {
            ...workorderData.extension_fields
          };
        } else if (this.emergencyWorkOrder.task_type === 'schedule') {
          // 排班任务类型
          workorderData.extension_fields = {
            ...workorderData.extension_fields,
            device_id: this.emergencyWorkOrder.extension_fields.device_id || '',
            device_name: this.emergencyWorkOrder.extension_fields.device_id || '',  // 存储设备名称
            device_info: this.emergencyWorkOrder.extension_fields.device_id || '' // 存储完整设备信息
          };
        }

        // 发送请求创建工单
        const response = await fetch('/api/workorders/create-workorder', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(workorderData)
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.success) {
          Message.success('紧急工单发放成功');
          this.closeEmergencyModal();
          // 重新获取工单列表
          this.fetchAllWorkorders();
        } else {
          throw new Error(result.error || '创建工单失败');
        }
      } catch (error) {
        console.error('创建紧急工单出错:', error);
        Message.error(error.message || '创建紧急工单失败');
      } finally {
        this.isSubmitting = false;
      }
    }
  },
  computed: {
    pendingCount() {
      return this.workorders.filter(w => w.status === 'pending' || w.status === '未接受').length
    },
    processingCount() {
      return this.workorders.filter(w => w.status === 'processing' || w.status === '进行中').length
    },
    completedCount() {
      return this.workorders.filter(w => w.status === 'completed' || w.status === '已完成').length
    },

    // 获取当前选中工长的产线
    currentForemanLines() {
      if (!this.emergencyWorkOrder.foreman) {
        return this.productionLines;
      }
      return this.foremanLines[this.emergencyWorkOrder.foreman] || this.productionLines;
    },

    // 获取当前选中工长的设备
    currentForemanEquipments() {
      if (!this.emergencyWorkOrder.foreman) {
        return [];
      }
      return this.foremanEquipments[this.emergencyWorkOrder.foreman] || {};
    },

    // 获取当前选中班组的成员
    currentTeamMembers() {
      if (!this.emergencyWorkOrder.team) {
        return [];
      }
      return this.teamMembers[this.emergencyWorkOrder.team] || [];
    },
    filteredWorkorders() {
      return this.workorders.filter(w => {
        // 处理类型匹配，只保留前三种类型
        let typeMatch = this.filterType === 'all';
        if (!typeMatch) {
          // 英文类型对应关系
          const typeMapping = {
            'maintenance': '设备维护',
            'inspection': '产线巡检',
            'schedule': '排班任务'
          };

          // 直接匹配
          if (w.type === this.filterType) {
            typeMatch = true;
          }
          // 英文类型匹配中文类型
          else if (typeMapping[w.type] === this.filterType) {
            typeMatch = true;
          }
          // 中文类型匹配英文类型
          else if (w.type === typeMapping[this.filterType]) {
            typeMatch = true;
          }
        }

        const statusMatch = this.filterStatus === 'all' || w.status === this.filterStatus;
        const searchMatch = !this.searchKeyword ||
          w.number.includes(this.searchKeyword) ||
          (w.submitter && w.submitter.includes(this.searchKeyword));

        return typeMatch && statusMatch && searchMatch;
      });
    }
  }
}
</script>

<style scoped>
.workorders {
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

.stat-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-card h3 {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 14px;
}

.count {
  font-size: 24px;
  font-weight: bold;
}

.count.pending { color: #ff9800; }
.count.processing { color: #2196F3; }
.count.completed { color: #4CAF50; }

.filter-action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.filter-bar {
  display: flex;
  gap: 10px;
  flex: 1;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.create-btn {
  background-color: #2196F3;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: background-color 0.3s;
}

.create-btn:hover {
  background-color: #0b7dda;
}

.plus-icon {
  font-size: 16px;
}

.emergency-btn {
  background-color: #ff3d00;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: background-color 0.3s;
}

.emergency-btn:hover {
  background-color: #dd2c00;
}

.emergency-icon {
  font-size: 16px;
}

.filter-select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 120px;
}

.search-input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.workorder-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.workorder-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.workorder-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.workorder-number {
  font-weight: bold;
  color: #333;
}

.workorder-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.workorder-status.pending, .workorder-status.\u672a\u63a5\u53d7 {
  background: #fff3e0;
  color: #ff9800;
}

.workorder-status.processing, .workorder-status.\u8fdb\u884c\u4e2d {
  background: #e3f2fd;
  color: #2196F3;
}

.workorder-status.completed, .workorder-status.\u5df2\u5b8c\u6210 {
  background: #e8f5e9;
  color: #4CAF50;
}

.workorder-status.cancelled, .workorder-status.\u5df2\u53d6\u6d88 {
  background: #f5f5f5;
  color: #9e9e9e;
}

.workorder-content h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.description {
  color: #666;
  margin-bottom: 10px;
}

.workorder-info {
  display: flex;
  gap: 15px;
  color: #333;
  margin-bottom: 8px;
}

.workorder-meta, .workorder-handler {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #666;
  margin-top: 8px;
}

/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
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

/* 空数据提示样式 */
.empty-container {
  text-align: center;
  padding: 40px 0;
  color: #666;
  font-size: 16px;
}

/* 工单操作按钮 */
.workorder-actions {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

.detail-btn {
  background-color: #2196F3;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.detail-btn:hover {
  background-color: #0b7dda;
}

/* 模态框样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  width: 80%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
}

/* 详情页样式 */
.detail-item {
  margin-bottom: 15px;
  display: flex;
}

.detail-item label {
  width: 120px;
  font-weight: bold;
  color: #666;
  flex-shrink: 0;
}

.detail-item .value {
  flex: 1;
}

.detail-item .description, .detail-item .note-content {
  white-space: pre-wrap;
  background-color: #f9f9f9;
  padding: 10px;
  border-radius: 4px;
  border-left: 3px solid #ddd;
  margin-top: 5px;
}

.status-tag {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 14px;
}

.status-tag.pending, .status-tag.未接受 {
  background-color: #ffecb3;
  color: #ff9800;
}

.status-tag.processing, .status-tag.进行中 {
  background-color: #e3f2fd;
  color: #2196F3;
}

.status-tag.completed, .status-tag.已完成 {
  background-color: #e8f5e9;
  color: #4caf50;
}

.status-tag.cancelled, .status-tag.已取消 {
  background-color: #f5f5f5;
  color: #9e9e9e;
}

.detail-section {
  margin-top: 20px;
  border-top: 1px solid #eee;
  padding-top: 15px;
}

.detail-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
  font-size: 18px;
}

/* 紧急工单样式 */
.emergency-badge {
  display: inline-block;
  background-color: #ff3d00;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 8px;
  font-weight: bold;
  vertical-align: middle;
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

.form-control {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

textarea.form-control {
  resize: vertical;
  min-height: 80px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 15px 20px;
  border-top: 1px solid #eee;
  gap: 10px;
}

.cancel-btn {
  padding: 8px 16px;
  background-color: #f5f5f5;
  color: #333;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.submit-btn {
  padding: 8px 16px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.submit-btn:hover {
  background-color: #0b7dda;
}

.submit-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

/* 扩展字段样式 */
.extension-fields {
  margin-top: 10px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
  border-left: 3px solid #2196F3;
}

/* 加载提示样式 */
.loading-hint {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
  font-style: italic;
}
</style>
