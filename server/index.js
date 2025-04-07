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

  if (!username || !password || !role) {
    return res.status(400).json({ success: false, error: '请提供所有必需的字段' });
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

  if (!username || !password || !role) {
    return res.status(400).json({ success: false, error: '请提供所有必需的字段' });
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