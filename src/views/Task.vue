<template>
  <div class="task">
    <header class="header">
      <h1>任务</h1>
      <button class="add-button">添加</button>
    </header>
    
    <div class="content">
      <div class="calendar">
        <div class="calendar-header">2025年3月</div>
        <div class="weekdays">
          <div class="weekday">日</div>
          <div class="weekday">一</div>
          <div class="weekday">二</div>
          <div class="weekday">三</div>
          <div class="weekday">四</div>
          <div class="weekday">五</div>
          <div class="weekday">六</div>
        </div>
        <div class="days">
          <div class="day empty"></div>
          <div class="day empty"></div>
          <div class="day empty"></div>
          <div class="day empty"></div>
          <div class="day empty"></div>
          <div class="day empty"></div>
          <div class="day">1</div>
          <div class="day">2</div>
          <div class="day">3</div>
          <div class="day">4</div>
          <div class="day">5</div>
          <div class="day">6</div>
          <div class="day">7</div>
          <div class="day">8</div>
          <div class="day">9</div>
          <div class="day">10</div>
          <div class="day">11</div>
          <div class="day">12</div>
          <div class="day">13</div>
          <div class="day">14</div>
          <div class="day">15</div>
          <div class="day">16</div>
          <div class="day">17</div>
          <div class="day">18</div>
          <div class="day">19</div>
          <div class="day">20</div>
          <div class="day">21</div>
          <div class="day">22</div>
          <div class="day">23</div>
          <div class="day">24</div>
          <div class="day">25</div>
          <div class="day">26</div>
          <div class="day">27</div>
          <div class="day">28</div>
          <div class="day current">29</div>
        </div>
      </div>
    </div>
    
    <nav class="bottom-nav">
      <div class="nav-item" @click="$router.push('/')">
        <i class="nav-icon home-icon"></i>
        <span>首页</span>
      </div>
      <div class="nav-item active">
        <i class="nav-icon task-icon"></i>
        <span>任务</span>
      </div>
      <div class="nav-item" @click="$router.push('/notification')">
        <i class="nav-icon notification-icon"></i>
        <span>通知</span>
      </div>
      <div class="nav-item" @click="$router.push('/profile')">
        <i class="nav-icon profile-icon"></i>
        <span>我的</span>
      </div>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'TaskPage'
}
</script>

<style scoped>
.task {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.header {
  background-color: #2196F3;
  color: white;
  padding: 15px;
  text-align: center;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  margin: 0;
  flex: 1;
  text-align: center;
}

.add-button {
  background: none;
  border: none;
  color: white;
  font-size: 16px;
  cursor: pointer;
  padding: 5px 15px;
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 10px;
  overflow-y: auto;
}

.calendar {
  width: 100%;
}

.calendar-header {
  text-align: center;
  font-size: 18px;
  margin: 10px 0;
  font-weight: bold;
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 5px;
  margin-bottom: 5px;
}

.weekday {
  padding: 5px;
  font-weight: bold;
}

.days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 5px;
}

.day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 5px;
  border: 1px solid #e0e0e0;
}

.day.empty {
  border: none;
}

.day.current {
  background-color: #f00;
  color: white;
  font-weight: bold;
}

.bottom-nav {
  display: flex;
  justify-content: space-around;
  background-color: #f8f8f8;
  padding: 10px 0;
  border-top: 1px solid #e0e0e0;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}

.nav-icon {
  width: 24px;
  height: 24px;
  margin-bottom: 5px;
  background-color: #666;
  border-radius: 50%;
}

.nav-item.active {
  color: #2196F3;
}

.nav-item.active .nav-icon {
  background-color: #2196F3;
}
</style>