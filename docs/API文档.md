# 微信小程序打卡系统 - API文档

## 1. 接口概述

本API文档描述了微信小程序打卡系统后端提供的所有接口，包括登录、打卡、数据查询等功能。所有接口均采用RESTful风格设计，返回JSON格式数据。

## 2. 基础信息

### 2.1 接口前缀
所有API接口的前缀为：`/api`

### 2.2 请求方法
支持GET、POST、PUT、DELETE等HTTP方法

### 2.3 响应格式
```json
{
  "success": true,   // 布尔值，true表示成功，false表示失败
  "message": "success", // 提示信息
  "data": {}          // 响应数据（可选）
}
```

### 2.4 错误码说明
项目实际使用布尔值表示成功/失败，不使用具体错误码。常见错误信息如下：
| 错误信息 | 说明 |
|--------|------|
| 学号/工号和密码不能为空 | 参数错误 |
| 学号/工号或密码错误 | 用户名或密码错误 |
| 今日已打卡 | 重复打卡 |
| 未知的用户角色 | 角色错误 |

## 3. 具体接口

### 3.1 用户登录

**接口路径**：`/api/login`

**请求方法**：`POST`

**请求参数**：
```json
{
  "user_id": "string", // 学号/工号
  "password": "string"  // 密码
}
```

**响应数据**：
```json
{
  "success": true,
  "message": "登录成功",
  "user": {
    "username": "student1",
    "user_id": "202430800001",
    "role": "student", // student, teacher, monitor
    "class": "计算机1班"
  },
  "redirect_url": "/pages/student/student"
}
```

### 3.2 学生打卡

**接口路径**：`/api/student/punch`

**请求方法**：`POST`

**请求参数**：
```json
{
  "username": "string", // 用户名
  "user_id": "string", // 学生ID
  "role": "string", // 角色
  "class": "string" // 班级
}
```

**响应数据**：
```json
{
  "success": true,
  "message": "打卡成功",
  "data": {
    "punch_date": "2024-09-01"
  }
}
```

### 3.3 获取学生打卡记录

**接口路径**：`/api/student/records/<user_id>`

**请求方法**：`GET`

**请求参数**：
- `user_id`：学生ID（通过URL路径传递）

**响应数据**：
```json
{
  "success": true,
  "message": "查询成功",
  "data": [
    {
      "id": 1,
      "user_id": "202430800001",
      "username": "student1",
      "punch_date": "2024-09-01"
    },
    {
      "id": 2,
      "user_id": "202430800001",
      "username": "student1",
      "punch_date": "2024-09-02"
    }
    // ... 最多返回30条记录，按日期降序排列
  ]
}
```

### 3.4 任命班委

**接口路径**：`/api/teacher/appoint-monitor`

**请求方法**：`POST`

**请求参数**：
```json
{
  "student_id": "string", // 学生学号
  "teacher_id": "string", // 教师工号
  "class_name": "string" // 班级名称
}
```

**响应数据**：
```json
{
  "success": true,
  "message": "任命班委成功",
  "data": {
    "student_name": "student1",
    "student_id": "202430800001",
    "class": "计算机1班",
    "appointed_at": "2024-09-01 10:00:00"
  }
}
```

### 3.5 获取班级班委信息

**接口路径**：`/api/teacher/class-monitor/<class_name>`

**请求方法**：`GET`

**请求参数**：
- `class_name`：班级名称（通过URL路径传递）

**响应数据**：
```json
{
  "success": true,
  "message": "查询成功",
  "data": [
    {
      "username": "monitor1",
      "user_id": "202430800003"
    }
  ]
}
```

### 3.6 获取班级学生列表

**接口路径**：`/api/teacher/class-students/<class_name>`

**请求方法**：`GET`

**请求参数**：
- `class_name`：班级名称（通过URL路径传递）

**响应数据**：
```json
{
  "success": true,
  "message": "查询成功",
  "data": [
    {
      "username": "student1",
      "user_id": "202430800001",
      "role": "student"
    },
    {
      "username": "monitor1",
      "user_id": "202430800003",
      "role": "monitor"
    }
  ]
}
```

### 3.7 获取班级列表

**接口路径**：`/api/teacher/class-list`

**请求方法**：`GET`

**请求参数**：无

**响应数据**：
```json
{
  "success": true,
  "message": "查询成功",
  "data": [
    "计算机1班",
    "计算机2班"
  ]
}
```

### 3.8 移除班委

**接口路径**：`/api/teacher/remove-monitor`

**请求方法**：`POST`

**请求参数**：
```json
{
  "student_id": "string", // 学生学号
  "teacher_id": "string" // 教师工号
}
```

**响应数据**：
```json
{
  "success": true,
  "message": "移除班委成功",
  "data": {
    "student_name": "monitor1",
    "student_id": "202430800003",
    "class": "计算机1班",
    "removed_at": "2024-09-01 10:00:00"
  }
}
```

### 3.9 获取班级打卡记录（学生/班委）

**接口路径**：`/api/student/class-records/<class_name>`

**请求方法**：`GET`

**请求参数**：
- `class_name`：班级名称（通过URL路径传递）

**响应数据**：
```json
{
  "success": true,
  "message": "查询成功",
  "data": [
    {
      "username": "student1",
      "user_id": "202430800001",
      "role": "student",
      "punched": true,
      "punchTime": "已打卡"
    },
    {
      "username": "student2 (班委)",
      "user_id": "202430800002",
      "role": "monitor",
      "punched": false,
      "punchTime": "未打卡"
    },
    {
      "username": "student3",
      "user_id": "202430800003",
      "role": "student",
      "punched": false,
      "punchTime": "请假"
    }
  ]
}
```

### 3.10 学生提交请假申请

**接口路径**：`/api/student/apply-leave`

**请求方法**：`POST`

**请求参数**：
```json
{
  "username": "string", // 用户名
  "user_id": "string", // 学号
  "leave_start_date": "string", // 请假开始日期（YYYY-MM-DD）
  "leave_end_date": "string" // 请假结束日期（YYYY-MM-DD）
}
```

**响应数据**：
```json
{
  "success": true,
  "message": "请假申请提交成功，等待老师批准",
  "data": {
    "leave_start_date": "2024-09-01",
    "leave_end_date": "2024-09-03"
  }
}
```

### 3.11 学生获取请假记录

**接口路径**：`/api/student/leave-records`

**请求方法**：`GET`

**请求参数**：
- `user_id`：学生ID（通过URL查询参数传递）

**响应数据**：
```json
{
  "success": true,
  "message": "查询成功",
  "data": [
    {
      "id": 1,
      "user_id": "202430800001",
      "username": "student1",
      "leave_start_date": "2024-09-01",
      "leave_end_date": "2024-09-03",
      "leave_status": "approved"
    },
    {
      "id": 2,
      "user_id": "202430800001",
      "username": "student1",
      "leave_start_date": "2024-09-10",
      "leave_end_date": "2024-09-12",
      "leave_status": "pending"
    }
  ]
}
```

### 3.12 教师获取待审批请假申请

**接口路径**：`/api/teacher/leave-applications`

**请求方法**：`GET`

**请求参数**：
- `class_name`：班级名称（通过URL查询参数传递）

**响应数据**：
```json
{
  "success": true,
  "message": "查询成功",
  "data": [
    {
      "id": 2,
      "username": "student1",
      "user_id": "202430800001",
      "leave_start_date": "2024-09-10",
      "leave_end_date": "2024-09-12",
      "leave_status": "pending"
    }
  ]
}
```

### 3.13 教师审批请假申请

**接口路径**：`/api/teacher/approve-leave`

**请求方法**：`POST`

**请求参数**：
```json
{
  "id": "string", // 请假申请ID
  "status": "string", // 审批状态（approved/rejected）
  "teacher_id": "string" // 教师工号
}
```

**响应数据**：
```json
{
  "success": true,
  "message": "请假审批成功",
  "data": {
    "leave_id": "2",
    "status": "approved"
  }
}
```

### 4. 管理员接口

### 4.1 管理员登录

**接口路径**：`/api/admin/login`

**请求方法**：`POST`

**请求参数**：
```json
{
  "username": "string", // 管理员用户名
  "password": "string"  // 管理员密码
}
```

**响应数据**：
```json
{
  "success": true,
  "message": "登录成功",
  "admin": {
    "username": "admin",
    "user_id": "ADMIN001"
  }
}
```

### 4.2 获取所有用户列表

**接口路径**：`/api/admin/users`

**请求方法**：`GET`

**请求参数**：无

**响应数据**：
```json
{
  "success": true,
  "message": "查询成功",
  "data": [
    {
      "username": "admin",
      "user_id": "ADMIN001",
      "password": "admin123",
      "role": "admin",
      "class": ""
    },
    {
      "username": "student1",
      "user_id": "202430800001",
      "password": "123456",
      "role": "student",
      "class": "计算机1班"
    }
  ]
}
```

### 4.3 添加或修改用户

**接口路径**：`/api/admin/users`

**请求方法**：`POST`

**请求参数**：
```json
{
  "username": "string", // 用户名
  "user_id": "string", // 用户ID（学号/工号）
  "password": "string", // 密码
  "role": "string", // 角色（student, teacher, monitor, admin）
  "class": "string" // 班级名称（可选，管理员可以为空）
}
```

**响应数据**：
```json
{
  "success": true,
  "message": "用户添加成功" // 或 "用户更新成功"
}
```

### 4.4 删除用户

**接口路径**：`/api/admin/users/<user_id>`

**请求方法**：`DELETE`

**请求参数**：
- `user_id`：用户ID（通过URL路径传递）

**响应数据**：
```json
{
  "success": true,
  "message": "用户删除成功"
}
```

## 4. 数据模型

### 4.1 用户表（users）
| 字段名 | 类型 | 说明 |
|--------|------|------|
| username | TEXT | 用户名（主键） |
| password | TEXT | 密码 |
| role | TEXT | 角色（student, teacher, monitor, admin） |
| class | TEXT | 班级名称 |
| user_id | TEXT | 学号/工号，唯一标识 |

### 4.2 打卡记录表（punch_records）
| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 自增主键 |
| username | TEXT | 用户名 |
| user_id | TEXT | 学号/工号 |
| punch_date | DATE | 打卡日期（YYYY-MM-DD） |
| leave_start_date | DATE | 请假开始日期（YYYY-MM-DD），默认为NULL |
| leave_end_date | DATE | 请假结束日期（YYYY-MM-DD），默认为NULL |
| leave_status | TEXT | 请假状态：pending-待审批，approved-已批准，rejected-已拒绝 |
| FOREIGN KEY (username) REFERENCES users (username) | - | 外键约束，关联用户表 |
| FOREIGN KEY (user_id) REFERENCES users (user_id) | - | 外键约束，关联用户表 |

## 5. 健康检查接口

### 5.1 健康检查

**接口路径**：`/api/health`

**请求方法**：`GET`

**请求参数**：无

**响应数据**：
```json
{
  "status": "ok",
  "message": "后端服务运行正常"
}
```

## 6. 调用示例

### 6.1 使用JavaScript调用登录接口

```javascript
wx.request({
  url: 'http://localhost:5000/api/login',
  method: 'POST',
  data: {
    user_id: '202430800001',
    password: '123456'
  },
  success: function(res) {
    if (res.data.success) {
      console.log('登录成功', res.data.user);
      // 跳转到指定页面
      wx.redirectTo({ url: res.data.redirect_url });
    } else {
      console.error('登录失败', res.data.message);
    }
  }
});
```

### 6.2 使用Python调用打卡接口

```python
import requests

url = 'http://localhost:5000/api/student/punch'
data = {
    'username': 'student1',
    'user_id': '202430800001',
    'role': 'student',
    'class': '计算机1班'
}

response = requests.post(url, json=data)
result = response.json()

if result['success']:
    print('打卡成功')
else:
    print('打卡失败:', result['message'])
```

## 7. 接口测试

可以使用Postman、curl等工具测试接口，例如：

```bash
curl -X POST -H "Content-Type: application/json" -d '{"user_id":"202430800001","password":"123456"}' http://localhost:5000/api/login
```

## 8. 注意事项

1. 所有接口均需要在请求头中添加适当的认证信息
2. 接口调用频率建议不超过每秒10次
3. 敏感数据（如密码）建议使用加密传输
4. 学生打卡接口建议添加防重复打卡机制
5. 生产环境中建议添加接口限流和熔断机制
