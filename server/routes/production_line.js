const express = require('express');
const router = express.Router();
const { runPythonScript } = require('../utils/pythonRunner');
const { authMiddleware } = require('../middleware');

// 获取产线列表
router.get('/list', authMiddleware, async (req, res) => {
  try {
    const result = await runPythonScript(
      'pyScripts/production_line_unified.py',
      ['list'],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('获取产线列表出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 获取产线及其最新状态
router.get('/with-status', authMiddleware, async (req, res) => {
  const group_id = req.query.group_id;

  try {
    let result;

    if (group_id) {
      // 如果有组号参数，使用按组号获取产线的脚本
      result = await runPythonScript(
        'pyScripts/production_line_unified.py',
        ['list-by-group', '--group-id', group_id],
        { debug: true }
      );
    } else {
      // 如果没有组号参数，使用原来的脚本获取所有产线
      result = await runPythonScript(
        'pyScripts/production_line_unified.py',
        ['get-with-status'],
        { debug: true }
      );
    }

    res.json(result);
  } catch (error) {
    console.error('获取产线及状态出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 获取产线信息及负责的工长信息
router.get('/with-foremen', authMiddleware, async (req, res) => {
  try {
    const result = await runPythonScript(
      'pyScripts/production_line_unified.py',
      ['get-with-foremen'],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('获取产线及工长信息出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 分配工长到产线
router.post('/assign-foreman', authMiddleware, async (req, res) => {
  const { line_id, foreman_id } = req.body;

  if (!line_id || !foreman_id) {
    return res.status(400).json({
      success: false,
      error: '缺少产线ID或工长工号'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/production_line_unified.py',
      ['assign-foreman', '--line-id', line_id, '--foreman-id', foreman_id],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('分配工长到产线出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 获取产线状态历史
router.get('/status-history', authMiddleware, async (req, res) => {
  const line_id = req.query.line_id;
  const limit = req.query.limit || 10;

  if (!line_id) {
    return res.status(400).json({
      success: false,
      error: '缺少产线ID参数'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/production_line_unified.py',
      ['get-status', '--line-id', line_id, '--limit', limit],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('获取产线状态历史出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 获取单个产线的详细信息
router.get('/detail', authMiddleware, async (req, res) => {
  const line_id = req.query.line_id;

  if (!line_id) {
    return res.status(400).json({
      success: false,
      error: '缺少产线ID参数'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/production_line_unified.py',
      ['get-detail', '--line-id', line_id],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('获取产线详情出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 添加新产线
router.post('/add', authMiddleware, async (req, res) => {
  const lineData = req.body;

  if (!lineData || !lineData.line_name) {
    return res.status(400).json({
      success: false,
      error: '缺少必要的产线信息'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/production_line_unified.py',
      ['add-line', '--data', JSON.stringify(lineData)],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('添加产线出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 更新产线状态
router.post('/update-status', authMiddleware, async (req, res) => {
  const { line_id, status_data } = req.body;

  if (!line_id || !status_data) {
    return res.status(400).json({
      success: false,
      error: '缺少产线ID或状态数据'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/production_line_unified.py',
      ['update-status', '--line-id', line_id, '--data', JSON.stringify(status_data)],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('更新产线状态出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 更新产线静态信息
router.post('/update', authMiddleware, async (req, res) => {
  const { line_id, line_data } = req.body;

  if (!line_id || !line_data) {
    return res.status(400).json({
      success: false,
      error: '缺少产线ID或更新数据'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/production_line_unified.py',
      ['update-line', '--line-id', line_id, '--data', JSON.stringify(line_data)],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('更新产线信息出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 删除产线
router.delete('/delete/:line_id', authMiddleware, async (req, res) => {
  const { line_id } = req.params;

  // 不限制用户角色，任何用户都可以执行删除操作

  if (!line_id) {
    return res.status(400).json({
      success: false,
      error: '缺少产线ID'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/production_line_unified.py',
      ['delete-line', '--line-id', line_id],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('删除产线出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 创建产线表
router.post('/create-tables', authMiddleware, async (req, res) => {
  // 不限制用户角色，任何用户都可以执行创建表操作

  try {
    const result = await runPythonScript(
      'pyScripts/production_line_unified.py',
      ['create-tables'],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('创建产线表出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

module.exports = router;
