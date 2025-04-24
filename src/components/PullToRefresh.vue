<template>
  <div 
    class="pull-to-refresh-container"
    @touchstart="onTouchStart"
    @touchmove="onTouchMove"
    @touchend="onTouchEnd"
  >
    <div class="pull-indicator" :style="indicatorStyle">
      <div class="refresh-icon" :class="{ 'rotating': isRefreshing }"></div>
      <span>{{ refreshText }}</span>
    </div>
    <div class="content-wrapper" :style="contentStyle">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PullToRefresh',
  props: {
    threshold: {
      type: Number,
      default: 80
    },
    maxDistance: {
      type: Number,
      default: 120
    },
    refreshingTime: {
      type: Number,
      default: 1000
    }
  },
  data() {
    return {
      startY: 0,
      currentY: 0,
      isTouching: false,
      isRefreshing: false,
      pullDistance: 0
    }
  },
  computed: {
    contentStyle() {
      return {
        transform: `translateY(${this.pullDistance}px)`,
        transition: this.isTouching ? 'none' : 'transform 0.3s ease'
      }
    },
    indicatorStyle() {
      return {
        opacity: Math.min(this.pullDistance / this.threshold, 1),
        transform: `translateY(${Math.min(this.pullDistance - 50, 0)}px)`,
        transition: this.isTouching ? 'none' : 'all 0.3s ease'
      }
    },
    refreshText() {
      if (this.isRefreshing) {
        return '刷新中...';
      }
      return this.pullDistance >= this.threshold ? '释放刷新' : '下拉刷新';
    }
  },
  methods: {
    onTouchStart(e) {
      // 只有当滚动到顶部时才启用下拉刷新
      if (document.documentElement.scrollTop === 0) {
        this.startY = e.touches[0].clientY;
        this.isTouching = true;
      }
    },
    onTouchMove(e) {
      if (!this.isTouching || this.isRefreshing) return;
      
      this.currentY = e.touches[0].clientY;
      const distance = this.currentY - this.startY;
      
      // 只有下拉时才触发刷新
      if (distance > 0) {
        // 添加阻尼效果，使下拉越来越难
        this.pullDistance = Math.min(distance * 0.5, this.maxDistance);
        e.preventDefault(); // 防止页面滚动
      }
    },
    onTouchEnd() {
      if (!this.isTouching || this.isRefreshing) return;
      
      this.isTouching = false;
      
      if (this.pullDistance >= this.threshold) {
        this.refresh();
      } else {
        this.reset();
      }
    },
    refresh() {
      this.isRefreshing = true;
      this.pullDistance = this.threshold;
      
      // 触发刷新事件
      this.$emit('refresh');
      
      // 模拟刷新完成
      setTimeout(() => {
        this.reset();
        this.isRefreshing = false;
      }, this.refreshingTime);
    },
    reset() {
      this.pullDistance = 0;
    }
  }
}
</script>

<style scoped>
.pull-to-refresh-container {
  position: relative;
  overflow: hidden;
}

.pull-indicator {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 50px;
  color: #2196F3;
  font-size: 14px;
  opacity: 0;
  z-index: 10;
}

.refresh-icon {
  width: 20px;
  height: 20px;
  margin-right: 8px;
  border: 2px solid #2196F3;
  border-radius: 50%;
  border-top-color: transparent;
}

.refresh-icon.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.content-wrapper {
  min-height: 100%;
  will-change: transform;
}
</style>
