<template>
  <div class="profile">
    <header class="header">
      <h1>我的</h1>
    </header>
    
    <div class="content">
      <!-- 个人信息卡片 -->
      <div class="info-card">
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

      <!-- 系统设置区域 -->
      <div class="info-card">
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
        <button class="action-btn" @click="changePassword">修改密码</button>
        <button class="action-btn" @click="updatePhone">更新手机号</button>
        <button class="action-btn logout" @click="handleLogout">退出登录</button>
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
.account {
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

.info-card {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item label {
  color: #666;
}

.info-item .value {
  color: #333;
  font-size: 16px;
}

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
  background-color: #2196F3;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.action-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.action-btn {
  padding: 12px;
  border: none;
  border-radius: 8px;
  background: white;
  color: #2196F3;
  font-size: 16px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.action-btn.logout {
  color: #f44336;
}
</style>
