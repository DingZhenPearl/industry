/**
 * 导航辅助工具
 * 用于确保路由跳转时携带uid参数
 */

/**
 * 带有uid参数的路由跳转
 * @param {Object} router - Vue Router实例
 * @param {string} path - 目标路径
 * @param {Object} query - 额外的查询参数
 */
export function navigateWithUid(router, path, query = {}) {
  // 从当前路由或本地存储中获取uid
  const currentRoute = router.currentRoute;
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
  const uid = currentRoute.query.uid || userInfo.uid;
  
  // 如果有uid，添加到查询参数中
  if (uid) {
    router.push({
      path,
      query: { ...query, uid }
    });
  } else {
    router.push({
      path,
      query
    });
  }
}

/**
 * 带有uid参数的返回上一页
 * @param {Object} router - Vue Router实例
 */
export function goBackWithUid(router) {
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
  const uid = router.currentRoute.query.uid || userInfo.uid;
  
  if (window.history.length > 1) {
    router.go(-1);
  } else {
    // 如果没有历史记录，根据用户角色跳转到对应的首页
    const role = userInfo.role;
    let homePath = '/login';
    
    switch(role) {
      case 'supervisor':
        homePath = '/supervisor/monitor';
        break;
      case 'foreman':
        homePath = '/foreman/workorder';
        break;
      case 'member':
        homePath = '/worker/workorders';
        break;
      case 'safety_officer':
        homePath = '/safety-officer/monitoring';
        break;
    }
    
    if (uid) {
      router.push({ path: homePath, query: { uid } });
    } else {
      router.push(homePath);
    }
  }
}
