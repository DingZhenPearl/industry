<template>
  <div class="issues">
    <header class="header">
      <h1>故障上报</h1>
    </header>
    
    <div class="content">
      <div class="issues-content">
        <!-- 故障上报内容 -->
        <p>故障上报页面开发中...</p>
      </div>
    </div>

    <WorkerNav />
  </div>
</template>

<script>
import WorkerNav from '@/components/WorkerNav.vue'

export default {
  name: 'WorkerIssues',
  components: {
    WorkerNav
  }
}
</script>

<style scoped>
.issues {
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
