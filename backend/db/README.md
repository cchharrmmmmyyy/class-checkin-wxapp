# db/ — 数据库初始化与 Schema

负责数据库的创建、迁移式初始化和测试数据填充。所有表结构定义在 `schema/` 目录下，按编号顺序执行。

## 文件说明

### `__init__.py`
导出 `check_and_init_database` 和 `init_database` 供应用入口调用。

### `init_db.py`
**数据库初始化脚本** — 三个核心函数：

- `init_database()` — 遍历 `db/schema/` 下所有 `.sql` 文件，按文件名排序后依次执行。可重复执行（所有表使用 `CREATE TABLE IF NOT EXISTS`）
- `insert_test_data(cursor)` — 插入测试数据（默认管理员、示例校区/院系/专业/班级、示例时间段和围栏等）
- `check_and_init_database()` — 安全检查：只有 `users` 表不存在时才初始化，避免覆盖已有数据。由 `app.py` 启动时调用

是否插入测试数据由 `.env` 中的 `INSERT_TEST_DATA` 控制。

## schema/ 建表脚本

按依赖顺序编号，由 `init_db.py` 顺序执行。

| 编号 | 文件 | 创建对象 | 说明 |
|------|------|----------|------|
| 01 | `01_campuses.sql` | `campuses` | 校区表，组织架构顶层 |
| 02 | `02_departments.sql` | `departments` | 院系表，外键关联校区 |
| 03 | `03_majors.sql` | `majors` | 专业表，外键关联院系 |
| 04 | `04_grades.sql` | `grades` | 年级表，外键关联专业 |
| 05 | `05_classes.sql` | `classes` | 班级表，外键关联年级 |
| 06 | `06_users.sql` | `users` | 用户表（学生/教师/班委/管理员），含登录态字段和软删除 |
| 07 | `07_class_teachers.sql` | `class_teachers` | 教师-班级多对多关联表 |
| 08 | `08_punch_geofences.sql` | `punch_geofences` | 打卡围栏（圆心+半径 或 多边形） |
| 09 | `09_punch_time_slots.sql` | `punch_time_slots` | 打卡时间段定义 |
| 10 | `10_punch_rules.sql` | `punch_rules` | 打卡规则：将时段与围栏绑定，含优先级 |
| 11 | `11_punches.sql` | `punches` | 打卡记录主体 |
| 12 | `12_leaves.sql` | `leaves` | 请假申请记录 |
| 13 | `13_makeup_requests.sql` | `makeup_requests` | 补签申请记录 |
| 14 | `14_punch_config.sql` | `punch_config` | 全局打卡配置（单行） |
| 15 | `15_operation_logs.sql` | `operation_logs` | 操作审计日志 |
| 16 | `16_notifications.sql` | `notifications` | 系统通知消息 |
| 17 | `17_read_views.sql` | `v_leave_user_read`, `v_makeup_user_read` | 视图：将请假/补签与用户表 JOIN 以方便查询 |

### 层级关系

```
campuses (校区)
  └── departments (院系)
        └── majors (专业)
              └── grades (年级)
                    └── classes (班级)
                          ├── users (学生)
                          └── class_teachers (教师分配)
```
