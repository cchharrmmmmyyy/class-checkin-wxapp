# 微信小程序打卡系统

基于微信小程序的简单打卡系统，支持学生打卡、教师管理和班委统计功能，和基本的请假功能。

## 🚀 项目简介

本项目是一个基于微信小程序的课堂打卡系统，主要解决传统考勤方式效率低下的问题，使用SQLite数据库存储打卡数据。

### 核心特点

- 💾 **关系型数据库存储**：使用SQLite存储打卡记录
- 👥 **多角色支持**：学生、教师、班委、管理员四种角色
- 📱 **微信小程序原生开发**：无需下载额外应用
- 🌐 **Web管理界面**：管理员可通过浏览器进行用户管理

## 🛠️ 技术架构

| 模块 | 技术栈 | 功能 |
|------|--------|------|
| 前端 | 微信小程序原生开发 | 用户界面、打卡操作 |
| 后端 | Flask + SQLite | 用户认证、数据存储、业务逻辑 |
| 数据存储 | SQLite关系型数据库 | 存储打卡记录

## 📁 项目结构

```
.
├── backend/                # 后端服务
│   ├── app.py             # Flask应用入口
│   ├── database.py        # 数据库初始化和操作
│   ├── student.py         # 学生相关API
│   ├── teacher.py         # 教师相关API
│   └── admin.py           # 管理员相关API
├── admin.html             # 管理员Web管理界面
├── miniprogram/           # 微信小程序前端
│   ├── pages/             # 页面文件
│   │   ├── login/         # 登录页面
│   │   │   ├── login.js        # 登录页面逻辑
│   │   │   ├── login.json      # 登录页面配置
│   │   │   ├── login.wxml      # 登录页面结构
│   │   │   └── login.wxss      # 登录页面样式
│   │   ├── student/       # 学生页面（包含打卡功能）
│   │   │   ├── leave-apply.js        # 请假申请页面
│   │   │   ├── leave-apply.json      # 请假申请页面配置
│   │   │   ├── leave-apply.wxml      # 请假申请页面结构
│   │   │   ├── leave-apply.wxss      # 请假申请页面样式
│   │   │   ├── leave-records.js      # 请假记录页面
│   │   │   ├── leave-records.json    # 请假记录页面配置
│   │   │   ├── leave-records.wxml    # 请假记录页面结构
│   │   │   ├── leave-records.wxss    # 请假记录页面样式
│   │   │   ├── student-detail.js     # 学生详情页面
│   │   │   ├── student-detail.json   # 学生详情页面配置
│   │   │   ├── student-detail.wxml   # 学生详情页面结构
│   │   │   ├── student-detail.wxss   # 学生详情页面样式
│   │   │   ├── student.js            # 学生主页面
│   │   │   ├── student.json          # 学生主页面配置
│   │   │   ├── student.wxml          # 学生主页面结构
│   │   │   └── student.wxss          # 学生主页面样式
│   │   └── teacher/       # 教师管理页面
│   │       ├── teacher.js          # 教师主页面
│   │       ├── teacher.json        # 教师主页面配置
│   │       ├── teacher.wxml        # 教师主页面结构
│   │       └── teacher.wxss        # 教师主页面样式
│   ├── utils/             # 工具函数
│   │   └── auth.js        # 认证工具和API调用
│   └── app.js             # 小程序入口
└── docs/                  # 项目文档
```

### 主要文件说明

#### 后端文件

| 文件 | 功能 |
|------|------|
| `backend/app.py` | Flask应用入口，处理HTTP请求和路由 |
| `backend/database.py` | 数据库初始化、连接和查询操作 |
| `backend/student.py` | 学生相关API，如打卡、查询打卡记录 |
| `backend/teacher.py` | 教师相关API，如查看学生打卡情况、统计数据 |
| `backend/admin.py` | 管理员相关API，如用户管理、权限控制 |
| `admin.html` | 管理员Web管理界面，用于用户管理操作 |

#### 前端文件

| 文件 | 功能 |
|------|------|
| `miniprogram/pages/login/login.js` | 登录页面逻辑，处理用户登录请求 |
| `miniprogram/pages/student/student.js` | 学生主页面逻辑，包含打卡功能 |
| `miniprogram/pages/student/student-detail.js` | 学生详情页面逻辑 |
| `miniprogram/pages/student/leave-apply.js` | 学生请假申请页面逻辑 |
| `miniprogram/pages/student/leave-records.js` | 学生请假记录页面逻辑 |
| `miniprogram/pages/teacher/teacher.js` | 教师管理页面逻辑，显示学生打卡统计 |
| `miniprogram/utils/auth.js` | 认证工具，处理登录状态管理和API调用 |
| `miniprogram/utils/geo.js` | 地理位置相关工具函数 |

## ✨ 主要功能

### 1. 登录功能

- 支持学生、教师、班委三种角色登录
- 预分配账户系统，无需注册（当前版本暂不支持用户注册功能）
- 基于学号/工号和密码验证

### 2. 学生打卡功能

- 一键快速打卡
- 自动记录打卡时间
- 使用SQLite数据库存储打卡记录

### 3. 教师管理功能

- 查看总学生数
- 查看今日打卡人数
- 查看学生列表及打卡状态
- 支持班委任命

### 4. 班委功能

- 拥有学生角色的所有功能
- 可查看本班学生打卡情况

### 5. 请假功能

- **学生端**：
  - 提交请假申请（选择开始和结束日期）
  - 查看请假记录和审批状态
- **教师端**：
  - 查看班级待审批请假申请
  - 审批请假申请（批准/拒绝）
- **打卡记录自动处理**：
  - 已批准的请假记录会自动标记为已打卡
  - 请假状态在打卡统计中显示

### 6. 管理员功能

- **用户管理**：
  - 查看所有用户列表
  - 添加新用户
  - 修改用户信息
  - 删除用户
  - 重置用户密码
- **Web管理界面**：
  - 通过浏览器访问：`http://localhost:5000/admin`
  - 支持简单易用的表格操作
  - 管理员账户：用户名`admin`，密码`admin123`

## 📋 快速开始

### 开发环境

- 微信开发者工具
- Python 3.7+
- Flask 2.0+

### 后端部署

1. 进入后端目录
```bash
cd backend
```

2. 安装依赖
```bash
pip install flask flask-cors
```

3. 启动后端服务
```bash
python app.py
```

4. 后端服务将运行在 `http://localhost:5000`

### 前端部署

1. 使用微信开发者工具导入 `miniprogram` 目录
2. 在微信开发者工具中配置项目
3. 修改 `utils/auth.js` 中的API地址为后端服务地址
4. 编译并运行小程序

## 🧪 测试

### 单元测试重点

- 打卡记录测试：验证打卡记录是否正确存储到数据库
- 登录验证测试：测试账号密码验证逻辑
- 权限控制测试：验证不同角色的权限是否正确

### 集成测试流程

1. 学生登录 → 一键打卡 → 验证数据库记录
2. 老师登录 → 查看统计 → 验证数据显示
3. 班委登录 → 查看本班情况 → 验证权限控制

## 📊 数据存储说明

### 存储方式

使用SQLite关系型数据库存储打卡记录，每个打卡记录包含以下字段：

- 用户名：标识打卡用户
- 用户ID：学号/工号
- 打卡日期：记录打卡时间
- 请假开始日期：请假的开始日期
- 请假结束日期：请假的结束日期
- 请假状态：请假审批状态（pending-待审批, approved-已批准, rejected-已拒绝）

### 存储优势

- 结构清晰：便于查询和统计
- 支持索引：查询效率高
- 易于扩展：可灵活添加新字段
- 数据安全：支持事务和外键约束

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🌟 致谢

感谢所有为本项目做出贡献的开发者！

---

**欢迎使用微信小程序打卡系统！** 🎉