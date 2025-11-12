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