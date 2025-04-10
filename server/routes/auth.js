const express = require('express');
const router = express.Router();
const { runPythonScript } = require('../utils/pythonRunner');

// 登录路由
router.post('/login', async (req, res) => {
  const { username, password, role } = req.body;

  const missingFields = [];
  if (!username) missingFields.push('用户名');
  if (!password) missingFields.push('密码');
  if (!role) missingFields.push('角色');

  if (missingFields.length > 0) {
    return res.status(400).json({ success: false, error: `请提供以下必需字段: ${missingFields.join(', ')}` });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/user_data_operations.py',
      ['verify-user', username, password, role]
    );

    if (result.authenticated) {
      // 设置会话
      req.session.user = {
        username: result.username,
        role: result.role,
        phone: result.phone,
        employee_id: result.employee_id,
        group_id: result.group_id
      };

      res.json({
        success: true,
        user: req.session.user
      });
    } else {
      res.json({ success: false, error: result.error || '认证失败' });
    }
  } catch (error) {
    console.error('处理登录请求时出错:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

// 注册路由
router.post('/register', async (req, res) => {
  const { username, password, role } = req.body;

  const missingFields = [];
  if (!username) missingFields.push('用户名');
  if (!password) missingFields.push('密码');
  if (!role) missingFields.push('角色');

  if (missingFields.length > 0) {
    return res.status(400).json({ success: false, error: `请提供以下必需字段: ${missingFields.join(', ')}` });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/user_data_operations.py',
      ['register', username, password, role]
    );

    res.json(result);
  } catch (error) {
    console.error('处理注册请求时出错:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

// 获取当前用户信息
router.get('/user', (req, res) => {
  res.json({ user: req.session.user });
});

// 退出登录
router.post('/logout', (req, res) => {
  req.session.destroy();
  res.json({ success: true });
});

module.exports = router;
