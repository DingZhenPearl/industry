<template>
  <div class="account">
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
          <div class="role-badge">班组长</div>
        </div>
      </div>
      
      <!-- 个人信息卡片 -->
      <div class="info-card">
        <h3 class="card-title">个人信息</h3>
        <div class="info-item">
          <label>工号</label>
          <div class="value">{{ userInfo.employee_id || '未分配' }}</div>
        </div>
        <div class="info-item">
          <label>用户名</label>
          <div class="value">
            {{ userInfo.username }}
            <button class="edit-btn" @click="showUpdateUsernameDialog">
              <i class="icon-edit"></i>
              编辑
            </button>
          </div>
        </div>
        <div class="info-item">
          <label>角色</label>
          <div class="value">{{ userInfo.role === 'foreman' ? '班组长' : '' }}</div>
        </div>
        <div class="info-item">
          <label>手机号</label>
          <div class="value">{{ userInfo.phone || '未设置' }}</div>
        </div>
      </div>

      <!-- 团队管理统计 -->
      <div class="info-card">
        <h3 class="card-title">团队管理</h3>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">8</div>
            <div class="stat-label">团队成员</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">15</div>
            <div class="stat-label">待分配工单</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">92%</div>
            <div class="stat-label">团队效率</div>
          </div>
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

    <ForemanNav />

    <!-- 更新用户名对话框 -->
    <div v-if="showDialog" class="dialog-overlay">
      <div class="dialog">
        <h3>更新用户名</h3>
        <div class="dialog-content">
          <input
            type="text"
            v-model="newUsername"
            placeholder="请输入新的用户名"
            class="input"
          >
          <div class="error-message" v-if="updateError">{{ updateError }}</div>
        </div>
        <div class="dialog-actions">
          <button class="cancel-btn" @click="cancelUpdate">取消</button>
          <button class="confirm-btn" @click="confirmUpdate">确认</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ForemanNav from '@/components/ForemanNav.vue'

export default {
  name: 'ForemanAccount',
  components: {
    ForemanNav
  },
  data() {
    return {
      userInfo: JSON.parse(localStorage.getItem('userInfo') || '{}'),
      showDialog: false,
      newUsername: '',
      updateError: ''
    }
  },
  methods: {
    changePassword() {
      this.$prompt('请输入新密码', '修改密码', {
        inputType: 'password',
        confirmButtonText: '确认',
        cancelButtonText: '取消'
      }).then(async ({ value: newPassword }) => {
        try {
          const data = await fetch('http://localhost:3000/api/update-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              newPassword,
              role: this.userInfo.role,
              username: this.userInfo.username
            }),
            credentials: 'include'
          }).then(res => res.json());

          if (data.success) {
            this.$message.success('密码更新成功');
          } else {
            this.$message.error(data.error || '密码更新失败');
          }
        } catch (error) {
          this.$message.error('服务器连接失败');
        }
      }).catch(() => {});
    },
    
    updatePhone() {
      this.$prompt('请输入新手机号', '更新手机号', {
        inputPattern: /^1[3-9]\d{9}$/,
        inputErrorMessage: '请输入有效的手机号',
        confirmButtonText: '确认',
        cancelButtonText: '取消'
      }).then(async ({ value: phone }) => {
        try {
          const response = await fetch('http://localhost:3000/api/update-phone', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              phone,
              role: this.userInfo.role,
              username: this.userInfo.username
            }),
            credentials: 'include'
          });
          
          const data = await response.json();
          if (data.success) {
            this.userInfo.phone = phone;
            localStorage.setItem('userInfo', JSON.stringify(this.userInfo));
            this.$message.success('手机号更新成功');
          } else {
            this.$message.error(data.error || '手机号更新失败');
          }
        } catch (error) {
          this.$message.error('服务器连接失败');
        }
      }).catch(() => {});
    },
    async handleLogout() {
      try {
        // 调用后端登出接口
        await fetch('http://localhost:3000/api/logout', {
          method: 'POST',
          credentials: 'include'
        });
      } catch (error) {
        console.error('登出请求失败:', error);
      } finally {
        // 清理所有本地存储
        localStorage.clear();
        this.$router.push('/login');
      }
    },
    showUpdateUsernameDialog() {
      this.showDialog = true;
      this.newUsername = this.userInfo.username;
      this.updateError = '';
    },
    cancelUpdate() {
      this.showDialog = false;
      this.newUsername = '';
      this.updateError = '';
    },
    async confirmUpdate() {
      if (!this.newUsername.trim()) {
        this.updateError = '用户名不能为空';
        return;
      }

      try {
        const response = await fetch('http://localhost:3000/api/update-username', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: this.newUsername,
            role: this.userInfo.role,
            currentUsername: this.userInfo.username
          }),
          credentials: 'include'
        });

        const data = await response.json();

        if (data.success) {
          this.userInfo.username = this.newUsername;
          localStorage.setItem('userInfo', JSON.stringify(this.userInfo));
          this.showDialog = false;
          this.updateError = '';
        } else {
          this.updateError = data.error || '更新失败';
        }
      } catch (error) {
        console.error('更新用户名时出错:', error);
        this.updateError = '服务器连接失败，请稍后重试';
      }
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
  border: 3px solid #e3f2fd;
  box-shadow: 0 4px 8px rgba(33, 150, 243, 0.2);
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
  color: #ff4444;
}

.edit-btn {
  margin-left: 10px;
  padding: 2px 8px;
  border: 1px solid #2196F3;
  border-radius: 4px;
  color: #2196F3;
  background: transparent;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s;
}

.edit-btn:hover {
  background: #2196F3;
  color: white;
}

.icon-edit:before {
  content: '✏️';
  margin-right: 4px;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog {
  background: white;
  border-radius: 12px;
  padding: 20px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.dialog h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.dialog-content {
  margin-bottom: 20px;
}

.input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  margin-bottom: 10px;
  font-size: 14px;
  transition: all 0.3s;
}

.input:focus {
  border-color: #2196F3;
  outline: none;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}

.error-message {
  color: #ff4444;
  font-size: 14px;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.cancel-btn,
.confirm-btn {
  padding: 8px 20px;
  border-radius: 8px;
  cursor: pointer;
  border: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.cancel-btn {
  background: #f5f5f5;
  color: #666;
}

.cancel-btn:hover {
  background: #e8e8e8;
}

.confirm-btn {
  background: #2196F3;
  color: white;
}

.confirm-btn:hover {
  background: #1976D2;
}
</style>
