# API端点文档

## 基础信息

- **Base URL**: `http://api-admin.myle.tech/api/v1`
- **认证方式**: Bearer Token
- **请求头**: 
  ```
  Authorization: Bearer {token}
  Content-Type: application/json
  ```

## 端点列表

### 1. 认证验证
```
GET /auth/verify
```
验证Token是否有效

**响应示例**:
```json
{
  "success": true,
  "data": {
    "user_id": 850,
    "fleet_id": 34,
    "type": "admin"
  }
}
```

---

### 2. 获取司机列表
```
GET /drivers
```

**查询参数**:
- `status`: 司机状态 (active, inactive, all)
- `page`: 页码
- `per_page`: 每页数量

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "name": "张三",
      "phone": "13800138000",
      "status": "active",
      "vehicle_type": "轿车",
      "license_plate": "京A12345",
      "rating": 4.8
    }
  ]
}
```

---

### 3. 获取司机详情
```
GET /drivers/{driver_id}
```

**路径参数**:
- `driver_id`: 司机ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 123,
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "status": "active",
    "vehicle": {
      "id": 456,
      "type": "轿车",
      "plate": "京A12345",
      "model": "丰田凯美瑞"
    },
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

---

### 4. 获取车辆列表
```
GET /vehicles
```

**查询参数**:
- `type`: 车型类型
- `status`: 车辆状态
- `page`: 页码

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 456,
      "plate": "京A12345",
      "type": "轿车",
      "model": "丰田凯美瑞",
      "status": "available",
      "driver_id": 123
    }
  ]
}
```

---

### 5. 获取排班/时间段
```
GET /schedules
```

**查询参数**:
- `driver_id`: 司机ID
- `date`: 日期 (YYYY-MM-DD)
- `start_date`: 开始日期
- `end_date`: 结束日期

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 789,
      "driver_id": 123,
      "driver_name": "张三",
      "date": "2025-11-20",
      "time_slot": "09:00-12:00",
      "status": "scheduled",
      "order_id": 1001
    }
  ]
}
```

---

### 6. 派工
```
POST /dispatch
```

**请求体**:
```json
{
  "driver_id": 123,
  "order_id": 1001,
  "date": "2025-11-20",
  "time_slot": "09:00-12:00",
  "notes": "备注信息"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "派工成功",
  "data": {
    "dispatch_id": 999,
    "driver_id": 123,
    "order_id": 1001,
    "date": "2025-11-20",
    "time_slot": "09:00-12:00"
  }
}
```

---

### 7. 退工
```
POST /withdraw
```

**请求体**:
```json
{
  "order_id": 1001,
  "driver_id": 123,
  "reason": "司机请假"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "退工成功",
  "data": {
    "order_id": 1001,
    "previous_driver_id": 123,
    "withdrawn_at": "2025-11-20T10:30:00Z"
  }
}
```

---

### 8. 订单转派
```
POST /transfer
```

**请求体**:
```json
{
  "order_id": 1001,
  "from_driver_id": 123,
  "to_driver_id": 124,
  "date": "2025-11-20",
  "reason": "司机调整"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "转派成功",
  "data": {
    "order_id": 1001,
    "from_driver_id": 123,
    "to_driver_id": 124,
    "transferred_at": "2025-11-20T11:00:00Z"
  }
}
```

---

## 错误响应

所有错误都返回类似结构：

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  }
}
```

### 常见错误码

| 错误码 | HTTP状态码 | 说明 |
|--------|-----------|------|
| `UNAUTHORIZED` | 401 | Token无效或过期 |
| `FORBIDDEN` | 403 | 无权限访问 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `VALIDATION_ERROR` | 422 | 请求参数错误 |
| `SERVER_ERROR` | 500 | 服务器内部错误 |

---

## 注意事项

### Token管理
- Token有效期：24小时
- 需要每天更新Token
- Token格式必须包含 "Bearer " 前缀

### 请求限制
- 建议每秒不超过10个请求
- 批量操作时注意添加延迟
- 大量数据建议分页获取

### 时区
- 所有时间使用北京时间 (UTC+8)
- 日期格式: `YYYY-MM-DD`
- 时间格式: `HH:MM:SS`

### 最佳实践
1. 始终检查响应的 `success` 字段
2. 处理所有可能的错误情况
3. 记录所有API调用日志
4. 使用重试机制处理网络错误

---

## 测试示例

### 使用curl测试

```bash
# 验证连接
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://api-admin.myle.tech/api/v1/auth/verify

# 获取司机列表
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://api-admin.myle.tech/api/v1/drivers

# 派工
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"driver_id":123,"order_id":1001,"date":"2025-11-20"}' \
     http://api-admin.myle.tech/api/v1/dispatch
```

### 使用Python测试

```python
import requests

TOKEN = "Bearer YOUR_TOKEN"
BASE_URL = "http://api-admin.myle.tech/api/v1"

headers = {
    "Authorization": TOKEN,
    "Content-Type": "application/json"
}

# 获取司机列表
response = requests.get(f"{BASE_URL}/drivers", headers=headers)
print(response.json())

# 派工
payload = {
    "driver_id": 123,
    "order_id": 1001,
    "date": "2025-11-20"
}
response = requests.post(f"{BASE_URL}/dispatch", json=payload, headers=headers)
print(response.json())
```

---

**注意**: 以上API端点可能需要根据实际系统调整。如果端点不匹配，请查看系统文档或联系系统管理员获取正确的API端点信息。
