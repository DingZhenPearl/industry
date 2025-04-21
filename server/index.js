const express = require('express');
const path = require('path');
const { setupMiddleware } = require('./middleware');
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
app.use('/api/workorders', workorderRoutes);
app.use('/api/equipment', equipmentRoutes);
app.use('/api/production_line', productionLineRoutes);
app.use('/api/attendance', attendanceRoutes);

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

// 启动服务器
app.listen(port, () => {
  console.log(`服务器运行在 http://localhost:${port}`);
});
