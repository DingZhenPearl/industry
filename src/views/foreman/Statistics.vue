<template>
  <div class="statistics">
    <header class="header">
      <h1>统计分析</h1>
    </header>
    
    <div class="content">
      <div class="statistics-content">
        <!-- 统计分析内容 -->
        <p>统计分析页面开发中...</p>
      </div>
    </div>

    <ForemanNav />
  </div>
</template>

<script>
import ForemanNav from '@/components/ForemanNav.vue'

export default {
  name: 'ForemanStatistics',
  components: {
    ForemanNav
  }
}
</script>

<style scoped>
.statistics {
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
</style>
