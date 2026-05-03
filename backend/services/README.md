# services/ — 服务层

业务逻辑核心层，每个文件封装一个业务领域。Service 负责编排 DAO 调用、校验业务规则、管理事务，对上暴露给路由层调用。

## 文件说明

### `__init__.py`
集中导出所有 Service 类：`AuthService`、`PunchService`、`LeaveService`、`MakeupService`、`TeacherService`、`AdminService`、`LogService`、`NotificationService`、`ConfigService`、`StatisticsService`、`MonitorService`。

### `auth_service.py`
**认证服务** — 处理登录、修改密码、重置密码。

- 登录时验证密码，检查账户锁定状态（登录失败次数过多会锁账户）
- 登入成功后清除失败计数，记录登录时间和 IP
- 修改密码需验证旧密码；重置密码无需旧密码

### `punch_service.py`
**打卡签到服务** — 核心业务。

- 验证打卡位置是否在围栏内（调用 `utils/geo.py` 的 Haversine 公式计算距离）
- 匹配当前时间所属的时间段
- 检查是否重复打卡、是否已有请假记录
- 支持单次/多次打卡配置（`ConfigService`）

### `leave_service.py`
**请假服务** — 处理请假申请与审批。

- 提交时校验日期范围合法性，检测与已有请假是否重叠
- 教师可查看所带班级的待审批列表并批准/拒绝

### `makeup_service.py`
**补签服务** — 处理过期补签到申请。

- 限制补签范围（默认 3 天内），防止无限制追补
- 检测同一日期是否已打卡或已提交过补签申请
- 教师审批通过后写入正式的打卡记录

### `teacher_service.py`
**教师服务** — 教师特有的管理操作。

- 任命/撤销班委（monitor）
- 查看自己班级的学生列表和班委列表

### `admin_service.py`
**管理后台服务** — 系统最大的 Service，处理管理员的所有操作。

- **CRUD 管理**：校区、院系、专业、年级、班级、用户、教学分配
- **打卡规则管理**：时间段、地理围栏、规则绑定（含优先级冲突校验）
- **考勤记录管理**：手动增删改签到/请假记录
- **数据导出与统计**：考勤数据分页查询、仪表盘统计

### `log_service.py`
**操作日志服务** — 审计追踪。

- 支持的操作类型有白名单限制：`LOGIN`、`PUNCH`、`LEAVE`、`APPROVE` 等
- 记录操作前后的数据快照（`before_data` / `after_data`）
- 支持按操作人、操作类型、目标对象等维度查询

### `notification_service.py`
**通知服务** — 系统消息推送。

- 支持单人发送和批量发送
- 按已读/未读、通知类型筛选
- 单条标记已读或全部已读

### `config_service.py`
**配置服务** — 全局打卡配置的读写。

- 配置项：时间检查开关、位置检查开关、允许多次打卡、允许补签、节假日范围
- 提供 `is_holiday(date)`、`is_time_check_enabled()` 等便捷判断方法，供其他 Service 调用

### `statistics_service.py`
**统计服务** — 考勤数据分析。

- 班级维度统计：出勤率、缺勤人数等
- 学生维度统计：个人出勤历史
- 缺勤预警：低于设定出勤阈值的学生列表
- 趋势数据：过去 N 天的出勤变化

### `monitor_service.py`
**班委视角服务** — 供班委（monitor）查看班级考勤概况。

- 当日应到/实到/请假人数
- 班级请假和打卡记录列表
- 汇总统计
