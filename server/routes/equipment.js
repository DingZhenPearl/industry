const express = require('express');
const router = express.Router();
const { runPythonScript } = require('../utils/pythonRunner');
const { authMiddleware } = require('../middleware');

// 获取设备列表
router.get('/list', authMiddleware, async (req, res) => {
  const line_id = req.query.line_id;
  const status = req.query.status;
  
  try {
    const args = ['list'];
    if (line_id) args.push('--line-id', line_id);
    if (status) args.push('--status', status);
    
    const result = await runPythonScript(
      'pyScripts/equipment_manager.py',
      args,
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('获取设备列表出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 获取设备及其最新状态
router.get('/with-status', authMiddleware, async (req, res) => {
  const line_id = req.query.line_id;
  
  try {
    const args = ['get-with-status'];
    if (line_id) args.push('--line-id', line_id);
    
    const result = await runPythonScript(
      'pyScripts/equipment_manager.py',
      args,
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('获取设备及状态出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 获取设备状态历史
router.get('/status-history', authMiddleware, async (req, res) => {
  const equipment_id = req.query.equipment_id;
  const limit = req.query.limit || 10;
  
  if (!equipment_id) {
    return res.status(400).json({
      success: false,
      error: '缺少设备ID参数'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/equipment_manager.py',
      ['get-status', '--equipment-id', equipment_id, '--limit', limit],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('获取设备状态历史出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 添加新设备
router.post('/add', authMiddleware, async (req, res) => {
  const equipmentData = req.body;
  
  if (!equipmentData || !equipmentData.equipment_name || !equipmentData.equipment_code || !equipmentData.line_id) {
    return res.status(400).json({
      success: false,
      error: '缺少必要的设备信息'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/equipment_manager.py',
      ['add-equipment', '--data', JSON.stringify(equipmentData)],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('添加设备出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 更新设备状态
router.post('/update-status', authMiddleware, async (req, res) => {
  const { equipment_id, status_data } = req.body;
  
  if (!equipment_id || !status_data) {
    return res.status(400).json({
      success: false,
      error: '缺少设备ID或状态数据'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/equipment_manager.py',
      ['update-status', '--equipment-id', equipment_id, '--data', JSON.stringify(status_data)],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('更新设备状态出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 创建设备表（仅管理员可用）
router.post('/create-tables', authMiddleware, async (req, res) => {
  // 检查用户角色，仅允许管理员执行此操作
  if (req.session.user.role !== 'supervisor') {
    return res.status(403).json({
      success: false,
      error: '权限不足，仅管理员可执行此操作'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/equipment_manager.py',
      ['create-tables'],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('创建设备表出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

module.exports = router;
