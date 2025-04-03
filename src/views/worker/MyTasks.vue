<template>
  <div class="my-tasks">
    <header class="header">
      <h1>我的任务</h1>
    </header>
    
    <div class="content">
      <div class="tasks-content">
        <!-- 任务列表内容 -->
        <p>我的任务页面开发中...</p>
      </div>
    </div>

    <WorkerNav />
  </div>
</template>

<script>
import WorkerNav from '@/components/WorkerNav.vue'

export default {
  name: 'MyTasks',
  components: {
    WorkerNav
  }
}
</script>

<style scoped>
.my-tasks {
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
