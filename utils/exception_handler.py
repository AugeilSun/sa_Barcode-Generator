"""
全局异常处理模块
提供全局异常捕获和处理功能
"""

import sys
import traceback
from PyQt5.QtWidgets import QMessageBox
from utils.logger import app_logger


class GlobalExceptionHandler:
    """全局异常处理器"""
    
    def __init__(self):
        """初始化全局异常处理器"""
        # 安装异常钩子
        sys.excepthook = self.handle_exception
        
        app_logger.info("全局异常处理器已安装")
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """
        处理未捕获的异常
        
        Args:
            exc_type: 异常类型
            exc_value: 异常值
            exc_traceback: 异常回溯信息
        """
        # 记录异常信息到日志
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        app_logger.error(f"未捕获的异常:\n{error_msg}")
        
        # 显示错误对话框
        self.show_error_dialog(exc_type.__name__, str(exc_value))
    
    def show_error_dialog(self, error_type, error_message):
        """
        显示错误对话框
        
        Args:
            error_type: 错误类型
            error_message: 错误消息
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("程序错误")
        msg_box.setText(f"程序发生了一个未处理的错误:\n\n错误类型: {error_type}\n错误信息: {error_message}")
        msg_box.setInformativeText("程序将继续运行，但某些功能可能无法正常工作。")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


# 创建全局异常处理器实例
global_exception_handler = GlobalExceptionHandler()