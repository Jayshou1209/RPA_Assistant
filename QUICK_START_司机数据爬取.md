# 快速使用指南 - 司机数据爬取

## 快速开始

### 1. 启动程序
双击 `启动RPA助手.bat` 或运行：
```bash
python gui_scraper.py
```

### 2. 点击 "爬取司机数据" 按钮
![爬取司机数据按钮](位于左侧功能按钮区域)

### 3. 等待爬取完成
系统将自动：
- ✅ 获取所有司机基本信息（支持分页）
- ✅ 获取每位司机的详细证件信息
- ✅ 获取车辆信息和证件
- ✅ 导出Excel文件
- ✅ 自动打开Excel文件

### 4. 查看导出的Excel文件
文件保存在 `data` 目录下，文件名格式：
```
司机完整数据_20251230_133045.xlsx
```

---

## Excel字段说明（共53个字段）

### 司机个人信息
- Name, First Name, Middle Name, Last Name
- **Date of Birth** (出生日期)
- **SSN** (社会保障号)
- **Sex** (性别)
- Email, Phone
- Address, City, State, Zip Code

### 司机证件
- **Driver License**: Number, Issue Date, Expired Date, State, Class
- **TLC License**: Number, Expired Date
- **Sentry Drug Test**: Number, Expired Date, Status
- **ARRO Drug Test**: Number, Expired Date, Status

### 车辆信息
- **基本**: VIN Number, Make, Model, Year, Plate Number, Color, Type
- **FHV Diamond**: Number, Expired Date, State
- **Insurance**: Policy Number, Expired Date, State, Company, Effective Date
- **Registration**: Number, Expired Date, State
- **NYS Inspection Sticker**: Number, Expired Date

---

## 注意事项

1. **确保Token有效**
   - 在GUI中点击"测试连接"确认
   - Token文件: `token.txt`

2. **耐心等待**
   - 获取详细信息需要时间
   - 每个司机约0.3秒
   - GUI会显示实时进度

3. **数据完整性**
   - 所有字段使用英文标题
   - 空字段显示为空白
   - 日期格式: YYYY-MM-DD

---

## 常见问题

**Q: 为什么有些字段是空的？**  
A: 某些司机可能未上传该证件或信息

**Q: 如何查看原始数据？**  
A: 运行 `python test_driver_extraction.py` 查看数据结构

**Q: 导出失败怎么办？**  
A: 
1. 检查Token是否有效
2. 查看 `log` 目录下的日志文件
3. 确保网络连接正常

---

## 技术支持

详细说明请查看: `司机数据提取功能更新说明.md`
