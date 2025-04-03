<template>
  <div class="login-container">
    <div class="login-form">
      <h2 class="title">工厂产线管理系统</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <input 
            id="username" 
            type="text" 
            v-model="username" 
            placeholder="用户名"
            required
            class="modern-input"
          />
        </div>
        <div class="form-group">
          <input 
            id="password" 
            type="password" 
            v-model="password" 
            placeholder="密码"
            required
            class="modern-input"
          />
        </div>
        <div class="form-group">
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
        <button type="submit" class="login-btn">登 录</button>
        <div class="footer-note">
          <p>请使用工厂授权的账号登录系统</p>
          <p>如有问题请联系IT部门: 123-456789</p>
        </div>
      </form>
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
    // 如果已登录就直接跳转到首页
    if (localStorage.getItem('token')) {
      this.$router.push('/home');
    }
  },
  methods: {
    handleLogin() {
      // 模拟登录成功，存储登录信息
      localStorage.setItem('userInfo', JSON.stringify({
        username: this.username,
        role: this.role
      }));
      localStorage.setItem('token', 'mock-token-' + Date.now());
      
      // 跳转到首页
      this.$router.push('/home');
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
  background: linear-gradient(135deg, #2c3e50 0%, #4a6b8a 100%);
  padding: 20px;
}

.login-form {
  width: 100%;
  max-width: 420px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
}

.title {
  text-align: center;
  margin-bottom: 32px;
  color: #2c3e50;
  font-size: 28px;
  font-weight: 600;
}

.form-group {
  margin-bottom: 24px;
}

.modern-input {
  width: 100%;
  padding: 14px 16px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.9);
}

.modern-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
  outline: none;
}

.login-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(to right, #2c3e50, #4a6b8a);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.social-login {
  margin-top: 32px;
}

.divider {
  text-align: center;
  position: relative;
  margin-bottom: 24px;
  color: #7f8c8d;
}

.divider::before,
.divider::after {
  content: "";
  position: absolute;
  top: 50%;
  width: 45%;
  height: 1px;
  background: rgba(0, 0, 0, 0.1);
}

.divider::before {
  left: 0;
}

.divider::after {
  right: 0;
}

.social-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.social-btn {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
}

.social-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.social-btn.google {
  background: #db4437;
}

.social-btn.github {
  background: #24292e;
}

.social-btn.wechat {
  background: #07c160;
}
</style>