const express = require('express');
const path = require('path');
const { setupMiddleware, uidMiddleware } = require('./middleware');
const authRoutes = require('./routes/auth');
const userRoutes = require('./routes/users');
const workorderRoutes = require('./routes/workorders');
const equipmentRoutes = require('./routes/equipment');
const productionLineRoutes = require('./routes/production_line');
const attendanceRoutes = require('./routes/attendance');

// 创建Express应用
const app = express();
const port = 3000;

// 设置中间件
setupMiddleware(app);

// 注册路由
app.use('/api', authRoutes);
app.use('/api', userRoutes);

// 应用uid中间件到需要验证的路由
app.use('/api/workorders', uidMiddleware, workorderRoutes);
app.use('/api/equipment', uidMiddleware, equipmentRoutes);
app.use('/api/production_line', uidMiddleware, productionLineRoutes);
app.use('/api/attendance', uidMiddleware, attendanceRoutes);

// 打印所有注册的路由
console.log('已注册的路由:');
app._router.stack.forEach(function(r){
  if (r.route && r.route.path){
    console.log(r.route.path)
  }
});

// 处理Vue路由 - 所有未匹配的路由返回index.html
app.get('*', (_, res) => {
  res.sendFile(path.join(__dirname, '..', 'dist', 'index.html'));
});

// 启动服务器 - 监听所有网络接口
app.listen(port, '0.0.0.0', () => {
  console.log(`服务器运行在 http://0.0.0.0:${port}`);
  console.log(`请使用本机实际IP地址访问服务器，以便安卓模拟器可以连接`);
});
