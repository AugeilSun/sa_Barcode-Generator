"""
批量生成界面模块
提供批量生成条形码和二维码的用户界面
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLabel, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
                            QPushButton, QCheckBox, QColorDialog, QFileDialog,
                            QGroupBox, QGridLayout, QTextEdit, QScrollArea,
                            QFrame, QSizePolicy, QRadioButton, QButtonGroup,
                            QProgressBar, QTabWidget, QTableWidget, QTableWidgetItem,
                            QHeaderView, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QThread, pyqtSlot
from PyQt5.QtGui import QPixmap, QFont, QColor
from core.batch_processor import BatchProcessor
from utils.logger import app_logger
from utils.file_handler import FileHandler


class BatchProcessThread(QThread):
    """批量处理线程"""
    
    # 定义信号
    progress_updated = pyqtSignal(int, int)  # 当前进度, 总数
    process_completed = pyqtSignal(dict)  # 处理结果
    status_updated = pyqtSignal(str)  # 状态消息
    
    def __init__(self, processor, process_type, data_source, output_dir, **kwargs):
        """
        初始化批量处理线程
        
        Args:
            processor: 批量处理器实例
            process_type: 处理类型 ('barcode' 或 'qrcode')
            data_source: 数据源
            output_dir: 输出目录
            **kwargs: 其他参数
        """
        super().__init__()
        self.processor = processor
        self.process_type = process_type
        self.data_source = data_source
        self.output_dir = output_dir
        self.kwargs = kwargs
        self.result = None
    
    def run(self):
        """运行批量处理"""
        try:
            self.status_updated.emit("正在处理数据...")
            app_logger.info(f"开始批量处理: 类型={self.process_type}, 数据源={self.data_source}, 输出目录={self.output_dir}")
            
            # 验证输入参数
            if not self.data_source:
                raise ValueError("数据源为空")
            
            if not self.output_dir:
                raise ValueError("输出目录为空")
            
            # 确保输出目录存在
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir, exist_ok=True)
                app_logger.info(f"创建输出目录: {self.output_dir}")
            
            if self.process_type == 'barcode':
                app_logger.info("开始批量生成条形码")
                self.result = self.processor.batch_generate_barcodes(
                    self.data_source, self.output_dir, **self.kwargs
                )
            else:  # qrcode
                app_logger.info("开始批量生成二维码")
                self.result = self.processor.batch_generate_qrcodes(
                    self.data_source, self.output_dir, **self.kwargs
                )
            
            # 验证结果
            if not self.result:
                raise ValueError("处理结果为空")
            
            # 发送进度更新
            total = self.result.get('success', 0) + self.result.get('failed', 0)
            self.progress_updated.emit(total, total)
            
            # 记录处理结果
            success_count = self.result.get('success', 0)
            failed_count = self.result.get('failed', 0)
            app_logger.info(f"批量处理完成: 成功={success_count}, 失败={failed_count}")
            
            # 如果有错误，记录错误信息
            errors = self.result.get('errors', [])
            if errors:
                app_logger.warning(f"处理过程中发生 {len(errors)} 个错误")
                for error in errors[:5]:  # 只记录前5个错误
                    app_logger.warning(f"错误: {error}")
            
            # 发送完成信号
            self.process_completed.emit(self.result)
            
        except ValueError as ve:
            error_msg = f"参数错误: {str(ve)}"
            self.status_updated.emit(error_msg)
            app_logger.error(error_msg)
            self.result = {'success': 0, 'failed': 0, 'errors': [error_msg]}
            self.process_completed.emit(self.result)
            
        except FileNotFoundError as fnfe:
            error_msg = f"文件未找到: {str(fnfe)}"
            self.status_updated.emit(error_msg)
            app_logger.error(error_msg)
            self.result = {'success': 0, 'failed': 0, 'errors': [error_msg]}
            self.process_completed.emit(self.result)
            
        except PermissionError as pe:
            error_msg = f"权限错误: {str(pe)}"
            self.status_updated.emit(error_msg)
            app_logger.error(error_msg)
            self.result = {'success': 0, 'failed': 0, 'errors': [error_msg]}
            self.process_completed.emit(self.result)
            
        except Exception as e:
            error_msg = f"批量处理失败: {str(e)}"
            self.status_updated.emit(error_msg)
            app_logger.error(f"批量处理异常: {type(e).__name__}: {str(e)}")
            import traceback
            app_logger.error(f"异常堆栈: {traceback.format_exc()}")
            self.result = {'success': 0, 'failed': 0, 'errors': [error_msg]}
            self.process_completed.emit(self.result)


class BatchTab(QWidget):
    """批量生成选项卡"""
    
    # 定义信号
    status_updated = pyqtSignal(str)
    
    def __init__(self):
        """初始化批量生成选项卡"""
        super().__init__()
        
        # 初始化批量处理器
        self.batch_processor = BatchProcessor()
        
        # 当前处理线程
        self.process_thread = None
        
        # 初始化UI
        self.init_ui()
        
        app_logger.info("批量生成选项卡初始化完成")
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 创建条形码批量生成选项卡
        barcode_tab = self.create_barcode_batch_tab()
        tab_widget.addTab(barcode_tab, "批量生成条形码")
        
        # 创建二维码批量生成选项卡
        qrcode_tab = self.create_qrcode_batch_tab()
        tab_widget.addTab(qrcode_tab, "批量生成二维码")
        
        main_layout.addWidget(tab_widget)
        
        # 创建进度和结果区域
        progress_result_widget = self.create_progress_result_widget()
        main_layout.addWidget(progress_result_widget)
    
    def create_barcode_batch_tab(self):
        """创建条形码批量生成选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 数据源设置组
        data_group = QGroupBox("数据源设置")
        data_layout = QFormLayout(data_group)
        
        # 数据源类型
        self.barcode_data_type_group = QButtonGroup()
        self.barcode_file_radio = QRadioButton("文件")
        self.barcode_file_radio.setChecked(True)
        self.barcode_data_type_group.addButton(self.barcode_file_radio, 0)
        
        self.barcode_list_radio = QRadioButton("数据列表")
        self.barcode_data_type_group.addButton(self.barcode_list_radio, 1)
        
        data_type_layout = QHBoxLayout()
        data_type_layout.addWidget(self.barcode_file_radio)
        data_type_layout.addWidget(self.barcode_list_radio)
        data_layout.addRow("数据源类型:", data_type_layout)
        
        # 文件路径
        self.barcode_file_path_input = QLineEdit()
        self.barcode_file_path_input.setPlaceholderText("选择包含数据的文件")
        self.barcode_browse_btn = QPushButton("浏览")
        self.barcode_browse_btn.clicked.connect(self.browse_barcode_data_file)
        
        file_path_layout = QHBoxLayout()
        file_path_layout.addWidget(self.barcode_file_path_input)
        file_path_layout.addWidget(self.barcode_browse_btn)
        data_layout.addRow("文件路径:", file_path_layout)
        
        # 数据列名
        self.barcode_data_column_combo = QComboBox()
        self.barcode_data_column_combo.setEnabled(False)
        data_layout.addRow("数据列:", self.barcode_data_column_combo)
        
        # 数据列表
        self.barcode_data_list_input = QTextEdit()
        self.barcode_data_list_input.setPlaceholderText("每行一个数据")
        self.barcode_data_list_input.setEnabled(False)
        data_layout.addRow("数据列表:", self.barcode_data_list_input)
        
        layout.addWidget(data_group)
        
        # 条形码设置组
        barcode_group = QGroupBox("条形码设置")
        barcode_layout = QFormLayout(barcode_group)
        
        # 条形码类型
        self.barcode_type_combo = QComboBox()
        for code, info in BatchProcessor().barcode_generator.SUPPORTED_BARCODE_TYPES.items():
            self.barcode_type_combo.addItem(f"{info['name']} ({code})", code)
        barcode_layout.addRow("条形码类型:", self.barcode_type_combo)
        
        # 文件前缀
        self.barcode_file_prefix_input = QLineEdit("barcode")
        barcode_layout.addRow("文件前缀:", self.barcode_file_prefix_input)
        
        # 文件格式
        self.barcode_file_format_combo = QComboBox()
        self.barcode_file_format_combo.addItems(["PNG", "JPEG", "BMP", "SVG"])
        barcode_layout.addRow("文件格式:", self.barcode_file_format_combo)
        
        # 输出目录
        self.barcode_output_dir_input = QLineEdit()
        self.barcode_output_dir_input.setText(os.path.join(os.getcwd(), "output"))
        self.barcode_output_browse_btn = QPushButton("浏览")
        self.barcode_output_browse_btn.clicked.connect(self.browse_barcode_output_dir)
        
        output_dir_layout = QHBoxLayout()
        output_dir_layout.addWidget(self.barcode_output_dir_input)
        output_dir_layout.addWidget(self.barcode_output_browse_btn)
        barcode_layout.addRow("输出目录:", output_dir_layout)
        
        layout.addWidget(barcode_group)
        
        # 操作按钮
        barcode_button_layout = QHBoxLayout()
        
        self.barcode_preview_btn = QPushButton("预览数据")
        self.barcode_preview_btn.clicked.connect(self.preview_barcode_data)
        barcode_button_layout.addWidget(self.barcode_preview_btn)
        
        self.barcode_generate_btn = QPushButton("批量生成")
        self.barcode_generate_btn.clicked.connect(self.batch_generate_barcodes)
        barcode_button_layout.addWidget(self.barcode_generate_btn)
        
        layout.addLayout(barcode_button_layout)
        
        # 连接信号
        self.barcode_file_radio.toggled.connect(self.on_barcode_data_type_changed)
        self.barcode_file_path_input.textChanged.connect(self.on_barcode_file_path_changed)
        
        return widget
    
    def create_qrcode_batch_tab(self):
        """创建二维码批量生成选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 数据源设置组
        data_group = QGroupBox("数据源设置")
        data_layout = QFormLayout(data_group)
        
        # 数据源类型
        self.qrcode_data_type_group = QButtonGroup()
        self.qrcode_file_radio = QRadioButton("文件")
        self.qrcode_file_radio.setChecked(True)
        self.qrcode_data_type_group.addButton(self.qrcode_file_radio, 0)
        
        self.qrcode_list_radio = QRadioButton("数据列表")
        self.qrcode_data_type_group.addButton(self.qrcode_list_radio, 1)
        
        data_type_layout = QHBoxLayout()
        data_type_layout.addWidget(self.qrcode_file_radio)
        data_type_layout.addWidget(self.qrcode_list_radio)
        data_layout.addRow("数据源类型:", data_type_layout)
        
        # 文件路径
        self.qrcode_file_path_input = QLineEdit()
        self.qrcode_file_path_input.setPlaceholderText("选择包含数据的文件")
        self.qrcode_browse_btn = QPushButton("浏览")
        self.qrcode_browse_btn.clicked.connect(self.browse_qrcode_data_file)
        
        file_path_layout = QHBoxLayout()
        file_path_layout.addWidget(self.qrcode_file_path_input)
        file_path_layout.addWidget(self.qrcode_browse_btn)
        data_layout.addRow("文件路径:", file_path_layout)
        
        # 数据列名
        self.qrcode_data_column_combo = QComboBox()
        self.qrcode_data_column_combo.setEnabled(False)
        data_layout.addRow("数据列:", self.qrcode_data_column_combo)
        
        # 数据列表
        self.qrcode_data_list_input = QTextEdit()
        self.qrcode_data_list_input.setPlaceholderText("每行一个数据")
        self.qrcode_data_list_input.setEnabled(False)
        data_layout.addRow("数据列表:", self.qrcode_data_list_input)
        
        layout.addWidget(data_group)
        
        # 二维码设置组
        qrcode_group = QGroupBox("二维码设置")
        qrcode_layout = QFormLayout(qrcode_group)
        
        # 文件前缀
        self.qrcode_file_prefix_input = QLineEdit("qrcode")
        qrcode_layout.addRow("文件前缀:", self.qrcode_file_prefix_input)
        
        # 文件格式
        self.qrcode_file_format_combo = QComboBox()
        self.qrcode_file_format_combo.addItems(["PNG", "JPEG", "BMP", "SVG"])
        qrcode_layout.addRow("文件格式:", self.qrcode_file_format_combo)
        
        # 输出目录
        self.qrcode_output_dir_input = QLineEdit()
        self.qrcode_output_dir_input.setText(os.path.join(os.getcwd(), "output"))
        self.qrcode_output_browse_btn = QPushButton("浏览")
        self.qrcode_output_browse_btn.clicked.connect(self.browse_qrcode_output_dir)
        
        output_dir_layout = QHBoxLayout()
        output_dir_layout.addWidget(self.qrcode_output_dir_input)
        output_dir_layout.addWidget(self.qrcode_output_browse_btn)
        qrcode_layout.addRow("输出目录:", output_dir_layout)
        
        layout.addWidget(qrcode_group)
        
        # 操作按钮
        qrcode_button_layout = QHBoxLayout()
        
        self.qrcode_preview_btn = QPushButton("预览数据")
        self.qrcode_preview_btn.clicked.connect(self.preview_qrcode_data)
        qrcode_button_layout.addWidget(self.qrcode_preview_btn)
        
        self.qrcode_generate_btn = QPushButton("批量生成")
        self.qrcode_generate_btn.clicked.connect(self.batch_generate_qrcodes)
        qrcode_button_layout.addWidget(self.qrcode_generate_btn)
        
        layout.addLayout(qrcode_button_layout)
        
        # 连接信号
        self.qrcode_file_radio.toggled.connect(self.on_qrcode_data_type_changed)
        self.qrcode_file_path_input.textChanged.connect(self.on_qrcode_file_path_changed)
        
        return widget
    
    def create_progress_result_widget(self):
        """创建进度和结果区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 结果表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setHorizontalHeaderLabels(["文件名", "状态", "备注"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result_table.setVisible(False)
        layout.addWidget(self.result_table)
        
        # 结果文本
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(150)
        self.result_text.setVisible(False)
        layout.addWidget(self.result_text)
        
        return widget
    
    def on_barcode_data_type_changed(self, checked):
        """条形码数据源类型改变"""
        is_file = self.barcode_file_radio.isChecked()
        
        self.barcode_file_path_input.setEnabled(is_file)
        self.barcode_browse_btn.setEnabled(is_file)
        self.barcode_data_column_combo.setEnabled(is_file)
        self.barcode_data_list_input.setEnabled(not is_file)
    
    def on_qrcode_data_type_changed(self, checked):
        """二维码数据源类型改变"""
        is_file = self.qrcode_file_radio.isChecked()
        
        self.qrcode_file_path_input.setEnabled(is_file)
        self.qrcode_browse_btn.setEnabled(is_file)
        self.qrcode_data_column_combo.setEnabled(is_file)
        self.qrcode_data_list_input.setEnabled(not is_file)
    
    def on_barcode_file_path_changed(self):
        """条形码文件路径改变"""
        file_path = self.barcode_file_path_input.text().strip()
        if not file_path:
            return
        
        # 获取CSV文件的列名
        success, columns, error_msg = self.batch_processor.get_csv_columns(file_path)
        
        if success:
            # 更新列名下拉框
            self.barcode_data_column_combo.clear()
            self.barcode_data_column_combo.addItems(columns)
            self.barcode_data_column_combo.setEnabled(True)
        else:
            self.barcode_data_column_combo.clear()
            self.barcode_data_column_combo.setEnabled(False)
    
    def on_qrcode_file_path_changed(self):
        """二维码文件路径改变"""
        file_path = self.qrcode_file_path_input.text().strip()
        if not file_path:
            return
        
        # 获取CSV文件的列名
        success, columns, error_msg = self.batch_processor.get_csv_columns(file_path)
        
        if success:
            # 更新列名下拉框
            self.qrcode_data_column_combo.clear()
            self.qrcode_data_column_combo.addItems(columns)
            self.qrcode_data_column_combo.setEnabled(True)
        else:
            self.qrcode_data_column_combo.clear()
            self.qrcode_data_column_combo.setEnabled(False)
    
    def browse_barcode_data_file(self):
        """浏览条形码数据文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择数据文件",
            os.getcwd(),
            "所有支持的文件 (*.csv *.txt *.json);;CSV文件 (*.csv);;文本文件 (*.txt);;JSON文件 (*.json);;所有文件 (*)"
        )
        
        if file_path:
            self.barcode_file_path_input.setText(file_path)
    
    def browse_qrcode_data_file(self):
        """浏览二维码数据文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择数据文件",
            os.getcwd(),
            "所有支持的文件 (*.csv *.txt *.json);;CSV文件 (*.csv);;文本文件 (*.txt);;JSON文件 (*.json);;所有文件 (*)"
        )
        
        if file_path:
            self.qrcode_file_path_input.setText(file_path)
    
    def browse_barcode_output_dir(self):
        """浏览条形码输出目录"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录",
            self.barcode_output_dir_input.text()
        )
        
        if dir_path:
            self.barcode_output_dir_input.setText(dir_path)
    
    def browse_qrcode_output_dir(self):
        """浏览二维码输出目录"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录",
            self.qrcode_output_dir_input.text()
        )
        
        if dir_path:
            self.qrcode_output_dir_input.setText(dir_path)
    
    def preview_barcode_data(self):
        """预览条形码数据"""
        data_source = self.get_barcode_data_source()
        if not data_source:
            self.status_updated.emit("请指定数据源")
            return
        
        # 读取数据
        if isinstance(data_source, str):  # 文件路径
            success, data_list, error_msg = self.batch_processor.read_data_from_file(data_source)
        else:  # 数据列表
            data_list = data_source
            success = True
        
        if success:
            # 显示预览
            preview_text = f"共 {len(data_list)} 条数据:\n\n"
            preview_text += "\n".join(data_list[:10])  # 只显示前10条
            if len(data_list) > 10:
                preview_text += f"\n\n... 还有 {len(data_list) - 10} 条数据"
            
            self.result_text.setText(preview_text)
            self.result_text.setVisible(True)
            self.result_table.setVisible(False)
            
            self.status_updated.emit(f"数据预览: 共 {len(data_list)} 条")
        else:
            self.status_updated.emit(f"读取数据失败: {error_msg}")
    
    def preview_qrcode_data(self):
        """预览二维码数据"""
        data_source = self.get_qrcode_data_source()
        if not data_source:
            self.status_updated.emit("请指定数据源")
            return
        
        # 读取数据
        if isinstance(data_source, str):  # 文件路径
            success, data_list, error_msg = self.batch_processor.read_data_from_file(data_source)
        else:  # 数据列表
            data_list = data_source
            success = True
        
        if success:
            # 显示预览
            preview_text = f"共 {len(data_list)} 条数据:\n\n"
            preview_text += "\n".join(data_list[:10])  # 只显示前10条
            if len(data_list) > 10:
                preview_text += f"\n\n... 还有 {len(data_list) - 10} 条数据"
            
            self.result_text.setText(preview_text)
            self.result_text.setVisible(True)
            self.result_table.setVisible(False)
            
            self.status_updated.emit(f"数据预览: 共 {len(data_list)} 条")
        else:
            self.status_updated.emit(f"读取数据失败: {error_msg}")
    
    def get_barcode_data_source(self):
        """获取条形码数据源"""
        if self.barcode_file_radio.isChecked():
            file_path = self.barcode_file_path_input.text().strip()
            if not file_path:
                return None
            
            data_column = None
            if self.barcode_data_column_combo.count() > 0:
                data_column = self.barcode_data_column_combo.currentText()
            
            return (file_path, data_column)
        else:
            data_text = self.barcode_data_list_input.toPlainText().strip()
            if not data_text:
                return None
            
            return [line.strip() for line in data_text.split('\n') if line.strip()]
    
    def get_qrcode_data_source(self):
        """获取二维码数据源"""
        if self.qrcode_file_radio.isChecked():
            file_path = self.qrcode_file_path_input.text().strip()
            if not file_path:
                return None
            
            data_column = None
            if self.qrcode_data_column_combo.count() > 0:
                data_column = self.qrcode_data_column_combo.currentText()
            
            return (file_path, data_column)
        else:
            data_text = self.qrcode_data_list_input.toPlainText().strip()
            if not data_text:
                return None
            
            return [line.strip() for line in data_text.split('\n') if line.strip()]
    
    def batch_generate_barcodes(self):
        """批量生成条形码"""
        # 获取数据源
        data_source = self.get_barcode_data_source()
        if not data_source:
            self.status_updated.emit("请指定数据源")
            return
        
        # 获取参数
        barcode_type = self.barcode_type_combo.currentData()
        output_dir = self.barcode_output_dir_input.text().strip()
        file_prefix = self.barcode_file_prefix_input.text().strip()
        file_format = self.barcode_file_format_combo.currentText()
        
        # 处理数据源
        if isinstance(data_source, tuple):  # 文件路径
            file_path, data_column = data_source
            # 启动批量处理线程
            self.start_batch_process('barcode', file_path, output_dir,
                                   barcode_type=barcode_type,
                                   file_prefix=file_prefix,
                                   file_format=file_format,
                                   data_column=data_column)
        else:  # 数据列表
            # 启动批量处理线程
            self.start_batch_process('barcode', data_source, output_dir,
                                   barcode_type=barcode_type,
                                   file_prefix=file_prefix,
                                   file_format=file_format)
    
    def batch_generate_qrcodes(self):
        """批量生成二维码"""
        # 获取数据源
        data_source = self.get_qrcode_data_source()
        if not data_source:
            self.status_updated.emit("请指定数据源")
            return
        
        # 获取参数
        output_dir = self.qrcode_output_dir_input.text().strip()
        file_prefix = self.qrcode_file_prefix_input.text().strip()
        file_format = self.qrcode_file_format_combo.currentText()
        
        # 处理数据源
        if isinstance(data_source, tuple):  # 文件路径
            file_path, data_column = data_source
            # 启动批量处理线程
            self.start_batch_process('qrcode', file_path, output_dir,
                                   file_prefix=file_prefix,
                                   file_format=file_format,
                                   data_column=data_column)
        else:  # 数据列表
            # 启动批量处理线程
            self.start_batch_process('qrcode', data_source, output_dir,
                                   file_prefix=file_prefix,
                                   file_format=file_format)
    
    def start_batch_process(self, process_type, data_source, output_dir, **kwargs):
        """启动批量处理线程"""
        try:
            # 验证输入参数
            if not process_type:
                raise ValueError("处理类型不能为空")
            
            if not data_source:
                raise ValueError("数据源不能为空")
            
            if not output_dir:
                raise ValueError("输出目录不能为空")
            
            # 如果已有线程在运行，先停止
            if self.process_thread and self.process_thread.isRunning():
                app_logger.info("停止正在运行的批量处理线程")
                self.process_thread.terminate()
                self.process_thread.wait(3000)  # 等待最多3秒
                if self.process_thread.isRunning():
                    app_logger.warning("批量处理线程未能正常停止")
            
            # 验证输出目录
            if not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir, exist_ok=True)
                    app_logger.info(f"创建输出目录: {output_dir}")
                except OSError as e:
                    raise OSError(f"无法创建输出目录 {output_dir}: {str(e)}")
            
            # 检查目录写入权限
            if not os.access(output_dir, os.W_OK):
                raise PermissionError(f"没有写入输出目录的权限: {output_dir}")
            
            # 显示进度条
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("准备中...")
            
            # 隐藏结果
            self.result_text.setVisible(False)
            self.result_table.setVisible(False)
            
            # 创建并启动线程
            self.process_thread = BatchProcessThread(
                self.batch_processor, process_type, data_source, output_dir, **kwargs
            )
            
            # 连接信号
            self.process_thread.progress_updated.connect(self.update_progress)
            self.process_thread.process_completed.connect(self.on_process_completed)
            self.process_thread.status_updated.connect(self.status_updated.emit)
            
            # 启动线程
            self.process_thread.start()
            
            self.status_updated.emit("开始批量生成...")
            app_logger.info(f"批量处理线程已启动: 类型={process_type}, 数据源={data_source}, 输出目录={output_dir}")
            
        except ValueError as ve:
            error_msg = f"参数错误: {str(ve)}"
            self.status_updated.emit(error_msg)
            app_logger.error(error_msg)
            
        except PermissionError as pe:
            error_msg = f"权限错误: {str(pe)}"
            self.status_updated.emit(error_msg)
            app_logger.error(error_msg)
            
        except OSError as oe:
            error_msg = f"系统错误: {str(oe)}"
            self.status_updated.emit(error_msg)
            app_logger.error(error_msg)
            
        except Exception as e:
            error_msg = f"启动批量处理失败: {str(e)}"
            self.status_updated.emit(error_msg)
            app_logger.error(error_msg)
            import traceback
            app_logger.error(f"异常堆栈: {traceback.format_exc()}")
    
    @pyqtSlot(int, int)
    def update_progress(self, current, total):
        """更新进度条"""
        if total > 0:
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
    
    @pyqtSlot(dict)
    def on_process_completed(self, result):
        """处理完成"""
        try:
            # 隐藏进度条
            self.progress_bar.setVisible(False)
            
            # 显示结果
            self.display_result(result)
            
            # 获取成功和失败数量
            success_count = result.get('success', 0)
            failed_count = result.get('failed', 0)
            total_count = success_count + failed_count
            
            # 记录处理结果
            if failed_count == 0:
                app_logger.info(f"批量处理全部成功: {success_count}/{total_count}")
            else:
                app_logger.warning(f"批量处理部分失败: 成功 {success_count}, 失败 {failed_count}")
            
            # 创建报告
            output_dir = None
            if hasattr(self, 'barcode_output_dir_input'):
                output_dir = self.barcode_output_dir_input.text()
            elif hasattr(self, 'qrcode_output_dir_input'):
                output_dir = self.qrcode_output_dir_input.text()
            
            if output_dir:
                try:
                    report_path = os.path.join(output_dir, "batch_report.md")
                    self.batch_processor.create_batch_report(result, report_path)
                    self.status_updated.emit(f"批量生成完成，报告已保存到: {report_path}")
                    app_logger.info(f"批量处理报告已保存: {report_path}")
                except Exception as e:
                    error_msg = f"创建批量处理报告失败: {str(e)}"
                    app_logger.error(error_msg)
                    self.status_updated.emit(error_msg)
            else:
                app_logger.warning("无法确定输出目录，未创建报告")
                
        except Exception as e:
            error_msg = f"处理完成时发生错误: {str(e)}"
            app_logger.error(error_msg)
            import traceback
            app_logger.error(f"异常堆栈: {traceback.format_exc()}")
            self.status_updated.emit(error_msg)
    
    def display_result(self, result):
        """显示结果"""
        success_count = result.get('success', 0)
        failed_count = result.get('failed', 0)
        errors = result.get('errors', [])
        
        # 显示结果文本
        result_text = f"批量生成完成:\n"
        result_text += f"- 成功: {success_count} 个\n"
        result_text += f"- 失败: {failed_count} 个\n"
        
        if errors:
            result_text += f"\n错误信息:\n"
            for i, error in enumerate(errors[:10], 1):  # 只显示前10个错误
                result_text += f"{i}. {error}\n"
            
            if len(errors) > 10:
                result_text += f"... 还有 {len(errors) - 10} 个错误\n"
        
        self.result_text.setText(result_text)
        self.result_text.setVisible(True)
        self.result_table.setVisible(False)