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

  return originalFetch.call(this, resource, config);
};

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')
