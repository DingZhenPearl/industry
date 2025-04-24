/**
 * 安卓手势支持
 * 提供常见的移动端手势支持，如双击、长按、滑动等
 */

// 手势配置
const GESTURE_CONFIG = {
  // 长按触发时间（毫秒）
  LONG_PRESS_DELAY: 500,
  // 双击最大间隔（毫秒）
  DOUBLE_TAP_DELAY: 300,
  // 滑动最小距离（像素）
  SWIPE_THRESHOLD: 50,
  // 滑动最大时间（毫秒）
  SWIPE_MAX_TIME: 300
};

/**
 * 添加长按手势
 * @param {HTMLElement} element - 要添加手势的元素
 * @param {Function} callback - 长按触发的回调函数
 * @returns {Object} - 包含移除事件监听器的方法
 */
export function addLongPressGesture(element, callback) {
  let timer = null;
  let isLongPress = false;
  
  const handleStart = (e) => {
    isLongPress = false;
    timer = setTimeout(() => {
      isLongPress = true;
      callback(e);
    }, GESTURE_CONFIG.LONG_PRESS_DELAY);
  };
  
  const handleEnd = () => {
    clearTimeout(timer);
  };
  
  const handleCancel = () => {
    clearTimeout(timer);
  };
  
  element.addEventListener('touchstart', handleStart);
  element.addEventListener('touchend', handleEnd);
  element.addEventListener('touchcancel', handleCancel);
  
  // 返回清理函数
  return {
    remove: () => {
      element.removeEventListener('touchstart', handleStart);
      element.removeEventListener('touchend', handleEnd);
      element.removeEventListener('touchcancel', handleCancel);
    }
  };
}

/**
 * 添加双击手势
 * @param {HTMLElement} element - 要添加手势的元素
 * @param {Function} callback - 双击触发的回调函数
 * @param {Function} singleTapCallback - 单击触发的回调函数（可选）
 * @returns {Object} - 包含移除事件监听器的方法
 */
export function addDoubleTapGesture(element, callback, singleTapCallback) {
  let lastTap = 0;
  let tapTimeout = null;
  
  const handleTap = (e) => {
    const currentTime = new Date().getTime();
    const tapLength = currentTime - lastTap;
    
    clearTimeout(tapTimeout);
    
    if (tapLength < GESTURE_CONFIG.DOUBLE_TAP_DELAY && tapLength > 0) {
      // 双击
      callback(e);
      lastTap = 0;
    } else {
      // 可能是单击，等待一段时间确认不是双击的一部分
      lastTap = currentTime;
      if (singleTapCallback) {
        tapTimeout = setTimeout(() => {
          singleTapCallback(e);
        }, GESTURE_CONFIG.DOUBLE_TAP_DELAY);
      }
    }
  };
  
  element.addEventListener('touchend', handleTap);
  
  // 返回清理函数
  return {
    remove: () => {
      element.removeEventListener('touchend', handleTap);
    }
  };
}

/**
 * 添加滑动手势
 * @param {HTMLElement} element - 要添加手势的元素
 * @param {Object} callbacks - 包含各方向滑动回调的对象 {onSwipeLeft, onSwipeRight, onSwipeUp, onSwipeDown}
 * @returns {Object} - 包含移除事件监听器的方法
 */
export function addSwipeGesture(element, callbacks) {
  let startX = 0;
  let startY = 0;
  let startTime = 0;
  
  const handleStart = (e) => {
    startX = e.touches[0].clientX;
    startY = e.touches[0].clientY;
    startTime = new Date().getTime();
  };
  
  const handleEnd = (e) => {
    const endX = e.changedTouches[0].clientX;
    const endY = e.changedTouches[0].clientY;
    const endTime = new Date().getTime();
    const diffTime = endTime - startTime;
    
    // 检查是否是快速滑动
    if (diffTime < GESTURE_CONFIG.SWIPE_MAX_TIME) {
      const diffX = endX - startX;
      const diffY = endY - startY;
      
      // 水平滑动距离大于垂直滑动
      if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > GESTURE_CONFIG.SWIPE_THRESHOLD) {
        if (diffX > 0 && callbacks.onSwipeRight) {
          callbacks.onSwipeRight(e);
        } else if (diffX < 0 && callbacks.onSwipeLeft) {
          callbacks.onSwipeLeft(e);
        }
      } 
      // 垂直滑动距离大于水平滑动
      else if (Math.abs(diffY) > Math.abs(diffX) && Math.abs(diffY) > GESTURE_CONFIG.SWIPE_THRESHOLD) {
        if (diffY > 0 && callbacks.onSwipeDown) {
          callbacks.onSwipeDown(e);
        } else if (diffY < 0 && callbacks.onSwipeUp) {
          callbacks.onSwipeUp(e);
        }
      }
    }
  };
  
  element.addEventListener('touchstart', handleStart);
  element.addEventListener('touchend', handleEnd);
  
  // 返回清理函数
  return {
    remove: () => {
      element.removeEventListener('touchstart', handleStart);
      element.removeEventListener('touchend', handleEnd);
    }
  };
}

/**
 * 添加捏合缩放手势
 * @param {HTMLElement} element - 要添加手势的元素
 * @param {Function} onPinch - 捏合时的回调，参数为缩放比例
 * @returns {Object} - 包含移除事件监听器的方法
 */
export function addPinchGesture(element, onPinch) {
  let initialDistance = 0;
  
  const getDistance = (e) => {
    if (e.touches.length < 2) return 0;
    
    const x1 = e.touches[0].clientX;
    const y1 = e.touches[0].clientY;
    const x2 = e.touches[1].clientX;
    const y2 = e.touches[1].clientY;
    
    return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
  };
  
  const handleStart = (e) => {
    if (e.touches.length === 2) {
      initialDistance = getDistance(e);
    }
  };
  
  const handleMove = (e) => {
    if (e.touches.length === 2 && initialDistance > 0) {
      const currentDistance = getDistance(e);
      const scale = currentDistance / initialDistance;
      
      if (onPinch) {
        onPinch(scale, e);
      }
    }
  };
  
  const handleEnd = () => {
    initialDistance = 0;
  };
  
  element.addEventListener('touchstart', handleStart);
  element.addEventListener('touchmove', handleMove);
  element.addEventListener('touchend', handleEnd);
  element.addEventListener('touchcancel', handleEnd);
  
  // 返回清理函数
  return {
    remove: () => {
      element.removeEventListener('touchstart', handleStart);
      element.removeEventListener('touchmove', handleMove);
      element.removeEventListener('touchend', handleEnd);
      element.removeEventListener('touchcancel', handleEnd);
    }
  };
}

// 导出所有手势
export default {
  addLongPressGesture,
  addDoubleTapGesture,
  addSwipeGesture,
  addPinchGesture
};
