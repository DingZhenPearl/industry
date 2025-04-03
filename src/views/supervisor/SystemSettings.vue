<template>
  <div class="settings">
    <header class="header">
      <h1>系统设置</h1>
    </header>
    
    <div class="content">
      <div class="settings-section">
        <h2>基本设置</h2>
        <div class="setting-item">
          <span class="setting-label">系统通知</span>
          <label class="switch">
            <input type="checkbox" v-model="settings.notifications">
            <span class="slider"></span>
          </label>
        </div>
        <div class="setting-item">
          <span class="setting-label">数据自动同步</span>
          <label class="switch">
            <input type="checkbox" v-model="settings.autoSync">
            <span class="slider"></span>
          </label>
        </div>
      </div>

      <div class="settings-section">
        <h2>安全设置</h2>
        <div class="setting-item">
          <span class="setting-label">双因素认证</span>
          <label class="switch">
            <input type="checkbox" v-model="settings.twoFactorAuth">
            <span class="slider"></span>
          </label>
        </div>
      </div>

      <button class="save-btn" @click="saveSettings">保存设置</button>
      
      <!-- 添加退出登录按钮 -->
      <button class="logout-btn" @click="handleLogout">退出登录</button>
    </div>

    <SupervisorNav />
  </div>
</template>

<script>
import SupervisorNav from '@/components/SupervisorNav.vue'

export default {
  name: 'SystemSettings',
  components: {
    SupervisorNav
  },
  data() {
    return {
      settings: {
        notifications: true,
        autoSync: false,
        twoFactorAuth: false
      }
    }
  },
  methods: {
    saveSettings() {
      console.log('Saving settings:', this.settings)
    },
    handleLogout() {
      // 清除用户信息和token
      localStorage.removeItem('userInfo')
      localStorage.removeItem('token')
      // 跳转到登录页
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.settings {
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

.settings-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.settings-section h2 {
  margin: 0 0 20px 0;
  font-size: 18px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
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

.save-btn {
  width: 100%;
  padding: 12px;
  background: #2196F3;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
}

/* 添加退出登录按钮样式 */
.logout-btn {
  width: 100%;
  padding: 12px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 20px;
}

.logout-btn:hover {
  background: #d32f2f;
}
</style>
