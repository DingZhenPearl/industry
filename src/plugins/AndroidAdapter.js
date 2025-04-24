/**
 * 安卓样式适配插件
 * 用于在Vue应用中自动检测安卓设备并应用特定样式
 */

import { Capacitor } from '@capacitor/core';

export default {
  install(Vue) {
    // 检测是否为安卓设备
    const isAndroidDevice = () => {
      // 检查是否在Capacitor环境中运行
      const isNative = Capacitor.isNativePlatform();
      
      // 检查平台是否为Android
      const isAndroid = Capacitor.getPlatform() === 'android';
      
      // 通过用户代理检测Android
      const userAgent = navigator.userAgent.toLowerCase();
      const isAndroidUA = /android/.test(userAgent);
      
      return (isNative && isAndroid) || isAndroidUA;
    };

    // 添加全局混入
    Vue.mixin({
      created() {
        // 在组件创建时检测安卓设备
        if (isAndroidDevice()) {
          // 如果是安卓设备，添加特定类
          document.documentElement.classList.add('android-device');
          
          // 设置安全区域变量
          this.updateSafeAreaInsets();
          
          // 监听屏幕旋转事件
          window.addEventListener('resize', this.updateSafeAreaInsets);
        }
      },
      beforeDestroy() {
        // 移除事件监听器
        window.removeEventListener('resize', this.updateSafeAreaInsets);
      },
      methods: {
        // 更新安全区域变量
        updateSafeAreaInsets() {
          // 获取安全区域尺寸
          const safeAreaTop = window.getComputedStyle(document.documentElement).getPropertyValue('--safe-area-inset-top') || '0px';
          const safeAreaRight = window.getComputedStyle(document.documentElement).getPropertyValue('--safe-area-inset-right') || '0px';
          const safeAreaBottom = window.getComputedStyle(document.documentElement).getPropertyValue('--safe-area-inset-bottom') || '0px';
          const safeAreaLeft = window.getComputedStyle(document.documentElement).getPropertyValue('--safe-area-inset-left') || '0px';
          
          // 设置CSS变量
          document.documentElement.style.setProperty('--safe-area-inset-top', safeAreaTop);
          document.documentElement.style.setProperty('--safe-area-inset-right', safeAreaRight);
          document.documentElement.style.setProperty('--safe-area-inset-bottom', safeAreaBottom);
          document.documentElement.style.setProperty('--safe-area-inset-left', safeAreaLeft);
        }
      }
    });

    // 添加全局指令：v-android-ripple
    Vue.directive('android-ripple', {
      inserted(el) {
        if (!isAndroidDevice()) return;
        
        // 添加涟漪效果容器
        const rippleContainer = document.createElement('span');
        rippleContainer.className = 'android-ripple-container';
        
        // 设置容器样式
        rippleContainer.style.position = 'absolute';
        rippleContainer.style.top = '0';
        rippleContainer.style.left = '0';
        rippleContainer.style.right = '0';
        rippleContainer.style.bottom = '0';
        rippleContainer.style.overflow = 'hidden';
        rippleContainer.style.borderRadius = 'inherit';
        rippleContainer.style.pointerEvents = 'none';
        
        // 确保元素有相对定位
        const position = window.getComputedStyle(el).position;
        if (position !== 'relative' && position !== 'absolute' && position !== 'fixed') {
          el.style.position = 'relative';
        }
        
        el.appendChild(rippleContainer);
        
        // 添加触摸事件
        el.addEventListener('touchstart', (e) => {
          // 创建涟漪元素
          const ripple = document.createElement('span');
          ripple.className = 'android-ripple';
          
          // 计算涟漪大小和位置
          const rect = el.getBoundingClientRect();
          const size = Math.max(rect.width, rect.height) * 2;
          const x = e.touches[0].clientX - rect.left;
          const y = e.touches[0].clientY - rect.top;
          
          // 设置涟漪样式
          ripple.style.position = 'absolute';
          ripple.style.width = `${size}px`;
          ripple.style.height = `${size}px`;
          ripple.style.top = `${y - size / 2}px`;
          ripple.style.left = `${x - size / 2}px`;
          ripple.style.borderRadius = '50%';
          ripple.style.backgroundColor = 'rgba(0, 0, 0, 0.1)';
          ripple.style.transform = 'scale(0)';
          ripple.style.transition = 'transform 0.5s ease-out, opacity 0.5s ease-out';
          ripple.style.opacity = '1';
          
          // 添加到容器
          rippleContainer.appendChild(ripple);
          
          // 触发涟漪动画
          setTimeout(() => {
            ripple.style.transform = 'scale(1)';
          }, 0);
          
          // 触摸结束后移除涟漪
          const handleTouchEnd = () => {
            ripple.style.opacity = '0';
            
            setTimeout(() => {
              if (rippleContainer.contains(ripple)) {
                rippleContainer.removeChild(ripple);
              }
            }, 500);
            
            document.removeEventListener('touchend', handleTouchEnd);
            document.removeEventListener('touchcancel', handleTouchEnd);
          };
          
          document.addEventListener('touchend', handleTouchEnd);
          document.addEventListener('touchcancel', handleTouchEnd);
        });
      }
    });
  }
};
