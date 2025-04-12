# 社交互动相关接口

## 获取关注列表

### 请求
- 方法：GET
- 路径：/api/social/following/
- 认证：需要Bearer Token
- 请求头：
  ```
  Authorization: Bearer <access_token>
  ```
- 查询参数：
  ```
  page: 1
  page_size: 20
  ```

### 响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "list": [
      {
        "id": 1,
        "username": "用户名",
        "avatar": "http://example.com/avatar.jpg",
        "is_online": true,
        "last_active": "2024-01-01T00:00:00Z"
      }
    ]
  }
}
```

## 获取粉丝列表

### 请求
- 方法：GET
- 路径：/api/social/followers/
- 认证：需要Bearer Token
- 请求头：
  ```
  Authorization: Bearer <access_token>
  ```
- 查询参数：
  ```
  page: 1
  page_size: 20
  ```

### 响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "list": [
      {
        "id": 1,
        "username": "用户名",
        "avatar": "http://example.com/avatar.jpg",
        "is_online": true,
        "last_active": "2024-01-01T00:00:00Z"
      }
    ]
  }
}
```

## 获取喜欢列表

### 请求
- 方法：GET
- 路径：/api/social/likes/
- 认证：需要Bearer Token
- 请求头：
  ```
  Authorization: Bearer <access_token>
  ```
- 查询参数：
  ```
  page: 1
  page_size: 20
  ```

### 响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "list": [
      {
        "id": 1,
        "username": "用户名",
        "avatar": "http://example.com/avatar.jpg",
        "is_online": true,
        "last_active": "2024-01-01T00:00:00Z",
        "liked_at": "2024-01-01T00:00:00Z"
      }
    ]
  }
}
```

## 获取匹配列表

### 请求
- 方法：GET
- 路径：/api/social/matches/
- 认证：需要Bearer Token
- 请求头：
  ```
  Authorization: Bearer <access_token>
  ```
- 查询参数：
  ```
  page: 1
  page_size: 20
  ```

### 响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "list": [
      {
        "id": 1,
        "username": "用户名",
        "avatar": "http://example.com/avatar.jpg",
        "is_online": true,
        "last_active": "2024-01-01T00:00:00Z",
        "matched_at": "2024-01-01T00:00:00Z",
        "compatibility_score": 85
      }
    ]
  }
}
```

## 获取未读消息数

### 请求
- 方法：GET
- 路径：/api/social/unread-messages/
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
    "total": 5,
    "by_type": {
      "chat": 3,
      "system": 2
    }
  }
}
``` 