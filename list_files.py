#!/usr/bin/env python3
"""
文件信息列表脚本
列出指定目录下所有文件的详细信息，包括文件名、大小、修改时间、权限等
"""

import os
import stat
import time
from pathlib import Path
import argparse


def format_size(size_bytes):
    """格式化文件大小显示"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"


def format_permissions(mode):
    """格式化文件权限显示"""
    permissions = stat.filemode(mode)
    return permissions


def get_file_info(file_path):
    """获取文件的详细信息"""
    try:
        file_stat = os.stat(file_path)
        
        # 基本信息
        name = os.path.basename(file_path)
        full_path = os.path.abspath(file_path)
        size = file_stat.st_size
        size_formatted = format_size(size)
        
        # 时间信息
        modified_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stat.st_mtime))
        created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stat.st_ctime))
        accessed_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stat.st_atime))
        
        # 权限信息
        permissions = format_permissions(file_stat.st_mode)
        
        # 文件类型
        if os.path.isfile(file_path):
            file_type = "文件"
        elif os.path.isdir(file_path):
            file_type = "目录"
        elif os.path.islink(file_path):
            file_type = "符号链接"
        else:
            file_type = "其他"
        
        return {
            'name': name,
            'full_path': full_path,
            'type': file_type,
            'size': size,
            'size_formatted': size_formatted,
            'permissions': permissions,
            'modified_time': modified_time,
            'created_time': created_time,
            'accessed_time': accessed_time
        }
    
    except (OSError, IOError) as e:
        return {
            'name': os.path.basename(file_path),
            'full_path': os.path.abspath(file_path),
            'error': str(e)
        }


def list_directory_files(directory_path, include_hidden=False, recursive=True):
    """列出目录下的所有文件信息"""
    files_info = []
    
    try:
        if recursive:
            # 递归遍历所有子目录
            for root, dirs, files in os.walk(directory_path):
                # 处理目录
                for dir_name in dirs:
                    if not include_hidden and dir_name.startswith('.'):
                        continue
                    dir_path = os.path.join(root, dir_name)
                    files_info.append(get_file_info(dir_path))
                
                # 处理文件
                for file_name in files:
                    if not include_hidden and file_name.startswith('.'):
                        continue
                    file_path = os.path.join(root, file_name)
                    files_info.append(get_file_info(file_path))
        else:
            # 只遍历当前目录
            for item in os.listdir(directory_path):
                if not include_hidden and item.startswith('.'):
                    continue
                item_path = os.path.join(directory_path, item)
                files_info.append(get_file_info(item_path))
    
    except (OSError, IOError) as e:
        print(f"错误：无法访问目录 {directory_path}: {e}")
        return []
    
    return files_info


def save_to_file(files_info, output_file):
    """将文件信息保存到txt文件"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("文件信息列表\n")
            f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # 统计信息
            total_files = sum(1 for info in files_info if info.get('type') == '文件')
            total_dirs = sum(1 for info in files_info if info.get('type') == '目录')
            total_size = sum(info.get('size', 0) for info in files_info if info.get('type') == '文件')
            
            f.write(f"统计信息:\n")
            f.write(f"  总文件数: {total_files}\n")
            f.write(f"  总目录数: {total_dirs}\n")
            f.write(f"  总大小: {format_size(total_size)}\n\n")
            
            f.write("-" * 80 + "\n")
            f.write("详细信息:\n")
            f.write("-" * 80 + "\n\n")
            
            # 按类型和名称排序
            files_info.sort(key=lambda x: (x.get('type', ''), x.get('name', '').lower()))
            
            for i, info in enumerate(files_info, 1):
                if 'error' in info:
                    f.write(f"{i:4d}. 【错误】 {info['name']}\n")
                    f.write(f"      路径: {info['full_path']}\n")
                    f.write(f"      错误: {info['error']}\n\n")
                else:
                    f.write(f"{i:4d}. 【{info['type']}】 {info['name']}\n")
                    f.write(f"      路径: {info['full_path']}\n")
                    f.write(f"      大小: {info['size_formatted']}\n")
                    f.write(f"      权限: {info['permissions']}\n")
                    f.write(f"      修改时间: {info['modified_time']}\n")
                    f.write(f"      创建时间: {info['created_time']}\n")
                    f.write(f"      访问时间: {info['accessed_time']}\n\n")
        
        print(f"文件信息已保存到: {output_file}")
        return True
    
    except (OSError, IOError) as e:
        print(f"错误：无法保存文件 {output_file}: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='列出目录下所有文件的详细信息')
    parser.add_argument('directory', nargs='?', default='.', 
                       help='要扫描的目录路径 (默认: 当前目录)')
    parser.add_argument('-o', '--output', default='files_info.txt',
                       help='输出文件名 (默认: files_info.txt)')
    parser.add_argument('--include-hidden', action='store_true',
                       help='包含隐藏文件和目录')
    parser.add_argument('--no-recursive', action='store_true',
                       help='不递归扫描子目录')
    
    args = parser.parse_args()
    
    # 检查目录是否存在
    if not os.path.exists(args.directory):
        print(f"错误：目录 '{args.directory}' 不存在")
        return 1
    
    if not os.path.isdir(args.directory):
        print(f"错误：'{args.directory}' 不是一个目录")
        return 1
    
    print(f"正在扫描目录: {os.path.abspath(args.directory)}")
    print(f"递归扫描: {'否' if args.no_recursive else '是'}")
    print(f"包含隐藏文件: {'是' if args.include_hidden else '否'}")
    print("扫描中...")
    
    # 获取文件信息
    files_info = list_directory_files(
        args.directory, 
        include_hidden=args.include_hidden,
        recursive=not args.no_recursive
    )
    
    if not files_info:
        print("未找到任何文件")
        return 1
    
    print(f"找到 {len(files_info)} 个项目")
    
    # 保存到文件
    if save_to_file(files_info, args.output):
        print("完成！")
        return 0
    else:
        return 1


if __name__ == '__main__':
    exit(main())