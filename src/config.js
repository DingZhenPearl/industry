/**
 * 统一配置文件
 * 包含应用配置和服务器配置
 */
import { Capacitor } from '@capacitor/core';

// 判断是否在移动设备上运行
const isMobileApp = () => {
  return Capacitor.isNativePlatform() || 
         window.location.protocol === 'capacitor:' || 
         window.location.protocol === 'file:' ||
         /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase());
};

// 服务器配置
const SERVER_CONFIG = {
  // 开发环境服务器地址
  local: {
    // 本地开发服务器（相对路径）
    url: '',
    // 本机IP地址，用于移动设备访问
    mobileUrl: 'http://10.29.101.231:3000'
  },
  // 生产环境服务器地址
  cloud: {
    // 云服务器地址，部署时修改这里
    url: 'http://your-cloud-server-ip:3000'
  },
  // 当前使用的服务器模式
  currentMode: 'local'
};

/**
 * 获取服务器基础URL
 * @returns {string} 服务器基础URL
 */
const getApiBaseUrl = () => {
  // 如果是云服务器模式
  if (SERVER_CONFIG.currentMode === 'cloud') {
    return SERVER_CONFIG.cloud.url;
  }
  
  // 如果是移动应用，使用本机IP
  if (isMobileApp()) {
    return SERVER_CONFIG.local.mobileUrl;
  }
  
  // 在Web环境中使用相对路径
  return SERVER_CONFIG.local.url;
};

/**
 * 构建完整的API URL
 * @param {string} path - API路径，如 '/api/login'
 * @returns {string} 完整的API URL
 */
const buildApiUrl = (path) => {
  const baseUrl = getApiBaseUrl();
  
  // 如果baseUrl为空（相对路径）或path已经是完整URL，直接返回path
  if (!baseUrl || path.startsWith('http')) {
    return path;
  }
  
  // 确保path以/开头
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  
  // 构建完整URL
  return `${baseUrl}${normalizedPath}`;
};

// 导出配置对象
export default {
  // 基本配置
  apiBaseUrl: getApiBaseUrl(),
  isMobileApp: isMobileApp(),
  buildApiUrl,
  
  // 服务器配置管理
  getServerConfig: () => ({
    mode: SERVER_CONFIG.currentMode,
    localUrl: SERVER_CONFIG.local.mobileUrl,
    cloudUrl: SERVER_CONFIG.cloud.url
  }),
  
  // 设置本地服务器地址
  setLocalUrl: (url) => {
    SERVER_CONFIG.local.mobileUrl = url;
  },
  
  // 设置云服务器地址
  setCloudUrl: (url) => {
    SERVER_CONFIG.cloud.url = url;
  },
  
  // 切换到云服务器
  useCloudServer: () => {
    SERVER_CONFIG.currentMode = 'cloud';
    console.log('已切换到云服务器模式，使用地址:', SERVER_CONFIG.cloud.url);
  },
  
  // 切换到本地服务器
  useLocalServer: () => {
    SERVER_CONFIG.currentMode = 'local';
    console.log('已切换到本地服务器模式');
  }
};
