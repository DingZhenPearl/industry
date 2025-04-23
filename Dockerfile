# 使用Node.js作为基础镜像
FROM node:14-alpine AS build

# 设置工作目录
WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制所有源代码
COPY . .

# 构建前端应用
RUN npm run build

# 第二阶段：运行时镜像
FROM node:14-alpine

# 安装Python和MySQL客户端
RUN apk add --no-cache python3 py3-pip mysql-client && \
    pip3 install mysql-connector-python

# 设置工作目录
WORKDIR /app

# 从构建阶段复制构建结果和必要文件
COPY --from=build /app/dist ./dist
COPY --from=build /app/server ./server
COPY --from=build /app/pyScripts ./pyScripts
COPY --from=build /app/package*.json ./

# 只安装生产环境依赖
RUN npm install --only=production

# 创建配置目录
RUN mkdir -p /app/config

# 复制启动脚本
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# 暴露端口
EXPOSE 3000

# 设置环境变量
ENV NODE_ENV=production
ENV DB_HOST=mysql
ENV DB_USER=root
ENV DB_PASSWORD=mwYgR7#*X2
ENV DB_NAME=industry_db

# 启动应用
ENTRYPOINT ["/app/docker-entrypoint.sh"]
