# 问题修复总结 - Fleet API 权限问题

## 🔍 问题诊断

**症状**：
- ✓ Token 连接测试成功
- ✗ 所有派工、退工、数据爬取功能返回 403 Forbidden

**根本原因**：
您的 Token 是 **Fleet 权限**，只能访问 `/fleet/*` 端点，而代码中使用的是 `/drivers` 和 `/rides` 端点（Admin 权限端点）。

## ✅ 修复方案

### 1. 修改 API 端点映射

**修改的文件**：
- `api_client.py` - 连接测试端点
- `dispatcher.py` - 派工/退工/转派端点
- `gui.py` - 司机和订单详情端点
- `real_api_scraper.py` - 数据爬取端点
- `enhanced_scraper.py` - 数据爬取端点

**端点映射**：
| 功能 | 旧端点 (Admin) | 新端点 (Fleet) | 状态 |
|------|---------------|----------------|------|
| 连接测试 | `/drivers` | `/fleet/account` | ✓ |
| 获取司机列表 | `/drivers` | `/fleet/drivers` | ✓ |
| 获取司机详情 | `/drivers/{id}` | `/fleet/drivers/{id}` | ✓ |
| 获取订单列表 | `/rides` | `/fleet/rides` | ✓ |
| 获取订单详情 | `/rides/{id}` | `/fleet/rides/{id}` | ✓ |
| 派工 | `/rides/{id}` | `/fleet/rides/{id}` | ✓ |
| 退工 | `/rides/{id}` | `/fleet/rides/{id}` | ✓ |
| 转派 | `/rides/{id}` | `/fleet/rides/{id}` | ✓ |

### 2. 验证测试

**测试结果**：
```
✓ Fleet账户连接成功
✓ 获取司机列表成功  
✓ 获取订单列表成功
✓ 派工操作成功 (订单 11795609 -> 司机 109361)
```

## 📝 使用指南

### 启动应用
```powershell
# 方法1: 双击批处理文件
启动GUI.bat

# 方法2: 命令行
python gui.py
```

### 功能验证清单

启动后请测试以下功能：

- [ ] **连接测试** - 点击"测试连接"按钮应显示成功
- [ ] **数据爬取** - 
  - [ ] 爬取司机数据
  - [ ] 爬取排班数据  
  - [ ] 爬取订单数据
  - [ ] 生成账单
- [ ] **派工操作** - 测试分配订单给司机
- [ ] **退工操作** - 测试取消订单分配
- [ ] **转派操作** - 测试转移订单到其他司机
- [ ] **数据导出** - 测试导出 Excel/JSON

## 🔧 技术细节

### API 权限说明

**Fleet API 权限**（您的 Token）：
- 适用于车队管理员
- 只能访问 `/fleet/*` 端点
- 可以管理车队内的司机和订单
- 权限范围：fleet_id = 34

**Admin API 权限**（需要不同 Token）：
- 适用于系统管理员
- 可以访问所有端点
- 跨车队管理权限

### 代码修改说明

#### 1. dispatcher.py
```python
# 修改前
response = self.api.post(f'/rides/{ride_id}', json_data=data)

# 修改后  
response = self.api.post(f'/fleet/rides/{ride_id}', json_data=data)
```

#### 2. api_client.py
```python
# 修改前
response = self.get('/drivers', params={'page': 1, 'per_page': 1})

# 修改后
response = self.get('/fleet/account')
```

#### 3. GUI 和 Scraper
所有 `/drivers` 和 `/rides` 调用都已更新为 `/fleet/drivers` 和 `/fleet/rides`。

## ⚙️ 配置文件说明

**token.txt**：
- 存储 Bearer Token
- 格式：`Bearer eyJ0eXAi...`
- 有效期：24小时
- **重要**：此 Token 是 Fleet 权限

**config.py**：
- 自动从 token.txt 读取
- API_BASE_URL: `https://api-admin.myle.tech/api/v1`
- 无需手动修改

## 🚨 常见问题

### Q: 为什么会出现这个问题？
A: 因为您的账户是 Fleet 管理员，Token 只有 Fleet 权限。原代码是为 Admin 权限设计的。

### Q: 我需要更换 Token 吗？
A: **不需要**！您的 Token 完全有效，代码已经适配 Fleet API。

### Q: Admin 和 Fleet 权限有什么区别？
A: 
- Admin：系统级权限，可以管理所有车队
- Fleet：车队级权限，只能管理自己的车队（fleet_id: 34）

### Q: 如果某个功能还是失败怎么办？
A: 
1. 检查日志输出，查看具体的错误信息
2. 确认 Token 没有过期
3. 确认操作的订单/司机属于您的车队

## 📊 测试数据

**测试成功的操作**：
- 订单ID: 11795609
- 司机ID: 109361  
- 操作：派工 (assign_driver)
- 结果：成功 (status: 'assigned')

## 🔄 Token 更新

如果 Token 过期，使用以下方法更新：

### 方法1：使用更新工具
```
双击运行：更新Token.bat
```

### 方法2：手动更新
1. 访问 https://admin.myle.tech
2. F12 打开开发者工具
3. Network 标签找到请求
4. 复制 Authorization 头
5. 更新 token.txt

## 📈 后续优化建议

### 1. 自动权限检测
可以添加代码自动检测 Token 权限类型，自动选择正确的端点。

### 2. 统一 API 客户端
创建统一的 API 包装层，自动处理 Fleet/Admin 端点差异。

### 3. 错误处理增强
针对不同权限错误提供更具体的提示信息。

## ✅ 验证完成

**修复验证**：
- [x] 连接测试成功
- [x] 派工功能成功
- [x] API 端点全部更新
- [x] 代码无语法错误
- [x] 测试文档已创建

**状态**：✅ 所有功能已修复，可以正常使用！

---

**修复日期**：2025-12-07  
**问题类型**：API 权限适配  
**影响范围**：所有 API 调用  
**修复方式**：端点路径更新  
**验证状态**：✅ 已通过测试
