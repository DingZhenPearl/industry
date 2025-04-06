<template>
  <div class="profile">
    <header class="header">
      <h1>我的</h1>
    </header>
    
    <div class="content">
      <!-- 用户信息卡片 -->
      <div class="user-profile-card">
        <div class="avatar-section">
          <div class="avatar">
            <img src="@/assets/avatar.svg" alt="用户头像">
          </div>
          <h2 class="username">{{ userInfo.username }}</h2>
          <div class="role-badge">厂长</div>
        </div>
      </div>
      
      <!-- 个人信息卡片 -->
      <div class="info-card">
        <h3 class="card-title">个人信息</h3>
        <div class="info-item">
          <label>用户名</label>
          <div class="value">{{ userInfo.username }}</div>
        </div>
        <div class="info-item">
          <label>职位</label>
          <div class="value">厂长</div>
        </div>
        <div class="info-item">
          <label>手机号</label>
          <div class="value">{{ userInfo.phone || '未设置' }}</div>
        </div>
      </div>

      <!-- 管理统计卡片 -->
      <div class="info-card">
        <h3 class="card-title">管理统计</h3>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">3</div>
            <div class="stat-label">生产线</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">42</div>
            <div class="stat-label">员工数量</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">95%</div>
            <div class="stat-label">生产效率</div>
          </div>
        </div>
      </div>
      
      <!-- 系统设置区域 -->
      <div class="info-card">
        <h3 class="card-title">系统设置</h3>
        <div class="info-item">
          <label>系统通知</label>
          <label class="switch">
            <input type="checkbox" v-model="settings.notifications">
            <span class="slider"></span>
          </label>
        </div>
        <div class="info-item">
          <label>数据自动同步</label>
          <label class="switch">
            <input type="checkbox" v-model="settings.autoSync">
            <span class="slider"></span>
          </label>
        </div>
        <div class="info-item">
          <label>双因素认证</label>
          <label class="switch">
            <input type="checkbox" v-model="settings.twoFactorAuth">
            <span class="slider"></span>
          </label>
        </div>
      </div>

      <!-- 操作按钮列表 -->
      <div class="action-list">
        <button class="action-btn" @click="changePassword">
          <i class="icon-lock"></i>
          修改密码
        </button>
        <button class="action-btn" @click="updatePhone">
          <i class="icon-phone"></i>
          更新手机号
        </button>
        <button class="action-btn logout" @click="handleLogout">
          <i class="icon-logout"></i>
          退出登录
        </button>
      </div>
    </div>

    <SupervisorNav />
  </div>
</template>

<script>
import SupervisorNav from '@/components/SupervisorNav.vue'

export default {
  name: 'SupervisorProfile',
  components: {
    SupervisorNav
  },
  data() {
    return {
      userInfo: JSON.parse(localStorage.getItem('userInfo') || '{}'),
      settings: {
        notifications: true,
        autoSync: false,
        twoFactorAuth: false
      }
    }
  },
  methods: {
    changePassword() {
      console.log('修改密码')
    },
    updatePhone() {
      console.log('更新手机号')
    },
    handleLogout() {
      localStorage.removeItem('userInfo')
      localStorage.removeItem('token')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.profile {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding-bottom: 60px;
  background-color: #f5f7fa;
}

.header {
  background-color: #2196F3;
  color: white;
  padding: 15px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.content {
  flex: 1;
  padding: 15px;
}

/* 用户资料卡片样式 */
.user-profile-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 15px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  text-align: center;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  margin-bottom: 10px;
  border: 3px solid #e8f5e9;
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.2);
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.username {
  font-size: 18px;
  font-weight: 600;
  margin: 5px 0;
  color: #333;
}

.role-badge {
  background-color: #e8f5e9;
  color: #4CAF50;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  margin-top: 5px;
}

/* 信息卡片样式 */
.info-card {
  background: white;
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 15px 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item label {
  color: #666;
  font-size: 14px;
}

.info-item .value {
  color: #333;
  font-size: 14px;
  font-weight: 500;
}

/* 统计数据样式 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  text-align: center;
}

.stat-item {
  padding: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #4CAF50;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #666;
}

/* 开关样式 */
.switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 34px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #4CAF50;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

/* 操作按钮样式 */
.action-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.action-btn {
  display: flex;
  align-items: center;
  padding: 14px;
  border: none;
  border-radius: 12px;
  background: white;
  color: #2196F3;
  font-size: 16px;
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
}

.action-btn:hover {
  background-color: #f5f9ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.action-btn i {
  margin-right: 10px;
  font-size: 18px;
}

.icon-lock:before {
  content: '🔒';
}

.icon-phone:before {
  content: '📱';
}

.icon-logout:before {
  content: '🚪';
}

.action-btn.logout {
  color: #f44336;
}
</style>
