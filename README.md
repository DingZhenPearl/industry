# 工厂智能管理系统

## 项目结构
```
├── android/            # Android应用项目（使用Capacitor生成）
├── pyScripts/          # Python数据库操作脚本
├── server/             # Node.js后端服务器
├── src/                # Vue前端代码
├── public/             # 静态资源文件
├── dist/               # 构建输出目录（不包含在版本控制中）
├── node_modules/       # Node.js依赖（不包含在版本控制中）
├── package.json        # 项目配置和依赖
├── package-lock.json   # 依赖版本锁定文件
├── vue.config.js       # Vue CLI配置
├── capacitor.config.js # Capacitor配置文件
├── babel.config.js     # Babel配置
├── jsconfig.json       # JavaScript项目配置
└── .gitignore          # Git忽略文件列表
```

## 环境要求
- Node.js 14+
- Python 3.12+
- MySQL 5.7+
- Conda (推荐使用Anaconda或Miniconda)
- Android Studio 4.0+ (用于构建安卓应用)
- JDK 11+ (用于安卓开发)

## 安装步骤

### 1. 使用Conda创建Python环境
```bash
# 使用environment.yml创建环境
conda env create -f environment.yml

# 激活环境
conda activate industry-env
```

### 1.1 手动安装Python依赖（不使用Conda时）
```bash
pip install mysql-connector-python
```

### 2. 配置数据库
1. 确保MySQL服务已启动
2. 修改 `pyScripts/verify_user.py` 和 `pyScripts/init_db.py` 中的数据库连接信息
3. 初始化数据库：
```bash
python pyScripts/init_db.py
```

### 3. 安装并启动Node.js服务器
```bash
cd server
npm install
npm run dev
```

### 4. 安装并启动Vue前端
```bash
npm install
npm run dev
```

## 测试账号
- 厂长：SP0001 / admin1
- 工长：FM0002 / foreman123
- 产线工人：WK0008 / worker123
- 安全员：SF0009 / safety123

## 功能说明
- 支持多角色登录系统
- 使用Session进行身份验证
- 密码加密存储
- 自动根据角色跳转到对应页面

## 根目录文件说明

### 1. package.json

项目的核心配置文件，定义了项目的元数据、依赖项和脚本命令。

主要内容：
- **项目信息**: 名称、版本、私有性等
- **脚本命令**:
  - `serve`: 启动Vue开发服务器
  - `build`: 构建Vue前端项目
  - `lint`: 运行代码检查
  - `server`: 启动Node.js服务器
  - `server:dev`: 使用nodemon启动服务器（开发模式）
  - `watch:build`: 监视文件变化并自动重新构建
- **依赖项**:
  - 前端依赖: Vue、Vue Router、Element UI、ECharts等
  - 后端依赖: Express、CORS、body-parser等
  - 开发依赖: Babel、ESLint、Vue CLI等

### 2. vue.config.js

Vue CLI的配置文件，用于自定义构建过程。

### 3. babel.config.js

Babel配置文件，定义JavaScript转译规则。

### 4. jsconfig.json

JavaScript项目配置文件，提供TypeScript支持和路径别名。

主要内容：
- **编译选项**: 目标ES版本、模块系统等
- **路径别名**: 定义`@`指向`src`目录
- **库引用**: 包含的JavaScript库

### 5. .gitignore

Git版本控制忽略文件列表。

### 6. public/index.html

前端应用的HTML模板文件。

### 7. environment.yml

Conda环境配置文件，定义了Python环境及其依赖包。

主要内容：
- Python 3.12
- mysql-connector-python 8.4.0
- 其他基本工具包

## 构建和运行流程

### 1. 环境准备

1. **准备Python环境**:
   ```bash
   # 创建并激活 Conda 环境
   conda env create -f environment.yml
   conda activate industry-env

   # 初始化数据库
   python pyScripts/init_db.py
   ```

2. **安装Node.js依赖**:
   ```bash
   # 安装项目依赖
   npm install

   # 安装服务器依赖
   cd server
   npm install
   cd ..
   ```

### 2. 开发模式

1. **启动后端服务器**:
   ```bash
   # 方式1：从项目根目录启动
   npm run server:dev

   # 方式2：从 server 目录启动
   cd server
   npm run dev
   ```

2. **启动前端开发服务器**:
   ```bash
   # 在新的终端窗口中执行
   npm run serve
   ```

3. **模拟监控数据**(可选):
   ```bash
   # 在新的终端窗口中执行
   python pyScripts/simulate_monitoring_data.py
   ```

### 3. 生产构建

1. **构建前端**:
   ```bash
   # 构建前端代码，生成静态文件到 dist 目录
   npm run build
   ```

2. **启动生产服务器**:
   ```bash
   # 启动生产环境服务器
   npm run server
   ```

### 4. 访问应用

- 开发模式: 浏览器访问 `http://localhost:5173`
- 生产模式: 浏览器访问 `http://localhost:3000`

### 5. 常见问题排查

- **数据库连接错误**: 检查 MySQL 服务是否运行，并确认 `pyScripts` 中的数据库连接信息是否正确
- **前端请求失败**: 确认后端服务器是否正常运行，检查浏览器控制台的网络请求错误
- **Python脚本错误**: 查看服务器控制台输出的Python错误信息

## 使用Capacitor构建安卓应用

本项目使用Capacitor将Vue应用打包成安卓原生应用。

### 1. 安装Capacitor依赖

```bash
npm install @capacitor/core @capacitor/cli @capacitor/android
```

### 2. 构建前端应用

```bash
npm run build
```

### 3. 同步到安卓项目

```bash
npx cap sync
```

### 4. 打开Android Studio

```bash
npx cap open android
```

### 5. 配置安卓项目

在Android Studio中，您可能需要进行以下操作：

## 服务器配置

本项目使用统一的服务器配置文件，方便在不同环境中部署。

### 配置文件位置

服务器配置文件位于 `src/config/server.js`。

### 修改服务器地址

如果需要部署到云服务器，请修改配置文件中的 `PROD_SERVER.cloud` 值：

```javascript
// 生产环境服务器地址
const PROD_SERVER = {
  // 云服务器地址，部署时修改这里
  cloud: 'http://your-cloud-server-ip:3000'
};
```

将 `'http://your-cloud-server-ip:3000'` 替换为您的实际云服务器地址。

### 切换服务器模式

在代码中，您可以使用以下方法切换服务器模式：

```javascript
// 切换到云服务器
import config from './config';
config.useCloudServer();

// 切换回本地服务器
config.useLocalServer();
```

我们还提供了一个组件 `ServerConfigSwitcher.vue`，可以在界面上切换服务器配置。

1. 更新应用图标：替换 `android/app/src/main/res` 目录下的图标文件
2. 修改应用名称：编辑 `android/app/src/main/res/values/strings.xml` 文件
3. 配置网络安全：确保 `android/app/src/main/AndroidManifest.xml` 中已添加网络安全配置

### 6. 构建安卓应用

在Android Studio中，选择 `Build > Build Bundle(s) / APK(s) > Build APK(s)` 来构建 APK 文件。

### 7. 安装到设备

构建完成后，您可以将APK文件安装到安卓设备上进行测试。

### 8. 注意事项

- 在移动应用中，需要在 `src/config.js` 文件中配置正确的后端服务器地址
- 确保移动设备和后端服务器在同一网络中，或者后端服务器可以从外部访问

### 模拟器调试
 在网易模拟器的shell文件夹下运行CMD，输入以下命令
 adb.exe connect 127.0.0.1:16384