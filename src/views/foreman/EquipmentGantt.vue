<template>
  <div class="equipment-gantt">
    <div class="gantt-controls">
      <div class="date-range">
        <input type="date" v-model="startDate" @change="updateGantt">
        <span>至</span>
        <input type="date" v-model="endDate" @change="updateGantt">
      </div>
      <div class="status-filter">
        <label><input type="checkbox" v-model="showRunning" @change="updateGantt"> 正常运行</label>
        <label><input type="checkbox" v-model="showMaintenance" @change="updateGantt"> 维护中</label>
        <label><input type="checkbox" v-model="showFault" @change="updateGantt"> 故障</label>
        <label><input type="checkbox" v-model="showStandby" @change="updateGantt"> 待机</label>
      </div>
    </div>
    <div class="gantt-container" ref="ganttContainer"></div>
  </div>
</template>

<script>
import 'dhtmlx-gantt/codebase/dhtmlxgantt.css'

export default {
  name: 'EquipmentGantt',
  data() {
    return {
      startDate: new Date().toISOString().split('T')[0],
      endDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      showRunning: true,
      showMaintenance: true,
      showFault: true,
      showStandby: true,
      tasks: [
        {
          id: 1,
          text: '注塑机A-01',
          utilization: 95,
          type: 'running',
          start_date: '2023-07-10 08:00',
          end_date: '2023-07-10 12:00'
        },
        {
          id: 2,
          text: '注塑机A-01',
          type: 'maintenance',
          start_date: '2023-07-10 12:00',
          end_date: '2023-07-10 14:00'
        },
        {
          id: 3,
          text: '检测仪B-01',
          utilization: 85,
          type: 'fault',
          start_date: '2023-07-10 09:00',
          end_date: '2023-07-10 11:00'
        }
      ]
    }
  },
  mounted() {
    this.initGantt()
  },
  methods: {
    initGantt() {
      const gantt = window.gantt
      
      // 配置甘特图
      gantt.config.date_format = '%Y-%m-%d %H:%i'
      gantt.config.scale_height = 60
      
      // 启用鼠标滚轮缩放
      gantt.config.min_column_width = 20
      gantt.config.scroll_on = true
      gantt.ext.zoom.init({
        levels: [
          {
            name: '小时',
            scale_height: 60,
            min_column_width: 30,
            scales: [
              {unit: 'day', step: 1, format: '%d %M'},
              {unit: 'hour', step: 1, format: '%H:00'}
            ]
          },
          {
            name: '日',
            scale_height: 60,
            min_column_width: 70,
            scales: [
              {unit: 'week', step: 1, format: '第%W周'},
              {unit: 'day', step: 1, format: '%d日'}
            ]
          },
          {
            name: '周',
            scale_height: 60,
            min_column_width: 100,
            scales: [
              {unit: 'month', step: 1, format: '%M'},
              {unit: 'week', step: 1, format: '第%W周'}
            ]
          }
        ]
      });
      
      gantt.config.columns = [
        {name: 'text', label: '设备名称', tree: true, width: 200},
        {name: 'utilization', label: '产能利用率', align: 'center', width: 100, template: (task) => task.utilization + '%'}
      ]

      // 自定义任务样式
      gantt.templates.task_class = (start, end, task) => {
        return task.type || ''
      }

      // 绑定鼠标滚轮事件
      gantt.attachEvent("onMouseWheel", function(e){
        if (e.deltaY < 0) {
          gantt.ext.zoom.zoomIn();
        } else {
          gantt.ext.zoom.zoomOut();
        }
        return true;
      });

      gantt.init(this.$refs.ganttContainer)

      gantt.parse({data: this.tasks})
    },
    updateGantt() {
      const gantt = window.gantt
      gantt.config.start_date = new Date(this.startDate)
      gantt.config.end_date = new Date(this.endDate)
      
      // 根据状态筛选显示的任务
      gantt.clearAll()
      const filteredTasks = this.tasks.filter(task => {
        switch(task.type) {
          case 'running': return this.showRunning
          case 'maintenance': return this.showMaintenance
          case 'fault': return this.showFault
          case 'standby': return this.showStandby
          default: return true
        }
      })
      
      gantt.parse({data: filteredTasks})
    }
  }
}
</script>

<style>
.equipment-gantt {
  padding: 20px;
}

.gantt-controls {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 10px;
}

.date-range input[type="date"] {
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.status-filter {
  display: flex;
  gap: 15px;
}

.status-filter label {
  display: flex;
  align-items: center;
  gap: 5px;
}

.gantt-container {
  height: 500px;
  width: 100%;
}

/* 任务状态样式 */
.gantt_task_line.running {
  background-color: #4CAF50;
}

.gantt_task_line.maintenance {
  background-color: #2196F3;
}

.gantt_task_line.fault {
  background-color: #f44336;
}

.gantt_task_line.standby {
  background-color: #FFC107;
}
</style>