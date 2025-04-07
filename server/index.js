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
                role: result.role,
                phone: result.phone  // 添加手机号返回
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

// 更新密码
app.post('/api/update-password', async (req, res) => {
  const { newPassword, username, role } = req.body;
  
  try {
    const result = await new Promise((resolve) => {
      const pythonProcess = spawn('python', [
        'pyScripts/verify_user.py', 
        'update_password',
        username,       // 第一个参数是用户名
        role,           // 第二个参数是角色
        newPassword     // 第三个参数是新密码
      ], {
        encoding: 'utf-8'  // 明确指定编码
      });
      
      let output = '';
      pythonProcess.stdout.on('data', (data) => {
        // 只收集最后一行输出
        const lines = data.toString().split('\n');
        output = lines[lines.length - 2]; // 获取倒数第二行(最后一行是空行)
      });

      pythonProcess.stderr.on('data', (data) => {
        console.error(`Python脚本错误输出: ${data}`);
        output += data.toString(); // 收集错误输出
      });

      pythonProcess.on('close', (code) => {
        console.log(`Python脚本退出代码: ${code}, 输出: ${output}`);
        try {
          const result = JSON.parse(output);
          resolve(result);
        } catch (error) {
          console.error('解析Python输出失败:', error, '原始输出:', output);
          resolve({ 
            success: false, 
            error: '密码更新失败',
            details: output // 返回原始错误信息
          });
        }
      });
    });
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

// 更新手机号
app.post('/api/update-phone', async (req, res) => {
  const { phone, username, role } = req.body;
  
  if (!phone || phone.length !== 11 || !/^\d+$/.test(phone)) {
    return res.status(400).json({ 
      success: false, 
      error: '请输入有效的11位手机号' 
    });
  }

  try {
    const result = await new Promise((resolve) => {
      const pythonProcess = spawn('python', [
        'pyScripts/verify_user.py', 
        'update_user', 
        username,
        role,
        phone
      ], {
        encoding: 'utf-8'
      });
      
      let output = '';
      pythonProcess.stdout.on('data', (data) => {
        const lines = data.toString().split('\n');
        output = lines[lines.length - 2];
      });
      
      pythonProcess.on('close', (code) => {
        try {
          resolve(JSON.parse(output));
        } catch (error) {
          resolve({ success: false, error: '解析响应失败' });
        }
      });
    });
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: '服务器内部错误' });
  }
});

// 更新用户信息接口
app.post('/api/update-user', async (req, res) => {
  const { username, role, phone } = req.body;
  
  try {
    const result = await new Promise((resolve) => {
      const pythonProcess = spawn('python', [
        'pyScripts/verify_user.py', 
        'update_user', 
        username,
        role,
        phone
      ], {
        encoding: 'utf-8'
      });
      
      let output = '';
      pythonProcess.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      pythonProcess.on('close', (code) => {
        resolve(JSON.parse(output));
      });
    });
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: '服务器错误' });
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