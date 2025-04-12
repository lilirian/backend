# 用户相关接口

## 获取用户详细信息

### 请求
- 方法：GET
- 路径：/api/user/profile/
- 认证：需要Bearer Token
- 请求头：
  ```
  Authorization: Bearer <access_token>
  ```

### 响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "用户名",
    "email": "user@example.com",
    "avatar": "http://example.com/avatar.jpg",
    "following": 10,
    "followers": 20,
    "likes": 30,
    "matches": 5,
    "is_vip": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

## 更新用户头像

### 请求
- 方法：POST
- 路径：/api/user/avatar/
- 认证：需要Bearer Token
- 请求头：
  ```
  Authorization: Bearer <access_token>
  Content-Type: multipart/form-data
  ```
- 请求体：
  ```
  avatar: <file>
  ```

### 响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "avatar": "http://example.com/new-avatar.jpg"
  }
}
```

## 获取用户统计数据

### 请求
- 方法：GET
- 路径：/api/user/stats/
- 认证：需要Bearer Token
- 请求头：
  ```
  Authorization: Bearer <access_token>
  ```

### 响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "following": 10,
    "followers": 20,
    "likes": 30,
    "matches": 5,
    "unread_messages": 3
  }
}
``` 