"""
CLI包初始化文件
"""

from .main import main, parse_arguments, process_single_image, process_directory

__all__ = ['main', 'parse_arguments', 'process_single_image', 'process_directory']
__version__ = '1.0.0'