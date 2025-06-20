import Vue from 'vue'
import App from './App.vue'
import router from './router'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import './assets/mobile.css'; // 导入移动端样式
import './assets/android.css'; // 导入安卓特定样式
import config from './config'; // 导入配置文件
import { Capacitor } from '@capacitor/core'; // 导入Capacitor
import { request } from './services/http'; // 导入HTTP服务模块
import AndroidAdapter from './plugins/AndroidAdapter'; // 导入安卓适配插件

Vue.use(ElementUI);
Vue.use(AndroidAdapter); // 使用安卓适配插件

Vue.config.productionTip = false

// 检查是否在原生平台运行
const isNative = Capacitor.isNativePlatform();
console.log('是否在原生平台运行:', isNative);

// 添加请求拦截器
const originalFetch = window.fetch;
window.fetch = async function (...args) {
  let [resource, fetchConfig] = args;

  // 如果在原生环境中，使用我们的HTTP服务模块
  if (isNative) {
    console.log('在原生环境中使用自定义HTTP服务模块');
    return request(resource, fetchConfig);
  }

  // 在Web环境中，使用修改后的fetch
  const token = localStorage.getItem('token');
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');

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
      // 使用统一的服务器配置构建完整URL
      resource = config.buildApiUrl(resource);
      console.log('使用统一配置构建的URL:', resource);
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
