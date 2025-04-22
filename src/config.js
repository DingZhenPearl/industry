// 应用配置文件
import serverConfig from './config/server';

// 判断是否在移动设备上运行
const isMobileApp = () => {
  return window.location.protocol === 'capacitor:' ||
         window.location.protocol === 'file:' ||
         /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase());
};



// 获取API基础URL
const getApiBaseUrl = () => {
  return serverConfig.getServerUrl({
    isNative: isMobileApp()
  });
};

// 构建完整API URL
const buildApiUrl = (path) => {
  return serverConfig.buildApiUrl(path, {
    isNative: isMobileApp()
  });
};

export default {
  apiBaseUrl: getApiBaseUrl(),
  isMobileApp: isMobileApp(),
  buildApiUrl,

  // 切换到云服务器
  useCloudServer: serverConfig.useCloudServer,

  // 切换到本地服务器
  useLocalServer: serverConfig.useLocalServer,

  // 获取当前服务器配置
  getServerConfig: () => ({
    useCloud: serverConfig.ENV.useCloud,
    cloudServer: serverConfig.PROD_SERVER.cloud,
    localIP: serverConfig.DEV_SERVER.localIP
  }),

  // 设置云服务器地址
  setCloudServer: (url) => {
    serverConfig.PROD_SERVER.cloud = url;
  },

  // 设置本地IP地址
  setLocalIP: (url) => {
    serverConfig.DEV_SERVER.localIP = url;
  }
};
