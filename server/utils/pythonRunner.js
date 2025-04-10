const { spawn } = require('child_process');

/**
 * 运行Python脚本并返回结果
 * @param {string} scriptPath - Python脚本路径
 * @param {string[]} args - 脚本参数
 * @param {Object} options - 额外选项
 * @returns {Promise<Object>} - 脚本执行结果
 */
async function runPythonScript(scriptPath, args, options = {}) {
  const encoding = options.encoding || 'utf-8';
  const debug = options.debug || false;
  
  return new Promise((resolve) => {
    const pythonProcess = spawn('python', [scriptPath, ...args], { encoding });
    let output = '';
    let errorOutput = '';

    pythonProcess.stdout.on('data', (data) => {
      const dataStr = data.toString();
      output += dataStr;
      if (debug) {
        console.log(`Python stdout: ${dataStr}`);
      }
    });

    pythonProcess.stderr.on('data', (data) => {
      const dataStr = data.toString();
      errorOutput += dataStr;
      if (debug) {
        console.error(`Python stderr: ${dataStr}`);
      }
    });

    pythonProcess.on('close', (code) => {
      if (debug) {
        console.log(`Python process exited with code ${code}`);
        console.log(`Output: ${output}`);
      }

      if (code !== 0) {
        resolve({
          success: false,
          error: 'Python脚本执行失败',
          details: errorOutput || '未知错误'
        });
        return;
      }

      try {
        const cleanOutput = output.trim();
        const result = JSON.parse(cleanOutput);
        resolve(result);
      } catch (error) {
        if (debug) {
          console.error('Failed to parse Python output:', error);
          console.error('Raw output:', output);
        }
        resolve({
          success: false,
          error: '解析Python脚本输出失败',
          details: error.message,
          rawOutput: output
        });
      }
    });
  });
}

module.exports = { runPythonScript };
