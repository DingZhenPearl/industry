<template>
  <div class="team">
    <header class="header">
      <h1>团队管理</h1>
    </header>
    
    <div class="content">
      <div class="team-content">
        <!-- 团队管理内容 -->
        <p>团队管理页面开发中...</p>
      </div>
    </div>

    <ForemanNav />
  </div>
</template>

<script>
import ForemanNav from '@/components/ForemanNav.vue'

export default {
  name: 'ForemanTeam',
  components: {
    ForemanNav
  }
}
</script>

<style scoped>
.team {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding-bottom: 60px;
}

.header {
  background-color: #2196F3;
  color: white;
  padding: 15px;
}

.content {
  flex: 1;
  padding: 15px;
}
</style>
