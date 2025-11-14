# 条形码和二维码生成器

一个基于Python的Windows客户端应用程序，用于生成各种类型的条形码和二维码，支持批量生成功能。

## 功能特点

- 支持多种条形码编码格式（EAN-13, UPC-A, Code128, Code39等）
- 支持二维码生成
- 批量生成条形码和二维码
- 自定义条形码/二维码尺寸和样式
- 导出为PNG、SVG等多种格式
- 简洁易用的图形界面
- 完善的错误处理和日志记录
- 支持多种数据源格式（CSV、TXT、JSON、Excel）
- 生成详细的处理报告

## 项目结构

```
sa_Barcode Generator/
│── main.py                 # 主程序入口
│── requirements.txt        # 项目依赖
│── README.md              # 项目说明文档
│── config/
│   └── __init__.py
├── ui/
│   ├── __init__.py
│   ├── main_window.py     # 主窗口界面
│   ├── barcode_tab.py     # 条形码生成界面
│   ├── qrcode_tab.py      # 二维码生成界面
│   └── batch_tab.py       # 批量生成界面
├── core/
│   ├── __init__.py
│   ├── barcode_generator.py  # 条形码生成核心功能
│   ├── qrcode_generator.py   # 二维码生成核心功能
│   └── batch_processor.py    # 批量处理功能
├── utils/
│   ├── __init__.py
│   ├── logger.py          # 日志记录工具
│   ├── file_handler.py    # 文件处理工具
│   └── exception_handler.py  # 异常处理工具
├── assets/
│   └── icons/             # 图标资源
└── output/                # 输出目录
    ├── barcodes/          # 条形码输出
    ├── qrcodes/           # 二维码输出
    └── temp/              # 临时文件
```

## 安装与运行

1. 确保已安装Python 3.7或更高版本
2. 安装项目依赖：
   ```
   pip install -r requirements.txt
   ```
3. 运行应用程序：
   ```
   python main.py
   ```

## 使用说明

### 单个条形码/二维码生成
1. 选择条形码或二维码标签页
2. 输入要编码的内容
3. 选择编码类型
4. 调整尺寸和样式
5. 点击生成按钮
6. 保存生成的图像

### 批量生成
1. 切换到批量生成标签页
2. 准备包含数据的CSV或文本文件
3. 选择编码类型和输出格式
4. 配置输出目录
5. 点击批量生成按钮

## 错误处理与日志记录

应用程序实现了完善的错误处理机制和日志记录系统：

### 错误处理
- **参数验证**：所有输入参数都经过严格验证，防止无效输入导致错误
- **异常分类**：对不同类型的异常进行分类处理，提供针对性的错误信息
- **错误恢复**：在可能的情况下尝试从错误中恢复，而不是直接崩溃
- **用户友好提示**：将技术错误转换为用户可以理解的提示信息

### 日志记录
- **多级日志**：支持DEBUG、INFO、WARNING、ERROR、CRITICAL五个级别
- **日志轮转**：自动管理日志文件大小，避免日志文件过大
- **详细记录**：记录关键操作、参数、结果和错误信息
- **日志位置**：日志文件保存在`logs/`目录下，按日期分割

### 错误类型
应用程序处理的主要错误类型包括：
- **ValueError**：参数值无效或超出范围
- **FileNotFoundError**：文件或目录不存在
- **PermissionError**：文件或目录权限不足
- **OSError**：操作系统级别的错误
- **RuntimeError**：运行时错误
- **ImportError**：依赖库缺失

## 依赖库

- PyQt5: 图形用户界面
- python-barcode: 条形码生成
- qrcode: 二维码生成
- Pillow: 图像处理
- pandas: 数据处理（批量生成）
- openpyxl: Excel文件处理（批量生成）

## 系统要求

- Windows 10或更高版本
- Python 3.7+
- 4GB RAM（推荐）

## 许可证

MIT License