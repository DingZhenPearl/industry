<template>
  <div class="knowledge">
    <header class="header">
      <h1>知识库</h1>
    </header>
    
    <div class="content">
      <!-- 搜索框 -->
      <div class="search-container">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜索知识库内容..."
          class="search-input"
        />
        <button class="search-btn" @click="searchKnowledge">搜索</button>
      </div>

      <!-- 知识库卡片 -->
      <div class="knowledge-cards">
        <!-- 设备维修指南 -->
        <div class="knowledge-card" @click="openSection('repair')">
          <div class="card-icon repair-icon"></div>
          <div class="card-content">
            <h3>设备维修指南</h3>
            <p>查看各类设备的维修手册和常见问题解决方案</p>
          </div>
          <i class="arrow-icon"></i>
        </div>

        <!-- 故障解决方案 -->
        <div class="knowledge-card" @click="openSection('troubleshoot')">
          <div class="card-icon troubleshoot-icon"></div>
          <div class="card-content">
            <h3>故障解决方案</h3>
            <p>常见故障的诊断和解决步骤</p>
          </div>
          <i class="arrow-icon"></i>
        </div>

        <!-- 操作手册 -->
        <div class="knowledge-card" @click="openSection('manual')">
          <div class="card-icon manual-icon"></div>
          <div class="card-content">
            <h3>操作手册查询</h3>
            <p>各类设备和系统的标准操作流程</p>
          </div>
          <i class="arrow-icon"></i>
        </div>

        <!-- 视频教程 -->
        <div class="knowledge-card" @click="openSection('video')">
          <div class="card-icon video-icon"></div>
          <div class="card-content">
            <h3>视频教程</h3>
            <p>设备操作和维护的视频指导</p>
          </div>
          <i class="arrow-icon"></i>
        </div>
      </div>

      <!-- 内容详情模态框 -->
      <div class="modal" v-if="showModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>{{ modalTitle }}</h2>
            <span class="close-btn" @click="closeModal">&times;</span>
          </div>
          <div class="modal-body">
            <p v-if="currentSection === 'empty'">选择一个类别查看详细内容</p>
            <div v-else-if="currentSection === 'repair'">
              <h3>设备维修指南</h3>
              <ul class="document-list">
                <li v-for="(doc, index) in repairDocs" :key="index" @click="viewDocument(doc)">
                  <span class="doc-icon"></span>
                  <span class="doc-title">{{ doc.title }}</span>
                  <span class="doc-type">{{ doc.type }}</span>
                </li>
              </ul>
            </div>
            <div v-else-if="currentSection === 'troubleshoot'">
              <h3>故障解决方案</h3>
              <ul class="document-list">
                <li v-for="(doc, index) in troubleshootDocs" :key="index" @click="viewDocument(doc)">
                  <span class="doc-icon"></span>
                  <span class="doc-title">{{ doc.title }}</span>
                  <span class="doc-type">{{ doc.type }}</span>
                </li>
              </ul>
            </div>
            <div v-else-if="currentSection === 'manual'">
              <h3>操作手册查询</h3>
              <ul class="document-list">
                <li v-for="(doc, index) in manualDocs" :key="index" @click="viewDocument(doc)">
                  <span class="doc-icon"></span>
                  <span class="doc-title">{{ doc.title }}</span>
                  <span class="doc-type">{{ doc.type }}</span>
                </li>
              </ul>
            </div>
            <div v-else-if="currentSection === 'video'">
              <h3>视频教程</h3>
              <ul class="document-list">
                <li v-for="(doc, index) in videoDocs" :key="index" @click="viewDocument(doc)">
                  <span class="video-doc-icon"></span>
                  <span class="doc-title">{{ doc.title }}</span>
                  <span class="doc-duration">{{ doc.duration }}</span>
                </li>
              </ul>
            </div>
            <div v-else-if="currentSection === 'document'" class="document-viewer">
              <h3>{{ currentDocument.title }}</h3>
              <div class="document-content">
                <p>{{ currentDocument.content }}</p>
              </div>
            </div>
          </div>
        </div>
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
  },
  data() {
    return {
      searchQuery: '',
      showModal: false,
      modalTitle: '',
      currentSection: 'empty',
      currentDocument: null,
      repairDocs: [
        { id: 1, title: '注塑机维修手册', type: 'PDF', content: '这是注塑机维修手册的内容...' },
        { id: 2, title: '装配线电机故障排查', type: 'DOC', content: '这是装配线电机故障排查的内容...' },
        { id: 3, title: '传送带维护指南', type: 'PDF', content: '这是传送带维护指南的内容...' }
      ],
      troubleshootDocs: [
        { id: 4, title: '电气系统常见故障', type: 'PDF', content: '这是电气系统常见故障的内容...' },
        { id: 5, title: '液压系统故障诊断', type: 'DOC', content: '这是液压系统故障诊断的内容...' },
        { id: 6, title: '传感器校准问题', type: 'PDF', content: '这是传感器校准问题的内容...' }
      ],
      manualDocs: [
        { id: 7, title: '生产线操作规程', type: 'PDF', content: '这是生产线操作规程的内容...' },
        { id: 8, title: '质量检测标准流程', type: 'DOC', content: '这是质量检测标准流程的内容...' },
        { id: 9, title: '安全操作指南', type: 'PDF', content: '这是安全操作指南的内容...' }
      ],
      videoDocs: [
        { id: 10, title: '设备启动与关闭流程', duration: '5:30', content: '视频内容：设备启动与关闭流程' },
        { id: 11, title: '日常维护操作演示', duration: '8:45', content: '视频内容：日常维护操作演示' },
        { id: 12, title: '故障排除实战指导', duration: '12:20', content: '视频内容：故障排除实战指导' }
      ]
    }
  },
  methods: {
    searchKnowledge() {
      // 实现搜索功能
      console.log('搜索:', this.searchQuery);
      // 这里可以添加实际的搜索逻辑
    },
    openSection(section) {
      this.currentSection = section;
      switch(section) {
        case 'repair':
          this.modalTitle = '设备维修指南';
          break;
        case 'troubleshoot':
          this.modalTitle = '故障解决方案';
          break;
        case 'manual':
          this.modalTitle = '操作手册查询';
          break;
        case 'video':
          this.modalTitle = '视频教程';
          break;
      }
      this.showModal = true;
    },
    viewDocument(doc) {
      this.currentDocument = doc;
      this.currentSection = 'document';
      this.modalTitle = doc.title;
    },
    closeModal() {
      this.showModal = false;
      this.currentSection = 'empty';
    }
  }
}
</script>

<style scoped>
.knowledge {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding-bottom: 60px;
  background-color: #f5f5f5;
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

/* 搜索框样式 */
.search-container {
  display: flex;
  margin-bottom: 15px;
}

.search-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
  font-size: 14px;
}

.search-btn {
  background-color: #2196F3;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

/* 知识库卡片样式 */
.knowledge-cards {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.knowledge-card {
  display: flex;
  align-items: center;
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.2s;
}

.knowledge-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.card-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 15px;
  background-color: #e3f2fd;
  display: flex;
  align-items: center;
  justify-content: center;
}

.repair-icon {
  background-color: #e3f2fd;
}

.troubleshoot-icon {
  background-color: #fff8e1;
}

.manual-icon {
  background-color: #e8f5e9;
}

.video-icon {
  background-color: #ffebee;
}

.card-content {
  flex: 1;
}

.card-content h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
}

.card-content p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.arrow-icon {
  width: 20px;
  height: 20px;
  opacity: 0.5;
}

/* 模态框样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 15px;
}

/* 文档列表样式 */
.document-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.document-list li {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
  cursor: pointer;
}

.document-list li:hover {
  background-color: #f9f9f9;
}

.doc-icon, .video-doc-icon {
  width: 24px;
  height: 24px;
  margin-right: 10px;
  background-color: #e3f2fd;
  border-radius: 4px;
}

.video-doc-icon {
  background-color: #ffebee;
}

.doc-title {
  flex: 1;
  font-size: 14px;
}

.doc-type, .doc-duration {
  font-size: 12px;
  color: #666;
  margin-left: 10px;
}

/* 文档查看器样式 */
.document-viewer {
  padding: 10px;
}

.document-content {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 4px;
  margin-top: 10px;
}
</style>
