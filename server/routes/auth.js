const express = require('express');
const router = express.Router();
const { runPythonScript } = require('../utils/pythonRunner');

// 登录路由
router.post('/login', async (req, res) => {
  const { employee_id, password, role } = req.body;

  const missingFields = [];
  if (!employee_id) missingFields.push('工号');
  if (!password) missingFields.push('密码');
  if (!role) missingFields.push('角色');

  if (missingFields.length > 0) {
    return res.status(400).json({ success: false, error: `请提供以下必需字段: ${missingFields.join(', ')}` });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/user_data_operations.py',
      ['verify-user-by-id', employee_id, password, role]
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
  const { password, role } = req.body;

  const missingFields = [];
  if (!password) missingFields.push('密码');
  if (!role) missingFields.push('角色');

  if (missingFields.length > 0) {
    return res.status(400).json({ success: false, error: `请提供以下必需字段: ${missingFields.join(', ')}` });
  }

  try {
    // 生成一个随机的用户名，因为我们不再要求用户输入用户名
    const tempUsername = `user_${Date.now()}_${Math.floor(Math.random() * 1000)}`;

    const result = await runPythonScript(
      'pyScripts/user_data_operations.py',
      ['register', tempUsername, password, role]
    );

    // 确保在注册成功后返回工号信息
    if (result.success && result.employee_id) {
      res.json({
        success: true,
        message: result.message,
        employee_id: result.employee_id
      });
    } else {
      res.json(result);
    }
  } catch (error) {
    console.error('处理注册请求时出错:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

// 获取当前用户信息
router.get('/user', (req, res) => {
  // 检查用户是否已登录
  if (!req.session || !req.session.user) {
    return res.status(401).json({ success: false, error: '用户未登录或会话已过期' });
  }

  res.json({ success: true, user: req.session.user });
});

// 退出登录
router.post('/logout', (req, res) => {
  req.session.destroy();
  res.json({ success: true });
});

module.exports = router;
