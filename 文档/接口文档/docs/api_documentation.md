# 恋爱桥 API 文档

## 基础信息

- 基础URL: `http://127.0.0.1:8000/api/`
- 所有请求都需要在 Header 中包含 `Content-Type: application/json`
- 需要认证的接口需要在 Header 中包含 `Authorization: Bearer <token>`

## 用户认证

### 用户注册
- **URL**: `/user/register/`
- **方法**: POST
- **描述**: 注册新用户
- **请求体**:
```json
{
    "username": "string",
    "email": "string",
    "password": "string",
    "gender": "M/F",
    "birth_date": "YYYY-MM-DD",
    "bio": "string"
}
```
- **响应**:
```json
{
    "message": "注册成功",
    "user": {
        "email": "string",
        "username": "string"
    },
    "tokens": {
        "refresh": "string",
        "access": "string"
    }
}
```

### 用户登录
- **URL**: `/user/login/`
- **方法**: POST
- **描述**: 用户登录
- **请求体**:
```json
{
    "username": "string",
    "password": "string"
}
```
- **响应**:
```json
{
    "refresh": "string",
    "access": "string",
    "user": {
        "id": "integer",
        "username": "string",
        "email": "string",
        "avatar": "string",
        "gender": "string",
        "birth_date": "string",
        "bio": "string",
        "age": "integer",
        "avatar_url": "string"
    }
}
```

## 用户管理

### 上传头像
- **URL**: `/user/users/upload_avatar/`
- **方法**: POST
- **描述**: 上传用户头像
- **认证**: 需要
- **Content-Type**: `multipart/form-data`
- **请求体**:
  - `avatar`: 图片文件（jpg/png，<2MB）
- **响应**:
```json
{
    "id": "integer",
    "username": "string",
    "email": "string",
    "avatar": "string",
    "gender": "string",
    "birth_date": "string",
    "bio": "string",
    "age": "integer",
    "avatar_url": "string"
}
```

### 获取用户头像
- **URL**: `/user/users/{user_id}/avatar/`
- **方法**: GET
- **描述**: 获取用户头像
- **认证**: 需要
- **响应**: 图片文件（content-type: image/jpeg）

## 匹配功能

### 获取推荐用户
- **URL**: `/user/match/recommendations/`
- **方法**: GET
- **描述**: 获取推荐用户列表
- **认证**: 需要
- **响应**:
```json
[
    {
        "id": "integer",
        "username": "string",
        "email": "string",
        "avatar": "string",
        "gender": "string",
        "birth_date": "string",
        "bio": "string",
        "age": "integer",
        "avatar_url": "string"
    }
]
```

### 喜欢用户
- **URL**: `/user/match/like/`
- **方法**: POST
- **描述**: 喜欢某个用户
- **认证**: 需要
- **请求体**:
```json
{
    "to_user_id": "integer"
}
```
- **响应**:
```json
{
    "id": "integer",
    "from_user": "integer",
    "to_user": "integer",
    "created_at": "datetime"
}
```

### 获取匹配列表
- **URL**: `/user/match/matches/`
- **方法**: GET
- **描述**: 获取互相喜欢的用户列表
- **认证**: 需要
- **响应**:
```json
[
    {
        "id": "integer",
        "user1": "integer",
        "user2": "integer",
        "status": "string",
        "created_at": "datetime"
    }
]
```

## 错误响应

### 400 Bad Request
```json
{
    "error": "错误信息"
}
```

### 401 Unauthorized
```json
{
    "error": "身份认证信息未提供"
}
```

### 404 Not Found
```json
{
    "error": "资源不存在"
}
```

## 注意事项

1. 头像上传限制：
   - 文件大小：最大 2MB
   - 文件类型：仅支持 JPG 和 PNG 格式

2. 用户认证：
   - 所有需要认证的接口都需要在 Header 中包含 `Authorization: Bearer <token>`
   - token 可以通过登录接口获取

3. 头像访问：
   - 头像 URL 可以通过用户信息中的 `avatar_url` 字段获取
   - 也可以通过 `/user/users/{user_id}/avatar/` 接口直接获取图片文件 