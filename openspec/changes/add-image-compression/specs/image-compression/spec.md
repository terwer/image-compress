## ADDED Requirements

### Requirement: 图像格式支持
系统 SHALL 支持常见图像格式的输入和输出，包括 JPEG、PNG、GIF、WebP 和 AVIF。

#### Scenario: 支持多种图像格式
- **WHEN** 用户提供 JPEG、PNG、GIF、WebP 或 AVIF 格式的图像
- **THEN** 系统 SHALL 正确处理并支持这些格式的输入/输出转换

### Requirement: 指定大小压缩
系统 SHALL 能够将图像压缩到指定大小限制（默认 20KB 或更小）。

#### Scenario: 压缩到20KB以下
- **WHEN** 用户指定压缩目标大小为 20KB
- **THEN** 系统 SHALL 将图像压缩到该大小或更小，同时保持可接受的视觉质量

### Requirement: 输入输出格式配置
系统 SHALL 允许用户指定输入图像路径、输出图像路径和输出格式。

#### Scenario: 自定义输入输出路径和格式
- **WHEN** 用户提供输入路径、输出路径和输出格式参数
- **THEN** 系统 SHALL 从指定路径读取图像，按照指定格式处理，并保存到输出路径

### Requirement: 自动质量平衡
系统 SHALL 实现自动质量平衡算法，在保持图像质量的同时最小化文件大小。

#### Scenario: 自动调整压缩质量
- **WHEN** 图像在初始压缩后未达到目标大小
- **THEN** 系统 SHALL 自动降低质量并重新压缩，直到满足大小要求或达到最低质量阈值

### Requirement: 命令行接口
系统 SHALL 提供命令行接口，允许用户通过命令行参数控制压缩过程。

#### Scenario: 通过命令行压缩图像
- **WHEN** 用户使用带有必要参数的命令行工具
- **THEN** 系统 SHALL 执行压缩操作并输出处理结果信息