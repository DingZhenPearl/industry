const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  // 确保publicPath为相对路径，这对于Capacitor应用很重要
  publicPath: '',
  // 禁用生产环境的source map以减小包体积
  productionSourceMap: false
})
