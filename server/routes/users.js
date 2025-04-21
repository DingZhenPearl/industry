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
      'pyScripts/user_data_operations.py',
      ['get-foremen']
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
      'pyScripts/user_data_operations.py',
      ['get-foremen']
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
  const { employee_id, group_id } = req.body;

  if (!employee_id || !group_id) {
    return res.status(400).json({
      success: false,
      error: '缺少必要参数：员工ID或组号'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/user_data_operations.py',
      ['update-group-by-id', employee_id, group_id]
    );

    res.json(result);
  } catch (error) {
    console.error('更新用户组号失败:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

// 根据工号查询用户名
router.get('/username/:employee_id', authMiddleware, async (req, res) => {
  try {
    const { employee_id } = req.params;

    const result = await runPythonScript(
      'pyScripts/user_data_operations.py',
      ['get-username', employee_id]
    );

    res.json(result);
  } catch (error) {
    console.error('根据工号查询用户名失败:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 批量查询用户名
router.post('/usernames', authMiddleware, async (req, res) => {
  try {
    const { employee_ids } = req.body;

    if (!Array.isArray(employee_ids)) {
      return res.status(400).json({ success: false, error: '请提供工号数组' });
    }

    // 并行查询所有工号对应的用户名
    const promises = employee_ids.map(async (id) => {
      try {
        const result = await runPythonScript(
          'pyScripts/user_data_operations.py',
          ['get-username', id]
        );
        return { employee_id: id, ...result };
      } catch (error) {
        console.error(`查询工号 ${id} 的用户名失败:`, error);
        return { employee_id: id, success: false, error: '查询失败' };
      }
    });

    const results = await Promise.all(promises);

    // 将结果转换为工号-用户名的映射
    const usernameMap = {};
    results.forEach(result => {
      if (result.success) {
        usernameMap[result.employee_id] = result.username;
      } else {
        usernameMap[result.employee_id] = null;
      }
    });

    res.json({ success: true, data: usernameMap });
  } catch (error) {
    console.error('批量查询用户名失败:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 工长获取分组成员列表
router.get('/users/foreman/team-members', authMiddleware, async (req, res) => {
  console.log('请求工长团队成员列表');
  const group_id = req.query.group_id;
  console.log('获取工长团队成员,组号:', group_id);

  if (!group_id) {
    return res.status(400).json({
      success: false,
      error: '缺少组号参数'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/user_data_operations.py',
      ['get-team', group_id],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('处理请求出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 工长获取分配的产线列表
router.get('/users/foreman/assigned-lines', authMiddleware, async (req, res) => {
  console.log('请求工长分配的产线列表');
  const employee_id = req.query.employee_id;
  console.log('获取工长产线信息,工号:', employee_id);

  if (!employee_id) {
    return res.status(400).json({
      success: false,
      error: '缺少工长工号参数'
    });
  }

  try {
    // 使用新的脚本获取产线信息
    const result = await runPythonScript(
      'pyScripts/production_line_unified.py',
      ['list-by-foreman', '--foreman-id', employee_id],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('处理请求出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

module.exports = router;
