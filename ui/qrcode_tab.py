"""
二维码生成界面模块
提供二维码生成的用户界面
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLabel, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
                            QPushButton, QCheckBox, QColorDialog, QFileDialog,
                            QGroupBox, QGridLayout, QTextEdit, QScrollArea,
                            QFrame, QSizePolicy, QSlider)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QFont, QColor
from PIL import Image
from core.qrcode_generator import QRCodeGenerator
from utils.logger import app_logger
from utils.file_handler import FileHandler


class QRCodeTab(QWidget):
    """二维码生成选项卡"""
    
    # 定义信号
    status_updated = pyqtSignal(str)
    
    def __init__(self):
        """初始化二维码选项卡"""
        super().__init__()
        
        # 初始化二维码生成器
        self.qrcode_generator = QRCodeGenerator()
        
        # 当前二维码图像
        self.current_qrcode_image = None
        
        # 初始化UI
        self.init_ui()
        
        app_logger.info("二维码选项卡初始化完成")
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 创建内容部件
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # 基本设置组
        basic_group = self.create_basic_settings_group()
        content_layout.addWidget(basic_group)
        
        # 颜色设置组
        color_group = self.create_color_settings_group()
        content_layout.addWidget(color_group)
        
        # Logo设置组
        logo_group = self.create_logo_settings_group()
        content_layout.addWidget(logo_group)
        
        # 文本设置组
        text_group = self.create_text_settings_group()
        content_layout.addWidget(text_group)
        
        # 预览和操作组
        preview_action_group = self.create_preview_action_group()
        content_layout.addWidget(preview_action_group)
        
        # 设置滚动区域的内容
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # 初始化二维码生成器
        from core.qrcode_generator import QRCodeGenerator
        self.qrcode_generator = QRCodeGenerator()
    
    def create_basic_settings_group(self):
        """创建基本设置组"""
        group = QGroupBox("基本设置")
        layout = QFormLayout(group)
        
        # 二维码数据输入
        self.data_input = QLineEdit()
        self.data_input.setPlaceholderText("请输入二维码数据")
        layout.addRow("二维码数据:", self.data_input)
        
        # 版本选择
        self.version_spin = QSpinBox()
        self.version_spin.setRange(1, 40)
        self.version_spin.setValue(1)
        self.version_spin.setToolTip("控制二维码的大小，1是最小的，40是最大的")
        layout.addRow("版本:", self.version_spin)
        
        # 纠错级别选择
        self.error_correction_combo = QComboBox()
        for code, info in QRCodeGenerator.ERROR_CORRECTION_LEVELS.items():
            self.error_correction_combo.addItem(f"{info['name']} - {info['description']}", code)
        layout.addRow("纠错级别:", self.error_correction_combo)
        
        # 模块大小
        self.box_size_spin = QSpinBox()
        self.box_size_spin.setRange(1, 50)
        self.box_size_spin.setValue(10)
        layout.addRow("模块大小:", self.box_size_spin)
        
        # 边框大小
        self.border_spin = QSpinBox()
        self.border_spin.setRange(0, 20)
        self.border_spin.setValue(4)
        layout.addRow("边框大小:", self.border_spin)
        
        return group
    
    def create_color_settings_group(self):
        """创建颜色设置组"""
        group = QGroupBox("颜色设置")
        layout = QGridLayout(group)
        
        # 前景色
        self.foreground_color_btn = QPushButton("选择前景色")
        self.foreground_color_btn.clicked.connect(self.choose_foreground_color)
        self.foreground_color_label = QLabel("黑色")
        self.foreground_color = QColor(0, 0, 0)
        layout.addWidget(QLabel("前景色:"), 0, 0)
        layout.addWidget(self.foreground_color_btn, 0, 1)
        layout.addWidget(self.foreground_color_label, 0, 2)
        
        # 背景色
        self.background_color_btn = QPushButton("选择背景色")
        self.background_color_btn.clicked.connect(self.choose_background_color)
        self.background_color_label = QLabel("白色")
        self.background_color = QColor(255, 255, 255)
        layout.addWidget(QLabel("背景色:"), 1, 0)
        layout.addWidget(self.background_color_btn, 1, 1)
        layout.addWidget(self.background_color_label, 1, 2)
        
        return group
    
    def create_logo_settings_group(self):
        """创建Logo设置组"""
        group = QGroupBox("Logo设置")
        layout = QGridLayout(group)
        
        # 添加Logo复选框
        self.add_logo_checkbox = QCheckBox("添加Logo")
        self.add_logo_checkbox.toggled.connect(self.on_add_logo_toggled)
        layout.addWidget(self.add_logo_checkbox, 0, 0, 1, 2)
        
        # Logo路径
        self.logo_path_input = QLineEdit()
        self.logo_path_input.setPlaceholderText("Logo文件路径")
        self.logo_path_input.setEnabled(False)
        layout.addWidget(QLabel("Logo路径:"), 1, 0)
        layout.addWidget(self.logo_path_input, 1, 1)
        
        # 浏览按钮
        self.browse_logo_btn = QPushButton("浏览")
        self.browse_logo_btn.clicked.connect(self.browse_logo)
        self.browse_logo_btn.setEnabled(False)
        layout.addWidget(self.browse_logo_btn, 1, 2)
        
        # Logo大小
        self.logo_size_spin = QSpinBox()
        self.logo_size_spin.setRange(10, 200)
        self.logo_size_spin.setValue(100)
        self.logo_size_spin.setEnabled(False)
        layout.addWidget(QLabel("Logo大小:"), 2, 0)
        layout.addWidget(self.logo_size_spin, 2, 1)
        
        return group
    
    def create_text_settings_group(self):
        """创建文本设置组"""
        group = QGroupBox("文本设置")
        layout = QGridLayout(group)
        
        # 添加文本复选框
        self.add_text_checkbox = QCheckBox("添加文本")
        self.add_text_checkbox.toggled.connect(self.on_add_text_toggled)
        layout.addWidget(self.add_text_checkbox, 0, 0, 1, 2)
        
        # 文本内容
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("要添加的文本")
        self.text_input.setEnabled(False)
        layout.addWidget(QLabel("文本内容:"), 1, 0)
        layout.addWidget(self.text_input, 1, 1)
        
        # 文本位置
        self.text_position_combo = QComboBox()
        self.text_position_combo.addItems(["顶部", "底部"])
        self.text_position_combo.setEnabled(False)
        layout.addWidget(QLabel("文本位置:"), 2, 0)
        layout.addWidget(self.text_position_combo, 2, 1)
        
        # 文本字体大小
        self.text_font_size_spin = QSpinBox()
        self.text_font_size_spin.setRange(8, 30)
        self.text_font_size_spin.setValue(12)
        self.text_font_size_spin.setEnabled(False)
        layout.addWidget(QLabel("字体大小:"), 3, 0)
        layout.addWidget(self.text_font_size_spin, 3, 1)
        
        # 文本颜色
        self.text_color_btn = QPushButton("选择文本颜色")
        self.text_color_btn.clicked.connect(self.choose_text_color)
        self.text_color_btn.setEnabled(False)
        self.text_color_label = QLabel("黑色")
        self.text_color = QColor(0, 0, 0)
        layout.addWidget(QLabel("文本颜色:"), 4, 0)
        layout.addWidget(self.text_color_btn, 4, 1)
        layout.addWidget(self.text_color_label, 4, 2)
        
        return group
    
    def create_preview_action_group(self):
        """创建预览和操作组"""
        group = QGroupBox("预览和操作")
        layout = QVBoxLayout(group)
        
        # 创建预览标签
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(300, 300)
        self.preview_label.setStyleSheet("border: 1px solid #ccc;")
        self.preview_label.setText("请输入数据并点击生成按钮")
        layout.addWidget(self.preview_label)
        
        # 二维码信息
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(100)
        layout.addWidget(QLabel("二维码信息:"))
        layout.addWidget(self.info_text)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("生成二维码")
        self.generate_btn.clicked.connect(self.generate_qrcode)
        button_layout.addWidget(self.generate_btn)
        
        self.save_btn = QPushButton("保存二维码")
        self.save_btn.clicked.connect(self.save_qrcode)
        self.save_btn.setEnabled(False)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        return group

    def create_input_panel(self):
        """创建输入面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 基本设置组
        basic_group = QGroupBox("基本设置")
        basic_layout = QFormLayout(basic_group)
        
        # 二维码数据输入
        self.data_input = QLineEdit()
        self.data_input.setPlaceholderText("请输入二维码数据")
        basic_layout.addRow("二维码数据:", self.data_input)
        
        # 版本选择
        self.version_spin = QSpinBox()
        self.version_spin.setRange(1, 40)
        self.version_spin.setValue(1)
        self.version_spin.setToolTip("控制二维码的大小，1是最小的，40是最大的")
        basic_layout.addRow("版本:", self.version_spin)
        
        # 纠错级别选择
        self.error_correction_combo = QComboBox()
        for code, info in QRCodeGenerator.ERROR_CORRECTION_LEVELS.items():
            self.error_correction_combo.addItem(f"{info['name']} - {info['description']}", code)
        basic_layout.addRow("纠错级别:", self.error_correction_combo)
        
        # 模块大小
        self.box_size_spin = QSpinBox()
        self.box_size_spin.setRange(1, 50)
        self.box_size_spin.setValue(10)
        basic_layout.addRow("模块大小:", self.box_size_spin)
        
        # 边框大小
        self.border_spin = QSpinBox()
        self.border_spin.setRange(0, 20)
        self.border_spin.setValue(4)
        basic_layout.addRow("边框大小:", self.border_spin)
        
        layout.addWidget(basic_group)
        
        # 颜色设置组
        color_group = QGroupBox("颜色设置")
        color_layout = QGridLayout(color_group)
        
        # 前景色
        self.foreground_color_btn = QPushButton("选择前景色")
        self.foreground_color_btn.clicked.connect(self.choose_foreground_color)
        self.foreground_color_label = QLabel("黑色")
        self.foreground_color = QColor(0, 0, 0)
        color_layout.addWidget(QLabel("前景色:"), 0, 0)
        color_layout.addWidget(self.foreground_color_btn, 0, 1)
        color_layout.addWidget(self.foreground_color_label, 0, 2)
        
        # 背景色
        self.background_color_btn = QPushButton("选择背景色")
        self.background_color_btn.clicked.connect(self.choose_background_color)
        self.background_color_label = QLabel("白色")
        self.background_color = QColor(255, 255, 255)
        color_layout.addWidget(QLabel("背景色:"), 1, 0)
        color_layout.addWidget(self.background_color_btn, 1, 1)
        color_layout.addWidget(self.background_color_label, 1, 2)
        
        layout.addWidget(color_group)
        
        # Logo设置组
        logo_group = QGroupBox("Logo设置")
        logo_layout = QGridLayout(logo_group)
        
        # 添加Logo复选框
        self.add_logo_checkbox = QCheckBox("添加Logo")
        self.add_logo_checkbox.toggled.connect(self.on_add_logo_toggled)
        logo_layout.addWidget(self.add_logo_checkbox, 0, 0, 1, 2)
        
        # Logo路径
        self.logo_path_input = QLineEdit()
        self.logo_path_input.setPlaceholderText("Logo文件路径")
        self.logo_path_input.setEnabled(False)
        logo_layout.addWidget(QLabel("Logo路径:"), 1, 0)
        logo_layout.addWidget(self.logo_path_input, 1, 1)
        
        # 浏览按钮
        self.browse_logo_btn = QPushButton("浏览")
        self.browse_logo_btn.clicked.connect(self.browse_logo)
        self.browse_logo_btn.setEnabled(False)
        logo_layout.addWidget(self.browse_logo_btn, 1, 2)
        
        # Logo大小
        self.logo_size_spin = QSpinBox()
        self.logo_size_spin.setRange(10, 200)
        self.logo_size_spin.setValue(100)
        self.logo_size_spin.setEnabled(False)
        logo_layout.addWidget(QLabel("Logo大小:"), 2, 0)
        logo_layout.addWidget(self.logo_size_spin, 2, 1)
        
        layout.addWidget(logo_group)
        
        # 文本设置组
        text_group = QGroupBox("文本设置")
        text_layout = QGridLayout(text_group)
        
        # 添加文本复选框
        self.add_text_checkbox = QCheckBox("添加文本")
        self.add_text_checkbox.toggled.connect(self.on_add_text_toggled)
        text_layout.addWidget(self.add_text_checkbox, 0, 0, 1, 2)
        
        # 文本内容
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("要添加的文本")
        self.text_input.setEnabled(False)
        text_layout.addWidget(QLabel("文本内容:"), 1, 0)
        text_layout.addWidget(self.text_input, 1, 1)
        
        # 文本位置
        self.text_position_combo = QComboBox()
        self.text_position_combo.addItems(["顶部", "底部"])
        self.text_position_combo.setEnabled(False)
        text_layout.addWidget(QLabel("文本位置:"), 2, 0)
        text_layout.addWidget(self.text_position_combo, 2, 1)
        
        # 文本字体大小
        self.text_font_size_spin = QSpinBox()
        self.text_font_size_spin.setRange(8, 30)
        self.text_font_size_spin.setValue(12)
        self.text_font_size_spin.setEnabled(False)
        text_layout.addWidget(QLabel("字体大小:"), 3, 0)
        text_layout.addWidget(self.text_font_size_spin, 3, 1)
        
        # 文本颜色
        self.text_color_btn = QPushButton("选择文本颜色")
        self.text_color_btn.clicked.connect(self.choose_text_color)
        self.text_color_btn.setEnabled(False)
        self.text_color_label = QLabel("黑色")
        self.text_color = QColor(0, 0, 0)
        text_layout.addWidget(QLabel("文本颜色:"), 4, 0)
        text_layout.addWidget(self.text_color_btn, 4, 1)
        text_layout.addWidget(self.text_color_label, 4, 2)
        
        layout.addWidget(text_group)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("生成二维码")
        self.generate_btn.clicked.connect(self.generate_qrcode)
        button_layout.addWidget(self.generate_btn)
        
        self.save_btn = QPushButton("保存二维码")
        self.save_btn.clicked.connect(self.save_qrcode)
        self.save_btn.setEnabled(False)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        # 添加弹性空间
        layout.addStretch()
        
        return panel
    
    def create_preview_panel(self):
        """创建预览面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 预览标题
        preview_label = QLabel("预览")
        preview_label.setFont(QFont("", 12, QFont.Bold))
        layout.addWidget(preview_label)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 创建预览标签
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(300, 300)
        self.preview_label.setStyleSheet("border: 1px solid #ccc;")
        self.preview_label.setText("请输入数据并点击生成按钮")
        
        scroll_area.setWidget(self.preview_label)
        layout.addWidget(scroll_area)
        
        # 二维码信息
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(100)
        layout.addWidget(QLabel("二维码信息:"))
        layout.addWidget(self.info_text)
        
        return panel
    
    def on_add_logo_toggled(self, checked):
        """添加Logo复选框状态改变"""
        self.logo_path_input.setEnabled(checked)
        self.browse_logo_btn.setEnabled(checked)
        self.logo_size_spin.setEnabled(checked)
    
    def on_add_text_toggled(self, checked):
        """添加文本复选框状态改变"""
        self.text_input.setEnabled(checked)
        self.text_position_combo.setEnabled(checked)
        self.text_font_size_spin.setEnabled(checked)
        self.text_color_btn.setEnabled(checked)
    
    def choose_foreground_color(self):
        """选择前景色"""
        color = QColorDialog.getColor(self.foreground_color, self, "选择前景色")
        if color.isValid():
            self.foreground_color = color
            self.foreground_color_label.setText(color.name())
    
    def choose_background_color(self):
        """选择背景色"""
        color = QColorDialog.getColor(self.background_color, self, "选择背景色")
        if color.isValid():
            self.background_color = color
            self.background_color_label.setText(color.name())
    
    def choose_text_color(self):
        """选择文本颜色"""
        color = QColorDialog.getColor(self.text_color, self, "选择文本颜色")
        if color.isValid():
            self.text_color = color
            self.text_color_label.setText(color.name())
    
    def browse_logo(self):
        """浏览Logo文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择Logo文件",
            os.getcwd(),
            "图像文件 (*.png *.jpg *.jpeg *.bmp *.gif);;所有文件 (*)"
        )
        
        if file_path:
            self.logo_path_input.setText(file_path)
    
    def get_qrcode_options(self):
        """获取二维码生成选项"""
        # 获取纠错级别
        error_correction_code = self.error_correction_combo.currentData()
        error_correction = QRCodeGenerator.ERROR_CORRECTION_LEVELS[error_correction_code]['value']
        
        options = {
            'version': self.version_spin.value(),
            'error_correction': error_correction,
            'box_size': self.box_size_spin.value(),
            'border': self.border_spin.value(),
            'fill_color': self.foreground_color.name(),
            'back_color': self.background_color.name(),
        }
        
        # Logo设置
        if self.add_logo_checkbox.isChecked():
            options['add_logo'] = True
            options['logo_path'] = self.logo_path_input.text()
            options['logo_size'] = (self.logo_size_spin.value(), self.logo_size_spin.value())
        else:
            options['add_logo'] = False
        
        # 文本设置
        if self.add_text_checkbox.isChecked():
            options['add_text'] = True
            options['text'] = self.text_input.text()
            options['text_position'] = 'top' if self.text_position_combo.currentIndex() == 0 else 'bottom'
            options['text_font_size'] = self.text_font_size_spin.value()
            options['text_color'] = self.text_color.name()
        else:
            options['add_text'] = False
        
        return options
    
    def generate_qrcode(self):
        """生成二维码"""
        try:
            # 获取二维码数据
            data = self.data_input.text().strip()
            if not data:
                self.status_updated.emit("请输入二维码数据")
                app_logger.warning("二维码数据为空")
                return
            
            # 获取基本参数
            version = self.version_spin.value()
            error_correction_code = self.error_correction_combo.currentData()
            error_correction = QRCodeGenerator.ERROR_CORRECTION_LEVELS[error_correction_code]['value']
            box_size = self.box_size_spin.value()
            border = self.border_spin.value()
            
            # 获取颜色参数
            fg_color = self.foreground_color.name()
            bg_color = self.background_color.name()
            
            # 获取Logo参数
            logo_path = self.logo_path_input.text().strip() if self.add_logo_checkbox.isChecked() else ""
            logo_size = self.logo_size_spin.value() if self.add_logo_checkbox.isChecked() else 0
            
            # 获取文本参数
            add_text = self.add_text_checkbox.isChecked()
            text_content = self.text_input.text().strip() if add_text else ""
            text_position = 'top' if self.text_position_combo.currentIndex() == 0 else 'bottom'
            text_font_size = self.text_font_size_spin.value() if add_text else 0
            text_color = self.text_color.name() if add_text else "#000000"
            
            # 验证Logo文件是否存在
            if self.add_logo_checkbox.isChecked() and logo_path and not os.path.exists(logo_path):
                self.status_updated.emit("Logo文件不存在")
                app_logger.error(f"Logo文件不存在: {logo_path}")
                return
            
            # 生成二维码
            app_logger.info(f"开始生成二维码: 版本={version}, 纠错级别={error_correction_code}, 数据长度={len(data)}")
            self.status_updated.emit("正在生成二维码...")
            
            options = {
                'version': version,
                'error_correction': error_correction,
                'box_size': box_size,
                'border': border,
                'fill_color': fg_color,
                'back_color': bg_color,
            }
            
            if self.add_logo_checkbox.isChecked():
                options['add_logo'] = True
                options['logo_path'] = logo_path
                options['logo_size'] = (logo_size, logo_size)
            else:
                options['add_logo'] = False
            
            if add_text:
                options['add_text'] = True
                options['text'] = text_content
                options['text_position'] = text_position
                options['text_font_size'] = text_font_size
                options['text_color'] = text_color
            else:
                options['add_text'] = False
            
            self.current_qrcode_image = self.qrcode_generator.generate_qrcode(data, options)
            
            if self.current_qrcode_image:
                # 显示二维码
                self.display_qrcode(self.current_qrcode_image)
                
                # 更新信息
                self.update_qrcode_info(data)
                
                # 启用保存按钮
                self.save_btn.setEnabled(True)
                
                self.status_updated.emit("二维码生成成功")
                app_logger.info("二维码生成成功")
            else:
                self.status_updated.emit("生成二维码失败")
                app_logger.error("生成二维码失败: 返回图像为空")
                
        except ValueError as e:
            error_msg = f"二维码数据验证失败: {str(e)}"
            app_logger.error(error_msg)
            self.status_updated.emit(error_msg)
        except FileNotFoundError as e:
            error_msg = f"找不到指定的Logo文件: {str(e)}"
            app_logger.error(error_msg)
            self.status_updated.emit(error_msg)
        except PermissionError as e:
            error_msg = f"文件权限错误: {str(e)}"
            app_logger.error(error_msg)
            self.status_updated.emit(error_msg)
        except Exception as e:
            error_msg = f"生成二维码时发生错误: {str(e)}"
            self.status_updated.emit(error_msg)
            app_logger.error(error_msg)
    
    def display_qrcode(self, qrcode_image):
        """显示二维码图像"""
        # 将PIL图像转换为QPixmap
        width, height = qrcode_image.size
        q_image = qrcode_image.toqimage()
        pixmap = QPixmap.fromImage(q_image)
        
        # 缩放图像以适应预览区域
        scaled_pixmap = pixmap.scaled(
            self.preview_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # 显示图像
        self.preview_label.setPixmap(scaled_pixmap)
    
    def update_qrcode_info(self, data):
        """更新二维码信息"""
        error_correction_code = self.error_correction_combo.currentData()
        error_correction_info = QRCodeGenerator.ERROR_CORRECTION_LEVELS[error_correction_code]
        
        info_text = f"二维码数据: {data}\n"
        info_text += f"版本: {self.version_spin.value()}\n"
        info_text += f"纠错级别: {error_correction_info['name']} - {error_correction_info['description']}"
        
        self.info_text.setText(info_text)
    
    def save_qrcode(self):
        """保存二维码"""
        try:
            if not self.current_qrcode_image:
                self.status_updated.emit("没有可保存的二维码，请先生成二维码")
                app_logger.warning("尝试保存二维码，但没有可保存的图像")
                return
            
            # 获取保存路径
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存二维码",
                os.path.join(os.getcwd(), "qrcode.png"),
                "PNG图像 (*.png);;JPEG图像 (*.jpg);;BMP图像 (*.bmp);;所有文件 (*)"
            )
            
            if not file_path:
                app_logger.info("用户取消了保存操作")
                return
            
            # 确保目录存在
            dir_path = os.path.dirname(file_path)
            if dir_path and not FileHandler.ensure_dir_exists(dir_path):
                error_msg = "无法创建输出目录"
                self.status_updated.emit(error_msg)
                app_logger.error(f"无法创建目录: {dir_path}")
                return
            
            # 保存图像
            self.current_qrcode_image.save(file_path)
            success_msg = f"二维码已保存到: {file_path}"
            self.status_updated.emit(success_msg)
            app_logger.info(f"二维码保存成功: {file_path}")
            
        except PermissionError as e:
            error_msg = f"文件权限错误，无法保存: {str(e)}"
            self.status_updated.emit(error_msg)
            app_logger.error(error_msg)
        except OSError as e:
            error_msg = f"文件系统错误: {str(e)}"
            self.status_updated.emit(error_msg)
            app_logger.error(error_msg)
        except Exception as e:
            error_msg = f"保存二维码时发生未知错误: {str(e)}"
            self.status_updated.emit(error_msg)
            app_logger.error(error_msg)
    
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        
        # 如果有二维码图像，重新显示以适应新的大小
        if self.current_qrcode_image:
            self.display_qrcode(self.current_qrcode_image)