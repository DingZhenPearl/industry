const express = require('express');
const router = express.Router();
const { runPythonScript } = require('../utils/pythonRunner');
const { authMiddleware } = require('../middleware');

// 获取工长组的工单列表
router.get('/foreman-workorders', authMiddleware, async (req, res) => {
  const group_id = req.query.group_id;
  console.log('获取工长组工单,组号:', group_id);

  if (!group_id) {
    return res.status(400).json({
      success: false,
      error: '缺少组号参数'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/workorder_manager.py',
      ['list', '--team', group_id],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('处理请求出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 创建新工单
router.post('/create-workorder', authMiddleware, async (req, res) => {
  const workorderData = req.body;

  if (!workorderData) {
    return res.status(400).json({
      success: false,
      error: '缺少工单数据'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/workorder_manager.py',
      ['add', '--data', JSON.stringify(workorderData)],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('创建工单出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 更新工单状态
router.post('/update-workorder', authMiddleware, async (req, res) => {
  const { workorder_number, update_data } = req.body;

  if (!workorder_number || !update_data) {
    return res.status(400).json({
      success: false,
      error: '缺少工单编号或更新数据'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/workorder_manager.py',
      ['update', '--number', workorder_number, '--data', JSON.stringify(update_data)],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('更新工单出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 获取工单详情
router.get('/workorder-detail', authMiddleware, async (req, res) => {
  const workorder_number = req.query.number;

  if (!workorder_number) {
    return res.status(400).json({
      success: false,
      error: '缺少工单编号'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/workorder_manager.py',
      ['get', '--number', workorder_number],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('获取工单详情出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 获取所有工单（厂长使用）
router.get('/all-workorders', authMiddleware, async (req, res) => {
  console.log('获取所有工单');

  try {
    const result = await runPythonScript(
      'pyScripts/workorder_manager.py',
      ['list'],  // 不指定组号，获取所有工单
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('获取所有工单出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

module.exports = router;
