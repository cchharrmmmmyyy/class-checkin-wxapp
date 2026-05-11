// Element Plus 按需加载入口
// 仅导入 admin.html 实际使用的组件和图标

// --- 组件样式按需导入 ---
import 'element-plus/es/components/menu/style/css'
import 'element-plus/es/components/icon/style/css'
import 'element-plus/es/components/tag/style/css'
import 'element-plus/es/components/input/style/css'
import 'element-plus/es/components/button/style/css'
import 'element-plus/es/components/table/style/css'
import 'element-plus/es/components/pagination/style/css'
import 'element-plus/es/components/select/style/css'
import 'element-plus/es/components/option/style/css'
import 'element-plus/es/components/date-picker/style/css'
import 'element-plus/es/components/dialog/style/css'
import 'element-plus/es/components/form/style/css'
import 'element-plus/es/components/form-item/style/css'
import 'element-plus/es/components/input-number/style/css'
import 'element-plus/es/components/switch/style/css'
import 'element-plus/es/components/time-picker/style/css'
import 'element-plus/es/components/radio-group/style/css'
import 'element-plus/es/components/radio/style/css'
import 'element-plus/es/components/checkbox/style/css'
import 'element-plus/es/components/message/style/css'
import 'element-plus/es/components/message-box/style/css'

// --- 组件导入 ---
import {
  ElMenu,
  ElSubMenu,
  ElMenuItem,
  ElIcon,
  ElTag,
  ElInput,
  ElButton,
  ElTable,
  ElTableColumn,
  ElPagination,
  ElSelect,
  ElOption,
  ElDatePicker,
  ElDialog,
  ElForm,
  ElFormItem,
  ElInputNumber,
  ElSwitch,
  ElTimePicker,
  ElRadioGroup,
  ElRadio,
  ElCheckbox,
  ElMessage,
  ElMessageBox,
} from 'element-plus'

// --- 图标导入（用于 <el-icon> 内） ---
import {
  DataLine,
  OfficeBuilding,
  User,
  UserFilled,
  Reading,
  Calendar,
  Filter,
  Setting,
  Document,
  Avatar,
  ArrowDown,
  CircleCheck,
  Clock,
  Warning,
} from '@element-plus/icons-vue'

// 组件列表（可通过 app.use() 注册）
const components = {
  ElMenu,
  ElSubMenu,
  ElMenuItem,
  ElIcon,
  ElTag,
  ElInput,
  ElButton,
  ElTable,
  ElTableColumn,
  ElPagination,
  ElSelect,
  ElOption,
  ElDatePicker,
  ElDialog,
  ElForm,
  ElFormItem,
  ElInputNumber,
  ElSwitch,
  ElTimePicker,
  ElRadioGroup,
  ElRadio,
  ElCheckbox,
}

// 图标列表（需通过 app.component() 注册）
const icons = {
  DataLine,
  OfficeBuilding,
  User,
  UserFilled,
  Reading,
  Calendar,
  Filter,
  Setting,
  Document,
  Avatar,
  ArrowDown,
  CircleCheck,
  Clock,
  Warning,
}

// 注册函数：供 admin.html 调用
if (typeof window !== 'undefined') {
  window.__EL_PLUS__ = {
    components,
    icons,
    ElMessage,
    ElMessageBox,
  }
}
