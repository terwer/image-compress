#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像压缩工具命令行界面

提供命令行方式进行图像压缩操作
"""

import os
import sys
import argparse
from typing import Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compressors.image_compressor import compress_image, compress_to_size, get_file_size_kb


def parse_arguments(argv=None):
    """
    解析命令行参数
    
    Args:
        argv: 命令行参数列表，如果为None则使用sys.argv
    
    Returns:
        argparse.Namespace: 解析后的参数对象
    """
    parser = argparse.ArgumentParser(
        prog='image-compress',
        description='高性能图像压缩工具，支持多种格式',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
示例：
    # 使用默认质量压缩单个图像
    image-compress input.jpg -o output.jpg
    
    # 指定压缩质量
    image-compress input.jpg -o output.jpg -q 80
    
    # 压缩到指定大小（KB）
    image-compress input.jpg -o output.jpg -s 100
    
    # 批量压缩目录中的所有图像
    image-compress -d images_folder -o compressed_folder
    
    # 转换图像格式
    image-compress input.png -o output.webp -f WEBP
"""
    )
    
    # 基本参数
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('input', nargs='?', help='输入图像文件路径')
    input_group.add_argument('-d', '--directory', help='输入目录路径（批量处理）')
    
    parser.add_argument('-o', '--output', help='输出路径（文件或目录）')
    parser.add_argument('-q', '--quality', type=int, default=85, 
                        help='压缩质量（1-100），默认85')
    parser.add_argument('-f', '--format', dest='target_format',
                        help='目标图像格式（JPEG、PNG、WEBP等）')
    
    # 特殊压缩模式
    parser.add_argument('-s', '--size', type=int, dest='target_size_kb',
                        help='目标文件大小（KB），默认20KB，启用指定大小压缩模式')
    parser.add_argument('-t', '--tolerance', type=float, default=5,
                        help='指定大小压缩的容差百分比（默认5%%）')
    parser.add_argument('-c', '--scale', type=float, dest='scale_factor',
                        help='图像缩放因子（0.1-1.0），例如0.5表示缩小到原尺寸的一半')
    
    # 其他选项
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='递归处理子目录')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='显示详细信息')
    
    return parser.parse_args(argv)


def validate_quality(quality: int) -> bool:
    """
    验证压缩质量参数
    
    Args:
        quality: 压缩质量参数
        
    Returns:
        bool: 是否有效
    """
    if quality < 1 or quality > 100:
        print(f"错误: 压缩质量必须在1-100之间，当前值: {quality}")
        return False
    return True


def validate_target_size(target_size_kb: int) -> bool:
    """
    验证目标大小参数
    
    Args:
        target_size_kb: 目标大小（KB）
        
    Returns:
        bool: 是否有效
    """
    if target_size_kb <= 0:
        print(f"错误: 目标大小必须大于0，当前值: {target_size_kb}")
        return False
    return True


def is_supported_image(file_path: str) -> bool:
    """
    检查文件是否为支持的图像格式
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 是否为支持的图像
    """
    # 支持的图像扩展名
    supported_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.gif', '.avif'}
    
    ext = os.path.splitext(file_path)[1].lower()
    return ext in supported_extensions


def process_single_image(input_path: str, output_path: Optional[str] = None,
                        quality: int = 85, target_format: Optional[str] = None,
                        target_size_kb: Optional[int] = None, tolerance: float = 5,
                        scale_factor: Optional[float] = None, verbose: bool = False) -> bool:
    """
    处理单个图像文件
    
    Args:
        input_path: 输入图像路径
        output_path: 输出图像路径
        quality: 压缩质量
        target_format: 目标格式
        target_size_kb: 目标大小（KB）
        tolerance: 容差百分比
        verbose: 是否显示详细信息
        
    Returns:
        bool: 是否处理成功
    """
    try:
        # 检查输入文件
        if not os.path.exists(input_path):
            print(f"错误: 输入文件不存在: {input_path}")
            return False
        
        if not os.path.isfile(input_path):
            print(f"错误: 输入路径不是文件: {input_path}")
            return False
        
        # 检查文件格式是否支持
        if not is_supported_image(input_path):
            print(f"警告: 不支持的图像格式: {input_path}")
            return False
        
        # 验证缩放因子参数
        if scale_factor is not None:
            if scale_factor < 0.1 or scale_factor > 1.0:
                print(f"错误: 缩放因子必须在0.1-1.0之间，当前值: {scale_factor}")
                return False
        
        # 计算默认输出路径
        if output_path is None:
            base, ext = os.path.splitext(input_path)
            # 如果指定了目标格式，使用新扩展名
            if target_format:
                output_path = f"{base}_compressed.{target_format.lower()}"
            else:
                output_path = f"{base}_compressed{ext}"
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 获取原始大小
        original_size_kb = get_file_size_kb(input_path)
        
        # 根据模式选择压缩方法
        if target_size_kb is not None:
            # 指定大小压缩模式
            output_path = compress_to_size(input_path, output_path, target_size_kb, tolerance, scale_factor)
            mode_info = f"目标大小: {target_size_kb}KB (容差: {tolerance}%)"
        else:
            # 质量压缩模式
            output_path = compress_image(input_path, output_path, quality, target_format)
            mode_info = f"质量: {quality}"
        
        # 获取压缩后大小
        compressed_size_kb = get_file_size_kb(output_path)
        
        # 计算压缩率
        compression_ratio = ((original_size_kb - compressed_size_kb) / original_size_kb) * 100 if original_size_kb > 0 else 0
        
        # 输出结果
        if verbose:
            print(f"处理成功: {input_path}")
            print(f"  输出: {output_path}")
            print(f"  模式: {mode_info}")
            print(f"  原始大小: {original_size_kb:.2f}KB")
            print(f"  压缩后大小: {compressed_size_kb:.2f}KB")
            print(f"  压缩率: {compression_ratio:.2f}%")
        else:
            print(f"✓ {os.path.basename(input_path)} - 压缩率: {compression_ratio:.2f}%")
        
        return True
        
    except Exception as e:
        print(f"错误: 处理 {input_path} 时失败: {str(e)}")
        return False


def process_directory(input_dir: str, output_dir: Optional[str] = None,
                     quality: int = 85, target_format: Optional[str] = None,
                     target_size_kb: Optional[int] = None, tolerance: float = 5,
                     scale_factor: Optional[float] = None, recursive: bool = False, verbose: bool = False) -> tuple[int, int]:
    """
    处理目录中的图像文件
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        quality: 压缩质量
        target_format: 目标格式
        target_size_kb: 目标大小（KB）
        tolerance: 容差百分比
        recursive: 是否递归处理子目录
        verbose: 是否显示详细信息
        
    Returns:
        tuple: (成功数量, 失败数量)
    """
    if not os.path.exists(input_dir):
        print(f"错误: 输入目录不存在: {input_dir}")
        return (0, 0)
    
    if not os.path.isdir(input_dir):
        print(f"错误: 输入路径不是目录: {input_dir}")
        return (0, 0)
    
    # 如果未指定输出目录，默认使用输入目录 + '_compressed'
    if output_dir is None:
        output_dir = f"{input_dir}_compressed"
    
    success_count = 0
    fail_count = 0
    total_count = 0
    
    # 获取所有图像文件
    image_files = []
    
    if recursive:
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if is_supported_image(file_path):
                    image_files.append(file_path)
    else:
        for file in os.listdir(input_dir):
            file_path = os.path.join(input_dir, file)
            if os.path.isfile(file_path) and is_supported_image(file_path):
                image_files.append(file_path)
    
    total_count = len(image_files)
    
    if total_count == 0:
        print(f"警告: 在 {input_dir} 中未找到支持的图像文件")
        return (0, 0)
    
    print(f"找到 {total_count} 个图像文件待处理...")
    
    # 处理每个图像文件
    for i, input_path in enumerate(image_files, 1):
        if verbose:
            print(f"处理 {i}/{total_count}: {input_path}")
        
        # 计算相对路径以保持目录结构
        rel_path = os.path.relpath(input_path, input_dir)
        output_path = os.path.join(output_dir, rel_path)
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 处理单个图像
        if process_single_image(input_path, output_path, quality, target_format,
                              target_size_kb, tolerance, scale_factor, verbose):
            success_count += 1
        else:
            fail_count += 1
    
    return (success_count, fail_count, total_count)


def main():
    """
    主函数
    """
    try:
        # 解析参数
        args = parse_arguments()
        
        # 验证参数
        if not validate_quality(args.quality):
            sys.exit(1)
        
        if args.target_size_kb is not None and not validate_target_size(args.target_size_kb):
            sys.exit(1)
        
        # 根据输入类型处理
        if args.input:
            # 处理单个文件
            success = process_single_image(
                args.input,
                args.output,
                args.quality,
                args.target_format,
                args.target_size_kb,
                args.tolerance,
                args.scale_factor,
                args.verbose
            )
            sys.exit(0 if success else 1)
        
        elif args.directory:
            # 处理目录
            success_count, fail_count, total_count = process_directory(
                args.directory,
                args.output,
                args.quality,
                args.target_format,
                args.target_size_kb,
                args.tolerance,
                args.scale_factor,
                args.recursive,
                args.verbose
            )
            
            # 输出摘要
            print("\n处理完成!")
            print(f"总计: {total_count}")
            print(f"成功: {success_count}")
            print(f"失败: {fail_count}")
            
            sys.exit(0 if fail_count == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()