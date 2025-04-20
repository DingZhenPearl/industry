const { spawn } = require('child_process');

// 运行Python脚本
function runPythonScript(scriptPath, args) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', [scriptPath, ...args]);
    
    let output = '';
    let errorOutput = '';
    
    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
      console.log(`Python stdout: ${data}`);
    });
    
    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
      console.error(`Python stderr: ${data}`);
    });
    
    pythonProcess.on('close', (code) => {
      console.log(`Python process exited with code ${code}`);
      
      if (code !== 0) {
        reject(new Error(`Python脚本执行失败: ${errorOutput}`));
        return;
      }
      
      try {
        const result = JSON.parse(output.trim());
        resolve(result);
      } catch (error) {
        reject(new Error(`解析Python输出失败: ${error.message}`));
      }
    });
  });
}

// 初始化考勤表
async function initAttendanceTables() {
  try {
    console.log('开始初始化考勤表...');
    const result = await runPythonScript('pyScripts/create_attendance_tables.py', ['--drop']);
    console.log('初始化考勤表结果:', result);
  } catch (error) {
    console.error('初始化考勤表失败:', error);
  }
}

// 执行初始化
initAttendanceTables();
