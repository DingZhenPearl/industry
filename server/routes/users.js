const express = require('express');
const router = express.Router();
const { runPythonScript } = require('../utils/pythonRunner');
const { authMiddleware } = require('../middleware');

// 获取所有用户列表
router.get('/users', authMiddleware, async (_, res) => {
  try {
    const result = await runPythonScript(
      'pyScripts/user_data_operations.py',
      ['get-users']
    );

    res.json(result);
  } catch (error) {
    console.error('获取用户列表失败:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 获取所有工长信息
router.get('/foremen', authMiddleware, async (_, res) => {
  try {
    const result = await runPythonScript(
      'pyScripts/get_foremen.py',
      []
    );

    res.json(result);
  } catch (error) {
    console.error('获取工长信息失败:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 为了兼容前端的/api/users/foremen路径
router.get('/users/foremen', authMiddleware, async (_, res) => {
  try {
    const result = await runPythonScript(
      'pyScripts/get_foremen.py',
      []
    );

    res.json(result);
  } catch (error) {
    console.error('获取工长信息失败:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 更新用户名
router.post('/update-username', authMiddleware, async (req, res) => {
  const { username, role, currentUsername } = req.body;

  console.log('更新用户名请求:', { username, role, currentUsername });

  const missingFields = [];
  if (!username) missingFields.push('新用户名');
  if (!role) missingFields.push('角色');
  if (!currentUsername) missingFields.push('当前用户名');

  if (missingFields.length > 0) {
    return res.status(400).json({ success: false, error: `请提供以下必需字段: ${missingFields.join(', ')}` });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/user_data_operations.py',
      ['update-username', currentUsername, role, username],
      { debug: true }
    );

    console.log('Python脚本返回结果:', result);
    res.json(result);
  } catch (error) {
    console.error('处理更新用户名请求时出错:', error);
    res.status(500).json({
      success: false,
      error: '服务器内部错误',
      details: error.message
    });
  }
});

// 更新密码
router.post('/update-password', authMiddleware, async (req, res) => {
  const { newPassword, username, role } = req.body;

  try {
    const result = await runPythonScript(
      'pyScripts/user_data_operations.py',
      ['update-password', username, role, newPassword],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('更新密码失败:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

// 更新手机号
router.post('/update-phone', authMiddleware, async (req, res) => {
  const { phone, username, role } = req.body;

  if (!phone || phone.length !== 11 || !/^\d+$/.test(phone)) {
    return res.status(400).json({
      success: false,
      error: '请输入有效的11位手机号'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/user_data_operations.py',
      ['update-user', username, role, phone]
    );

    res.json(result);
  } catch (error) {
    console.error('更新手机号失败:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

// 更新用户信息
router.post('/update-user', authMiddleware, async (req, res) => {
  const { username, role, phone } = req.body;

  try {
    const result = await runPythonScript(
      'pyScripts/user_data_operations.py',
      ['update-user', username, role, phone]
    );

    res.json(result);
  } catch (error) {
    console.error('更新用户信息失败:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 更新用户组号
router.post('/update-group', authMiddleware, async (req, res) => {
  const { username, role, group_id } = req.body;

  try {
    const result = await runPythonScript(
      'pyScripts/user_data_operations.py',
      ['update-group', username, role, group_id]
    );

    res.json(result);
  } catch (error) {
    console.error('更新用户组号失败:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

module.exports = router;
