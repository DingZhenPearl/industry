<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-side">
        <div class="logo">工厂智能管理系统</div>
        <div class="illustration"></div>
      </div>

      <div class="login-form-container">
        <h2 class="title">{{ isRegistering ? '用户注册' : '用户登录' }}</h2>
        <p class="subtitle">{{ isRegistering ? '欢迎注册新账号' : '欢迎回来，请登录您的账号' }}</p>

        <div class="toggle-container">
          <button
            :class="['toggle-btn', { active: !isRegistering }]"
            @click="isRegistering = false"
          >登录</button>
          <button
            :class="['toggle-btn', { active: isRegistering }]"
            @click="isRegistering = true"
          >注册</button>
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-wrapper">
            <div class="form-group" v-if="!isRegistering">
              <label for="employee_id">工号</label>
              <div class="input-container">
                <i class="input-icon user-icon"></i>
                <input
                  id="employee_id"
                  type="text"
                  v-model="employee_id"
                  placeholder="请输入工号"
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

            <div v-if="isRegistering" class="form-group">
              <label for="confirmPassword">确认密码</label>
              <div class="input-container">
                <i class="input-icon password-icon"></i>
                <input
                  id="confirmPassword"
                  type="password"
                  v-model="confirmPassword"
                  required
                  placeholder="请再次输入密码"
                  class="modern-input"
                />
              </div>
            </div>

            <div class="form-group">
              <label for="role">{{ isRegistering ? '注册身份' : '登录身份' }}</label>
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

          <div v-if="error" :class="{'error-message': !error.includes('注册成功'), 'success-message': error.includes('注册成功')}">{{ error }}</div>

          <button type="submit" class="login-btn">{{ isRegistering ? '注 册' : '登 录' }}</button>

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
      employee_id: '',
      password: '',
      confirmPassword: '',
      role: '',
      error: '',
      loading: false,
      isRegistering: false
    }
  },
  created() {
    // 如果已登录就直接跳转到对应的首页
    const token = localStorage.getItem('token');
    if (token) {
      const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
      this.redirectByRole(userInfo.role, userInfo.uid)
    }
  },
  methods: {
    async handleLogin() {
      if (this.loading) return;

      // 表单验证
      if (this.isRegistering && this.password !== this.confirmPassword) {
        this.error = '两次输入的密码不一致';
        return;
      }

      this.loading = true;
      this.error = '';

      try {
        const endpoint = this.isRegistering ? 'register' : 'login';
        const requestBody = this.isRegistering
          ? {
              password: this.password,
              role: this.role
            }
          : {
              employee_id: this.employee_id,
              password: this.password,
              role: this.role
            };

        const response = await fetch(`http://localhost:3000/api/${endpoint}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestBody),
          credentials: 'include'
        });

        const data = await response.json();

        if (this.isRegistering) {
          if (data.success) {
            this.error = '';
            this.isRegistering = false;
            this.password = '';
            this.confirmPassword = '';
            this.$nextTick(() => {
              if (data.employee_id) {
                this.error = `注册成功，您的工号是: ${data.employee_id}，请使用工号登录`;
                // 自动填充工号到登录表单
                this.employee_id = data.employee_id;
              } else {
                this.error = '注册成功，请登录';
              }
            });
          } else {
            this.error = data.error || '注册失败';
          }
        } else {
          if (response.ok && data.success) {
            // 确保保存完整的用户信息,包括group_id和uid
            const userInfo = {
              username: data.user.username,
              role: data.user.role,
              phone: data.user.phone,
              employee_id: data.user.employee_id,
              group_id: data.user.group_id,  // 确保保存组号
              uid: data.user.uid  // 保存用户唯一标识符
            };
            localStorage.setItem('userInfo', JSON.stringify(userInfo));
            localStorage.setItem('token', 'session-' + Date.now());
            this.redirectByRole(data.user.role, data.user.uid);
          } else {
            this.error = data.error || '登录失败，请重试';
          }
        }
      } catch (error) {
        this.error = '服务器连接失败，请稍后重试';
        console.error('请求错误:', error);
      } finally {
        this.loading = false;
      }
    },
    redirectByRole(role, uid) {
      // 获取uid，如果没有传入，尝试从本地存储中获取
      if (!uid) {
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
        uid = userInfo.uid;
      }

      // 构建带有uid参数的URL
      const uidParam = uid ? `?uid=${uid}` : '';

      switch(role) {
        case 'supervisor':
          this.$router.push(`/supervisor/monitor${uidParam}`);
          break;
        case 'foreman':
          this.$router.push(`/foreman/workorder${uidParam}`);
          break;
        case 'member':
          this.$router.push(`/worker/workorders${uidParam}`);
          break;
        case 'safety_officer':
          this.$router.push(`/safety-officer/monitoring${uidParam}`);
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
  padding: 20px 30px;
  display: flex;
  flex-direction: column;
  min-width: 400px;
}

.title {
  margin-bottom: 8px;
}

.subtitle {
  margin-bottom: 16px;
}

.form-group {
  margin-bottom: 10px;
}

.login-form {
  width: 100%;
  max-width: 360px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  min-height: 320px;
}

.form-wrapper {
  flex: 1;
  margin-bottom: 5px;
}

.form-group {
  margin-bottom: 12px;
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
  padding: 10px 10px 10px 36px;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s;
  background: #f9fafc;
  color: #333;
}

.input-container {
  position: relative;
  height: 38px;
}

.modern-input:focus {
  border-color: #4b6cb7;
  box-shadow: 0 0 0 3px rgba(75, 108, 183, 0.15);
  outline: none;
  background: white;
}

.login-btn {
  width: 100%;
  padding: 12px;
  margin: 8px 0;
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
.toggle-container {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
  background: #f5f7fa;
  padding: 4px;
  border-radius: 8px;
  width: 100%;
}

.toggle-btn {
  flex: 1;
  padding: 10px 24px;
  border: none;
  background: transparent;
  color: #666;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 6px;
}

.toggle-btn.active {
  background: #4b6cb7;
  color: white;
  box-shadow: 0 2px 8px rgba(75, 108, 183, 0.25);
}

.toggle-btn:hover:not(.active) {
  color: #4b6cb7;
  background: rgba(75, 108, 183, 0.1);
}

.error-message {
  color: #e53935;
  font-size: 14px;
  margin: 10px 0;
  padding: 8px 12px;
  background-color: rgba(229, 57, 53, 0.1);
  border-radius: 6px;
  text-align: center;
}

.success-message {
  color: #43a047;
  font-size: 14px;
  margin: 10px 0;
  padding: 8px 12px;
  background-color: rgba(67, 160, 71, 0.1);
  border-radius: 6px;
  text-align: center;
  font-weight: 500;
}
</style>