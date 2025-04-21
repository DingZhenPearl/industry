/**
 * UID生成器工具
 * 用于根据工号生成唯一的用户标识符
 */

const crypto = require('crypto');

/**
 * 根据工号生成唯一的UID
 * @param {string} employeeId - 用户工号
 * @returns {string} 生成的唯一UID
 */
function generateUid(employeeId) {
  if (!employeeId) {
    throw new Error('工号不能为空');
  }
  
  // 使用工号和当前时间戳生成唯一的字符串
  const baseString = `${employeeId}-${Date.now()}`;
  
  // 使用SHA-256哈希算法生成固定长度的哈希值
  const hash = crypto.createHash('sha256').update(baseString).digest('hex');
  
  // 取前16位作为uid，足够唯一且长度适中
  return hash.substring(0, 16);
}

/**
 * 验证UID是否有效
 * 注意：这里只是简单验证格式，实际应用中应该查询数据库验证
 * @param {string} uid - 要验证的UID
 * @returns {boolean} 是否有效
 */
function isValidUid(uid) {
  // 简单验证：检查是否为16位十六进制字符串
  return /^[0-9a-f]{16}$/.test(uid);
}

module.exports = {
  generateUid,
  isValidUid
};
