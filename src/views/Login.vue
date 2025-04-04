<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-side">
        <div class="logo">工厂智能管理系统</div>
        <div class="illustration"></div>
      </div>
      
      <div class="login-form-container">
        <h2 class="title">用户登录</h2>
        <p class="subtitle">欢迎回来，请登录您的账号</p>
        
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-wrapper">
            <div class="form-group">
              <label for="username">用户名</label>
              <div class="input-container">
                <i class="input-icon user-icon"></i>
                <input 
                  id="username" 
                  type="text" 
                  v-model="username" 
                  placeholder="请输入用户名"
                  required
                  class="modern-input"
                />
              </div>
            </div>
            
            <div class="form-group">
              <label for="password">密码</label>
              <div class="input-container">
                <i class="input-icon password-icon"></i>
                <input 
                  id="password" 
                  type="password" 
                  v-model="password" 
                  placeholder="请输入密码"
                  required
                  class="modern-input"
                />
              </div>
            </div>
            
            <div class="form-group">
              <label for="role">登录身份</label>
              <div class="input-container">
                <i class="input-icon role-icon"></i>
                <select 
                  id="role" 
                  v-model="role" 
                  required
                  class="modern-input"
                >
                  <option value="" disabled selected>请选择身份</option>
                  <option value="supervisor">厂长</option>
                  <option value="foreman">工长</option>
                  <option value="member">产线工人</option>
                  <option value="safety_officer">安全员</option>
                </select>
              </div>
            </div>
          </div>
          
          <button type="submit" class="login-btn">登 录</button>
          
          <div class="footer-note">
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginPage',
  data() {
    return {
      username: '',
      password: '',
      role: ''
    }
  },
  created() {
    // 如果已登录就直接跳转到对应的首页
    if (localStorage.getItem('token')) {
      const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
      this.redirectByRole(userInfo.role)
    }
  },
  methods: {
    handleLogin() {
      localStorage.setItem('userInfo', JSON.stringify({
        username: this.username,
        role: this.role
      }));
      localStorage.setItem('token', 'mock-token-' + Date.now());
      
      this.redirectByRole(this.role);
    },
    redirectByRole(role) {
      switch(role) {
        case 'supervisor':
          this.$router.push('/supervisor/monitor');
          break;
        case 'foreman':
          this.$router.push('/foreman/workorder');
          break;
        case 'member':
          this.$router.push('/worker/tasks');
          break;
        case 'safety_officer':
          this.$router.push('/safety/monitor');
          break;
        default:
          this.$router.push('/login');
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}

.login-content {
  display: flex;
  width: 900px;
  max-width: 100%;
  height: 600px;
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.05);
}

.login-side {
  flex: 1;
  background: linear-gradient(135deg, #4b6cb7 0%, #182848 100%);
  color: white;
  display: flex;
  flex-direction: column;
  padding: 40px;
  position: relative;
}

.logo {
  font-size: 22px;
  font-weight: 600;
  letter-spacing: 1px;
  margin-bottom: 30px;
}

.illustration {
  flex: 1;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" fill="none"><path d="M400 300C500 200 600 300 700 250" stroke="white" stroke-width="2" stroke-dasharray="5 5"/><path d="M100 350C200 300 300 400 400 300" stroke="white" stroke-width="2"/><circle cx="250" cy="350" r="50" fill="rgba(255,255,255,0.1)"/><circle cx="550" cy="250" r="100" fill="rgba(255,255,255,0.05)"/></svg>');
  background-repeat: no-repeat;
  background-position: center;
  background-size: contain;
}

.login-form-container {
  flex: 1;
  padding: 60px 40px;
  display: flex;
  flex-direction: column;
  min-width: 400px;
}

.login-form {
  width: 100%;
  max-width: 360px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  min-height: 450px; /* 设置最小高度 */
}

.form-wrapper {
  flex: 1;
  margin-bottom: 40px; /* 增加与footer的间距 */
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #555;
  font-weight: 500;
}

.input-container {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  opacity: 0.5;
}

.user-icon {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>');
}

.password-icon {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>');
}

.role-icon {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><line x1="20" y1="8" x2="20" y2="14"></line><line x1="23" y1="11" x2="17" y2="11"></line></svg>');
}

.modern-input {
  width: 100%;
  padding: 14px 14px 14px 40px;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.3s;
  background: #f9fafc;
  color: #333;
}

.modern-input:focus {
  border-color: #4b6cb7;
  box-shadow: 0 0 0 3px rgba(75, 108, 183, 0.15);
  outline: none;
  background: white;
}

.login-btn {
  width: 100%;
  padding: 14px;
  margin: 24px 0;
  background: #4b6cb7;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(75, 108, 183, 0.25);
}

.login-btn:hover {
  background: #3a5aa1;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(75, 108, 183, 0.35);
}

.login-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(75, 108, 183, 0.25);
}

.footer-note {
  margin-top: auto;
  padding: 20px 40px;
  text-align: center;
  font-size: 13px;
  color: #888;
  position: relative; /* 改为相对定位 */
  padding: 0 40px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .login-content {
    flex-direction: column;
    height: auto;
  }
  
  .login-side {
    display: none;
  }
  
  .login-form-container {
    min-width: auto; /* 移动端取消最小宽度限制 */
    padding: 40px 20px; /* 减小内边距 */
  }
  
  .login-form {
    max-width: 100%;
    margin-bottom: 100px; /* 增加底部间距 */
    min-height: 400px; /* 移动端稍微减小最小高度 */
  }

  .footer-note {
    position: relative; /* 移动端使用相对定位 */
    bottom: auto;
    margin-top: 40px;
    padding: 20px;
  }
}

/* 动画效果 */
.login-form-container, .login-side {
  animation: fadeIn 0.6s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>