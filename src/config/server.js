/**
 * 服务器配置文件
 * 所有与服务器连接相关的配置都集中在这里
 * 部署时只需修改这个文件
 */

// 开发环境服务器地址
const DEV_SERVER = {
  // 本地开发服务器
  local: '',  // 空字符串表示使用相对路径
  // 本机IP地址，用于移动设备访问
  localIP: 'http://10.29.101.231:3000'
};

// 生产环境服务器地址
const PROD_SERVER = {
  // 云服务器地址，部署时修改这里
  cloud: 'http://your-cloud-server-ip:3000'
};

// 当前环境配置
const ENV = {
  // 是否是生产环境
  isProd: process.env.NODE_ENV === 'production',
  // 是否使用云服务器
  useCloud: false  // 设置为true时使用云服务器地址
};

/**
 * 获取服务器基础URL
 * @param {Object} options - 配置选项
 * @param {boolean} options.isNative - 是否在原生环境中运行
 * @returns {string} 服务器基础URL
 */
export function getServerUrl(options = {}) {
  const { isNative } = options;

  // 如果配置为使用云服务器，直接返回云服务器地址
  if (ENV.useCloud) {
    return PROD_SERVER.cloud;
  }

  // 在原生环境中使用本机IP
  if (isNative) {
    return DEV_SERVER.localIP;
  }

  // 在Web环境中使用相对路径
  return DEV_SERVER.local;
}

/**
 * 构建完整的API URL
 * @param {string} path - API路径，如 '/api/login'
 * @param {Object} options - 配置选项
 * @returns {string} 完整的API URL
 */
export function buildApiUrl(path, options = {}) {
  const baseUrl = getServerUrl(options);

  // 如果baseUrl为空（相对路径）或path已经是完整URL，直接返回path
  if (!baseUrl || path.startsWith('http')) {
    return path;
  }

  // 确保path以/开头
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;

  // 构建完整URL
  return `${baseUrl}${normalizedPath}`;
}

// 导出配置对象
export default {
  DEV_SERVER,
  PROD_SERVER,
  ENV,
  getServerUrl,
  buildApiUrl,

  // 切换到云服务器
  useCloudServer() {
    ENV.useCloud = true;
    console.log('已切换到云服务器模式，使用地址:', PROD_SERVER.cloud);
  },

  // 切换到本地服务器
  useLocalServer() {
    ENV.useCloud = false;
    console.log('已切换到本地服务器模式');
  }
};
