const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const session = require('express-session');
const { spawn } = require('child_process');
const path = require('path');

const app = express();
const port = 3000;

// 中间件配置
app.use(cors({
  origin: 'http://localhost:5173', // Vue开发服务器地址
  credentials: true
}));

app.use(bodyParser.json());
app.use(session({
  secret: 'your-secret-key',
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: false,
    maxAge: 24 * 60 * 60 * 1000 // 24小时
  }
}));

// 登录路由
app.post('/api/login', async (req, res) => {
  const { username, password, role } = req.body;

  const missingFields = [];
  if (!username) missingFields.push('用户名');
  if (!password) missingFields.push('密码');
  if (!role) missingFields.push('角色');
  
  if (missingFields.length > 0) {
    return res.status(400).json({ success: false, error: `请提供以下必需字段: ${missingFields.join(', ')}` });
  }

  try {
    const result = await new Promise((resolve) => {
      const pythonProcess = spawn('python', ['pyScripts/verify_user.py', 'verify', username, password, role]);
      let output = '';

      pythonProcess.stdout.on('data', (data) => {
        output += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        console.error(`Python脚本错误: ${data}`);
      });

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          resolve({ success: false, error: 'Python脚本执行失败' });
          return;
        }
        try {
          const result = JSON.parse(output);
          if (result.authenticated) {
            resolve({
              success: true,
              user: {
                username: result.username,
                role: result.role
              }
            });
          } else {
            resolve({ success: false, error: result.error || '认证失败' });
          }
        } catch (error) {
          resolve({ success: false, error: '解析Python脚本输出失败' });
        }
      });
    });

    res.json(result);
  } catch (error) {
    console.error('处理登录请求时出错:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

app.post('/api/register', async (req, res) => {
  const { username, password, role } = req.body;

  const missingFields = [];
  if (!username) missingFields.push('用户名');
  if (!password) missingFields.push('密码');
  if (!role) missingFields.push('角色');
  
  if (missingFields.length > 0) {
    return res.status(400).json({ success: false, error: `请提供以下必需字段: ${missingFields.join(', ')}` });
  }

  try {
    const result = await new Promise((resolve) => {
      const pythonProcess = spawn('python', ['pyScripts/verify_user.py', 'register', username, password, role]);
      let output = '';

      pythonProcess.stdout.on('data', (data) => {
        output += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        console.error(`Python脚本错误: ${data}`);
      });

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          resolve({ success: false, error: 'Python脚本执行失败' });
          return;
        }
        try {
          const result = JSON.parse(output);
          resolve(result);
        } catch (error) {
          resolve({ success: false, error: '解析Python脚本输出失败' });
        }
      });
    });

    res.json(result);
  } catch (error) {
    console.error('处理注册请求时出错:', error);
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

// 会话验证中间件
const authMiddleware = (req, res, next) => {
  if (req.session && req.session.user) {
    next();
  } else {
    res.status(401).json({ error: '未登录' });
  }
};

// 获取当前用户信息
app.get('/api/user', authMiddleware, (req, res) => {
  res.json({ user: req.session.user });
});

// 更新用户名
app.post('/api/update-username', async (req, res) => {
  const { username, role, currentUsername } = req.body;
  
  console.log('更新用户名请求:', { username, role, currentUsername }); // 添加请求日志

  const missingFields = [];
  if (!username) missingFields.push('新用户名');
  if (!role) missingFields.push('角色');
  if (!currentUsername) missingFields.push('当前用户名');
  
  if (missingFields.length > 0) {
    return res.status(400).json({ success: false, error: `请提供以下必需字段: ${missingFields.join(', ')}` });
  }

  try {
    const result = await new Promise((resolve) => {
      const pythonProcess = spawn('python', [
        'pyScripts/verify_user.py', 
        'update_username', 
        currentUsername,  // 第一个参数应该是当前用户名
        role,             // 第二个参数是角色
        username          // 第三个参数是新用户名
      ], {
        encoding: 'utf-8'  // 明确指定编码
      });
      
      let output = '';
      let errorOutput = '';
      
      pythonProcess.stdout.on('data', (data) => {
        // 只收集最后一行输出，避免调试信息干扰
        const lines = data.toString().split('\n');
        output = lines[lines.length - 2]; // 获取倒数第二行(最后一行是空行)
      });

      pythonProcess.stderr.on('data', (data) => {
        errorOutput += data.toString();
        console.error(`Python脚本错误输出: ${data}`);
      });

      pythonProcess.on('close', (code) => {
        console.log(`Python脚本退出代码: ${code}, 输出: ${output}`);
        try {
          const cleanOutput = output.trim();
          if (!cleanOutput) {
            throw new Error('Python脚本无输出');
          }
          const result = JSON.parse(cleanOutput);
          resolve(result);
        } catch (error) {
          console.error('解析Python输出失败:', error);
          resolve({ 
            success: false, 
            error: '解析Python脚本输出失败',
            details: `原始输出: ${output}\n错误: ${error.message}`
          });
        }
      });
    });

    console.log('Python脚本返回结果:', result); // 添加结果日志
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

// 退出登录
app.post('/api/logout', (req, res) => {
  req.session.destroy();
  res.json({ success: true });
});

// 静态文件服务
app.use(express.static(path.join(__dirname, '..', 'dist')));

// 处理Vue路由
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'dist', 'index.html'));
});

app.listen(port, () => {
  console.log(`服务器运行在 http://localhost:${port}`);
});