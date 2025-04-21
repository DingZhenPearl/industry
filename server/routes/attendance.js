const express = require('express');
const router = express.Router();
const { runPythonScript } = require('../utils/pythonRunner');
const { authMiddleware } = require('../middleware');


// 上班打卡
router.post('/check-in', authMiddleware, async (req, res) => {
  const { employee_id } = req.body;

  if (!employee_id) {
    return res.status(400).json({
      success: false,
      error: '缺少员工工号'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/employee_status_manager.py',
      ['check-in', employee_id]
    );

    res.json(result);
  } catch (error) {
    console.error('上班打卡失败:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

// 下班打卡
router.post('/check-out', authMiddleware, async (req, res) => {
  const { employee_id } = req.body;

  if (!employee_id) {
    return res.status(400).json({
      success: false,
      error: '缺少员工工号'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/employee_status_manager.py',
      ['check-out', employee_id]
    );

    res.json(result);
  } catch (error) {
    console.error('下班打卡失败:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

// 提交请假申请
router.post('/submit-leave', authMiddleware, async (req, res) => {
  const { employee_id, leave_type, start_date, end_date, reason } = req.body;

  if (!employee_id || !leave_type || !start_date || !end_date) {
    return res.status(400).json({
      success: false,
      error: '缺少必要参数'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/employee_status_manager.py',
      ['submit-leave', employee_id, leave_type, start_date, end_date, reason || '']
    );

    res.json(result);
  } catch (error) {
    console.error('提交请假申请失败:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

// 批准请假申请
router.post('/approve-leave', authMiddleware, async (req, res) => {
  const { leave_id, approver_id, notes } = req.body;

  if (!leave_id || !approver_id) {
    return res.status(400).json({
      success: false,
      error: '缺少必要参数'
    });
  }

  try {
    const args = ['approve-leave', leave_id, approver_id];
    if (notes) {
      args.push('--notes', notes);
    }

    const result = await runPythonScript(
      'pyScripts/employee_status_manager.py',
      args
    );

    res.json(result);
  } catch (error) {
    console.error('批准请假申请失败:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

// 拒绝请假申请
router.post('/reject-leave', authMiddleware, async (req, res) => {
  const { leave_id, approver_id, notes } = req.body;

  if (!leave_id || !approver_id) {
    return res.status(400).json({
      success: false,
      error: '缺少必要参数'
    });
  }

  try {
    const args = ['reject-leave', leave_id, approver_id];
    if (notes) {
      args.push('--notes', notes);
    }

    const result = await runPythonScript(
      'pyScripts/employee_status_manager.py',
      args
    );

    res.json(result);
  } catch (error) {
    console.error('拒绝请假申请失败:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

// 取消请假申请
router.post('/cancel-leave', authMiddleware, async (req, res) => {
  const { leave_id, employee_id } = req.body;

  if (!leave_id || !employee_id) {
    return res.status(400).json({
      success: false,
      error: '缺少必要参数'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/employee_status_manager.py',
      ['cancel-leave', leave_id, employee_id]
    );

    res.json(result);
  } catch (error) {
    console.error('取消请假申请失败:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

// 获取员工考勤记录
router.get('/attendance/:employee_id', authMiddleware, async (req, res) => {
  const { employee_id } = req.params;
  const { start, end } = req.query;

  try {
    const args = ['get-attendance', employee_id];
    if (start) {
      args.push('--start', start);
    }
    if (end) {
      args.push('--end', end);
    }

    const result = await runPythonScript(
      'pyScripts/employee_status_manager.py',
      args
    );

    res.json(result);
  } catch (error) {
    console.error('获取考勤记录失败:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

// 获取员工请假记录
router.get('/leave-records/:employee_id', authMiddleware, async (req, res) => {
  const { employee_id } = req.params;
  const { status } = req.query;

  try {
    const args = ['get-leave-records', employee_id];
    if (status) {
      args.push('--status', status);
    }

    const result = await runPythonScript(
      'pyScripts/employee_status_manager.py',
      args
    );

    res.json(result);
  } catch (error) {
    console.error('获取请假记录失败:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

// 获取待审批的请假申请
router.get('/pending-leaves', authMiddleware, async (req, res) => {
  const { group_id, all, approver_id } = req.query;

  try {
    const args = ['get-pending-leaves'];

    // 如果是厂长请求所有请假申请
    if (all === 'true') {
      args.push('--all');
    }
    // 如果是工长或安全员请求组内请假申请
    else if (group_id && group_id.trim()) {
      args.push('--group-id', group_id.trim());

      // 如果提供了审批人ID，排除审批人自己的请假申请
      if (approver_id && approver_id.trim()) {
        args.push('--approver-id', approver_id.trim());
      }
    }

    console.log('请求参数:', args); // 调试日志

    const result = await runPythonScript(
      'pyScripts/employee_status_manager.py',
      args
    );

    console.log('返回结果:', result); // 调试日志

    res.json(result);
  } catch (error) {
    console.error('获取待审批请假申请失败:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

// 获取已处理的请假申请
router.get('/processed-leaves', authMiddleware, async (req, res) => {
  const { group_id, all } = req.query;

  try {
    const args = ['get-processed-leaves'];

    // 如果是厂长请求所有请假申请
    if (all === 'true') {
      args.push('--all');
    }
    // 如果是工长或安全员请求组内请假申请
    else if (group_id && group_id.trim()) {
      args.push('--group-id', group_id.trim());
    }

    console.log('请求参数:', args); // 调试日志

    const result = await runPythonScript(
      'pyScripts/employee_status_manager.py',
      args
    );

    console.log('返回结果:', result); // 调试日志

    res.json(result);
  } catch (error) {
    console.error('获取已处理请假申请失败:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

// 更新员工状态
router.post('/update-status', authMiddleware, async (req, res) => {
  const { employee_id, status } = req.body;

  if (!employee_id || !status) {
    return res.status(400).json({
      success: false,
      error: '缺少必要参数'
    });
  }

  try {
    const result = await runPythonScript(
      'pyScripts/employee_status_manager.py',
      ['update-status', employee_id, status]
    );

    res.json(result);
  } catch (error) {
    console.error('更新员工状态失败:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

// 获取员工今日考勤状态
router.get('/today-status/:employee_id', authMiddleware, async (req, res) => {
  const { employee_id } = req.params;

  try {
    const result = await runPythonScript(
      'pyScripts/employee_status_manager.py',
      ['get-today-status', employee_id]
    );

    res.json(result);
  } catch (error) {
    console.error('获取今日考勤状态失败:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

module.exports = router;
