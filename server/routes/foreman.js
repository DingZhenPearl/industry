const express = require('express');
const router = express.Router();
const { runPythonScript } = require('../utils/pythonRunner');
const { authMiddleware } = require('../middleware');

// 工长获取分组成员列表
router.get('/team-members', authMiddleware, async (req, res) => {
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
router.get('/assigned-lines', authMiddleware, async (req, res) => {
  const group_id = req.query.group_id;
  console.log('获取工长产线信息,组号:', group_id);

  if (!group_id) {
    return res.status(400).json({
      success: false,
      error: '缺少组号参数'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/user_data_operations.py',
      ['get-lines', group_id],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('处理请求出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

module.exports = router;
