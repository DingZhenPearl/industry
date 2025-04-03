<template>
  <div class="account">
    <header class="header">
      <h1>账号管理</h1>
    </header>
    
    <div class="content">
      <div class="account-info">
        <div class="info-item">
          <label>用户名</label>
          <div class="value">{{ userInfo.username }}</div>
        </div>
        <div class="info-item">
          <label>角色</label>
          <div class="value">{{ userInfo.role === 'member' ? '产线工人' : '' }}</div>
        </div>
        <div class="info-item">
          <label>手机号</label>
          <div class="value">{{ userInfo.phone || '未设置' }}</div>
        </div>
      </div>

      <div class="action-list">
        <button class="action-btn" @click="changePassword">修改密码</button>
        <button class="action-btn" @click="updatePhone">更新手机号</button>
        <button class="action-btn logout" @click="handleLogout">退出登录</button>
      </div>
    </div>

    <WorkerNav />
  </div>
</template>

<script>
import WorkerNav from '@/components/WorkerNav.vue'

export default {
  name: 'WorkerAccount',
  components: {
    WorkerNav
  },
  data() {
    return {
      userInfo: JSON.parse(localStorage.getItem('userInfo') || '{}')
    }
  },
  methods: {
    changePassword() {
      // 实现修改密码逻辑
      console.log('修改密码')
    },
    updatePhone() {
      // 实现更新手机号逻辑
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

.account-info {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
}

.info-item {
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item label {
  color: #666;
  margin-bottom: 5px;
  display: block;
}

.info-item .value {
  color: #333;
  font-size: 16px;
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
}

.action-btn.logout {
  color: #ff4444;
}
</style>
