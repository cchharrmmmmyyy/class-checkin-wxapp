// ECharts 轻量入口 - 仅导入 admin.html 使用的图表类型
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { CanvasRenderer } from 'echarts/renderers'
import {
  GridComponent,
  TooltipComponent,
  TitleComponent,
} from 'echarts/components'

echarts.use([LineChart, CanvasRenderer, GridComponent, TooltipComponent, TitleComponent])

// 保持与现有代码兼容：echarts.init(), echarts.graphic.LinearGradient 等
if (typeof window !== 'undefined') {
  window.echarts = echarts
}
