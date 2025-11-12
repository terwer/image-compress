#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def parse_arguments(argv=None):
    parser = argparse.ArgumentParser(
        prog='image-compress',
        description='高性能图像压缩工具，支持多种格式'
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
                        help='目标文件大小（KB），启用指定大小压缩模式')
    parser.add_argument('-t', '--tolerance', type=float, default=5,
                        help='指定大小压缩的容差百分比（默认5%%）')
    
    # 其他选项
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='递归处理子目录')
    parser.add_argument('--verbose', action='store_true',
                        help='显示详细信息')
    
    return parser.parse_args(argv)

def main():
    try:
        # 解析参数
        args = parse_arguments()
        print("参数解析成功!")
        
    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()