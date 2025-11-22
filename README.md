# RPA调度系统自动化脚本

一个功能完整的自动化脚本，用于管理调度系统的司机、车辆和订单调度。

## 功能特性

### 1. 数据爬取
- 自动爬取司机资料（姓名、ID、状态等）
- 获取车辆信息和车型数据
- 获取司机开工时间段和排班信息
- 数据自动保存为JSON格式

### 2. 调度管理
- **派工**: 将订单分配给指定司机
- **退工**: 取消订单分配
- **订单转派**: 在司机之间转移订单
- 支持批量操作
- 可指定日期和时间段

### 3. 自动化特性
- 自动使用Token登录系统
- 完整的错误处理和日志记录
- 支持每日Token更新
- 交互式命令行界面

## 项目结构

```
RPA操作助手/
├── config.py           # 配置文件（Token、API端点）
├── api_client.py       # API客户端（处理HTTP请求）
├── scraper.py          # 数据爬取模块
├── dispatcher.py       # 调度功能模块
├── main.py             # 主程序入口
├── requirements.txt    # Python依赖包
├── data/               # 数据存储目录（自动创建）
│   └── driver_data.json
└── automation.log      # 运行日志
```

## 安装步骤

### 1. 安装Python依赖

```powershell
pip install -r requirements.txt
```

### 2. 配置Token

每天更新 `config.py` 中的 `BEARER_TOKEN`：

```python
BEARER_TOKEN = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

## 使用方法

### 🎨 GUI可视化界面（推荐）

```powershell
# 方法1: 双击批处理文件
启动GUI.bat

# 方法2: 命令行运行
python gui.py
```

**GUI界面功能：**
- ✅ 可视化Token管理（输入、保存、测试）
- ✅ 一键数据爬取（司机、车辆、排班）
- ✅ 数据导出（JSON/Excel格式）
- ✅ 派工/退工/转派对话框
- ✅ 批量操作支持
- ✅ 实时日志显示
- ✅ 打开数据目录

### 命令行界面

```powershell
python main.py
```

### 功能菜单

程序启动后会显示交互式菜单：

#### 数据操作
1. **爬取所有数据** - 获取司机、车辆、排班信息并保存
2. **查看司机列表** - 显示所有司机的基本信息
3. **查看车辆列表** - 显示车辆信息
4. **查看排班信息** - 显示开工时间段

#### 调度操作
5. **派工（单个）** - 将订单分配给司机
   - 输入：司机ID、订单ID、日期、时间段
   
6. **批量派工** - 一次分配多个订单
   - 格式：`司机ID,订单ID,日期,时间段`
   - 示例：`123,456,2025-11-20,09:00-12:00`

7. **退工（单个）** - 取消订单分配
   - 输入：订单ID、退工原因

8. **批量退工** - 批量取消订单
   - 输入：订单ID列表（逗号分隔）

9. **订单转派** - 在司机间转移订单
   - 输入：订单ID、原司机ID、目标司机ID、日期、原因

10. **查看司机订单** - 查询司机的订单列表
    - 输入：司机ID、日期

#### 系统操作
11. **更新Token** - 手动更新Bearer Token
12. **测试连接** - 验证API连接状态
0. **退出** - 退出程序

## 使用示例

### 示例1: 爬取数据并查看

```
1. 选择 [1] 爬取所有数据
2. 选择 [2] 查看司机列表
```

### 示例2: 单个派工

```
1. 选择 [5] 派工
2. 输入司机ID: 123
3. 输入订单ID: 456
4. 输入日期: 2025-11-20 (或直接回车使用今天)
5. 输入时间段: 09:00-12:00
```

### 示例3: 批量派工

```
1. 选择 [6] 批量派工
2. 输入派工信息:
   123,456,2025-11-20,09:00-12:00
   124,457,2025-11-20,13:00-17:00
   125,458,2025-11-20,18:00-22:00
3. 输入空行完成
```

### 示例4: 订单转派

```
1. 选择 [9] 订单转派
2. 输入订单ID: 456
3. 输入原司机ID: 123
4. 输入目标司机ID: 124
5. 输入日期: 2025-11-20
6. 输入原因: 司机临时请假
```

## API端点说明

脚本使用以下API端点（在 `config.py` 中配置）：

- `/auth/verify` - Token验证
- `/drivers` - 司机信息
- `/vehicles` - 车辆信息
- `/schedules` - 排班信息
- `/dispatch` - 派工
- `/withdraw` - 退工
- `/transfer` - 订单转派

## 数据格式

### 司机数据
```json
{
  "id": 123,
  "name": "张三",
  "status": "active",
  "vehicle_type": "轿车"
}
```

### 派工请求
```json
{
  "driver_id": 123,
  "order_id": 456,
  "date": "2025-11-20",
  "time_slot": "09:00-12:00"
}
```

## 日志

所有操作都会记录到 `automation.log` 文件中，包括：
- API请求和响应
- 操作成功/失败信息
- 错误堆栈跟踪

查看日志：
```powershell
Get-Content automation.log -Tail 50
```

## Token更新

### 方法1: 修改配置文件
编辑 `config.py`，更新 `BEARER_TOKEN`

### 方法2: 程序内更新
运行程序后选择菜单项 [11] 更新Token

### Token自动化脚本
可以创建批处理文件自动更新Token：

```powershell
# update_token.ps1
$newToken = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
(Get-Content config.py) -replace 'BEARER_TOKEN = "Bearer.*"', "BEARER_TOKEN = `"$newToken`"" | Set-Content config.py
```

## 高级用法

### 作为模块使用

```python
from api_client import APIClient
from dispatcher import Dispatcher

# 初始化
client = APIClient("your_token_here")
dispatcher = Dispatcher(client)

# 派工
result = dispatcher.dispatch_order(
    driver_id=123,
    order_id=456,
    date="2025-11-20",
    time_slot="09:00-12:00"
)

# 订单转派
result = dispatcher.transfer_order(
    order_id=456,
    from_driver_id=123,
    to_driver_id=124
)
```

### 定时任务

Windows任务计划程序示例：

```powershell
# 每天8点执行数据爬取
$action = New-ScheduledTaskAction -Execute "python" -Argument "c:\Users\enjia\OneDrive\桌面\RPA操作助手\main.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "RPA数据爬取"
```

## 故障排除

### 连接失败
- 检查Token是否有效
- 确认API_BASE_URL正确
- 查看 `automation.log` 获取详细错误信息

### Token过期
- 每天更新Token
- 检查Token格式是否完整（包含"Bearer "前缀）

### 数据爬取失败
- 确认有权限访问API端点
- 检查网络连接
- 查看日志了解具体错误

## 注意事项

1. **Token安全**: 不要将Token提交到版本控制系统
2. **每日更新**: Token需要每天更新
3. **并发限制**: 批量操作时注意API速率限制
4. **数据备份**: 重要数据请定期备份

## 技术栈

- Python 3.7+
- requests - HTTP请求
- logging - 日志记录
- json - 数据序列化

## 维护

- 查看日志文件排查问题
- 定期清理旧的日志和数据文件
- 根据API变化更新端点配置

## 联系支持

如遇到问题，请查看：
1. `automation.log` 日志文件
2. API响应错误信息
3. 配置是否正确

---

**最后更新**: 2025-11-20
**版本**: 1.0.0
