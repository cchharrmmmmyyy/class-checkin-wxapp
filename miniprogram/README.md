# 微信小程序前端

## 概述

课堂打卡系统的微信小程序前端，基于微信小程序原生开发框架，提供学生、班委和教师三种角色的交互界面，实现打卡、请假、班级管理等核心功能。

## 技术栈

- **开发框架**: 微信小程序原生开发
- **开发语言**: JavaScript
- **样式**: WXSS (类似 CSS)
- **页面结构**: WXML (类似 HTML)

## 目录结构

```
miniprogram/
├── app.js                 # 小程序入口文件
├── app.json               # 小程序全局配置
├── app.wxss               # 小程序全局样式
├── pages/                 # 页面目录
│   ├── login/             # 登录页面
│   │   ├── login.js       # 登录逻辑
│   │   ├── login.json     # 页面配置
│   │   ├── login.wxml     # 页面结构
│   │   └── login.wxss     # 页面样式
│   ├── student/           # 学生页面
│   │   ├── leave-apply.js     # 请假申请逻辑
│   │   ├── leave-apply.json   # 请假申请配置
│   │   ├── leave-apply.wxml   # 请假申请结构
│   │   ├── leave-apply.wxss   # 请假申请样式
│   │   ├── leave-records.js   # 请假记录逻辑
│   │   ├── leave-records.json # 请假记录配置
│   │   ├── leave-records.wxml # 请假记录结构
│   │   ├── leave-records.wxss # 请假记录样式
│   │   ├── student.js         # 学生主页面逻辑
│   │   ├── student.json       # 学生主页面配置
│   │   ├── student.wxml       # 学生主页面结构
│   │   ├── student.wxss       # 学生主页面样式
│   │   ├── student-detail.js  # 学生详情页面逻辑
│   │   ├── student-detail.json# 学生详情页面配置
│   │   ├── student-detail.wxml# 学生详情页面结构
│   │   └── student-detail.wxss# 学生详情页面样式
│   └── teacher/           # 教师页面
│       ├── teacher.js     # 教师页面逻辑
│       ├── teacher.json   # 教师页面配置
│       ├── teacher.wxml   # 教师页面结构
│       └── teacher.wxss   # 教师页面样式
└── utils/                 # 工具函数
    ├── auth.js           # 认证相关工具
    └── geo.js            # 地理位置相关工具（预留）
```

## 核心功能

### 1. 用户认证模块
- 登录页面
- 角色权限验证
- 会话管理

### 2. 学生功能模块
- 打卡主页面
- 个人打卡记录查询
- 请假申请
- 请假记录查询

### 3. 班委功能模块
- 个人打卡功能
- 班级打卡记录查询

### 4. 教师功能模块
- 班级学生管理
- 班委任命
- 班级打卡统计

## 快速开始

### 开发环境

1. **安装微信开发者工具**
   - 从 [微信公众平台](https://mp.weixin.qq.com/) 下载并安装
   - 注册微信小程序开发者账号

2. **导入项目**
   - 打开微信开发者工具
   - 选择 "导入项目"
   - 选择 `miniprogram` 目录
   - 填写 AppID（测试阶段可使用体验 AppID）

3. **配置后端地址**
   - 在 `app.js` 中配置后端服务地址
   - 默认地址为 `http://127.0.0.1:5000`

4. **编译运行**
   - 点击 "编译" 按钮
   - 使用微信扫码预览
   - 或在模拟器中查看效果

## 页面说明

### 登录页面 (login)
- 账号密码登录
- 角色自动识别
- 登录状态保持

### 学生主页面 (student)
- 一键打卡功能
- 上次打卡时间显示
- 请假申请入口
- 请假记录查询入口

### 学生详情页面 (student-detail)
- 个人打卡记录查询
- 班级打卡记录查询（仅班委）

### 请假申请页面 (leave-apply)
- 请假开始日期选择
- 请假结束日期选择
- 请假天数自动计算
- 请假申请提交

### 请假记录页面 (leave-records)
- 请假记录列表
- 请假状态显示

### 教师页面 (teacher)
- 班级学生列表
- 学生打卡状态显示
- 班委任命功能

## 开发指南

### 代码规范
- 遵循微信小程序开发规范
- 使用 meaningful 的变量名和函数名
- 添加必要的注释
- 页面逻辑与 UI 分离

### 样式设计
- 使用 WXSS 变量统一管理颜色和尺寸
- 采用响应式设计，适配不同屏幕尺寸
- 保持样式的一致性

### 数据交互
- 使用 `wx.request` 与后端 API 交互
- 合理使用缓存 `wx.setStorageSync` 和 `wx.getStorageSync`
- 处理网络请求错误和加载状态

### 调试技巧
- 使用微信开发者工具的调试面板
- 使用 `console.log` 打印调试信息
- 使用真机调试查看真实效果

## 注意事项

- 开发阶段需要开启 "不校验合法域名" 选项
- 上线前需要配置合法域名
- 需要获取用户授权才能使用地理位置等功能
- 小程序大小限制为 2MB，超过需要使用分包加载

## 更新日志

### v1.0.0 (2025-12-04)
- 实现学生打卡功能
- 实现请假申请和记录查询
- 实现班委和教师功能
- 优化页面样式和用户体验

### v0.1.0 (2025-11-20)
- 初始化小程序项目
- 实现登录页面
- 实现基本的打卡功能

## 相关文档

- [微信小程序开发文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)
- [微信开发者工具使用指南](https://developers.weixin.qq.com/miniprogram/dev/devtools/devtools.html)
- [微信小程序设计指南](https://developers.weixin.qq.com/miniprogram/design/)

## 贡献指南

欢迎各位开发者贡献代码，共同完善这个项目。贡献前请阅读项目根目录的 CONTRIBUTING.md 文件。