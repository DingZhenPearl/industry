<template>
  <div class="profile">
    <header class="header">
      <h1>我的</h1>
    </header>
    
    <div class="content">
      <!-- 用户信息卡片 -->
      <div class="user-card">
        <div class="avatar">
          <img src="@/assets/avatar.svg" alt="用户头像">
        </div>
        <div class="user-info">
          <h2 class="username">test-zg</h2>
          <p class="team-info">班组: 暂无</p>
          
          <div class="department-position">
            <div class="department">
              <p class="label">部门</p>
              <p class="value">运维部门</p>
            </div>
            <div class="divider"></div>
            <div class="position">
              <p class="label">职位</p>
              <p class="value">主管</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 电话信息 -->
      <div class="phone-info">
        <div class="phone-icon">
          <i class="icon-phone"></i>
        </div>
        <span>电话信息</span>
        <span class="phone-number">13888086606</span>
      </div>
      
      <!-- 功能菜单列表 -->
      <div class="menu-list">
        <div class="menu-item" @click="goToPersonalInfo">
          <div class="menu-icon">
            <i class="icon-person"></i>
          </div>
          <span class="menu-text">个人信息</span>
          <i class="icon-arrow"></i>
        </div>
        
        <div class="menu-item" @click="goToStaffManagement">
          <div class="menu-icon">
            <i class="icon-staff"></i>
          </div>
          <span class="menu-text">人员管理</span>
          <i class="icon-arrow"></i>
        </div>
        
        <div class="menu-item" @click="logout">
          <div class="menu-icon">
            <i class="icon-logout"></i>
          </div>
          <span class="menu-text">退出登录</span>
          <i class="icon-arrow"></i>
        </div>
      </div>
    </div>
    
    <nav class="bottom-nav">
      <div class="nav-item" @click="$router.push('/')">
        <i class="nav-icon home-icon"></i>
        <span>首页</span>
      </div>
      <div class="nav-item" @click="$router.push('/task')">
        <i class="nav-icon task-icon"></i>
        <span>任务</span>
      </div>
      <div class="nav-item" @click="$router.push('/notification')">
        <i class="nav-icon notification-icon"></i>
        <span>通知</span>
      </div>
      <div class="nav-item active">
        <i class="nav-icon profile-icon"></i>
        <span>我的</span>
      </div>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'ProfilePage',
  methods: {
    goToPersonalInfo() {
      // 跳转到个人信息页面
      console.log('跳转到个人信息页面')
    },
    goToStaffManagement() {
      // 跳转到人员管理页面
      console.log('跳转到人员管理页面')
    },
    logout() {
      // 退出登录
      console.log('退出登录')
    }
  }
}
</script>

<style scoped>
.profile {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
}

.header {
  background-color: #2196F3;
  color: white;
  padding: 15px 0;
  text-align: center;
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow-y: auto;
}

/* 用户信息卡片样式 */
.user-card {
  background-color: white;
  padding: 20px;
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  overflow: hidden;
  background-color: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-info {
  flex: 1;
}

.username {
  font-size: 18px;
  font-weight: bold;
  margin: 0 0 5px 0;
}

.team-info {
  font-size: 14px;
  color: #666;
  margin: 0 0 10px 0;
}

.department-position {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin-top: 10px;
}

.department, .position {
  text-align: center;
  flex: 1;
}

.divider {
  width: 1px;
  height: 40px;
  background-color: #e0e0e0;
  margin: 0 15px;
}

.label {
  font-size: 12px;
  color: #999;
  margin: 0;
}

.value {
  font-size: 16px;
  font-weight: bold;
  margin: 5px 0 0 0;
}

/* 电话信息样式 */
.phone-info {
  background-color: white;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.phone-icon {
  width: 24px;
  height: 24px;
  background-color: #e0e0e0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
}

.icon-phone::before {
  content: '📞';
  font-size: 14px;
}

.phone-number {
  margin-left: auto;
  color: #666;
}

/* 菜单列表样式 */
.menu-list {
  background-color: white;
}

.menu-item {
  padding: 15px 20px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
}

.menu-icon {
  width: 24px;
  height: 24px;
  background-color: #e0e0e0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
}

.icon-person::before {
  content: '👤';
  font-size: 14px;
}

.icon-staff::before {
  content: '👥';
  font-size: 14px;
}

.icon-logout::before {
  content: '🚪';
  font-size: 14px;
}

.menu-text {
  flex: 1;
}

.icon-arrow::after {
  content: '>';
  color: #ccc;
}

/* 底部导航栏样式 */
.bottom-nav {
  display: flex;
  justify-content: space-around;
  background-color: #f8f8f8;
  padding: 10px 0;
  border-top: 1px solid #e0e0e0;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}

.nav-icon {
  width: 24px;
  height: 24px;
  margin-bottom: 5px;
  background-color: #666;
  border-radius: 50%;
}

.nav-item.active {
  color: #2196F3;
}

.nav-item.active .nav-icon {
  background-color: #2196F3;
}
</style>