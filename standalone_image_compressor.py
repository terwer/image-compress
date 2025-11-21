#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone Image Compressor
==========================

这是一个独立的图像压缩工具，可以被打包成.exe文件在没有Python环境的系统上运行。
支持多种图像格式(JPEG, PNG, GIF, WebP, AVIF等)的压缩和格式转换。

Features:
- 压缩到指定质量
- 压缩到指定文件大小
- 批量处理
- 格式转换
- 详细的压缩信息输出

Usage:
    # 压缩单个文件
    standalone_image_compressor.py input.jpg -o output.jpg -q 80
    
    # 压缩到指定大小
    standalone_image_compressor.py input.jpg -o output.jpg -s 20
    
    # 批量处理目录
    standalone_image_compressor.py -d images_folder -o compressed_folder

Author: Qwen
Version: 1.0
"""

import os
import sys
import argparse
from PIL import Image
import tempfile
import shutil


def get_file_size_kb(file_path):
    """获取文件大小（KB）"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    return round(os.path.getsize(file_path) / 1024, 2)


def is_supported_image(file_path):
    """检查文件是否为支持的图像格式"""
    supported_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif', '.avif'}
    ext = os.path.splitext(file_path)[1].lower()
    return ext in supported_extensions


def compress_image(input_path, output_path=None, quality=85, target_format=None):
    """
    压缩图像
    
    Args:
        input_path: 输入图像路径
        output_path: 输出图像路径
        quality: 压缩质量 (1-100)
        target_format: 目标格式
        
    Returns:
        str: 压缩后的图像路径
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入文件不存在: {input_path}")
    
    # 确定输出路径
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_compressed{ext}"
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # 格式映射
    format_aliases = {
        'JPG': 'JPEG',
        'TIF': 'TIFF'
    }
    
    supported_formats = {
        'JPEG': {'extensions': ['.jpg', '.jpeg']},
        'PNG': {'extensions': ['.png']},
        'WEBP': {'extensions': ['.webp']},
        'GIF': {'extensions': ['.gif']},
        'BMP': {'extensions': ['.bmp']},
        'TIFF': {'extensions': ['.tiff', '.tif']},
        'AVIF': {'extensions': ['.avif']}
    }
    
    try:
        with Image.open(input_path) as img:
            # 确定目标格式
            if target_format:
                target_format_upper = target_format.upper()
                # 处理格式别名
                if target_format_upper in format_aliases:
                    target_format_upper = format_aliases[target_format_upper]
                
                # 验证目标格式
                if target_format_upper not in supported_formats:
                    supported_list = ', '.join(supported_formats.keys())
                    raise ValueError(f"不支持的目标格式: {target_format}。支持的格式有: {supported_list}")
                
                img_format = target_format_upper
                # 更新输出文件扩展名
                base, _ = os.path.splitext(output_path)
                ext = supported_formats[img_format]['extensions'][0]
                output_path = f"{base}{ext}"
            else:
                # 保持原格式
                img_format = img.format
            
            # 根据不同格式处理图像
            if img_format == 'JPEG':
                # JPEG处理
                if img.mode in ['RGBA', 'LA'] or (img.mode == 'P' and 'transparency' in img.info):
                    # 处理带透明度的图像
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[3])
                    else:
                        background.paste(img, mask=img.convert('RGBA').split()[3])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
            elif img_format == 'PNG':
                # PNG处理
                if img.mode == 'P':
                    img = img.convert('RGBA')
            elif img_format == 'WEBP':
                # WebP处理
                if img.mode == 'P':
                    img = img.convert('RGBA')
            
            # 保存压缩后的图像
            save_params = {
                'format': img_format,
                'quality': quality,
                'optimize': True
            }
            
            # 为不同格式添加特定参数
            if img_format == 'PNG':
                save_params['compress_level'] = 9  # 最高压缩级别
            elif img_format == 'JPEG':
                save_params['progressive'] = True  # 使用渐进式JPEG
            elif img_format == 'WEBP':
                # WebP特有参数
                if img.mode == 'RGBA':
                    save_params['method'] = 6  # 最高压缩质量
            
            # 保存图像
            img.save(output_path, **save_params)
            
            return output_path
            
    except Exception as e:
        raise Exception(f"压缩图像时出错: {str(e)}")


def compress_to_size(input_path, output_path=None, target_size_kb=20, tolerance_percent=5, scale_factor=None, verbose=False):
    """
    压缩图像到指定大小
    
    Args:
        input_path: 输入图像路径
        output_path: 输出图像路径
        target_size_kb: 目标文件大小（KB）
        tolerance_percent: 容差百分比
        scale_factor: 图像缩放因子（0.1-1.0）
        verbose: 是否显示详细信息
        
    Returns:
        str: 压缩后的图像路径
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入文件不存在: {input_path}")
    
    # 验证缩放因子
    if scale_factor is not None:
        if scale_factor < 0.1 or scale_factor > 1.0:
            raise ValueError(f"缩放因子必须在0.1-1.0之间，当前值: {scale_factor}")
    
    # 确定输出路径
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_target_size{ext}"
    
    # 目标大小（字节）和容差范围
    target_size_bytes = target_size_kb * 1024
    tolerance = target_size_bytes * (tolerance_percent / 100)
    min_size = target_size_bytes - tolerance
    max_size = target_size_bytes + tolerance
    
    # 创建临时文件用于处理
    temp_path = None
    processing_path = input_path
    
    # 如果指定了缩放因子，先进行缩放
    if scale_factor is not None and scale_factor != 1.0:
        temp_path = output_path + ".temp.jpg"
        processing_path = temp_path
        
        try:
            with Image.open(input_path) as img:
                # 计算新尺寸
                new_width = int(img.width * scale_factor)
                new_height = int(img.height * scale_factor)
                
                if verbose:
                    print(f"按比例缩放: {img.width}x{img.height} -> {new_width}x{new_height}")
                
                # 缩放图像
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                # 保存到临时文件
                resized_img.save(temp_path, format='JPEG', quality=95)
                
                if verbose:
                    resized_size = os.path.getsize(temp_path)
                    print(f"缩放后文件大小: {resized_size/1024:.2f}KB")
        except Exception as e:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            raise Exception(f"缩放图像时出错: {str(e)}")
    
    # 确保在函数结束时清理临时文件
    try:
        # 首先尝试转换为WebP格式以获得更好的压缩效果
        if not output_path.lower().endswith('.webp'):
            webp_output = os.path.splitext(output_path)[0] + '.webp'
        else:
            webp_output = output_path
        
        if verbose:
            print(f"尝试转换为WebP格式: {webp_output}")
        
        # 使用二分查找确定最佳质量
        low = 1
        high = 95
        best_quality = high
        best_file = None
        
        while low <= high:
            mid = (low + high) // 2
            
            # 压缩到临时文件
            temp_compressed = webp_output + f".temp{mid}.webp"
            try:
                with Image.open(processing_path) as img:
                    # 转换为RGB模式（确保兼容性）
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 保存为WebP格式
                    img.save(temp_compressed, format='WEBP', quality=mid)
            except Exception as e:
                if os.path.exists(temp_compressed):
                    os.remove(temp_compressed)
                raise Exception(f"压缩过程中出错: {str(e)}")
            
            # 检查文件大小
            compressed_size = os.path.getsize(temp_compressed)
            
            if verbose:
                print(f"质量 {mid}: 大小 {compressed_size/1024:.2f}KB")
            
            # 如果大小符合要求，尝试更高质量
            if compressed_size <= target_size_bytes:
                best_quality = mid
                if best_file and os.path.exists(best_file):
                    os.remove(best_file)
                best_file = temp_compressed
                low = mid + 1
            else:
                # 大小过大，尝试更低质量
                os.remove(temp_compressed)
                high = mid - 1
        
        # 如果找到了合适的质量
        if best_file and os.path.exists(best_file):
            # 重命名为最终输出文件
            if os.path.exists(webp_output):
                os.remove(webp_output)
            os.rename(best_file, webp_output)
            
            # 如果用户指定了不同格式的输出路径，进行格式转换
            if webp_output != output_path:
                try:
                    with Image.open(webp_output) as img:
                        img.save(output_path)
                    # 仅当输出成功时才删除webp文件
                    os.remove(webp_output)
                except Exception as e:
                    # 如果转换失败，保留webp文件
                    if verbose:
                        print(f"转换到指定格式失败，保留WebP文件: {str(e)}")
                    output_path = webp_output
            
            final_size = os.path.getsize(output_path)
            if verbose:
                print(f"最佳质量: {best_quality}, 最终大小: {final_size/1024:.2f}KB")
            
            # 检查是否满足目标大小要求
            if final_size <= target_size_bytes + tolerance:
                return output_path
        
        # 如果WebP格式仍然太大，尝试缩小尺寸
        if verbose:
            print("WebP压缩后仍然太大，尝试缩小尺寸")
        
        # 计算需要缩小的比例
        with Image.open(processing_path) as img:
            current_size = os.path.getsize(processing_path)
            size_ratio = target_size_bytes / current_size if current_size > 0 else 0.5
            scale_factor_for_size = size_ratio ** 0.5  # 使用平方根进行缩小
            
            # 确保最小缩放比例
            min_scale = 0.1
            scale_factor_for_size = max(scale_factor_for_size, min_scale)
            
            # 计算新尺寸
            new_width = max(1, int(img.width * scale_factor_for_size))
            new_height = max(1, int(img.height * scale_factor_for_size))
            
            if verbose:
                print(f"缩小到 {new_width}x{new_height} (比例: {scale_factor_for_size:.2f})")
            
            # 缩小并保存
            try:
                with Image.open(processing_path) as img:
                    # 缩小图像
                    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # 保存为WebP格式以获得最佳压缩效果
                    resized_img.save(output_path, format='WEBP', quality=85)
            except Exception as e:
                raise Exception(f"调整尺寸时出错: {str(e)}")
        
        final_size = os.path.getsize(output_path)
        if verbose:
            print(f"最终结果: {final_size/1024:.2f}KB")
        
        return output_path
    finally:
        # 确保清理临时文件
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def process_single_image(input_path, output_path=None, quality=85, target_format=None,
                        target_size_kb=None, tolerance=5, scale_factor=None, verbose=False):
    """
    处理单个图像文件
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
            output_path = compress_to_size(input_path, output_path, target_size_kb, tolerance, scale_factor, verbose)
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


def process_directory(input_dir, output_dir=None, quality=85, target_format=None,
                     target_size_kb=None, tolerance=5, scale_factor=None, recursive=False, verbose=False):
    """
    处理目录中的图像文件
    """
    if not os.path.exists(input_dir):
        print(f"错误: 输入目录不存在: {input_dir}")
        return (0, 0, 0)
    
    if not os.path.isdir(input_dir):
        print(f"错误: 输入路径不是目录: {input_dir}")
        return (0, 0, 0)
    
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
        return (0, 0, 0)
    
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
    """主函数"""
    parser = argparse.ArgumentParser(
        prog='standalone_image_compressor',
        description='独立图像压缩工具 - 可打包为exe文件使用',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
示例：
    # 使用默认质量压缩单个图像
    standalone_image_compressor input.jpg -o output.jpg
    
    # 指定压缩质量
    standalone_image_compressor input.jpg -o output.jpg -q 80
    
    # 压缩到指定大小（KB）
    standalone_image_compressor input.jpg -o output.jpg -s 20
    
    # 批量压缩目录中的所有图像
    standalone_image_compressor -d images_folder -o compressed_folder
    
    # 转换图像格式
    standalone_image_compressor input.png -o output.webp -f WEBP
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
    
    # 解析参数
    args = parser.parse_args()
    
    try:
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