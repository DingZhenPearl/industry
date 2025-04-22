const cors = require('cors');
const bodyParser = require('body-parser');
const session = require('express-session');
const express = require('express');
const path = require('path');
const { isValidUid } = require('./utils/uidGenerator');

/**
 * 配置Express应用的中间件
 * @param {Object} app - Express应用实例
 */
function setupMiddleware(app) {
  // CORS配置
  app.use(cors({
    origin: '*', // 允许所有源访问
    credentials: true
  }));

  // 请求体解析
  app.use(bodyParser.json());

  // 会话管理
  app.use(session({
    secret: 'your-secret-key',
    resave: false,
    saveUninitialized: false,
    cookie: {
      secure: false,
      maxAge: 24 * 60 * 60 * 1000 // 24小时
    }
  }));

  // 静态文件服务
  app.use(express.static(path.join(__dirname, '..', 'dist')));
}

/**
 * 认证中间件
 */
const authMiddleware = (req, res, next) => {
  // 优先检查session
  if (req.session && req.session.user) {
    next();
    return;
  }

  // 如果没有session，再检查token
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (token) {
    // 这里可以添加token验证逻辑
    // 注意：当前实现中没有实际验证token，只是检查存在性
    // 在生产环境中应该添加验证逻辑
    console.warn('警告：使用了未验证的token认证');
    next();
    return;
  }

  res.status(401).json({
    success: false,
    error: '未登录或会话已过期'
  });
};

/**
 * UID验证中间件
 * 验证请求中的uid参数是否有效
 */
const uidMiddleware = (req, res, next) => {
  // 从URL参数或请求体中获取uid
  const uid = req.query.uid || req.body.uid;

  // 如果没有提供uid，则跳过验证
  if (!uid) {
    return next();
  }

  // 验证uid格式是否有效
  if (!isValidUid(uid)) {
    return res.status(400).json({
      success: false,
      error: '无效的用户标识符'
    });
  }

  // 如果有会话，验证uid是否与会话中的uid匹配
  if (req.session && req.session.user && req.session.user.uid) {
    if (uid !== req.session.user.uid) {
      return res.status(403).json({
        success: false,
        error: '用户标识符不匹配'
      });
    }
  }

  // uid有效，继续处理请求
  next();
};

module.exports = { setupMiddleware, authMiddleware, uidMiddleware };
