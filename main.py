"""
条形码和二维码生成器主程序入口
"""

import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from ui.main_window import MainWindow
from utils.logger import app_logger
from utils.file_handler import FileHandler
from utils.exception_handler import global_exception_handler


def setup_application():
    """
    设置应用程序
    
    Returns:
        QApplication: 应用程序实例
        
    Raises:
        RuntimeError: 应用程序创建失败
    """
    try:
        # 设置高DPI支持
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # 创建应用程序
        app = QApplication(sys.argv)
        app.setApplicationName("条形码和二维码生成器")
        app.setOrganizationName("SA Tools")
        
        app_logger.info("应用程序初始化完成")
        return app
        
    except Exception as e:
        app_logger.error(f"应用程序初始化失败: {str(e)}")
        raise RuntimeError(f"应用程序初始化失败: {str(e)}")


def check_dependencies():
    """
    检查依赖项
    
    Returns:
        Tuple[bool, str]: (是否成功, 错误信息)
    """
    try:
        missing_deps = []
        
        # 检查必要的库
        try:
            import PyQt5
            app_logger.debug("PyQt5 依赖检查通过")
        except ImportError:
            missing_deps.append("PyQt5")
            app_logger.warning("PyQt5 依赖缺失")
        
        try:
            import barcode
            app_logger.debug("python-barcode 依赖检查通过")
        except ImportError:
            missing_deps.append("python-barcode")
            app_logger.warning("python-barcode 依赖缺失")
        
        try:
            import qrcode
            app_logger.debug("qrcode 依赖检查通过")
        except ImportError:
            missing_deps.append("qrcode[pil]")
            app_logger.warning("qrcode 依赖缺失")
        
        try:
            import pandas
            app_logger.debug("pandas 依赖检查通过")
        except ImportError:
            missing_deps.append("pandas")
            app_logger.warning("pandas 依赖缺失")
        
        try:
            import PIL
            app_logger.debug("Pillow 依赖检查通过")
        except ImportError:
            missing_deps.append("Pillow")
            app_logger.warning("Pillow 依赖缺失")
        
        # 如果有缺失的依赖项，显示错误信息
        if missing_deps:
            error_msg = f"缺少以下依赖项: {', '.join(missing_deps)}\n\n"
            error_msg += "请使用以下命令安装:\n"
            error_msg += f"pip install {' '.join(missing_deps)}\n\n"
            error_msg += "或者安装所有依赖项:\n"
            error_msg += "pip install -r requirements.txt"
            
            app_logger.error(f"缺少依赖项: {', '.join(missing_deps)}")
            return False, error_msg
        
        app_logger.info("所有依赖项检查通过")
        return True, ""
        
    except Exception as e:
        error_msg = f"检查依赖项时发生错误: {str(e)}"
        app_logger.error(error_msg)
        return False, error_msg


def create_output_directories():
    """
    创建输出目录
    
    Returns:
        bool: 是否成功
    """
    try:
        output_dirs = [
            os.path.join(os.getcwd(), "output"),
            os.path.join(os.getcwd(), "output", "barcodes"),
            os.path.join(os.getcwd(), "output", "qrcodes"),
            os.path.join(os.getcwd(), "output", "temp")
        ]
        
        for dir_path in output_dirs:
            try:
                # 检查目录是否已存在
                if os.path.exists(dir_path):
                    if not os.path.isdir(dir_path):
                        app_logger.warning(f"路径存在但不是目录: {dir_path}")
                        continue
                    
                    # 检查目录是否可写
                    if not os.access(dir_path, os.W_OK):
                        app_logger.warning(f"目录不可写: {dir_path}")
                        continue
                    
                    app_logger.debug(f"目录已存在且可写: {dir_path}")
                    continue
                
                # 创建目录
                os.makedirs(dir_path, exist_ok=True)
                app_logger.info(f"创建输出目录: {dir_path}")
                
            except PermissionError:
                app_logger.error(f"没有权限创建目录: {dir_path}")
                return False
            except OSError as e:
                app_logger.error(f"创建目录失败: {dir_path}, 错误: {str(e)}")
                return False
        
        return True
        
    except Exception as e:
        app_logger.error(f"创建输出目录时发生错误: {str(e)}")
        return False


def handle_unexpected_exception(exc_type, exc_value, exc_traceback):
    """
    处理未捕获的异常
    
    Args:
        exc_type: 异常类型
        exc_value: 异常值
        exc_traceback: 异常回溯
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # 允许Ctrl+C正常退出
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # 记录异常信息
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    app_logger.critical(f"未捕获的异常: {error_msg}")
    
    # 显示错误对话框
    try:
        QMessageBox.critical(
            None, 
            "程序错误", 
            f"程序遇到未预期的错误:\n\n{str(exc_value)}\n\n详细信息已记录到日志文件。"
        )
    except:
        # 如果无法显示错误对话框，至少打印到控制台
        print(f"未捕获的异常: {exc_type.__name__}: {exc_value}")


def main():
    """
    主函数
    
    Returns:
        int: 退出代码
    """
    try:
        # 设置全局异常处理器
        sys.excepthook = handle_unexpected_exception
        
        app_logger.info("=" * 50)
        app_logger.info("应用程序启动")
        app_logger.info("=" * 50)
        
        # 设置应用程序
        app = setup_application()
        
        # 检查依赖项
        deps_ok, error_msg = check_dependencies()
        if not deps_ok:
            try:
                QMessageBox.critical(None, "依赖项错误", error_msg)
            except:
                print(f"依赖项错误: {error_msg}")
            return 1
        
        # 创建输出目录
        dirs_ok = create_output_directories()
        if not dirs_ok:
            error_msg = "创建输出目录失败，请检查权限设置"
            try:
                QMessageBox.critical(None, "目录创建错误", error_msg)
            except:
                print(f"目录创建错误: {error_msg}")
            return 1
        
        # 创建并显示主窗口
        try:
            main_window = MainWindow()
            main_window.show()
            app_logger.info("主窗口创建并显示成功")
        except Exception as e:
            error_msg = f"创建主窗口失败: {str(e)}"
            app_logger.error(error_msg)
            try:
                QMessageBox.critical(None, "窗口创建错误", error_msg)
            except:
                print(f"窗口创建错误: {error_msg}")
            return 1
        
        app_logger.info("应用程序启动成功")
        
        # 运行应用程序
        try:
            exit_code = app.exec_()
            app_logger.info(f"应用程序退出，退出代码: {exit_code}")
            return exit_code
        except Exception as e:
            error_msg = f"运行应用程序时发生错误: {str(e)}"
            app_logger.error(error_msg)
            try:
                QMessageBox.critical(None, "运行时错误", error_msg)
            except:
                print(f"运行时错误: {error_msg}")
            return 1
    
    except Exception as e:
        error_msg = f"应用程序启动失败: {str(e)}"
        app_logger.error(error_msg)
        try:
            QMessageBox.critical(None, "启动错误", error_msg)
        except:
            print(f"启动错误: {error_msg}")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"程序退出时发生错误: {str(e)}")
        sys.exit(1)