// 应用配置文件

// 判断是否在移动设备上运行
const isMobileApp = () => {
  return window.location.protocol === 'capacitor:' || 
         window.location.protocol === 'file:' ||
         /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase());
};

// API基础URL
const getApiBaseUrl = () => {
  // 如果是移动应用，使用实际的服务器地址
  if (isMobileApp()) {
    // 这里需要替换为您的实际服务器地址
    return 'http://192.168.1.100:3000';
  }
  
  // 开发环境使用相对路径
  return '';
};

export default {
  apiBaseUrl: getApiBaseUrl(),
  isMobileApp: isMobileApp()
};
