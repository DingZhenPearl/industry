import Vue from 'vue'
import App from './App.vue'
import router from './router'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';

Vue.use(ElementUI);

Vue.config.productionTip = false

// 添加请求拦截器
const originalFetch = window.fetch;
window.fetch = function (...args) {
  const token = localStorage.getItem('token');
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
  let [resource, config] = args;

  if (!config) {
    config = {};
  }

  if (!config.headers) {
    config.headers = {};
  }

  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }

  // 如果是API请求且用户有uid，添加uid参数
  if (resource.includes('/api/') && userInfo.uid) {
    // 判断是GET请求还是POST请求
    if (!config.method || config.method.toUpperCase() === 'GET') {
      // GET请求，将uid添加到URL参数
      const separator = resource.includes('?') ? '&' : '?';
      resource = `${resource}${separator}uid=${userInfo.uid}`;
    } else {
      // POST请求，将uid添加到请求体
      if (!config.body) {
        config.body = JSON.stringify({ uid: userInfo.uid });
      } else {
        try {
          const body = JSON.parse(config.body);
          body.uid = userInfo.uid;
          config.body = JSON.stringify(body);
        } catch (e) {
          // 如果请求体不是JSON格式，忽略错误
          console.warn('无法将uid添加到非JSON格式的请求体');
        }
      }
    }
  }

  return originalFetch.call(this, resource, config);
};

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')
