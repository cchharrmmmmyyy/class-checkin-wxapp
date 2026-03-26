# 微信小程序班级打卡系统

基于微信小程序的班级考勤打卡系统，支持学生打卡、教师管理、班委统计、请假审批以及位置范围打卡功能。

## 项目简介

本项目是一个完整的班级考勤解决方案，使用微信小程序作为前端，Flask后端提供API服务，SQLite数据库存储数据。系统支持多种角色登录、地理位置范围打卡、请假审批等功能。

### 核心特点

- **多角色支持**：学生、教师、班委、管理员四种角色
- **位置打卡**：支持设置打卡位置范围，学生必须在范围内才能打卡成功
- **请假审批**：完整的请假申请和审批流程
- **主题切换**：支持多主题切换，适配不同用户偏好
- **Web管理后台**：管理员可通过浏览器管理用户和考勤记录

## 技术架构

| 模块 | 技术栈 | 说明 |
|------|--------|------|
| 前端 | 微信小程序原生开发 | 用户界面、打卡操作、地图展示 |
| 后端 | Flask + Flask-CORS | RESTful API服务 |
| 数据库 | SQLite | 轻量级关系型数据库 |
| 管理后台 | HTML + JavaScript | 管理员Web界面 |

## 项目结构

```
class-checkin-wxapp/
├── backend/                      # Flask后端服务
│   ├── app.py                    # 应用入口、登录接口
│   ├── database.py               # 数据库初始化和操作
│   ├── student.py                # 学生相关API（打卡、请假）
│   ├── teacher.py                # 教师相关API（班委管理、请假审批）
│   ├── admin.py                  # 管理员API（用户管理、位置配置）
│   ├── admin.html                # 管理员Web管理界面
│   ├── user.db                   # SQLite数据库文件
│   ├── requirements.txt          # Python依赖
│   └── docs/                     # 后端文档
├── miniprogram/                   # 微信小程序前端
│   ├── config/
│   │   └── api.js                # API接口配置
│   ├── network/
│   │   ├── api.js                # API调用封装
│   │   └── request.js            # 网络请求封装
│   ├── pages/
│   │   ├── login/                # 登录页面
│   │   │   ├── login.js
│   │   │   ├── login.wxml
│   │   │   ├── login.wxss
│   │   │   └── login.json
│   │   ├── student/              # 学生页面
│   │   │   ├── student.js        # 打卡主页面（含地图）
│   │   │   ├── student.wxml
│   │   │   ├── student.wxss
│   │   │   ├── student-detail.js  # 打卡记录查询
│   │   │   ├── leave-apply.js     # 请假申请
│   │   │   └── leave-records.js  # 请假记录
│   │   └── teacher/              # 教师页面
│   │       ├── teacher.js        # 班级管理
│   │       ├── teacher.wxml
│   │       └── teacher.wxss
│   ├── utils/
│   │   ├── auth.js               # 认证工具
│   │   ├── theme.js              # 主题管理
│   │   └── utils.js              # 通用工具
│   ├── styles/
│   │   ├── base.wxss             # 基础样式
│   │   └── theme.wxss            # 主题样式
│   ├── app.js                   # 小程序入口
│   ├── app.json                 # 小程序配置
│   └── app.wxss                 # 全局样式
├── README.md                     # 项目说明文档
└── requirements.txt              # 项目依赖
```

## 功能列表

### 1. 登录认证
- 支持学生、教师、班委、管理员四种角色
- 学号/工号 + 密码登录
- 登录成功后自动存储用户信息

### 2. 学生功能
- **打卡签到**：一键打卡，自动获取当前位置
- **地图展示**：页面显示实时位置地图
- **位置验证**：必须在管理员设置的范围内才能打卡成功
- **请假申请**：提交请假开始和结束日期
- **打卡记录**：查看历史打卡记录
- **请假记录**：查看请假申请状态

### 3. 教师功能
- **班级学生列表**：查看班级学生及打卡状态
- **班委任命**：任命学生为班委
- **班委移除**：移除学生班委职务
- **请假审批**：查看并审批学生请假申请
- **班级列表**：获取所有班级信息

### 4. 管理员功能
- **用户管理**：添加、修改、删除用户
- **考勤记录管理**：查看、添加、修改、删除考勤记录
- **打卡位置配置**：设置打卡位置（名称、经纬度、半径）
- **考勤筛选**：按用户名、用户ID、日期范围、请假状态筛选

### 5. 主题切换
- 支持多主题颜色切换
- 主题状态全局保存

## 数据库表结构

### users 表 - 用户信息
| 字段 | 类型 | 说明 |
|------|------|------|
| username | TEXT | 用户名（主键） |
| password | TEXT | 密码 |
| role | TEXT | 角色：student/teacher/monitor/admin |
| class | TEXT | 班级 |
| user_id | TEXT | 学号/工号（唯一） |

### punch_records 表 - 打卡记录
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 自增主键 |
| username | TEXT | 用户名 |
| user_id | TEXT | 学号/工号 |
| punch_date | DATE | 打卡日期 |
| leave_start_date | DATE | 请假开始日期 |
| leave_end_date | DATE | 请假结束日期 |
| leave_status | TEXT | 请假状态：pending/approved/rejected |

### punch_location 表 - 打卡位置配置
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 自增主键 |
| name | TEXT | 位置名称 |
| latitude | REAL | 纬度 |
| longitude | REAL | 经度 |
| radius | REAL | 允许打卡半径（米） |
| enabled | INTEGER | 是否启用：0/1 |

## API接口

### 认证接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/login | 用户登录 |

### 学生接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/student/punch | 提交打卡 |
| GET | /api/student/records/<user_id> | 获取个人打卡记录 |
| GET | /api/student/class-records/<class_name> | 获取班级打卡记录 |
| POST | /api/student/apply-leave | 提交请假申请 |
| GET | /api/student/leave-records | 获取个人请假记录 |

### 教师接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/teacher/class-list | 获取班级列表 |
| GET | /api/teacher/leave-applications | 获取请假申请列表 |
| POST | /api/teacher/approve-leave | 审批请假申请 |
| POST | /api/teacher/appoint-monitor | 任命班委 |
| POST | /api/teacher/remove-monitor | 移除班委 |
| GET | /api/teacher/class-monitor/<class_name> | 获取班级班委 |

### 管理员接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/admin/login | 管理员登录 |
| GET | /api/admin/users | 获取用户列表 |
| POST | /api/admin/users | 添加/修改用户 |
| DELETE | /api/admin/users/<user_id> | 删除用户 |
| GET | /api/admin/attendance-records | 获取考勤记录 |
| POST | /api/admin/attendance-records | 添加/修改考勤记录 |
| DELETE | /api/admin/attendance-records/<id> | 删除考勤记录 |
| GET | /api/admin/punch-location | 获取打卡位置配置 |
| POST | /api/admin/punch-location | 设置打卡位置 |

## 快速开始

### 1. 环境要求

- Python 3.7+
- 微信开发者工具
- Node.js（可选，用于代码检查）

### 2. 后端部署

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py
```

后端服务启动后：
- API服务：http://localhost:5000/api
- 管理后台：http://localhost:5000/admin

### 3. 前端配置

1. 使用微信开发者工具打开 `miniprogram` 目录
2. 修改 `miniprogram/config/api.js` 中的 `baseUrl` 为后端地址
3. 修改 `miniprogram/project.config.json` 中的 `appid` 为您的小程序AppID
4. 在微信开发者工具中启用"不校验合法域名"
5. 编译运行小程序

### 4. 首次部署检查清单

- [ ] 修改 `miniprogram/config/api.js` 中的 `baseUrl` 为实际服务器IP
- [ ] 修改 `miniprogram/project.config.json` 中的 `appid` 为您的小程序AppID
- [ ] 修改 `backend/database.py` 中的默认密码为安全密码
- [ ] 删除 `backend/user.db` 让系统重新初始化数据库

### 5. 测试账户

| 角色 | 用户ID | 用户名 | 密码 |
|------|--------|--------|------|
| 管理员 | admin001 | 管理员 | admin123 |
| 学生 | 2024001 | 张三 | 123456 |
| 学生 | 2024002 | 李四 | 123456 |
| 班委 | 2024003 | 王五 | 123456 |
| 教师 | t001 | 张老师 | 123456 |

## 打卡位置配置

管理员可通过管理后台配置打卡位置：

1. 访问 http://localhost:5000/admin
2. 登录管理员账户
3. 切换到"打卡位置管理"标签
4. 填写位置信息：
   - 位置名称：如"教学楼A"
   - 纬度：如 39.908823
   - 经度：如 116.397470
   - 半径（米）：如 100
5. 启用位置验证

学生打卡时，系统会：
1. 获取学生当前位置
2. 使用Haversine公式计算与设置位置的距离
3. 如果距离超过设置半径，返回打卡失败
4. 成功记录打卡，不保存学生位置信息

## 主题切换

学生页面支持主题切换：
1. 点击页面中的"切换主题"按钮
2. 选择喜欢的主题颜色
3. 主题设置会自动保存

## 注意事项

1. 首次启动后端会自动创建数据库和表
2. 如果修改了数据库结构，需要删除 `user.db` 重启服务
3. 微信小程序需要在 `app.json` 中配置定位权限
4. 位置打卡使用gcj02坐标系（微信坐标系）

## GitHub 部署注意事项

本项目已为 GitHub 开源做了以下处理：

1. **移除敏感信息**：
   - AppID 已替换为占位符 `YOUR_APPID_HERE`
   - 服务器地址已替换为占位符 `YOUR_SERVER_IP`
   - 管理员默认密码已改为普通密码 `admin123`

2. **.gitignore 文件**：
   - 排除数据库文件 (`*.db`)
   - 排除 Python 缓存 (`__pycache__/`)
   - 排除 IDE 配置 (`.vscode/`, `.idea/`)
   - 排除私有配置文件

3. **安全建议**：
   - 首次部署请修改默认密码
   - 生产环境建议使用 HTTPS
   - 考虑添加密码哈希存储
   - 配置防火墙规则限制访问

## 许可证

MIT License

---

欢迎使用微信小程序班级打卡系统！🎉
