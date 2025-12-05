# 后端服务

## 概述

课堂打卡系统的后端服务，基于 Python Flask 框架开发，提供学生、班委和教师三种角色的 API 接口，实现打卡管理、班级管理和请假管理等核心功能。

## 技术栈

- **框架**: Flask 2.x
- **数据库**: SQLite 3
- **开发语言**: Python 3.7+

## 目录结构

```
backend/
├── app.py              # Flask 应用入口，路由管理
├── database.py         # 数据库操作模块，封装 DB 交互
├── student.py          # 学生相关接口，处理学生端请求
├── teacher.py          # 教师相关接口，处理教师端请求
└── user.db             # SQLite 数据库文件
```

## 核心功能

### 1. 用户认证模块
- 账号密码登录
- 角色权限验证
- 会话管理

### 2. 打卡管理模块
- 每日打卡记录
- 打卡记录查询
- 班级打卡统计
- 位图算法存储打卡数据

### 3. 班级管理模块
- 学生信息管理
- 班委任命
- 班级数据统计

### 4. 请假管理模块
- 请假申请处理
- 请假记录查询
- 请假天数计算

## 快速开始

### 环境要求
- Python 3.7+
- Flask 2.x

### 安装依赖

```bash
# 安装 Flask
pip install flask
```

### 启动服务

```bash
# 进入后端目录
cd backend

# 启动 Flask 服务
python app.py
```

服务默认运行在 `http://127.0.0.1:5000`

## API 接口

### 认证接口
- `POST /login` - 用户登录

### 学生接口
- `POST /student/punch` - 学生打卡
- `GET /student/records` - 获取学生打卡记录
- `POST /student/leave` - 提交请假申请
- `GET /student/leave-records` - 获取学生请假记录

### 班委接口
- `GET /monitor/class-records` - 获取班级打卡记录

### 教师接口
- `GET /teacher/students` - 获取班级学生列表
- `POST /teacher/appoint-monitor` - 任命班委
- `GET /teacher/class-statistics` - 获取班级统计数据

## 数据库设计

### 用户表 (users)
- `id` - 主键
- `username` - 用户名/学号/工号
- `password` - 密码
- `role` - 角色 (student/monitor/teacher)
- `class` - 班级
- `name` - 姓名
- `punch_data` - 打卡数据（位图存储）

### 请假表 (leave_requests)
- `id` - 主键
- `student_id` - 学生ID
- `start_date` - 开始日期
- `end_date` - 结束日期
- `status` - 状态 (pending/approved/rejected)
- `created_at` - 创建时间

## 核心算法

### 位图打卡算法

系统采用位图算法高效存储打卡记录：
- 每个整数 32 位，可存储 32 天的打卡状态
- 5 个整数共 160 位，足够存储 150 天的打卡记录
- 打卡状态用位表示：0 表示未打卡，1 表示已打卡
- 计算某一天是否打卡只需判断对应位是否为 1

## 开发指南

### 代码规范
- 遵循 PEP 8 代码规范
- 使用 meaningful 的变量名和函数名
- 添加必要的注释

### 测试
- 推荐使用 Postman 或 curl 测试 API 接口
- 可以使用 pytest 编写单元测试

### 部署
- 开发环境：直接运行 `python app.py`
- 生产环境：建议使用 Gunicorn 或 uWSGI 部署

## 注意事项

- 首次启动服务会自动创建数据库表并插入示例数据
- 示例数据包含学生、班委和教师账号，详见根目录 README.md
- 数据库文件 `user.db` 会自动生成，请勿手动删除

## 更新日志

### v1.0.0 (2025-12-04)
- 实现基本的用户认证功能
- 完成打卡管理模块
- 实现班级管理和请假管理功能
- 集成位图打卡算法

### v0.1.0 (2025-11-20)
- 初始化后端项目结构
- 实现简单的 Flask 应用
- 设计数据库表结构