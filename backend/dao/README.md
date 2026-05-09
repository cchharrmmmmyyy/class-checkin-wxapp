# dao/ — 数据访问层

封装所有数据库操作，每个 DAO 对应一张表。DAO 层只包含 SQL 操作，不做业务判断。

## 文件说明

### `__init__.py`
集中导出全部 16 个 DAO 类及 `BaseDAO`。

### `base_dao.py`
**泛型抽象基类** — `BaseDAO(Generic[T])`，提供通用 CRUD 方法，其他 DAO 继承它。

通用方法：
- `count(where, params, conn)` — 计数查询
- `get_by_id(id, conn)` — 按主键查单条，返回 Model 对象
- `get_list(where, params, order_by, limit, offset, conn)` — 条件分页查询，返回 Model 列表
- `create(data, conn)` — 插入，返回自增主键
- `update(id, data, conn)` — 更新
- `delete(id, conn)` — 自动路由：支持软删除的表调 `soft_delete()`，否则调 `hard_delete()`
- `hard_delete(id, conn)` — 物理删除
- `soft_delete(id, conn)` — 软删除（设 `deleted_at` = CURRENT_TIMESTAMP）

安全校验：
- `VALID_TABLE_NAMES` — 表名白名单
- `SAFE_IDENTIFIER_PATTERN` — 列名校验
- `ORDER_BY_WHITELIST` — ORDER BY 白名单映射
- `SAFE_ORDER_BY_PATTERN` — ORDER BY 正则校验
- `SAFE_WHERE_PATTERN` — WHERE 子句安全模式校验

`_row_to_model()` 自动过滤 Model 不存在的列，所有方法支持可选 `conn` 参数以实现跨表事务。

### `campus_dao.py`
校区 DAO — 操作 `campuses` 表。硬删除。

### `department_dao.py`
院系 DAO — 操作 `departments` 表。硬删除。

### `major_dao.py`
专业 DAO — 操作 `majors` 表。硬删除。

### `grade_dao.py`
年级 DAO — 操作 `grades` 表。硬删除。

### `class_dao.py`
班级 DAO — 操作 `classes` 表，主键为 `class_name`（字符串）。`create()` 返回 `class_name`。

### `user_dao.py`
用户 DAO — 操作 `users` 表，`create()` 设置 `is_first_login` 默认值。

额外方法：
- `get_by_username(username)` — 按用户名查用户（登录用）
- `get_by_student_id(student_id)` — 按学号查用户
- `count_by_role(role)` — 按角色统计人数

### `class_teacher_dao.py`
教学分配 DAO — 操作 `class_teachers` 表，复合主键 `(class_name, teacher_id)`。`create()`、`update()`、`delete()` 均有独立 SQL。

### `punch_geofence_dao.py`
围栏 DAO — 操作 `punch_geofences` 表，`create()` 设置 `enabled` 默认值。

额外方法：
- `get_enabled_geofences()` — 获取所有启用且未软删除的围栏
- `get_first_enabled()` — 获取第一个启用的围栏

### `punch_time_slot_dao.py`
时段 DAO — 操作 `punch_time_slots` 表。

### `punch_rule_dao.py`
规则 DAO — 操作 `punch_rules` 表。`create()` 和 `update()` 设置 `priority`、`time_enabled`、`location_enabled`、`enabled` 默认值。

### `punch_dao.py`
打卡记录 DAO — 操作 `punches` 表。

额外方法：
- `get_punch_by_user_and_date(user_id, date)` — 查某用户某天是否已打卡
- `get_punches_by_user(user_id, limit)` — 查用户打卡记录（按日期倒序）
- `count_by_date(date)` — 统计某天打卡人数（按 user_id 去重）

### `leave_dao.py`
请假 DAO — 操作 `leaves` 表。`count()` 使用视图 `v_leave_user_read` 查询。

额外方法：
- `get_leave_records_by_user(user_id)` — 查用户请假记录
- `get_pending_leave_applications_by_class(class_name)` — 班级待审批请假
- `get_leave_record_by_id_and_class(leave_id, class_name)` — 根据 ID 和班级查请假
- `update_leave_status(id, status)` — 更新审批状态，设 `approved_at` 为当前时间
- `count_approved_by_date(date_str)` — 统计某日已批准的请假数
- `count_pending()` — 统计待审批请假数

### `makeup_request_dao.py`
补签 DAO — 操作 `makeup_requests` 表。`count()` 使用视图 `v_makeup_user_read` 查询。

额外方法：
- `get_by_user_and_date(user_id, date)` — 查是否已有补签申请
- `get_by_user(user_id)` — 查用户的所有补签申请
- `get_pending_by_class(class_name)` — 班级待审批补签
- `get_by_id_and_class(request_id, class_name)` — 根据 ID 和班级查补签
- `update_status(id, status)` — 更新审批状态，设 `approved_at` 为当前时间

### `punch_config_dao.py`
配置 DAO — 操作 `punch_config` 表（单行配置，ID 恒为 1）。

- `get_config()` — 获取全局配置
- `update(data)` — 更新配置字段

### `operation_log_dao.py`
操作日志 DAO — 操作 `operation_logs` 表。支持外部传入 `conn` 参数。

### `notification_dao.py`
通知 DAO — 操作 `notifications` 表。`delete()` 为硬删除。

额外方法：
- `mark_as_read(id, conn)` — 标记已读（支持事务内调用）
