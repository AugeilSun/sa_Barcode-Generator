"""
日志记录工具模块
提供应用程序的日志记录功能
"""

import logging
import os
from datetime import datetime


class Logger:
    """日志记录器类，提供统一的日志记录接口"""
    
    def __init__(self, name="BarcodeGenerator", log_level=logging.INFO):
        """
        初始化日志记录器
        
        Args:
            name (str): 日志记录器名称
            log_level (int): 日志级别
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 创建日志目录
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            # 创建文件处理器
            log_file = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(log_level)
            
            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            
            # 创建格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            # 设置格式化器
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加处理器
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def debug(self, message):
        """记录调试信息"""
        self.logger.debug(message)
    
    def info(self, message):
        """记录一般信息"""
        self.logger.info(message)
    
    def warning(self, message):
        """记录警告信息"""
        self.logger.warning(message)
    
    def error(self, message):
        """记录错误信息"""
        self.logger.error(message)
    
    def critical(self, message):
        """记录严重错误信息"""
        self.logger.critical(message)
    
    def exception(self, message):
        """记录异常信息，包含堆栈跟踪"""
        self.logger.exception(message)


# 创建全局日志记录器实例
app_logger = Logger("BarcodeGenerator")