const express = require('express');
const router = express.Router();
const { runPythonScript } = require('../utils/pythonRunner');
const { authMiddleware } = require('../middleware');

// 获取设备传感器项目列表
router.get('/:equipment_id', authMiddleware, async (req, res) => {
  const equipment_id = req.params.equipment_id;

  if (!equipment_id) {
    return res.status(400).json({
      success: false,
      error: '缺少设备ID'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/equipment_unified.py',
      ['get-sensor-projects', '--equipment-id', equipment_id],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('获取传感器项目列表出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

// 更新设备传感器项目列表
router.post('/:equipment_id', authMiddleware, async (req, res) => {
  const equipment_id = req.params.equipment_id;
  const sensor_projects = req.body;

  if (!equipment_id || !sensor_projects) {
    return res.status(400).json({
      success: false,
      error: '缺少设备ID或传感器项目数据'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/equipment_unified.py',
      ['update-sensor-projects', '--equipment-id', equipment_id, '--data', JSON.stringify(sensor_projects)],
      { debug: true }
    );

    res.json(result);
  } catch (error) {
    console.error('更新传感器项目列表出错:', error);
    res.status(500).json({ success: false, error: '服务器错误' });
  }
});

module.exports = router;
