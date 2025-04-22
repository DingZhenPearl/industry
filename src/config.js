// 应用配置文件

// 判断是否在移动设备上运行
const isMobileApp = () => {
  return window.location.protocol === 'capacitor:' ||
         window.location.protocol === 'file:' ||
         /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase());
};

// 判断是否在模拟器中运行
const isEmulator = () => {
  // 检查用户代理中是否包含模拟器特征
  // 注意：这只是一个简单的检测方法，可能不是100%准确
  const userAgent = navigator.userAgent.toLowerCase();
  return userAgent.includes('android sdk') ||
         userAgent.includes('emulator') ||
         userAgent.includes('sdk_gphone') ||
         userAgent.includes('sdk built for');
};

// API基础URL
const getApiBaseUrl = () => {
  // 如果是移动应用，使用实际的服务器地址
  if (isMobileApp()) {
    // 这里需要替换为您的实际服务器地址
    // 使用局域网IP，确保可以从模拟器或真机访问
    return 'http://192.168.1.100:3000';
  }

  // 开发环境使用相对路径
  return '';
};

export default {
  apiBaseUrl: getApiBaseUrl(),
  isMobileApp: isMobileApp(),
  isEmulator: isEmulator()
};
