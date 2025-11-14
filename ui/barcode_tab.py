"""
条形码生成界面模块
提供条形码生成的用户界面
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLabel, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
                            QPushButton, QCheckBox, QColorDialog, QFileDialog,
                            QGroupBox, QGridLayout, QTextEdit, QScrollArea,
                            QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QFont, QColor
from PIL import Image
from core.barcode_generator import BarcodeGenerator
from utils.logger import app_logger
from utils.file_handler import FileHandler


class BarcodeTab(QWidget):
    """条形码生成选项卡"""
    
    # 定义信号
    status_updated = pyqtSignal(str)
    
    def __init__(self):
        """初始化条形码选项卡"""
        super().__init__()
        
        # 初始化条形码生成器
        self.barcode_generator = BarcodeGenerator()
        
        # 当前条形码图像
        self.current_barcode_image = None
        
        # 初始化UI
        self.init_ui()
        
        app_logger.info("条形码选项卡初始化完成")
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建左侧输入区域（带滚动）
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        left_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        left_panel = self.create_input_panel()
        left_scroll.setWidget(left_panel)
        main_layout.addWidget(left_scroll, 1)
        
        # 创建右侧预览区域
        right_panel = self.create_preview_panel()
        main_layout.addWidget(right_panel, 1)
    
    def create_input_panel(self):
        """创建输入面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 基本设置组
        basic_group = QGroupBox("基本设置")
        basic_layout = QFormLayout(basic_group)
        
        # 条形码类型选择
        self.barcode_type_combo = QComboBox()
        for code, info in BarcodeGenerator.SUPPORTED_BARCODE_TYPES.items():
            self.barcode_type_combo.addItem(f"{info['name']} ({code})", code)
        basic_layout.addRow("条形码类型:", self.barcode_type_combo)
        
        # 条形码数据输入
        self.data_input = QLineEdit()
        self.data_input.setPlaceholderText("请输入条形码数据")
        basic_layout.addRow("条形码数据:", self.data_input)
        
        # 自定义文本
        self.custom_text_input = QLineEdit()
        self.custom_text_input.setPlaceholderText("可选，留空则使用条形码数据")
        basic_layout.addRow("自定义文本:", self.custom_text_input)
        
        layout.addWidget(basic_group)
        
        # 样式设置组
        style_group = QGroupBox("样式设置")
        style_layout = QGridLayout(style_group)
        
        # 模块宽度
        self.module_width_spin = QDoubleSpinBox()
        self.module_width_spin.setRange(0.1, 2.0)
        self.module_width_spin.setSingleStep(0.1)
        self.module_width_spin.setValue(0.2)
        style_layout.addWidget(QLabel("模块宽度:"), 0, 0)
        style_layout.addWidget(self.module_width_spin, 0, 1)
        
        # 模块高度
        self.module_height_spin = QDoubleSpinBox()
        self.module_height_spin.setRange(5.0, 50.0)
        self.module_height_spin.setSingleStep(1.0)
        self.module_height_spin.setValue(15.0)
        style_layout.addWidget(QLabel("模块高度:"), 1, 0)
        style_layout.addWidget(self.module_height_spin, 1, 1)
        
        # 静区宽度
        self.quiet_zone_spin = QDoubleSpinBox()
        self.quiet_zone_spin.setRange(1.0, 20.0)
        self.quiet_zone_spin.setSingleStep(0.5)
        self.quiet_zone_spin.setValue(6.5)
        style_layout.addWidget(QLabel("静区宽度:"), 2, 0)
        style_layout.addWidget(self.quiet_zone_spin, 2, 1)
        
        # 字体大小
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(5, 30)
        self.font_size_spin.setValue(10)
        style_layout.addWidget(QLabel("字体大小:"), 3, 0)
        style_layout.addWidget(self.font_size_spin, 3, 1)
        
        # 文本距离
        self.text_distance_spin = QDoubleSpinBox()
        self.text_distance_spin.setRange(0.0, 20.0)
        self.text_distance_spin.setSingleStep(0.5)
        self.text_distance_spin.setValue(5.0)
        style_layout.addWidget(QLabel("文本距离:"), 4, 0)
        style_layout.addWidget(self.text_distance_spin, 4, 1)
        
        # 显示文本复选框
        self.show_text_checkbox = QCheckBox("显示文本")
        self.show_text_checkbox.setChecked(True)
        style_layout.addWidget(self.show_text_checkbox, 5, 0, 1, 2)
        
        layout.addWidget(style_group)
        
        # 颜色设置组
        color_group = QGroupBox("颜色设置")
        color_layout = QGridLayout(color_group)
        
        # 前景色
        self.foreground_color_btn = QPushButton("选择前景色")
        self.foreground_color_btn.clicked.connect(self.choose_foreground_color)
        self.foreground_color_label = QLabel("黑色")
        self.foreground_color = QColor(0, 0, 0)
        self.foreground_color_btn.setStyleSheet("background-color: #000000")
        self.foreground_color_btn.setProperty("color", "#000000")
        color_layout.addWidget(QLabel("前景色:"), 0, 0)
        color_layout.addWidget(self.foreground_color_btn, 0, 1)
        color_layout.addWidget(self.foreground_color_label, 0, 2)
        
        # 背景色
        self.background_color_btn = QPushButton("选择背景色")
        self.background_color_btn.clicked.connect(self.choose_background_color)
        self.background_color_label = QLabel("白色")
        self.background_color = QColor(255, 255, 255)
        self.background_color_btn.setStyleSheet("background-color: #FFFFFF")
        self.background_color_btn.setProperty("color", "#FFFFFF")
        color_layout.addWidget(QLabel("背景色:"), 1, 0)
        color_layout.addWidget(self.background_color_btn, 1, 1)
        color_layout.addWidget(self.background_color_label, 1, 2)
        
        layout.addWidget(color_group)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("生成条形码")
        self.generate_btn.clicked.connect(self.generate_barcode)
        button_layout.addWidget(self.generate_btn)
        
        self.save_btn = QPushButton("保存条形码")
        self.save_btn.clicked.connect(self.save_barcode)
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
        self.preview_label.setMinimumSize(300, 200)
        self.preview_label.setStyleSheet("border: 1px solid #ccc;")
        self.preview_label.setText("请输入数据并点击生成按钮")
        
        scroll_area.setWidget(self.preview_label)
        layout.addWidget(scroll_area)
        
        # 条形码信息
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(100)
        layout.addWidget(QLabel("条形码信息:"))
        layout.addWidget(self.info_text)
        
        return panel
    
    def choose_foreground_color(self):
        """选择前景色"""
        color = QColorDialog.getColor(
            QColor(self.foreground_color_btn.property("color") or "#000000"),
            self,
            "选择前景色"
        )
        
        if color.isValid():
            hex_color = color.name()
            self.foreground_color_btn.setStyleSheet(f"background-color: {hex_color}")
            self.foreground_color_btn.setProperty("color", hex_color)
            self.foreground_color_label.setText(hex_color)
    
    def choose_background_color(self):
        """选择背景色"""
        color = QColorDialog.getColor(
            QColor(self.background_color_btn.property("color") or "#FFFFFF"),
            self,
            "选择背景色"
        )
        
        if color.isValid():
            hex_color = color.name()
            self.background_color_btn.setStyleSheet(f"background-color: {hex_color}")
            self.background_color_btn.setProperty("color", hex_color)
            self.background_color_label.setText(hex_color)
    
    def get_barcode_options(self):
        """获取条形码生成选项"""
        # 获取前景色
        foreground_color = self.foreground_color_btn.property("color")
        if not foreground_color:
            foreground_color = "#000000"  # 默认黑色
        
        # 获取背景色
        background_color = self.background_color_btn.property("color")
        if not background_color:
            background_color = "#FFFFFF"  # 默认白色
            
        return {
            'module_width': self.module_width_spin.value(),
            'module_height': self.module_height_spin.value(),
            'quiet_zone': self.quiet_zone_spin.value(),
            'font_size': self.font_size_spin.value(),
            'text_distance': self.text_distance_spin.value(),
            'background': background_color,
            'foreground': foreground_color,
            'write_text': self.show_text_checkbox.isChecked(),
            'text': self.custom_text_input.text() if self.custom_text_input.text() else None
        }
    
    def generate_barcode(self):
        """生成条形码"""
        try:
            # 获取输入数据
            barcode_type = self.barcode_type_combo.currentData()
            data = self.data_input.text().strip()
            
            if not data:
                self.status_updated.emit("请输入条形码数据")
                app_logger.warning("条形码数据为空")
                return
            
            # 获取生成选项
            options = self.get_barcode_options()
            
            # 生成条形码
            app_logger.info(f"开始生成条形码: 类型={barcode_type}, 数据={data}")
            self.status_updated.emit("正在生成条形码...")
            
            self.current_barcode_image = self.barcode_generator.generate_barcode(barcode_type, data, options)
            
            if self.current_barcode_image:
                # 显示条形码
                self.display_barcode(self.current_barcode_image)
                
                # 更新信息
                self.update_barcode_info(barcode_type, data)
                
                # 启用保存按钮
                self.save_btn.setEnabled(True)
                
                self.status_updated.emit(f"成功生成{barcode_type}条形码")
                app_logger.info(f"条形码生成成功: {barcode_type}")
            else:
                self.status_updated.emit("生成条形码失败")
                app_logger.error("条形码生成失败: 生成器返回None")
                
        except ValueError as e:
            error_msg = f"条形码数据验证失败: {str(e)}"
            app_logger.error(error_msg)
            self.status_updated.emit(error_msg)
        except Exception as e:
            error_msg = f"生成条形码时发生错误: {str(e)}"
            app_logger.error(error_msg)
            self.status_updated.emit(error_msg)
    
    def display_barcode(self, barcode_image):
        """显示条形码图像"""
        # 将PIL图像转换为QPixmap
        width, height = barcode_image.size
        bytes_per_line = 3 * width
        q_image = barcode_image.toqimage()
        pixmap = QPixmap.fromImage(q_image)
        
        # 缩放图像以适应预览区域
        scaled_pixmap = pixmap.scaled(
            self.preview_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # 显示图像
        self.preview_label.setPixmap(scaled_pixmap)
    
    def update_barcode_info(self, barcode_type, data):
        """更新条形码信息"""
        barcode_info = BarcodeGenerator.SUPPORTED_BARCODE_TYPES.get(barcode_type, {})
        info_text = f"条形码类型: {barcode_info.get('name', barcode_type)}\n"
        info_text += f"条形码数据: {data}\n"
        info_text += f"描述: {barcode_info.get('description', '')}"
        
        self.info_text.setText(info_text)
    
    def save_barcode(self):
        """保存条形码"""
        try:
            if not self.current_barcode_image:
                self.status_updated.emit("没有可保存的条形码")
                app_logger.warning("尝试保存条形码，但没有可保存的图像")
                return
            
            # 获取保存路径
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存条形码",
                os.path.join(os.getcwd(), f"barcode.{self.data_input.text()}.png"),
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
            self.current_barcode_image.save(file_path)
            success_msg = f"条形码已保存到: {file_path}"
            self.status_updated.emit(success_msg)
            app_logger.info(f"条形码保存成功: {file_path}")
            
        except PermissionError as e:
            error_msg = f"保存失败: 没有写入权限 ({str(e)})"
            self.status_updated.emit(error_msg)
            app_logger.error(error_msg)
        except OSError as e:
            error_msg = f"保存失败: 磁盘空间不足或路径无效 ({str(e)})"
            self.status_updated.emit(error_msg)
            app_logger.error(error_msg)
        except Exception as e:
            error_msg = f"保存条形码失败: {str(e)}"
            self.status_updated.emit(error_msg)
            app_logger.error(error_msg)
    
    def reset_settings(self):
        """重置设置"""
        # 重置基本设置
        self.data_input.clear()
        self.barcode_type_combo.setCurrentIndex(0)
        
        # 重置样式设置
        self.module_width_spin.setValue(0.2)
        self.module_height_spin.setValue(15.0)
        self.quiet_zone_spin.setValue(6.5)
        self.font_size_spin.setValue(10)
        self.text_distance_spin.setValue(5.0)
        
        # 重置颜色设置
        self.foreground_color_btn.setStyleSheet("background-color: #000000")
        self.foreground_color_btn.setProperty("color", "#000000")
        self.foreground_color_label.setText("黑色")
        self.background_color_btn.setStyleSheet("background-color: #FFFFFF")
        self.background_color_btn.setProperty("color", "#FFFFFF")
        self.background_color_label.setText("白色")
        
        # 清除预览
        self.preview_label.clear()
        self.preview_label.setText("请输入数据并点击生成按钮")
        self.current_barcode_image = None
        self.save_btn.setEnabled(False)
        
        self.status_updated.emit("设置已重置")
    
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        
        # 如果有条形码图像，重新显示以适应新的大小
        if self.current_barcode_image:
            self.display_barcode(self.current_barcode_image)