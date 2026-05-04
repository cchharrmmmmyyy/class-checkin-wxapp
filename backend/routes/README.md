# routes/ — 路由层

HTTP 接口暴露层，每个文件是一个 Flask Blueprint。只做参数校验和调用 Service，不直接操作数据库。

## 文件说明

### `__init__.py`
集中注册并导出所有 Blueprint：`auth_bp`、`student_bp`、`teacher_bp`、`admin_bp`、`common_bp`。

### `auth.py`
认证相关接口，挂载在 `/api` 下。

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/login` | POST | 用户登录（学生/教师/管理员），返回 JWT Token |
| `/api/change-password` | POST | 修改密码（需提供旧密码） |
| `/api/current-user` | GET | 获取当前登录用户信息 |

### `student.py`
学生端接口，挂载在 `/api/student` 下。需要 `token_required` 鉴权。

| 端点 | 功能 |
|------|------|
| `POST /punch` | 打卡签到（含 GPS 坐标） |
| `GET /punch-records` | 查询个人打卡记录（分页） |
| `POST /leave` | 提交请假申请 |
| `GET /leave-records` | 查询个人请假记录 |
| `POST /makeup` | 提交补签申请 |
| `GET /makeup-records` | 查询个人补签记录 |
| `GET /notifications` | 获取通知列表 |
| `GET /monitor/class-punch-status` | （班委）查看班级签到概况 |
| `GET /monitor/class-leaves` | （班委）查看班级请假情况 |
| `GET /monitor/class-makeups` | （班委）查看班级补签情况 |

### `teacher.py`
教师端接口，挂载在 `/api/teacher` 下。需要教师角色。

| 端点 | 功能 |
|------|------|
| `GET /classes` | 获取教师所带班级列表 |
| `GET /class-students` | 查看班级学生 |
| `GET /class-punch-summary` | 班级签到汇总 |
| `GET /pending-leaves` | 待审批请假列表 |
| `POST /approve-leave` | 审批请假（通过/拒绝） |
| `GET /pending-makeups` | 待审批补签列表 |
| `POST /approve-makeup` | 审批补签（通过/拒绝） |
| `POST /appoint-monitor` | 任命班委 |
| `POST /remove-monitor` | 取消班委 |
| `GET /monitors` | 查看班委列表 |

### `admin.py`
管理员端接口，挂载在 `/api/admin` 下。需要管理员角色。是本系统最大的路由文件，涵盖：

- **用户管理**：创建/编辑/删除用户、重置密码
- **组织架构**：校区 → 院系 → 专业 → 年级 → 班级的完整 CRUD
- **教学分配**：教师-班级关联管理
- **打卡配置**：时间段、围栏、规则的 CRUD
- **考勤记录**：签到/请假记录的手动增删改、导出 CSV
- **仪表盘**：统计数据、趋势图

### `common.py`
公共接口，挂载在 `/api` 下。供所有角色使用。

| 端点 | 功能 |
|------|------|
| `GET /notifications` | 获取通知（与 student 中不同，这是通用版） |
| `POST /notifications/mark-read` | 标记通知已读 |
| `GET /notifications/unread-count` | 获取未读通知数量 |
| `GET /operation-logs` | 查看操作日志 |

### `compat.py`（已删除）
旧版 API 兼容层已于 2026-05-04 移除，小程序未引用任何旧路径。
