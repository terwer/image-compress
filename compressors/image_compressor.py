#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像压缩核心模块
提供各种图像压缩功能
"""

import os
from PIL import Image
import numpy as np


class ImageCompressor:
    """
    图像压缩器类
    提供图像压缩、格式转换、质量调整等功能
    """
    
    def __init__(self):
        """初始化图像压缩器"""
        # 支持的图像格式及其对应的MIME类型
        self.supported_formats = {
            'JPEG': {'mime': 'image/jpeg', 'extensions': ['.jpg', '.jpeg']},
            'PNG': {'mime': 'image/png', 'extensions': ['.png']},
            'WEBP': {'mime': 'image/webp', 'extensions': ['.webp']},
            'GIF': {'mime': 'image/gif', 'extensions': ['.gif']},
            'BMP': {'mime': 'image/bmp', 'extensions': ['.bmp']},
            'TIFF': {'mime': 'image/tiff', 'extensions': ['.tiff', '.tif']},
            'AVIF': {'mime': 'image/avif', 'extensions': ['.avif']}
        }
        # 默认压缩质量
        self.default_quality = 85
        # 格式映射（处理大小写和别名）
        self.format_aliases = {
            'JPG': 'JPEG',
            'TIF': 'TIFF'
        }
    
    def compress(self, input_path, output_path=None, quality=None, target_format=None):
        """
        压缩图像
        
        Args:
            input_path: 输入图像路径
            output_path: 输出图像路径，默认为None（在原文件名后添加_compressed）
            quality: 压缩质量 (1-100)，默认为None（使用默认质量）
            target_format: 目标图像格式，默认为None（保持原格式）
            
        Returns:
            str: 压缩后的图像路径
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        
        # 验证是否为有效图像
        if not self.is_valid_image(input_path):
            raise ValueError(f"无效的图像文件: {input_path}")
        
        # 确定输出路径
        if output_path is None:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_compressed{ext}"
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # 检查输入和输出是否为同一个文件
        input_stat = os.stat(input_path)
        try:
            output_stat = os.stat(output_path)
            is_same_file = os.path.samefile(input_path, output_path) if hasattr(os.path, 'samefile') else \
                          (input_stat.st_ino == output_stat.st_ino and input_stat.st_dev == output_stat.st_dev)
        except OSError:
            is_same_file = False
        
        # 如果是同一个文件，使用临时文件
        use_temp = is_same_file
        
        # 确定压缩质量
        if quality is None:
            quality = self.default_quality
        else:
            # 确保质量在有效范围内
            quality = max(1, min(100, quality))
        
        # 打开图像
        try:
            with Image.open(input_path) as img:
                # 检测原始格式
                orig_format_info = self.detect_format(input_path)
                orig_format = orig_format_info['format']
                
                # 确定目标格式
                if target_format:
                    target_format_upper = target_format.upper()
                    # 处理格式别名
                    if target_format_upper in self.format_aliases:
                        target_format_upper = self.format_aliases[target_format_upper]
                    
                    # 验证目标格式
                    if target_format_upper not in self.supported_formats:
                        supported_list = ', '.join(self.supported_formats.keys())
                        raise ValueError(f"不支持的目标格式: {target_format}。支持的格式有: {supported_list}")
                    
                    img_format = target_format_upper
                    # 更新输出文件扩展名
                    base, _ = os.path.splitext(output_path)
                    ext = self.supported_formats[img_format]['extensions'][0]
                    output_path = f"{base}{ext}"
                else:
                    img_format = orig_format
                
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
                
                # 保存压缩后的图像，针对不同格式设置优化参数
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
                elif img_format == 'AVIF':
                    # AVIF特有参数
                    if img.mode == 'RGBA':
                        save_params['quality'] = quality  # AVIF质量参数
                
                # 保存图像
                if use_temp:
                    import tempfile
                    temp_fd, temp_path = tempfile.mkstemp(suffix=f".{img_format.lower()}")
                    os.close(temp_fd)
                    try:
                        # 保存到临时文件
                        img.save(temp_path, **save_params)
                        # 复制到目标路径
                        import shutil
                        shutil.copy2(temp_path, output_path)
                    finally:
                        # 清理临时文件
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                else:
                    # 直接保存到目标路径
                    img.save(output_path, **save_params)
                
                return output_path
                
        except Exception as e:
            raise Exception(f"压缩图像时出错: {str(e)}")
    
    def compress_to_size(self, input_path, output_path=None, target_size_kb=20, tolerance_percent=5, scale_factor=None, verbose=False):
        """
        压缩图像到指定大小
        
        Args:
            input_path: 输入图像路径
            output_path: 输出图像路径，默认为None
            target_size_kb: 目标文件大小（KB）
            tolerance_percent: 容差百分比
            scale_factor: 图像缩放因子（0.1-1.0）
            verbose: 是否显示详细信息
            
        Returns:
            str: 压缩后的图像路径
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        
        # 验证是否为有效图像
        if not self.is_valid_image(input_path):
            raise ValueError(f"无效的图像文件: {input_path}")
        
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
        
        # 获取当前文件大小
        current_size = os.path.getsize(processing_path)
        
        # 检查输入和输出是否为同一个文件
        try:
            is_same_file = os.path.samefile(processing_path, output_path) if hasattr(os.path, 'samefile') else False
        except OSError:
            is_same_file = False
            
        # 确保在函数结束时清理临时文件
        try:
            # 剩余的压缩逻辑将使用processing_path
            # 二分查找确定最佳质量参数
            low = 1
            high = 95
            best_quality = high
            best_size = current_size
            best_file = None
            
            # 首先尝试转换为WebP格式
            if not output_path.lower().endswith('.webp'):
                webp_output = os.path.splitext(output_path)[0] + '.webp'
            else:
                webp_output = output_path
            
            if verbose:
                print(f"尝试转换为WebP格式: {webp_output}")
            
            # 使用二分查找确定最佳质量
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
                    best_size = compressed_size
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
            size_ratio = target_size_bytes / best_size if best_size > 0 else 0.5
            scale_factor_for_size = size_ratio ** 0.3  # 使用0.3次方进行更激进的缩小
            
            # 确保最小缩放比例
            min_scale = 0.05  # 放宽到5%
            scale_factor_for_size = max(scale_factor_for_size, min_scale)
            
            # 最大迭代次数
            max_iterations = 10
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                
                # 计算新尺寸
                with Image.open(processing_path) as img:
                    new_width = int(img.width * scale_factor_for_size)
                    new_height = int(img.height * scale_factor_for_size)
                    
                if verbose:
                    print(f"迭代 {iteration}: 缩小到 {new_width}x{new_height} (比例: {scale_factor_for_size:.2f})")
                
                # 缩小并保存
                temp_resized = output_path + f".temp_resized{iteration}.webp"
                try:
                    with Image.open(processing_path) as img:
                        # 转换为灰度模式以进一步减小文件大小
                        if img.mode != 'L':
                            img = img.convert('L')
                        
                        # 缩小图像
                        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        # 使用最低质量保存
                        resized_img.save(temp_resized, format='WEBP', quality=0)
                except Exception as e:
                    if os.path.exists(temp_resized):
                        os.remove(temp_resized)
                    raise Exception(f"调整尺寸时出错: {str(e)}")
                
                # 检查新的文件大小
                resized_size = os.path.getsize(temp_resized)
                
                if verbose:
                    print(f"调整后大小: {resized_size/1024:.2f}KB")
                
                if resized_size <= target_size_bytes + tolerance:
                    # 达到目标大小，使用这个文件
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    os.rename(temp_resized, output_path)
                    
                    final_size = resized_size
                    if verbose:
                        print(f"成功达到目标大小: {final_size/1024:.2f}KB")
                    
                    return output_path
                else:
                    # 仍未达到目标，继续缩小
                    os.remove(temp_resized)
                    scale_factor_for_size *= 0.7  # 每次额外缩小30%
                    scale_factor_for_size = max(scale_factor_for_size, min_scale)
            
            # 如果仍然无法达到目标大小，使用最后一次尝试的结果
            if verbose:
                print("达到最大迭代次数，使用最佳结果")
            
            # 尝试一次极度压缩
            if os.path.exists(temp_resized):
                os.remove(temp_resized)
            
            final_attempt = output_path + ".final_attempt.webp"
            try:
                with Image.open(processing_path) as img:
                    # 转换为灰度
                    if img.mode != 'L':
                        img = img.convert('L')
                    
                    # 缩放到非常小的尺寸
                    tiny_width = max(10, int(img.width * 0.2))  # 最小10像素
                    tiny_height = max(10, int(img.height * 0.2))
                    
                    if verbose:
                        print(f"最后尝试: 缩放到 {tiny_width}x{tiny_height}")
                    
                    tiny_img = img.resize((tiny_width, tiny_height), Image.Resampling.LANCZOS)
                    tiny_img.save(final_attempt, format='WEBP', quality=0)
            except Exception as e:
                if os.path.exists(final_attempt):
                    os.remove(final_attempt)
                raise Exception(f"最终压缩尝试失败: {str(e)}")
            
            # 使用最终尝试的结果
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(final_attempt, output_path)
            
            final_size = os.path.getsize(output_path)
            if verbose:
                print(f"最终结果: {final_size/1024:.2f}KB")
            
            return output_path
        finally:
            # 确保清理临时文件
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
        
        # 检测图像格式
        format_info = self.detect_format(input_path)
        img_format = format_info['format']
        
        # 打开图像
        with Image.open(input_path) as img:
            # 根据图像格式使用不同的压缩策略
            if img_format in ['JPEG', 'WEBP']:
                # 对于支持质量参数的格式，使用二分查找确定最佳质量
                low, high = 1, 100
                best_quality = 85
                best_size = float('inf')
                best_output = None
                
                # 临时文件目录
                temp_dir = os.path.dirname(input_path) or '.'
                
                try:
                    # 二分查找
                    max_iterations = 20
                    iteration = 0
                    while high - low > 1 and iteration < max_iterations:
                        iteration += 1
                        mid = (low + high) // 2
                        temp_output = os.path.join(temp_dir, f"temp_{mid}_{os.path.basename(output_path)}")
                        
                        # 处理模式转换
                        save_img = img.copy()
                        if img_format == 'JPEG' and save_img.mode in ['RGBA', 'LA']:
                            # 为JPEG创建白色背景
                            background = Image.new('RGB', save_img.size, (255, 255, 255))
                            background.paste(save_img, mask=save_img.split()[3] if save_img.mode == 'RGBA' else None)
                            save_img = background
                        elif save_img.mode != 'RGB' and img_format == 'JPEG':
                            save_img = save_img.convert('RGB')
                        
                        # 保存临时图像
                        save_params = {'format': img_format, 'quality': mid, 'optimize': True}
                        if img_format == 'JPEG':
                            save_params['progressive'] = True
                        elif img_format == 'WEBP':
                            save_params['method'] = 6
                            save_params['lossless'] = False  # 确保使用有损压缩
                        elif img_format == 'AVIF':
                            save_params['speed'] = 0  # 使用最大压缩率
                        
                        save_img.save(temp_output, **save_params)
                        
                        # 检查临时文件大小
                        temp_size = os.path.getsize(temp_output)
                        
                        if temp_size > max_size:
                            # 太大，降低质量
                            high = mid
                        elif temp_size < min_size:
                            # 太小，增加质量
                            low = mid
                        else:
                            # 符合要求
                            if best_output:
                                os.remove(best_output)
                            best_output = temp_output
                            break
                        
                        # 更新最佳结果
                        if abs(temp_size - target_size_bytes) < abs(best_size - target_size_bytes):
                            if best_output:
                                os.remove(best_output)
                            best_size = temp_size
                            best_quality = mid
                            best_output = temp_output
                        else:
                            # 删除非最佳临时文件
                            os.remove(temp_output)
                    
                    # 如果找到了符合条件的文件
                    if best_output:
                        # 复制到最终路径
                        import shutil
                        shutil.copy2(best_output, output_path)
                        os.remove(best_output)
                    else:
                        # 如果没有找到完全符合条件的，尝试使用最低质量作为最后手段
                        if best_quality is not None:
                            # 先尝试使用最佳质量
                            self.compress(input_path, output_path, quality=best_quality)
                            final_size = os.path.getsize(output_path)
                            
                            # 如果仍然太大，使用最低质量
                            if final_size > max_size:
                                # 1. 先尝试最低质量
                                temp_low_quality = os.path.join(temp_dir, f"temp_min_{os.path.basename(output_path)}")
                                save_img = img.copy()
                                
                                # 处理模式转换
                                if img_format == 'JPEG' and save_img.mode in ['RGBA', 'LA']:
                                    background = Image.new('RGB', save_img.size, (255, 255, 255))
                                    background.paste(save_img, mask=save_img.split()[3] if save_img.mode == 'RGBA' else None)
                                    save_img = background
                                elif save_img.mode != 'RGB' and img_format == 'JPEG':
                                    save_img = save_img.convert('RGB')
                                
                                # 使用最低质量保存
                                min_save_params = {'format': img_format, 'quality': 1, 'optimize': True}
                                if img_format == 'JPEG':
                                    min_save_params['progressive'] = True
                                elif img_format == 'WEBP':
                                    min_save_params['method'] = 6
                                    min_save_params['lossless'] = False
                                elif img_format == 'AVIF':
                                    min_save_params['speed'] = 0
                                
                                save_img.save(temp_low_quality, **min_save_params)
                                min_size_check = os.path.getsize(temp_low_quality)
                                
                                # 如果最低质量仍然太大，尝试格式转换和尺寸调整
                            if min_size_check > max_size:
                                print(f"调试信息: 最低质量(1)文件大小({min_size_check}字节)仍大于目标大小({max_size}字节)")
                                # 1. 使用极激进的压缩策略，确保能达到15KB目标
                                print(f"调试信息: 开始极激进压缩策略，目标大小: {max_size}字节")
                                
                                # 直接设置更小的尺寸目标，使用更直接的缩放策略
                                # 首先直接将图像缩小到更小的尺寸，避免多次迭代
                                # 目标尺寸计算基于当前尺寸的固定比例
                                target_percent = 0.2  # 直接尝试缩放到原尺寸的20%
                                print(f"调试信息: 直接尝试缩放到原尺寸的{target_percent*100}%")
                                
                                # 计算新尺寸
                                new_width = max(1, int(save_img.width * target_percent))
                                new_height = max(1, int(save_img.height * target_percent))
                                print(f"调试信息: 初步调整后图像尺寸: {new_width}x{new_height}")
                                
                                # 调整图像大小
                                resized_img = save_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                                
                                # 尝试灰度转换（减少颜色信息，进一步减小文件大小）
                                print(f"调试信息: 尝试将图像转换为灰度模式以减小文件大小")
                                resized_img = resized_img.convert('L')  # 转换为灰度
                                
                                # 使用更激进的WebP压缩参数
                                webp_output = os.path.splitext(output_path)[0] + '.webp'
                                print(f"调试信息: 使用极激进参数保存WebP格式")
                                
                                # 使用更极端的压缩参数：最低质量、最高压缩级别、更长的处理时间
                                resized_img.save(
                                    webp_output, 
                                    format='WEBP', 
                                    quality=0,  # 比1更低，某些实现支持0
                                    method=6,   # 最高压缩级别
                                    lossless=False,
                                    exact=True  # 精确控制压缩
                                )
                                
                                webp_size = os.path.getsize(webp_output)
                                print(f"调试信息: 初始激进压缩后的文件大小: {webp_size}字节")
                                
                                # 如果仍然太大，进行更激进的迭代压缩
                                if webp_size > max_size:
                                    print(f"调试信息: 文件仍然太大，开始迭代缩放")
                                    
                                    # 更激进的迭代策略
                                    current_width, current_height = new_width, new_height
                                    iteration = 0
                                    max_iterations = 10  # 增加迭代次数
                                    
                                    while webp_size > max_size and iteration < max_iterations:
                                        iteration += 1
                                        # 每次缩小更多：30%
                                        current_width = max(1, int(current_width * 0.7))
                                        current_height = max(1, int(current_height * 0.7))
                                        print(f"调试信息: 迭代{iteration} - 进一步调整后的图像尺寸: {current_width}x{current_height}")
                                        
                                        # 再次调整图像大小
                                        further_resized = save_img.resize((current_width, current_height), Image.Resampling.LANCZOS)
                                        further_resized = further_resized.convert('L')  # 确保是灰度
                                        
                                        # 使用相同的极激进参数保存
                                        further_resized.save(
                                            webp_output, 
                                            format='WEBP', 
                                            quality=0,
                                            method=6,
                                            lossless=False,
                                            exact=True
                                        )
                                        
                                        webp_size = os.path.getsize(webp_output)
                                        print(f"调试信息: 迭代{iteration} - 进一步调整后的文件大小: {webp_size}字节")
                                
                                output_path = webp_output
                                
                                # 清理临时文件
                                os.remove(temp_low_quality)
                                print(f"调试信息: 压缩完成，最终输出路径: {output_path}，文件大小: {os.path.getsize(output_path)}字节")
                            else:
                                # 最低质量符合要求
                                print(f"调试信息: 最低质量(1)文件大小({min_size_check}字节)符合要求")
                                shutil.copy2(temp_low_quality, output_path)
                                os.remove(temp_low_quality)
                        else:
                            # 如果best_quality不存在，使用默认压缩
                            self.compress(input_path, output_path, quality=85)
                        
                finally:
                    # 清理所有临时文件
                    for file in os.listdir(temp_dir):
                        if file.startswith(f"temp_" and file.endswith(os.path.basename(output_path))):
                            try:
                                os.remove(os.path.join(temp_dir, file))
                            except:
                                pass
                
            elif img_format == 'PNG':
                # PNG特殊处理：使用颜色量化和压缩级别
                # 先尝试不同的颜色数量
                color_counts = [256, 128, 64, 32, 16, 8, 4]
                
                # 临时文件
                temp_output = os.path.join(os.path.dirname(input_path) or '.', f"temp_png_{os.path.basename(output_path)}")
                best_size = float('inf')
                best_output = None
                
                try:
                    for colors in color_counts:
                        # 复制图像
                        save_img = img.copy()
                        
                        # 量化颜色
                        if img.mode == 'RGBA':
                            # 对于RGBA图像，保留透明度
                            save_img = save_img.convert('P', palette=Image.ADAPTIVE, colors=colors)
                            # 确保透明度正确保留
                            if 'transparency' in img.info:
                                save_img.info['transparency'] = img.info['transparency']
                        else:
                            # 对于RGB图像，直接转换
                            save_img = save_img.convert('P', palette=Image.ADAPTIVE, colors=colors)
                        
                        # 保存并检查大小
                        save_img.save(temp_output, format='PNG', optimize=True, compress_level=9)
                        temp_size = os.path.getsize(temp_output)
                        
                        if min_size <= temp_size <= max_size:
                            # 符合要求
                            if best_output:
                                os.remove(best_output)
                            best_output = temp_output
                            break
                        
                        # 更新最佳结果
                        if abs(temp_size - target_size_bytes) < abs(best_size - target_size_bytes):
                            if best_output and best_output != temp_output:
                                os.remove(best_output)
                            best_size = temp_size
                            best_output = temp_output  # 直接引用临时文件，不需要复制
                    
                    # 如果找到了符合条件的文件
                    if best_output:
                        # 检查目标路径和最佳输出是否为同一个文件
                        try:
                            is_same_destination = os.path.samefile(best_output, output_path) if hasattr(os.path, 'samefile') else False
                        except OSError:
                            is_same_destination = False
                            
                        if not is_same_destination:
                            # 复制到最终路径
                            import shutil
                            shutil.copy2(best_output, output_path)
                    else:
                        # 如果没有找到完全符合条件的，转换为WebP格式
                        webp_output = output_path.replace('.png', '.webp')
                        self.compress(input_path, webp_output, quality=80, target_format='WEBP')
                        output_path = webp_output
                        
                finally:
                    # 清理临时文件
                    for file in [temp_output, best_output]:
                        if file and os.path.exists(file):
                            try:
                                os.remove(file)
                            except:
                                pass
                
            else:
                # 对于其他格式，转换为WebP或JPEG
                # 尝试AVIF（更好的压缩率），如果失败则尝试WebP
                try:
                    avif_output = output_path.rsplit('.', 1)[0] + '.avif'
                    self.compress(input_path, avif_output, quality=80, target_format='AVIF')
                    output_path = avif_output
                except:
                    # 回退到WebP
                    webp_output = output_path.rsplit('.', 1)[0] + '.webp'
                    self.compress(input_path, webp_output, quality=80, target_format='WEBP')
                    output_path = webp_output
                
        return output_path
    
    def get_image_info(self, image_path):
        """
        获取图像信息
        
        Args:
            image_path: 图像路径
            
        Returns:
            dict: 图像信息
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图像文件不存在: {image_path}")
        
        try:
            with Image.open(image_path) as img:
                info = {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height,
                    'file_size_kb': round(os.path.getsize(image_path) / 1024, 2)
                }
                return info
        except Exception as e:
            raise Exception(f"获取图像信息时出错: {str(e)}")
    
    def detect_format(self, image_path):
        """
        检测图像格式
        
        Args:
            image_path: 图像路径
            
        Returns:
            dict: 包含格式信息的字典
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图像文件不存在: {image_path}")
        
        try:
            # 首先通过文件扩展名初步判断
            _, ext = os.path.splitext(image_path.lower())
            detected_by_extension = None
            for format_name, info in self.supported_formats.items():
                if ext in info['extensions']:
                    detected_by_extension = format_name
                    break
            
            # 然后通过PIL库检测实际格式
            with Image.open(image_path) as img:
                actual_format = img.format.upper()
                # 处理别名
                if actual_format in self.format_aliases:
                    actual_format = self.format_aliases[actual_format]
                
                # 验证格式是否受支持
                is_supported = actual_format in self.supported_formats
                
                return {
                    'format': actual_format,
                    'detected_by_extension': detected_by_extension,
                    'is_supported': is_supported,
                    'mime_type': self.supported_formats.get(actual_format, {}).get('mime', 'unknown')
                }
                
        except IOError:
            # 如果PIL无法打开，尝试仅通过扩展名判断
            _, ext = os.path.splitext(image_path.lower())
            for format_name, info in self.supported_formats.items():
                if ext in info['extensions']:
                    return {
                        'format': format_name,
                        'detected_by_extension': format_name,
                        'is_supported': True,
                        'mime_type': info['mime'],
                        'warning': '无法通过PIL库验证图像格式，仅基于扩展名判断'
                    }
            raise Exception(f"无法识别图像格式: {image_path}")
        except Exception as e:
            raise Exception(f"检测图像格式时出错: {str(e)}")
    
    def convert_format(self, input_path, output_path, target_format):
        """
        转换图像格式
        
        Args:
            input_path: 输入图像路径
            output_path: 输出图像路径
            target_format: 目标格式
            
        Returns:
            str: 转换后的图像路径
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        
        # 标准化目标格式
        target_format = target_format.upper()
        
        # 处理格式别名
        if target_format in self.format_aliases:
            target_format = self.format_aliases[target_format]
        
        # 验证目标格式是否受支持
        if target_format not in self.supported_formats:
            supported_list = ', '.join(self.supported_formats.keys())
            raise ValueError(f"不支持的目标格式: {target_format}。支持的格式有: {supported_list}")
        
        # 更新输出文件扩展名
        base, _ = os.path.splitext(output_path)
        ext = self.supported_formats[target_format]['extensions'][0]
        output_path = f"{base}{ext}"
        
        try:
            with Image.open(input_path) as img:
                # 处理不同格式的特殊情况
                if target_format == 'JPEG':
                    # JPEG不支持透明度，需要处理RGBA图像
                    if img.mode == 'RGBA':
                        # 创建白色背景
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        # 粘贴图像，使用alpha通道作为蒙版
                        background.paste(img, mask=img.split()[3])
                        img = background
                    elif img.mode != 'RGB':
                        # 转换其他模式到RGB
                        img = img.convert('RGB')
                elif target_format == 'PNG':
                    # PNG支持透明度，保持模式
                    if img.mode == 'P':
                        # 转换调色板模式到RGBA以支持更好的透明度
                        img = img.convert('RGBA')
                elif target_format == 'WEBP':
                    # WebP也支持透明度
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                
                # 保存转换后的图像
                img.save(output_path, format=target_format, quality=self.default_quality, optimize=True)
                
                # 返回转换结果信息
                return output_path
                
        except Exception as e:
            raise Exception(f"转换图像格式时出错: {str(e)}")
    
    def is_valid_image(self, file_path):
        """
        验证文件是否为有效的图像
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否为有效图像
        """
        if not os.path.exists(file_path):
            return False
        
        try:
            with Image.open(file_path) as img:
                # 尝试加载图像数据
                img.verify()
                return True
        except:
            return False


# 模块级别便捷函数
def compress_image(input_path, output_path=None, quality=85, target_format=None):
    """
    模块级别的图像压缩便利函数
    
    Args:
        input_path: 输入图像路径
        output_path: 输出图像路径，默认为None
        quality: 压缩质量 (1-100)
        target_format: 目标格式
        
    Returns:
        str: 压缩后的图像路径
    """
    compressor = ImageCompressor()
    return compressor.compress(input_path, output_path, quality, target_format)


def compress_to_size(input_path, output_path=None, target_size_kb=20, tolerance_percent=5, tolerance=None, scale_factor=None, verbose=False):
    """
    压缩图像到指定大小的便捷函数
    
    Args:
        input_path: 输入图像路径
        output_path: 输出图像路径，默认为None
        target_size_kb: 目标文件大小（KB），默认为20KB
        tolerance_percent: 容差百分比，默认为5%
        tolerance: 容差百分比的别名，为兼容CLI使用
    
    Returns:
        str: 压缩后的图像路径
    """
    # 如果提供了tolerance参数，使用它代替tolerance_percent
    if tolerance is not None:
        tolerance_percent = tolerance
    
    compressor = ImageCompressor()
    return compressor.compress_to_size(input_path, output_path, target_size_kb, tolerance_percent, scale_factor, verbose)


def get_file_size_kb(file_path):
    """
    获取文件大小（KB）
    
    Args:
        file_path: 文件路径
        
    Returns:
        float: 文件大小（KB）
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    return round(os.path.getsize(file_path) / 1024, 2)