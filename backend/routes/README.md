# routes/ — 路由层

HTTP 接口暴露层，每个文件是一个 Flask Blueprint。只做参数校验和调用 Service，不直接操作数据库。

## 文件说明

### `__init__.py`
集中注册并导出所有 Blueprint：`auth_bp`、`student_bp`、`teacher_bp`、`admin_*_bp`、`common_bp`。

### `auth.py`
认证相关接口，挂载在 `/api` 下。

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/login` | POST | 用户登录（学生/教师/管理员），返回 JWT Token |
| `/api/change-password` | POST | 修改密码（需提供旧密码） |

### `student.py`
学生端接口，挂载在 `/api/student` 下。需要 `token_required` 鉴权。

| 端点 | 功能 |
|------|------|
| `POST /punch` | 打卡签到（含 GPS 坐标） |
| `GET /punch-records` | 查询个人打卡记录（分页） |
| `POST /leave/apply` | 提交请假申请 |
| `GET /leave/records` | 查询个人请假记录 |
| `POST /makeup/apply` | 提交补签申请 |
| `GET /makeup/records` | 查询个人补签记录 |
| `GET /monitor/class-punch-status` | （班委）查看班级签到概况 |
| `GET /monitor/class-leaves` | （班委）查看班级请假情况 |
| `GET /monitor/class-makeups` | （班委）查看班级补签情况 |

### `teacher.py`
教师端接口，挂载在 `/api/teacher` 下。需要教师角色。

| 端点 | 功能 |
|------|------|
| `GET /classes` | 获取教师所带班级列表 |
| `GET /class/students` | 查看班级学生 |
| `GET /class/punch-summary` | 班级签到汇总 |
| `GET /leave/pending` | 待审批请假列表 |
| `POST /leave/approve` | 审批请假（通过/拒绝） |
| `GET /makeup/pending` | 待审批补签列表 |
| `POST /makeup/approve` | 审批补签（通过/拒绝） |
| `POST /monitor/appoint` | 任命班委 |
| `DELETE /monitor/remove` | 取消班委 |
| `GET /monitors` | 查看班委列表 |

### `admin/` 目录
管理员端接口，挂载在 `/api/admin` 下。需要管理员角色。分为以下子模块：

#### `admin/user.py` - 用户管理
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/admin/users` | GET | 获取用户列表（分页） |
| `/api/admin/users` | POST | 创建用户 |
| `/api/admin/users/<user_id>` | PUT | 更新用户 |
| `/api/admin/users/<user_id>` | DELETE | 删除用户 |
| `/api/admin/users/reset-password` | POST | 重置用户密码 |

#### `admin/org.py` - 组织架构管理
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/admin/org/campuses` | GET/POST | 获取/创建校区 |
| `/api/admin/org/campuses/<campus_id>` | PUT/DELETE | 更新/删除校区 |
| `/api/admin/org/departments` | GET/POST | 获取/创建院系 |
| `/api/admin/org/departments/<department_id>` | PUT/DELETE | 更新/删除院系 |
| `/api/admin/org/majors` | GET/POST | 获取/创建专业 |
| `/api/admin/org/majors/<major_id>` | PUT/DELETE | 更新/删除专业 |
| `/api/admin/org/grades` | GET/POST | 获取/创建年级 |
| `/api/admin/org/grades/<grade_id>` | PUT/DELETE | 更新/删除年级 |
| `/api/admin/org/classes` | GET/POST | 获取/创建班级 |
| `/api/admin/org/classes/<class_name>` | PUT/DELETE | 更新/删除班级 |

#### `admin/teaching.py` - 教学分配管理
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/admin/teaching/assignments` | GET/POST | 获取/创建教师班级关联 |
| `/api/admin/teaching/assignments/<class_name>/<teacher_id>` | PUT/DELETE | 更新/删除教师班级关联 |

#### `admin/rule.py` - 打卡规则配置
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/admin/rules/time-slots` | GET/POST | 获取/创建时间段 |
| `/api/admin/rules/time-slots/<slot_id>` | PUT/DELETE | 更新/删除时间段 |
| `/api/admin/rules/punch-geofences` | GET/POST | 获取/创建打卡围栏 |
| `/api/admin/rules/punch-geofences/<geofence_id>` | PUT/DELETE | 更新/删除打卡围栏 |
| `/api/admin/rules/punch-rules` | GET/POST | 获取/创建打卡规则 |
| `/api/admin/rules/punch-rules/<rule_id>` | PUT/DELETE | 更新/删除打卡规则 |

#### `admin/attendance.py` - 考勤记录管理
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/admin/attendance-records` | GET | 获取考勤记录（兼容层） |
| `/api/admin/attendance-records` | POST | 创建考勤记录（兼容层） |
| `/api/admin/attendance-records/<record_id>` | DELETE | 删除考勤记录（兼容层） |
| `/api/admin/attendance/export` | GET | 导出考勤记录 CSV |
| `/api/admin/attendance/punch-records` | POST | 创建打卡记录 |
| `/api/admin/attendance/punch-records/<record_id>` | PUT/DELETE | 更新/删除打卡记录 |
| `/api/admin/attendance/leave-records` | POST | 创建请假记录 |
| `/api/admin/attendance/leave-records/<record_id>` | PUT/DELETE | 更新/删除请假记录 |

#### `admin/dashboard.py` - 仪表盘
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/admin/dashboard/stats` | GET | 获取统计数据 |
| `/api/admin/dashboard/trend` | GET | 获取考勤趋势 |
| `/api/admin/config` | GET/PUT | 获取/更新系统配置 |
| `/api/admin/punch-location` | GET/POST | 获取/设置打卡地点（兼容层） |

### `common.py`
公共接口，挂载在 `/api` 下。供所有角色使用。

| 端点 | 功能 |
|------|------|
| `GET /notifications` | 获取通知列表 |
| `POST /notifications/mark-read` | 标记通知已读 |
| `GET /notifications/unread-count` | 获取未读通知数量 |
| `GET /operation-logs` | 查看操作日志 |

### `compat.py`（已删除）
旧版 API 兼容层已于 2026-05-04 移除，小程序未引用任何旧路径。
