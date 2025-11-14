"""
主窗口界面模块
提供应用程序的主界面
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTabWidget, QMenuBar, QStatusBar, 
                            QAction, QMessageBox, QFileDialog, QLabel, 
                            QPushButton, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
from ui.barcode_tab import BarcodeTab
from ui.qrcode_tab import QRCodeTab
from ui.batch_tab import BatchTab
from utils.logger import app_logger


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("条形码和二维码生成器")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        # 初始化UI
        try:
            self.init_ui()
            app_logger.info("主窗口初始化成功")
        except Exception as e:
            app_logger.error(f"主窗口初始化失败: {str(e)}")
            QMessageBox.critical(self, "初始化错误", f"主窗口初始化失败: {str(e)}")
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建标题标签
        title_label = QLabel("条形码和二维码生成器")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # 创建分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)
        
        # 创建选项卡部件
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        # 创建各个选项卡
        self.barcode_tab = BarcodeTab()
        self.qrcode_tab = QRCodeTab()
        self.batch_tab = BatchTab()
        
        # 添加选项卡
        self.tab_widget.addTab(self.barcode_tab, "条形码")
        self.tab_widget.addTab(self.qrcode_tab, "二维码")
        self.tab_widget.addTab(self.batch_tab, "批量生成")
        
        main_layout.addWidget(self.tab_widget)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建状态栏
        self.create_status_bar()
        
        # 连接信号和槽
        self.connect_signals()
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        # 退出动作
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("退出应用程序")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        # 关于动作
        about_action = QAction("关于(&A)", self)
        about_action.setStatusTip("关于本应用程序")
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def connect_signals(self):
        """连接信号和槽"""
        # 选项卡切换时更新状态栏
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # 连接各选项卡的状态更新信号
        self.barcode_tab.status_updated.connect(self.update_status)
        self.qrcode_tab.status_updated.connect(self.update_status)
        self.batch_tab.status_updated.connect(self.update_status)
    
    def on_tab_changed(self, index):
        """选项卡切换时的处理"""
        tab_names = ["条形码", "二维码", "批量生成"]
        if 0 <= index < len(tab_names):
            self.status_bar.showMessage(f"当前选项卡: {tab_names[index]}")
    
    def update_status(self, message):
        """更新状态栏消息"""
        self.status_bar.showMessage(message)
    
    def show_about_dialog(self):
        """显示关于对话框"""
        try:
            about_text = """
            <h2>条形码和二维码生成器</h2>
            <p>版本: 1.0.0</p>
            <p>一个基于Python的Windows客户端应用程序，用于生成各种类型的条形码和二维码。</p>
            <p>支持的功能:</p>
            <ul>
                <li>多种条形码编码格式</li>
                <li>二维码生成</li>
                <li>批量生成功能</li>
                <li>自定义样式和尺寸</li>
            </ul>
            <p>Copyright © 2023</p>
            """
            QMessageBox.about(self, "关于", about_text)
            app_logger.info("显示关于对话框")
        except Exception as e:
            app_logger.error(f"显示关于对话框失败: {str(e)}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        reply = QMessageBox.question(
            self, '确认退出', 
            '确定要退出应用程序吗？',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            app_logger.info("应用程序正常退出")
            event.accept()
        else:
            event.ignore()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())