import Vue from 'vue'
import App from './App.vue'
import router from './router'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import './assets/mobile.css'; // 导入移动端样式
import config from './config'; // 导入配置文件

Vue.use(ElementUI);

Vue.config.productionTip = false

// 添加请求拦截器
const originalFetch = window.fetch;
window.fetch = function (...args) {
  const token = localStorage.getItem('token');
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
  let [resource, fetchConfig] = args;

  if (!fetchConfig) {
    fetchConfig = {};
  }

  if (!fetchConfig.headers) {
    fetchConfig.headers = {};
  }

  if (token) {
    fetchConfig.headers['Authorization'] = `Bearer ${token}`;
  }

  // 如果是API请求
  if (resource.includes('/api/')) {
    // 在移动应用中，添加完整的API基础URL
    if (config.isMobileApp && resource.indexOf('http') !== 0) {
      resource = `${config.apiBaseUrl}${resource}`;
    }

    // 如果用户有uid，添加uid参数
    if (userInfo.uid) {
      // 判断是GET请求还是POST请求
      if (!fetchConfig.method || fetchConfig.method.toUpperCase() === 'GET') {
        // GET请求，将uid添加到URL参数
        const separator = resource.includes('?') ? '&' : '?';
        resource = `${resource}${separator}uid=${userInfo.uid}`;
      } else {
        // POST请求，将uid添加到请求体
        if (!fetchConfig.body) {
          fetchConfig.body = JSON.stringify({ uid: userInfo.uid });
        } else {
          try {
            const body = JSON.parse(fetchConfig.body);
            body.uid = userInfo.uid;
            fetchConfig.body = JSON.stringify(body);
          } catch (e) {
            // 如果请求体不是JSON格式，忽略错误
            console.warn('无法将uid添加到非JSON格式的请求体');
          }
        }
      }
    }
  }

  return originalFetch.call(this, resource, fetchConfig);
};

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')
