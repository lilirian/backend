# 用户认证系统API文档

## 1. 用户注册

### 接口说明
- **接口地址**: `/api/auth/register/`
- **请求方式**: POST
- **接口描述**: 用户注册新账号

### 请求参数
```json
{
    "email": "string",      // 必填，用户邮箱
    "username": "string",   // 必填，用户名
    "password": "string",   // 必填，密码（至少6位）
    "password2": "string"   // 必填，确认密码
}
```

### 响应参数
成功响应 (201 Created):
```json
{
    "message": "注册成功",
    "user": {
        "email": "user@example.com",
        "username": "username"
    },
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

错误响应 (400 Bad Request):
```json
{
    "email": ["该邮箱已被注册"],
    "password": ["密码太短", "密码不能全是数字"],
    "password2": ["两次输入的密码不一致"]
}
```

## 2. 用户登录

### 接口说明
- **接口地址**: `/api/auth/login/`
- **请求方式**: POST
- **接口描述**: 用户登录获取访问令牌

### 请求参数
```json
{
    "email": "string",    // 必填，用户邮箱
    "password": "string"  // 必填，用户密码
}
```

### 响应参数
成功响应 (200 OK):
```json
{
    "message": "登录成功",
    "user": {
        "email": "user@example.com",
        "username": "username"
    },
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

错误响应 (401 Unauthorized):
```json
{
    "error": "邮箱或密码错误"
}
```

## 3. 令牌说明

### 访问令牌 (Access Token)
- 用于访问需要认证的API接口
- 在请求头中添加：`Authorization: Bearer <access_token>`
- 有效期：60分钟

### 刷新令牌 (Refresh Token)
- 用于获取新的访问令牌
- 有效期：1天

## 4. 错误码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权/认证失败 |
| 500 | 服务器内部错误 |

## 5. 使用示例

### 注册请求示例
```bash
curl -X POST http://your-domain/api/auth/register/ \
-H "Content-Type: application/json" \
-d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123!",
    "password2": "password123!"
}'
```

### 登录请求示例
```bash
curl -X POST http://your-domain/api/auth/login/ \
-H "Content-Type: application/json" \
-d '{
    "email": "test@example.com",
    "password": "password123!"
}'
```

### 访问受保护API示例
```bash
curl -X GET http://your-domain/api/protected/ \
-H "Authorization: Bearer <access_token>"
```

## 6. 注意事项

1. 所有API请求都需要使用HTTPS协议
2. 密码要求：
   - 至少6个字符
   - 不能全是数字
   - 不能与用户名太相似
3. 邮箱必须是有效的邮箱格式
4. 建议定期更换密码
5. 请妥善保管访问令牌，不要泄露给他人 