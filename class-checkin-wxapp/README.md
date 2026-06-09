# 班级考勤系统

微信小程序 + Flask 后端的班级考勤管理系统，支持学生打卡、请假申请、班委监督、教师审批等功能。

## 项目结构

```
class-checkin-wxapp/
├── miniprogram/          # 微信小程序前端
│   ├── components/       # 通用组件 (tabbar、navbar)
│   ├── config/           # 配置文件 (API地址、错误码)
│   ├── network/         # 网络请求封装 (api.js、request.js)
│   ├── pages/           # 页面文件
│   │   ├── login/       # 登录页
│   │   ├── student/      # 学生端页面 (打卡、请假、记录等)
│   │   └── teacher/      # 教师端页面 (班级管理、审批等)
│   ├── styles/          # 全局样式 (主题、基础样式)
│   └── utils/           # 工具函数
│
├── backend/              # Flask 后端服务
│   ├── dao/              # 数据访问层 (数据库操作)
│   ├── db/               # 数据库相关
│   │   └── schema/       # SQL 迁移文件 (01~17)
│   ├── models/          # 数据模型
│   ├── routes/          # 路由层 (API 蓝图)
│   │   ├── admin/       # 管理后台 API
│   │   ├── auth.py      # 认证相关
│   │   ├── student.py   # 学生端 API
│   │   └── teacher.py   # 教师端 API
│   ├── services/        # 业务逻辑层
│   ├── static/          # 静态资源 (admin后台)
│   ├── templates/       # HTML 模板 (admin后台)
│   ├── utils/           # 工具函数 (JWT、响应封装、异常处理等)
│   ├── app.py           # 应用入口
│   └── config.py        # 配置管理
│
└── plans/               # 项目规划文档
```

## 角色权限

| 角色 | 功能 |
|------|------|
| **学生 (student)** | 考勤打卡、请假申请、补课申请、查看个人记录 |
| **班委 (monitor)** | 学生全部功能 + 班级考勤看板、待处理申请 |
| **教师 (teacher)** | 班级管理、审批请假/补课申请、管理班委 |
| **管理员 (admin)** | 组织架构管理、用户CRUD、考勤规则配置、数据统计 (Web后台) |

## 技术栈

**小程序端**
- 微信小程序框架
- 原生 JavaScript

**后端**
- Flask (Python Web 框架)
- SQLite (数据库)
- JWT (身份认证)

## 快速开始

### 后端启动

```bash
cd backend
cp .env.example .env    # 配置环境变量
pip install -r requirements.txt
python app.py           # 启动服务 (默认 http://0.0.0.0:5000)
```

### 小程序开发

1. 在微信开发者工具中导入 `miniprogram/` 目录
2. 修改 `config/api.js` 中的 `baseUrl` 为后端地址
3. 使用微信开发者工具预览/调试

## API 架构

```
请求 → routes/ (路由层) → services/ (业务逻辑) → dao/ (数据访问) → SQLite
```

- `routes/` — Flask 蓝图，只做参数校验，不含业务逻辑
- `services/` — 业务逻辑编排
- `dao/` — 所有 SQL 操作，使用 BaseDAO 泛型类实现类型安全的 CRUD
