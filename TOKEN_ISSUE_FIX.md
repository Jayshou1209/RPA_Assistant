# Token失效问题修复指南

## 问题症状

- GUI连接测试失败
- 显示"403 Forbidden"错误
- 提示"Token无效或已过期"

## 原因

系统使用JWT（JSON Web Token）进行身份验证，Token有24小时有效期。当Token过期后，所有API请求都会返回403错误。

## 解决方案

### 方法1: 使用Token更新工具（推荐）

1. 双击运行 `更新Token.bat`
2. 按照界面提示获取新Token：
   - 访问 https://admin.myle.tech
   - 登录账户
   - 按F12打开开发者工具
   - 切换到Network标签
   - 刷新页面或点击任何菜单
   - 找到任意请求，查看Request Headers
   - 复制完整的 `Authorization` 值（包括"Bearer "前缀）
3. 粘贴到工具界面，点击"更新Token"
4. 重新启动GUI应用

### 方法2: 手动更新token.txt

1. 用文本编辑器打开 `token.txt`
2. 删除旧Token
3. 粘贴新Token（必须以"Bearer "开头）
4. 保存文件
5. 重新启动GUI应用

### 方法3: 使用PowerShell脚本

```powershell
.\update_token.ps1 -NewToken "Bearer eyJ0eXAi..."
```

## 获取新Token的详细步骤

### 步骤1: 登录系统
打开浏览器访问 https://admin.myle.tech 并登录

### 步骤2: 打开开发者工具
- Windows/Linux: 按 `F12` 或 `Ctrl+Shift+I`
- Mac: 按 `Cmd+Option+I`

### 步骤3: 切换到Network标签
在开发者工具中找到"Network"（网络）标签并点击

### 步骤4: 触发请求
在页面中执行任何操作，例如：
- 刷新页面 (F5)
- 点击任何菜单项
- 查看司机列表
- 查看订单

### 步骤5: 找到请求
在Network列表中找到对 `api-admin.myle.tech` 的请求

### 步骤6: 查看请求头
- 点击该请求
- 找到 "Request Headers"（请求头）部分
- 找到 `Authorization` 字段

### 步骤7: 复制Token
复制Authorization字段的完整值，应该类似：
```
Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3M...（很长的字符串）
```

**重要提示：**
- ✓ 必须包含 "Bearer " 前缀（注意Bearer后面有个空格）
- ✓ Token通常有400-500个字符长
- ✗ 不要只复制JWT部分，要包含"Bearer "
- ✗ 不要添加引号或其他字符

### 步骤8: 更新Token
使用上述三种方法之一更新Token

## 验证Token是否有效

更新Token后：
1. 启动GUI应用 `python gui.py`
2. 点击"测试连接"按钮
3. 如果显示"连接测试成功"，说明Token有效
4. 如果仍然失败，请检查：
   - Token是否完整复制
   - 是否包含"Bearer "前缀
   - 是否登录了正确的账户
   - 网络连接是否正常

## 常见问题

### Q: Token多久需要更新一次？
A: 通常24小时。系统会在启动时显示Token剩余有效期。

### Q: 能否自动更新Token？
A: 目前不支持，因为需要用户登录。建议每天工作前更新一次Token。

### Q: 为什么获取的Token无效？
A: 可能原因：
- 未包含"Bearer "前缀
- 复制不完整
- 账户权限不足
- 网络问题

### Q: Token存储在哪里？
A: `token.txt` 文件中。config.py会自动从该文件读取。

## 自动化建议

为了减少手动更新的麻烦，建议：
1. 每天上班时第一件事就是更新Token
2. 使用Token更新工具，操作更简单
3. 如果频繁使用，可以设置浏览器扩展自动提取Token

## 技术细节

Token是JWT格式，包含三部分（用.分隔）：
1. Header（头部）
2. Payload（载荷）- 包含用户信息和过期时间
3. Signature（签名）- 用于验证Token有效性

过期时间存储在Payload的`exp`字段中，为Unix时间戳。

## 需要帮助？

如果以上方法都无法解决问题，请检查：
1. 网络连接是否正常
2. API服务器是否可访问
3. 账户是否有足够权限
4. 是否使用了正确的登录账户

---

**更新日期：** 2025-12-07
**版本：** 1.0
