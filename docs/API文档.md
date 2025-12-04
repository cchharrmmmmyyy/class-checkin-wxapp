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
  "code": 0,          // 状态码，0表示成功，非0表示失败
  "message": "success", // 提示信息
  "data": {}          // 响应数据
}
```

### 2.4 错误码说明
| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1 | 参数错误 |
| 2 | 用户名或密码错误 |
| 3 | 权限不足 |
| 4 | 服务器内部错误 |
| 5 | 打卡失败 |

## 3. 具体接口

### 3.1 用户登录

**接口路径**：`/api/login`

**请求方法**：`POST`

**请求参数**：
```json
{
  "username": "string", // 用户名
  "password": "string"  // 密码
}
```

**响应数据**：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user_id": 1,
    "username": "student1",
    "role": "student", // student, teacher, monitor
    "name": "张三"
  }
}
```

### 3.2 学生打卡

**接口路径**：`/api/student/checkin`

**请求方法**：`POST`

**请求参数**：
```json
{
  "user_id": 1 // 学生ID
}
```

**响应数据**：
```json
{
  "code": 0,
  "message": "打卡成功",
  "data": {
    "checkin_date": "2024-01-01",
    "checkin_time": "08:30:00"
  }
}
```

### 3.3 获取学生打卡记录

**接口路径**：`/api/student/checkin_records`

**请求方法**：`GET`

**请求参数**：
- `user_id`：学生ID（必填）

**响应数据**：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user_id": 1,
    "name": "张三",
    "checkin_days": 15, // 总打卡天数
    "continuous_days": 3, // 连续打卡天数
    "checkin_records": [ // 最近30天打卡记录
      { "date": "2024-01-01", "status": 1 }, // 1表示已打卡，0表示未打卡
      { "date": "2024-01-02", "status": 1 },
      // ...
    ]
  }
}
```

### 3.4 获取班级学生列表（教师/班长）

**接口路径**：`/api/teacher/students`

**请求方法**：`GET`

**请求参数**：
- `class_id`：班级ID（可选，默认获取所有班级）

**响应数据**：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "students": [
      {
        "user_id": 1,
        "name": "张三",
        "username": "student1",
        "total_checkin": 15,
        "continuous_days": 3,
        "last_checkin": "2024-01-03"
      },
      // ...
    ]
  }
}
```

### 3.5 获取班级打卡统计（教师/班长）

**接口路径**：`/api/teacher/checkin_stats`

**请求方法**：`GET`

**请求参数**：
- `class_id`：班级ID（必填）
- `date`：日期，格式YYYY-MM-DD（可选，默认今天）

**响应数据**：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "class_id": 1,
    "class_name": "高三1班",
    "date": "2024-01-03",
    "total_students": 50,
    "checked_in": 45,
    "checkin_rate": 90.0,
    "absent_students": [ // 未打卡学生
      { "user_id": 5, "name": "王五" },
      // ...
    ]
  }
}
```

### 3.6 获取学生详细信息（教师/班长）

**接口路径**：`/api/teacher/student_detail`

**请求方法**：`GET`

**请求参数**：
- `user_id`：学生ID（必填）

**响应数据**：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user_id": 1,
    "name": "张三",
    "username": "student1",
    "role": "student",
    "class_id": 1,
    "class_name": "高三1班",
    "total_checkin": 15,
    "continuous_days": 3,
    "checkin_records": [ // 最近150天打卡记录（位图数据）
      12345, // 第一个30天的打卡数据
      67890, // 第二个30天的打卡数据
      13579, // 第三个30天的打卡数据
      24680, // 第四个30天的打卡数据
      12345  // 第五个30天的打卡数据
    ]
  }
}
```

## 4. 数据模型

### 4.1 用户表（users）
| 字段名 | 类型 | 说明 |
|--------|------|------|
| user_id | INTEGER | 用户ID（主键） |
| username | TEXT | 用户名（唯一） |
| password | TEXT | 密码 |
| name | TEXT | 真实姓名 |
| role | TEXT | 角色（student, teacher, monitor） |
| class_id | INTEGER | 班级ID |

### 4.2 班级表（classes）
| 字段名 | 类型 | 说明 |
|--------|------|------|
| class_id | INTEGER | 班级ID（主键） |
| class_name | TEXT | 班级名称 |
| teacher_id | INTEGER | 班主任ID |

### 4.3 打卡表（checkins）
| 字段名 | 类型 | 说明 |
|--------|------|------|
| checkin_id | INTEGER | 打卡记录ID（主键） |
| user_id | INTEGER | 用户ID |
| checkin_date | TEXT | 打卡日期（YYYY-MM-DD） |
| checkin_time | TEXT | 打卡时间（HH:MM:SS） |

### 4.4 学生打卡统计表（student_checkin_stats）
| 字段名 | 类型 | 说明 |
|--------|------|------|
| user_id | INTEGER | 用户ID（主键） |
| total_days | INTEGER | 总打卡天数 |
| continuous_days | INTEGER | 连续打卡天数 |
| last_checkin_date | TEXT | 最后打卡日期 |
| bitmap1 | INTEGER | 第1-30天打卡数据 |
| bitmap2 | INTEGER | 第31-60天打卡数据 |
| bitmap3 | INTEGER | 第61-90天打卡数据 |
| bitmap4 | INTEGER | 第91-120天打卡数据 |
| bitmap5 | INTEGER | 第121-150天打卡数据 |

## 5. 位图算法说明

### 5.1 存储原理
- 使用5个32位整数存储150天的打卡数据
- 每个整数存储30天的打卡状态，每一位代表一天
- 1表示已打卡，0表示未打卡

### 5.2 计算方法
- 第n天的打卡状态：bitmap[(n-1)/30] & (1 << ((n-1) % 30))
- 例如，第1天对应bitmap1的第0位，第31天对应bitmap2的第0位

### 5.3 打卡状态更新
1. 计算当前日期是第几天（相对于基准日期）
2. 确定对应的bitmap和位数
3. 将对应位设置为1
4. 更新总打卡天数和连续打卡天数

## 6. 调用示例

### 6.1 使用JavaScript调用登录接口

```javascript
wx.request({
  url: 'http://localhost:5000/api/login',
  method: 'POST',
  data: {
    username: 'student1',
    password: '123456'
  },
  success: function(res) {
    if (res.data.code === 0) {
      console.log('登录成功', res.data.data);
    } else {
      console.error('登录失败', res.data.message);
    }
  }
});
```

### 6.2 使用Python调用打卡接口

```python
import requests

url = 'http://localhost:5000/api/student/checkin'
data = {'user_id': 1}

response = requests.post(url, json=data)
result = response.json()

if result['code'] == 0:
    print('打卡成功')
else:
    print('打卡失败:', result['message'])
```

## 7. 接口测试

可以使用Postman、curl等工具测试接口，例如：

```bash
curl -X POST -H "Content-Type: application/json" -d '{"username":"student1","password":"123456"}' http://localhost:5000/api/login
```

## 8. 注意事项

1. 所有接口均需要在请求头中添加适当的认证信息
2. 接口调用频率建议不超过每秒10次
3. 敏感数据（如密码）建议使用加密传输
4. 学生打卡接口建议添加防重复打卡机制
5. 生产环境中建议添加接口限流和熔断机制
