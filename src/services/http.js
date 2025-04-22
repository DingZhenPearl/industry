// HTTP服务模块 - 使用Capacitor的HTTP API
import { Capacitor } from '@capacitor/core';
import config from '../config';

// 检查是否在Capacitor环境中运行
const isNative = Capacitor.isNativePlatform();
console.log('是否在原生平台运行:', isNative);

// 动态导入Capacitor HTTP插件
// 注意：在Web环境中，我们仍然使用fetch API
let CapacitorHttp = null;
if (isNative) {
  try {
    // 在原生环境中导入Capacitor HTTP
    import('@capacitor/core').then(module => {
      CapacitorHttp = module.CapacitorHttp;
      console.log('已加载Capacitor HTTP插件');
    }).catch(err => {
      console.error('加载Capacitor HTTP插件失败:', err);
    });
  } catch (error) {
    console.error('导入Capacitor HTTP时出错:', error);
  }
}

/**
 * 发送HTTP请求
 * @param {string} url - 请求URL
 * @param {Object} options - 请求选项
 * @returns {Promise} - 返回Promise
 */
export async function request(url, options = {}) {
  // 获取用户信息和token
  const token = localStorage.getItem('token');
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');

  // 构建请求头
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };

  // 如果有token，添加到请求头
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // 处理API请求URL
  if (url.includes('/api/')) {
    console.log('原始请求URL:', url);

    // 在移动应用中，添加完整的API基础URL
    if (config.isMobileApp && !url.startsWith('http')) {
      // 使用统一的服务器配置构建URL
      url = config.buildApiUrl(url);
      console.log('使用统一配置构建的URL:', url);
    }

    // 如果用户有uid，添加uid参数
    if (userInfo.uid) {
      // 判断是GET请求还是POST请求
      if (!options.method || options.method.toUpperCase() === 'GET') {
        // GET请求，将uid添加到URL参数
        const separator = url.includes('?') ? '&' : '?';
        url = `${url}${separator}uid=${userInfo.uid}`;
      } else if (options.body) {
        // POST请求，将uid添加到请求体
        try {
          const body = JSON.parse(options.body);
          body.uid = userInfo.uid;
          options.body = JSON.stringify(body);
        } catch (e) {
          console.warn('无法将uid添加到非JSON格式的请求体');
        }
      }
    }
  }

  // 根据环境选择使用Capacitor HTTP还是fetch
  if (isNative && CapacitorHttp) {
    console.log('使用Capacitor HTTP发送请求:', url);
    try {
      // 构建Capacitor HTTP请求选项
      const httpOptions = {
        url,
        headers,
        method: options.method || 'GET'
      };

      // 如果有请求体，添加到选项中
      if (options.body) {
        httpOptions.data = JSON.parse(options.body);
      }

      // 发送请求
      const response = await CapacitorHttp.request(httpOptions);
      console.log('Capacitor HTTP响应:', response);

      // 构建类似fetch的响应对象
      return {
        ok: response.status >= 200 && response.status < 300,
        status: response.status,
        statusText: response.statusText || '',
        headers: response.headers,
        json: () => Promise.resolve(response.data),
        text: () => Promise.resolve(JSON.stringify(response.data))
      };
    } catch (error) {
      console.error('Capacitor HTTP请求失败:', error);
      throw error;
    }
  } else {
    console.log('使用fetch API发送请求:', url);
    // 在Web环境中使用fetch API
    return fetch(url, {
      ...options,
      headers
    });
  }
}

// 导出便捷方法
export const http = {
  get: (url, options = {}) => request(url, { ...options, method: 'GET' }),
  post: (url, data, options = {}) => request(url, {
    ...options,
    method: 'POST',
    body: JSON.stringify(data)
  }),
  put: (url, data, options = {}) => request(url, {
    ...options,
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  delete: (url, options = {}) => request(url, { ...options, method: 'DELETE' })
};

export default http;
