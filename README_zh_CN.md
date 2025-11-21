[English](README.md)

# 图像压缩工具

## 项目介绍
这是一个功能强大的图像压缩工具，能够将图像压缩到指定大小（默认20KB以下），同时保持最佳的视觉质量。支持多种图像格式，并提供灵活的命令行接口。

## 功能特性
- ✅ 支持多种图像格式：JPEG、PNG、GIF、WebP、AVIF等
- ✅ 指定大小压缩：可将图像压缩到目标大小（默认20KB）
- ✅ 自动质量平衡：在保证视觉质量的同时最小化文件大小
- ✅ 批量处理：支持单个文件和目录批量处理
- ✅ 格式转换：支持在压缩过程中进行格式转换
- ✅ 图像缩放：支持按比例缩放图像
- ✅ 详细信息输出：提供压缩前后的详细信息对比

## 技术栈
- Python 3.14+
- Pillow (PIL) - 图像处理基础库
- numpy - 数值计算支持

## 安装说明

### 1. 克隆项目
```bash
git clone [项目仓库地址]
cd image-compress
```

### 2. 安装依赖
使用清华镜像源安装依赖，提高下载速度：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 使用方法

### 基本使用

#### 1. 压缩单个图像（默认质量85%）
```bash
python cli/main.py input.jpg -o output.jpg
```

#### 2. 指定压缩质量
```bash
python cli/main.py input.jpg -o output.jpg -q 75
```

#### 3. 压缩到指定大小（KB）
```bash
python cli/main.py input.jpg -o output.jpg -s 20
```

#### 4. 转换图像格式
```bash
python cli/main.py input.png -o output.webp -f WEBP
```

#### 5. 调整图像大小并压缩
```bash
python cli/main.py input.jpg -o output.jpg -s 15 -c 0.8
```

#### 6. 批量压缩目录中的所有图像
```bash
python cli/main.py -d images_folder -o compressed_folder
```

#### 7. 递归处理子目录
```bash
python cli/main.py -d images_folder -o compressed_folder -r
```

### 独立可执行文件版本

该工具还可以打包成无需Python环境即可运行的独立可执行文件：

1. 安装打包工具：
   ```bash
   pip install pyinstaller pillow
   ```

2. 打包工具：
   ```bash
   pyinstaller --onefile --windowed standalone_image_compressor.py
   ```

3. 在 `dist/` 文件夹中找到可执行文件并直接使用：
   ```bash
   ./dist/standalone_image_compressor input.jpg -o output.jpg -q 80
   ./dist/standalone_image_compressor input.jpg -o output.jpg -s 20
   ./dist/standalone_image_compressor -d images_folder -o compressed_folder
   ```

在Windows系统上，可执行文件将具有 `.exe` 扩展名。

### 跨平台支持

独立版本支持所有主要平台：

- **Windows**: `.exe` 文件
- **macOS**: 独立可执行文件
- **Linux**: 独立可执行文件

对于Linux包管理系统：
- **DEB包** 适用于 Debian/Ubuntu
- **RPM包** 适用于 Red Hat/CentOS/Fedora

### 为不同平台构建

使用跨平台构建脚本为不同平台创建可执行文件：

```bash
# 为当前平台构建
python simple_cross_platform_build.py

# 为特定平台构建
python simple_cross_platform_build.py --platform windows
python simple_cross_platform_build.py --platform darwin
python simple_cross_platform_build.py --platform linux

# 为所有平台构建
python simple_cross_platform_build.py --all

# 创建Linux包（需要 dpkg-deb 和 rpmbuild）
python simple_cross_platform_build.py --platform linux --packages
```

### GitHub Actions 自动化构建

本仓库包含 GitHub Actions 工作流，可自动为所有平台构建和发布可执行文件：

- **工作流文件**: [.github/workflows/build-release.yml](.github/workflows/build-release.yml)
- **触发条件**: 推送以 `v` 开头的标签（例如 `v1.0.0`）
- **支持平台**: Windows、macOS 和 Linux
- **输出**: 包含所有平台可执行文件的 GitHub Release

#### 创建新版本

要创建带有自动构建的新版本：

```bash
# 提交更改
git add .
git commit -m "Prepare for release"

# 创建并推送新标签
git tag v1.0.0
git push origin main --tags
```

GitHub Actions 工作流将自动：
1. 为 Windows、macOS 和 Linux 构建可执行文件
2. 创建新的 GitHub Release
3. 将所有可执行文件作为发布资产上传

### 查看完整帮助信息
```bash
python cli/main.py -h
```

## 项目进度

### 已完成功能
- ✅ 核心压缩引擎实现
- ✅ 命令行接口开发
- ✅ 工具函数库
- ✅ 单元测试和集成测试
- ✅ 支持多种图像格式
- ✅ 指定大小压缩算法
- ✅ 自动质量平衡逻辑
- ✅ 独立可执行文件版本
- ✅ 跨平台支持
- ✅ GitHub Actions 自动化构建

### 待完成功能
- ⬜ 更多高级压缩选项
- ⬜ 图形用户界面（GUI）
- ⬜ 批处理配置文件支持
- ⬜ 更多文档和使用示例

## 测试
项目包含单元测试和集成测试，可以通过以下命令运行：

```bash
cd tests
python -m pytest test_compression.py -v
```

## 贡献指南
欢迎提交Issue和Pull Request来帮助改进这个项目！

## 许可证
[MIT License]