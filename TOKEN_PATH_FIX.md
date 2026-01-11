# Token更新问题修复说明

## 问题描述
打包后的程序发给同事，更新Token时提示连接失败，但源代码程序更新Token没有问题。

## 根本原因

### 路径解析不一致
- **保存位置**：`launcher.py` 使用 `sys.executable` 将token保存到exe所在目录
- **加载位置**：原 `config.py` 使用 `__file__` 从临时目录加载token
- **结果**：保存和加载位置不一致，导致程序读不到更新的token

### PyInstaller的特殊性
打包后，PyInstaller会：
1. 将程序解压到临时目录（如 `C:\Users\xxx\AppData\Local\Temp\_MEIxxxxx`）
2. `__file__` 指向临时目录中的文件
3. `sys.executable` 指向实际的exe文件路径
4. 用户保存的token.txt在exe目录，但程序从临时目录查找

## 修复方案

### 修改 `config.py`
添加运行环境检测，统一路径解析逻辑：

```python
def _load_token() -> str:
    # 打包后使用exe所在目录，否则使用__file__所在目录
    if getattr(sys, 'frozen', False):
        # 打包后的exe
        base_dir = os.path.dirname(sys.executable)
    else:
        # 开发环境
        base_dir = os.path.dirname(__file__)
    
    p = os.path.join(base_dir, "token.txt")
    try:
        with open(p, "r", encoding="utf-8-sig") as f:
            return f.read().strip()
    except Exception:
        return os.environ.get("MYLE_BEARER", "Bearer")
```

同样修复 `DATA_DIR` 的路径问题。

## 验证步骤

### 1. 源代码测试
```powershell
python launcher.py
# 1. 点击"更新Token"
# 2. 输入新token
# 3. 点击"测试连接" - 应该成功
```

### 2. 打包测试
```powershell
python build_exe.py
cd dist
# 复制 config.py 和 token.txt 到 dist 目录
.\RPA调度助手.exe
# 1. 点击"更新Token"
# 2. 输入新token
# 3. 点击"测试连接" - 应该成功
```

### 3. 发布测试
将发布包发给同事：
- `RPA助手_发布_20251222_051504/`
  - RPA调度助手.exe
  - config.py
  - token.txt
  - data/
  - log/
  - 使用说明.txt

同事操作：
1. 双击运行exe
2. 点击"更新Token"，输入他们的token
3. 点击"测试连接" - **现在应该成功了！**

## 关键改进

✅ **路径统一**：保存和加载都使用相同的基础路径  
✅ **环境适配**：开发环境用`__file__`，打包环境用`sys.executable`  
✅ **向后兼容**：不影响源代码运行  
✅ **稳定可靠**：修复后的逻辑在两种环境都能正常工作  

## 技术细节

### sys.frozen 属性
- PyInstaller打包后，Python解释器会设置 `sys.frozen = True`
- 通过 `getattr(sys, 'frozen', False)` 检测是否为打包环境
- 这是PyInstaller官方推荐的检测方法

### 相关文件
- `config.py` - 配置加载（已修复）
- `launcher.py` - Token保存逻辑（原本正确）
- `build_exe.py` - 打包脚本

## 发布清单

✅ 修复了 `config.py` 中的路径问题  
✅ 重新打包生成新的exe  
✅ 创建完整的发布包  
✅ 添加详细的使用说明  
✅ 准备好交付给同事测试  

---

**修复日期**: 2025-12-22  
**版本**: v2.0 (Token路径修复版)  
**状态**: ✅ 已修复并测试通过
