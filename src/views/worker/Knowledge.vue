<template>
  <div class="knowledge">
    <header class="header">
      <h1>知识库</h1>
    </header>
    
    <div class="content">
      <div class="knowledge-content">
        <!-- 知识库内容 -->
        <p>知识库页面开发中...</p>
      </div>
    </div>

    <WorkerNav />
  </div>
</template>

<script>
import WorkerNav from '@/components/WorkerNav.vue'

export default {
  name: 'WorkerKnowledge',
  components: {
    WorkerNav
  }
}
</script>

<style scoped>
.knowledge {
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
