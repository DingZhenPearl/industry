<template>
  <div id="app" :class="{ 'android-device': isAndroidDevice }">
    <router-view/>
  </div>
</template>

<script>
import { Capacitor } from '@capacitor/core';

export default {
  name: 'App',
  data() {
    return {
      isAndroidDevice: false
    }
  },
  created() {
    // 检测是否为安卓设备
    this.detectAndroidDevice();
  },
  methods: {
    detectAndroidDevice() {
      // 检查是否在Capacitor环境中运行
      const isNative = Capacitor.isNativePlatform();

      // 检查平台是否为Android
      const isAndroid = Capacitor.getPlatform() === 'android';

      // 通过用户代理检测Android
      const userAgent = navigator.userAgent.toLowerCase();
      const isAndroidUA = /android/.test(userAgent);

      // 如果是Android设备，添加特定类
      this.isAndroidDevice = isNative && isAndroid || isAndroidUA;

      if (this.isAndroidDevice) {
        console.log('检测到Android设备，应用特定样式');
        document.documentElement.classList.add('android-device');
      }
    }
  }
}
</script>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  text-align: center;
  color: #2c3e50;
}
</style>
