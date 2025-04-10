const cors = require('cors');
const bodyParser = require('body-parser');
const session = require('express-session');
const express = require('express');
const path = require('path');

/**
 * 配置Express应用的中间件
 * @param {Object} app - Express应用实例
 */
function setupMiddleware(app) {
  // CORS配置
  app.use(cors({
    origin: 'http://localhost:5173', // Vue开发服务器地址
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
  // 从请求头获取token
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (token) {
    // 这里可以添加token验证逻辑
    next();
    return;
  }

  // 再检查session
  if (req.session && req.session.user) {
    next();
    return;
  }

  res.status(401).json({
    success: false,
    error: '未登录'
  });
};

module.exports = { setupMiddleware, authMiddleware };
