"""
条形码生成核心功能模块
提供各种类型条形码的生成功能
"""

import os
import io
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple, Dict, Any
from utils.logger import app_logger
from utils.file_handler import FileHandler


class BarcodeGenerator:
    """条形码生成器类"""
    
    # 支持的条形码类型
    SUPPORTED_BARCODE_TYPES = {
        'ean8': {
            'name': 'EAN-8',
            'description': '8位欧洲商品条码',
            'length': (7, 8),  # (最小长度, 最大长度)
            'numeric_only': True
        },
        'ean13': {
            'name': 'EAN-13',
            'description': '13位欧洲商品条码',
            'length': (12, 13),
            'numeric_only': True
        },
        'ean14': {
            'name': 'EAN-14',
            'description': '14位欧洲商品条码',
            'length': (13, 14),
            'numeric_only': True
        },
        'upc': {
            'name': 'UPC-A',
            'description': '12位统一商品条码',
            'length': (11, 12),
            'numeric_only': True
        },
        'jan': {
            'name': 'JAN',
            'description': '日本商品条码',
            'length': (12, 13),
            'numeric_only': True
        },
        'isbn10': {
            'name': 'ISBN-10',
            'description': '10位国际标准书号',
            'length': (9, 10),
            'numeric_only': True
        },
        'isbn13': {
            'name': 'ISBN-13',
            'description': '13位国际标准书号',
            'length': (12, 13),
            'numeric_only': True
        },
        'issn': {
            'name': 'ISSN',
            'description': '国际标准期刊号',
            'length': (7, 8),
            'numeric_only': True
        },
        'code39': {
            'name': 'Code 39',
            'description': 'Code 39条码',
            'length': (1, 43),
            'numeric_only': False
        },
        'code128': {
            'name': 'Code 128',
            'description': 'Code 128条码',
            'length': (1, 80),
            'numeric_only': False
        },
        'pzn': {
            'name': 'PZN',
            'description': '德国医药中心编号',
            'length': (6, 8),
            'numeric_only': True
        },
        'gs1_128': {
            'name': 'GS1-128',
            'description': 'GS1-128条码',
            'length': (1, 80),
            'numeric_only': False
        },
        'itf': {
            'name': 'ITF',
            'description': '交叉25码',
            'length': (2, 80),
            'numeric_only': True
        },
        'gs1_14': {
            'name': 'GS1-14',
            'description': 'GS1-14条码',
            'length': (13, 14),
            'numeric_only': True
        }
    }
    
    def __init__(self):
        """初始化条形码生成器"""
        self.default_options = {
            'module_width': 0.2,  # 条码模块宽度
            'module_height': 15.0,  # 条码模块高度
            'quiet_zone': 6.5,  # 静区宽度
            'font_size': 10,  # 字体大小
            'text_distance': 5.0,  # 文本距离
            'background': 'white',  # 背景色
            'foreground': 'black',  # 前景色
            'write_text': True,  # 是否写入文本
            'text': ''  # 自定义文本
        }
        app_logger.info("条形码生成器初始化完成")
    
    def validate_barcode_data(self, barcode_type: str, data: str) -> Tuple[bool, str]:
        """
        验证条形码数据是否符合指定类型的要求
        
        Args:
            barcode_type (str): 条形码类型
            data (str): 条形码数据
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if barcode_type not in self.SUPPORTED_BARCODE_TYPES:
            return False, f"不支持的条形码类型: {barcode_type}"
        
        barcode_info = self.SUPPORTED_BARCODE_TYPES[barcode_type]
        min_length, max_length = barcode_info['length']
        numeric_only = barcode_info['numeric_only']
        
        # 检查长度
        if len(data) < min_length or len(data) > max_length:
            return False, f"数据长度应在{min_length}到{max_length}个字符之间"
        
        # 检查是否只包含数字
        if numeric_only and not data.isdigit():
            return False, f"{barcode_info['name']}条码只能包含数字"
        
        return True, ""
    
    def generate_barcode(self, barcode_type: str, data: str, options: Optional[Dict[str, Any]] = None) -> Optional[Image.Image]:
        """
        生成条形码图像
        
        Args:
            barcode_type (str): 条形码类型
            data (str): 条形码数据
            options (Optional[Dict[str, Any]]): 生成选项
            
        Returns:
            Optional[Image.Image]: 生成的条形码图像，失败则返回None
            
        Raises:
            ValueError: 数据验证失败
            RuntimeError: 生成失败
        """
        try:
            # 验证数据
            is_valid, error_msg = self.validate_barcode_data(barcode_type, data)
            if not is_valid:
                app_logger.error(f"条形码数据验证失败: {error_msg}")
                raise ValueError(error_msg)
            
            # 合并选项
            gen_options = self.default_options.copy()
            if options:
                gen_options.update(options)
            
            # 验证选项参数
            self._validate_options(gen_options)
            
            # 创建图像写入器
            writer = ImageWriter()
            
            # 创建条形码实例
            try:
                barcode_class = barcode.get_barcode_class(barcode_type)
                barcode_instance = barcode_class(data, writer=writer)
            except Exception as e:
                raise ValueError(f"创建条形码实例失败: {str(e)}")
            
            # 生成条形码图像
            try:
                # 准备writer选项，包括颜色设置
                writer_options = {
                    'module_width': gen_options.get('module_width', 0.2),
                    'module_height': gen_options.get('module_height', 15.0),
                    'quiet_zone': gen_options.get('quiet_zone', 6.5),
                    'font_size': gen_options.get('font_size', 10),
                    'text_distance': gen_options.get('text_distance', 5.0),
                    'background': gen_options.get('background', 'white'),
                    'foreground': gen_options.get('foreground', 'black'),
                    'text': gen_options.get('text', ''),
                    'write_text': gen_options.get('write_text', True)
                }
                
                # 记录颜色设置
                app_logger.info(f"条形码颜色设置: 前景色={writer_options['foreground']}, 背景色={writer_options['background']}")
                
                # 如果write_text为False，则禁用文本绘制
                if not writer_options['write_text']:
                    writer._callbacks["paint_text"] = None
                
                # 生成条形码图像
                barcode_image = barcode_instance.render(writer_options)
                
                # 验证生成的图像
                if barcode_image is None:
                    raise RuntimeError("条形码图像生成失败，返回为空")
                
                app_logger.info(f"成功生成{barcode_type}条形码: {data}")
                return barcode_image
                
            except Exception as e:
                raise RuntimeError(f"渲染条形码图像失败: {str(e)}")
            
        except ValueError as ve:
            app_logger.error(f"条形码生成参数错误: {str(ve)}")
            raise ve
        except RuntimeError as re:
            app_logger.error(f"条形码生成运行时错误: {str(re)}")
            raise re
        except Exception as e:
            error_msg = f"生成条形码时发生未知错误: {str(e)}"
            app_logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _validate_options(self, options: Dict[str, Any]) -> None:
        """
        验证生成选项参数
        
        Args:
            options: 生成选项字典
            
        Raises:
            ValueError: 参数验证失败
        """
        # 验证模块宽度
        module_width = options.get('module_width', self.default_options['module_width'])
        if not isinstance(module_width, (int, float)) or module_width <= 0 or module_width > 10:
            raise ValueError("模块宽度必须是0到10之间的正数")
        
        # 验证模块高度
        module_height = options.get('module_height', self.default_options['module_height'])
        if not isinstance(module_height, (int, float)) or module_height <= 0 or module_height > 500:
            raise ValueError("模块高度必须是0到500之间的正数")
        
        # 验证静区宽度
        quiet_zone = options.get('quiet_zone', self.default_options['quiet_zone'])
        if not isinstance(quiet_zone, (int, float)) or quiet_zone < 0 or quiet_zone > 20:
            raise ValueError("静区宽度必须是0到20之间的非负数")
        
        # 验证字体大小
        font_size = options.get('font_size', self.default_options['font_size'])
        if not isinstance(font_size, (int, float)) or font_size <= 0 or font_size > 50:
            raise ValueError("字体大小必须是0到50之间的正数")
        
        # 验证颜色
        foreground = options.get('foreground', self.default_options['foreground'])
        background = options.get('background', self.default_options['background'])
        
        try:
            from PIL import ImageColor
            ImageColor.getrgb(foreground)
            ImageColor.getrgb(background)
            
            if foreground.lower() == background.lower():
                raise ValueError("前景色和背景色不能相同")
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise ValueError(f"无效的颜色值: {str(e)}")
    
    def save_barcode(self, barcode_type: str, data: str, file_path: str, 
                    options: Optional[Dict[str, Any]] = None) -> bool:
        """
        生成并保存条形码到文件
        
        Args:
            barcode_type (str): 条形码类型
            data (str): 条形码数据
            file_path (str): 保存文件路径
            options (Optional[Dict[str, Any]]): 生成选项
            
        Returns:
            bool: 操作是否成功
            
        Raises:
            ValueError: 参数验证失败
            OSError: 文件操作失败
            RuntimeError: 生成失败
        """
        try:
            # 验证参数
            if not barcode_type:
                raise ValueError("条形码类型不能为空")
            
            if not data:
                raise ValueError("条形码数据不能为空")
            
            if not file_path:
                raise ValueError("保存路径不能为空")
            
            # 验证数据
            is_valid, error_msg = self.validate_barcode_data(barcode_type, data)
            if not is_valid:
                raise ValueError(error_msg)
            
            # 确保目录存在
            dir_path = os.path.dirname(file_path)
            if dir_path and not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    app_logger.info(f"创建目录: {dir_path}")
                except OSError as e:
                    raise OSError(f"无法创建目录 {dir_path}: {str(e)}")
            
            # 验证目录是否可写
            if dir_path and not os.access(dir_path, os.W_OK):
                raise OSError(f"目录 {dir_path} 不可写")
            
            # 生成条形码图像
            barcode_image = self.generate_barcode(barcode_type, data, options)
            if barcode_image is None:
                raise RuntimeError("条形码图像生成失败，返回为空")
            
            # 保存图像
            try:
                barcode_image.save(file_path)
                
                # 验证文件是否保存成功
                if not os.path.exists(file_path):
                    raise RuntimeError("条形码文件保存失败")
                
                # 检查文件大小
                file_size = os.path.getsize(file_path)
                if file_size == 0:
                    raise RuntimeError("保存的条形码文件为空")
                
                app_logger.info(f"条形码保存成功: {file_path} (大小: {file_size} 字节)")
                return True
                
            except Exception as e:
                raise RuntimeError(f"保存条形码图像失败: {str(e)}")
            
        except ValueError as ve:
            app_logger.error(f"条形码保存参数错误: {str(ve)}")
            raise ve
        except OSError as oe:
            app_logger.error(f"条形码保存文件系统错误: {str(oe)}")
            raise oe
        except RuntimeError as re:
            app_logger.error(f"条形码保存运行时错误: {str(re)}")
            raise re
        except Exception as e:
            error_msg = f"保存条形码时发生未知错误: {str(e)}"
            app_logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def batch_generate_barcodes(self, barcode_type: str, data_list: list, output_dir: str, 
                              file_prefix: str = 'barcode', file_format: str = 'PNG',
                              options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        批量生成条形码
        
        Args:
            barcode_type (str): 条形码类型
            data_list (list): 条形码数据列表
            output_dir (str): 输出目录
            file_prefix (str): 文件名前缀
            file_format (str): 文件格式
            options (Optional[Dict[str, Any]]): 生成选项
            
        Returns:
            Dict[str, Any]: 批量生成结果
        """
        result = {
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        # 确保输出目录存在
        if not FileHandler.ensure_dir_exists(output_dir):
            app_logger.error(f"无法创建输出目录: {output_dir}")
            result['errors'].append(f"无法创建输出目录: {output_dir}")
            return result
        
        for i, data in enumerate(data_list):
            try:
                # 生成文件名
                filename = f"{file_prefix}_{i+1}.{file_format.lower()}"
                file_path = os.path.join(output_dir, filename)
                
                # 生成并保存条形码
                if self.save_barcode(barcode_type, data, file_path, options):
                    result['success'] += 1
                    app_logger.info(f"批量生成条形码成功: {file_path}")
                else:
                    result['failed'] += 1
                    result['errors'].append(f"生成条形码失败: {data}")
                    
            except Exception as e:
                result['failed'] += 1
                error_msg = f"生成条形码时出错: {data}, 错误: {str(e)}"
                result['errors'].append(error_msg)
                app_logger.error(error_msg)
        
        app_logger.info(f"批量生成条形码完成: 成功{result['success']}个, 失败{result['failed']}个")
        return result