"""
文件处理工具模块
提供文件读写、路径处理等功能
"""

import os
import csv
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from .logger import app_logger


class FileHandler:
    """文件处理工具类"""
    
    @staticmethod
    def ensure_dir_exists(dir_path: str) -> bool:
        """
        确保目录存在，如果不存在则创建
        
        Args:
            dir_path (str): 目录路径
            
        Returns:
            bool: 操作是否成功
        """
        try:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                app_logger.info(f"创建目录: {dir_path}")
            return True
        except Exception as e:
            app_logger.error(f"创建目录失败: {dir_path}, 错误: {str(e)}")
            return False
    
    @staticmethod
    def save_file(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """
        保存文本内容到文件
        
        Args:
            file_path (str): 文件路径
            content (str): 文件内容
            encoding (str): 文件编码，默认为utf-8
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 确保目录存在
            dir_path = os.path.dirname(file_path)
            if dir_path and not FileHandler.ensure_dir_exists(dir_path):
                return False
                
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            app_logger.info(f"文件保存成功: {file_path}")
            return True
        except Exception as e:
            app_logger.error(f"文件保存失败: {file_path}, 错误: {str(e)}")
            return False
    
    @staticmethod
    def read_file(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        读取文件内容
        
        Args:
            file_path (str): 文件路径
            encoding (str): 文件编码，默认为utf-8
            
        Returns:
            Optional[str]: 文件内容，如果失败则返回None
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            app_logger.info(f"文件读取成功: {file_path}")
            return content
        except Exception as e:
            app_logger.error(f"文件读取失败: {file_path}, 错误: {str(e)}")
            return None
    
    @staticmethod
    def read_csv(file_path: str, delimiter: str = ',', encoding: str = 'utf-8') -> Optional[List[Dict[str, Any]]]:
        """
        读取CSV文件
        
        Args:
            file_path (str): 文件路径
            delimiter (str): 分隔符，默认为逗号
            encoding (str): 文件编码，默认为utf-8
            
        Returns:
            Optional[List[Dict[str, Any]]]: CSV数据，如果失败则返回None
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                data = list(reader)
            app_logger.info(f"CSV文件读取成功: {file_path}, 记录数: {len(data)}")
            return data
        except Exception as e:
            app_logger.error(f"CSV文件读取失败: {file_path}, 错误: {str(e)}")
            return None
    
    @staticmethod
    def save_csv(file_path: str, data: List[Dict[str, Any]], fieldnames: List[str] = None, 
                 delimiter: str = ',', encoding: str = 'utf-8') -> bool:
        """
        保存数据到CSV文件
        
        Args:
            file_path (str): 文件路径
            data (List[Dict[str, Any]]): 要保存的数据
            fieldnames (List[str]): 字段名列表，如果为None则使用第一行数据的键
            delimiter (str): 分隔符，默认为逗号
            encoding (str): 文件编码，默认为utf-8
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 确保目录存在
            dir_path = os.path.dirname(file_path)
            if dir_path and not FileHandler.ensure_dir_exists(dir_path):
                return False
                
            # 如果没有提供字段名，使用第一行数据的键
            if not fieldnames and data:
                fieldnames = list(data[0].keys())
                
            with open(file_path, 'w', newline='', encoding=encoding) as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(data)
            app_logger.info(f"CSV文件保存成功: {file_path}, 记录数: {len(data)}")
            return True
        except Exception as e:
            app_logger.error(f"CSV文件保存失败: {file_path}, 错误: {str(e)}")
            return False
    
    @staticmethod
    def get_unique_filename(base_path: str, extension: str = '') -> str:
        """
        生成唯一的文件名，避免覆盖现有文件
        
        Args:
            base_path (str): 基础文件路径（不含扩展名）
            extension (str): 文件扩展名
            
        Returns:
            str: 唯一的文件路径
        """
        if extension and not extension.startswith('.'):
            extension = '.' + extension
            
        file_path = base_path + extension
        counter = 1
        
        while os.path.exists(file_path):
            file_path = f"{base_path}_{counter}{extension}"
            counter += 1
            
        return file_path
    
    @staticmethod
    def get_timestamp_filename(prefix: str = '', extension: str = '') -> str:
        """
        生成带时间戳的文件名
        
        Args:
            prefix (str): 文件名前缀
            extension (str): 文件扩展名
            
        Returns:
            str: 带时间戳的文件名
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if extension and not extension.startswith('.'):
            extension = '.' + extension
            
        return f"{prefix}_{timestamp}{extension}" if prefix else f"{timestamp}{extension}"