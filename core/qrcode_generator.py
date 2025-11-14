"""
二维码生成核心功能模块
提供二维码的生成功能
"""

import os
import io
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple, Dict, Any
from utils.logger import app_logger
from utils.file_handler import FileHandler


class QRCodeGenerator:
    """二维码生成器类"""
    
    # 支持的纠错级别
    ERROR_CORRECTION_LEVELS = {
        'L': {
            'name': '低 (L)',
            'value': ERROR_CORRECT_L,
            'description': '约7%的纠错能力'
        },
        'M': {
            'name': '中 (M)',
            'value': ERROR_CORRECT_M,
            'description': '约15%的纠错能力'
        },
        'Q': {
            'name': '较高 (Q)',
            'value': ERROR_CORRECT_Q,
            'description': '约25%的纠错能力'
        },
        'H': {
            'name': '高 (H)',
            'value': ERROR_CORRECT_H,
            'description': '约30%的纠错能力'
        }
    }
    
    def __init__(self):
        """初始化二维码生成器"""
        self.default_options = {
            'version': 1,  # 控制二维码的大小，1是最小的
            'error_correction': ERROR_CORRECT_M,  # 纠错级别
            'box_size': 10,  # 每个框的像素数
            'border': 4,  # 边框的框数
            'fill_color': 'black',  # 前景色
            'back_color': 'white',  # 背景色
            'add_logo': False,  # 是否添加logo
            'logo_path': '',  # logo路径
            'logo_size': (100, 100),  # logo大小
            'add_text': False,  # 是否添加文本
            'text': '',  # 要添加的文本
            'text_position': 'bottom',  # 文本位置: top, bottom
            'text_font_size': 12,  # 文本字体大小
            'text_color': 'black',  # 文本颜色
        }
        app_logger.info("二维码生成器初始化完成")
    
    def validate_qr_data(self, data: str) -> Tuple[bool, str]:
        """
        验证二维码数据
        
        Args:
            data (str): 二维码数据
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if not data:
            return False, "二维码数据不能为空"
        
        # 检查数据长度（二维码有容量限制）
        if len(data) > 2953:  # 二维码最大容量（数字模式，版本40，纠错级别L）
            return False, "数据长度超过二维码最大容量限制"
        
        return True, ""
    
    def add_logo_to_qr(self, qr_image: Image.Image, logo_path: str, logo_size: Tuple[int, int]) -> Image.Image:
        """
        在二维码中心添加logo
        
        Args:
            qr_image (Image.Image): 二维码图像
            logo_path (str): logo文件路径
            logo_size (Tuple[int, int]): logo大小
            
        Returns:
            Image.Image: 添加了logo的二维码图像
        """
        try:
            # 打开logo图像
            logo = Image.open(logo_path)
            
            # 调整logo大小
            logo = logo.resize(logo_size, Image.LANCZOS)
            
            # 计算logo在二维码中的位置（居中）
            qr_width, qr_height = qr_image.size
            logo_width, logo_height = logo_size
            
            # 确保logo不会太大（不超过二维码图像的1/5）
            max_size = min(qr_width, qr_height) // 5
            if logo_width > max_size or logo_height > max_size:
                logo_width = min(logo_width, max_size)
                logo_height = min(logo_height, max_size)
                logo = logo.resize((logo_width, logo_height), Image.LANCZOS)
            
            # 计算位置
            pos = ((qr_width - logo_width) // 2, (qr_height - logo_height) // 2)
            
            # 创建一个透明背景的图像用于合成
            qr_with_logo = Image.new('RGBA', qr_image.size, (255, 255, 255, 0))
            qr_with_logo.paste(qr_image, (0, 0))
            
            # 粘贴logo
            qr_with_logo.paste(logo, pos, mask=logo if logo.mode == 'RGBA' else None)
            
            return qr_with_logo
            
        except Exception as e:
            app_logger.error(f"添加logo失败: {str(e)}")
            return qr_image
    
    def add_text_to_qr(self, qr_image: Image.Image, text: str, text_position: str = 'bottom',
                      text_font_size: int = 12, text_color: str = 'black') -> Image.Image:
        """
        在二维码上添加文本
        
        Args:
            qr_image (Image.Image): 二维码图像
            text (str): 要添加的文本
            text_position (str): 文本位置: top, bottom
            text_font_size (int): 文本字体大小
            text_color (str): 文本颜色
            
        Returns:
            Image.Image: 添加了文本的二维码图像
        """
        try:
            # 创建一个新的图像，为文本留出空间
            qr_width, qr_height = qr_image.size
            text_height = text_font_size + 10  # 文本区域高度
            
            if text_position == 'top':
                new_height = qr_height + text_height
                text_y = 5
                qr_y = text_height
            else:  # bottom
                new_height = qr_height + text_height
                text_y = qr_height + 5
                qr_y = 0
            
            # 创建新图像
            new_image = Image.new('RGB', (qr_width, new_height), 'white')
            
            # 粘贴二维码
            new_image.paste(qr_image, (0, qr_y))
            
            # 添加文本
            draw = ImageDraw.Draw(new_image)
            
            try:
                # 尝试使用系统字体
                font = ImageFont.truetype("arial.ttf", text_font_size)
            except:
                # 如果找不到系统字体，使用默认字体
                font = ImageFont.load_default()
            
            # 计算文本位置（居中）
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = (qr_width - text_width) // 2
            
            # 绘制文本
            draw.text((text_x, text_y), text, fill=text_color, font=font)
            
            return new_image
            
        except Exception as e:
            app_logger.error(f"添加文本失败: {str(e)}")
            return qr_image
    
    def generate(self, data, correction_level='M', box_size=10, border=4, 
                 fg_color='black', bg_color='white', logo_path=None, logo_size=None, text=None, text_color='black'):
        """
        生成二维码
        
        Args:
            data: 二维码数据
            correction_level: 纠错级别 (L, M, Q, H)
            box_size: 二维码大小
            border: 边框大小
            fg_color: 前景色
            bg_color: 背景色
            logo_path: Logo路径
            logo_size: Logo大小
            text: 文本
            text_color: 文本颜色
            
        Returns:
            str: 生成的二维码图片路径
            
        Raises:
            ValueError: 数据验证失败
            Exception: 生成失败
        """
        try:
            # 验证数据
            if not data:
                raise ValueError("二维码数据不能为空")
            
            # 验证纠错级别
            if correction_level not in ['L', 'M', 'Q', 'H']:
                raise ValueError("纠错级别必须是 L, M, Q 或 H")
            
            # 验证尺寸参数
            if not isinstance(box_size, int) or box_size < 1 or box_size > 50:
                raise ValueError("二维码大小必须是1到50之间的整数")
            
            if not isinstance(border, int) or border < 0 or border > 20:
                raise ValueError("边框大小必须是0到20之间的整数")
            
            # 验证颜色
            self._validate_colors(fg_color, bg_color, text_color)
            
            # 验证Logo
            logo_image = None
            if logo_path:
                logo_image = self._validate_and_load_logo(logo_path, logo_size)
            
            # 验证文本
            if text and not isinstance(text, str):
                raise ValueError("文本必须是字符串")
            
            app_logger.info(f"开始生成二维码: 纠错级别={correction_level}, 数据={data}")
            
            # 创建二维码实例
            qr = qrcode.QRCode(
                version=1,
                error_correction=self.ERROR_CORRECTION_LEVELS[correction_level]['value'],
                box_size=box_size,
                border=border,
            )
            
            # 添加数据
            qr.add_data(data)
            qr.make(fit=True)
            
            # 创建二维码图像
            qr_image = qr.make_image(fill_color=fg_color, back_color=bg_color)
            
            # 转换为RGBA模式以支持透明度
            qr_image = qr_image.convert('RGBA')
            
            # 添加Logo
            if logo_image:
                qr_image = self._add_logo_to_qrcode(qr_image, logo_image)
            
            # 添加文本
            if text:
                qr_image = self._add_text_to_qrcode(qr_image, text, text_color)
            
            # 生成唯一文件名
            filename = FileHandler.generate_unique_filename("qrcode", "png")
            filepath = os.path.join(FileHandler.get_temp_dir(), filename)
            
            # 保存二维码
            qr_image.save(filepath)
            
            # 验证文件是否生成成功
            if not os.path.exists(filepath):
                raise RuntimeError("二维码文件生成失败")
            
            app_logger.info(f"二维码生成成功: {filepath}")
            return filepath
            
        except ValueError as ve:
            app_logger.error(f"二维码数据验证失败: {str(ve)}")
            raise ve
        except Exception as e:
            error_msg = f"生成二维码失败: {str(e)}"
            app_logger.error(error_msg)
            raise Exception(error_msg)
    
    def _validate_colors(self, fg_color, bg_color, text_color):
        """
        验证颜色参数
        
        Args:
            fg_color: 前景色
            bg_color: 背景色
            text_color: 文本颜色
            
        Raises:
            ValueError: 颜色验证失败
        """
        try:
            from PIL import ImageColor
            
            # 验证前景色
            ImageColor.getrgb(fg_color)
            
            # 验证背景色
            ImageColor.getrgb(bg_color)
            
            # 验证文本颜色
            ImageColor.getrgb(text_color)
            
            # 检查前景色和背景色是否相同
            if fg_color.lower() == bg_color.lower():
                raise ValueError("前景色和背景色不能相同")
                
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise ValueError(f"无效的颜色值: {str(e)}")
    
    def _validate_and_load_logo(self, logo_path, logo_size):
        """
        验证并加载Logo
        
        Args:
            logo_path: Logo路径
            logo_size: Logo大小
            
        Returns:
            PIL.Image: Logo图像
            
        Raises:
            ValueError: Logo验证失败
            FileNotFoundError: Logo文件不存在
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(logo_path):
                raise FileNotFoundError(f"Logo文件不存在: {logo_path}")
            
            # 加载Logo
            logo_image = Image.open(logo_path)
            
            # 转换为RGBA模式
            logo_image = logo_image.convert('RGBA')
            
            # 调整Logo大小
            if logo_size:
                if not isinstance(logo_size, int) or logo_size < 10 or logo_size > 200:
                    raise ValueError("Logo大小必须是10到200之间的整数")
                logo_image = logo_image.resize((logo_size, logo_size), Image.LANCZOS)
            
            return logo_image
            
        except FileNotFoundError:
            raise
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"加载Logo失败: {str(e)}")
    
    def _add_logo_to_qrcode(self, qr_image, logo_image):
        """
        将Logo添加到二维码中心
        
        Args:
            qr_image: 二维码图像
            logo_image: Logo图像
            
        Returns:
            PIL.Image: 添加Logo后的二维码图像
        """
        # 计算Logo位置
        qr_width, qr_height = qr_image.size
        logo_width, logo_height = logo_image.size
        
        # 确保Logo不超过二维码大小的1/5
        max_logo_size = min(qr_width, qr_height) // 5
        if logo_width > max_logo_size or logo_height > max_logo_size:
            logo_image = logo_image.resize((max_logo_size, max_logo_size), Image.LANCZOS)
            logo_width, logo_height = logo_image.size
        
        # 计算Logo位置（居中）
        logo_pos = ((qr_width - logo_width) // 2, (qr_height - logo_height) // 2)
        
        # 创建一个透明背景的图像
        combined = Image.new('RGBA', (qr_width, qr_height), (0, 0, 0, 0))
        combined.paste(qr_image, (0, 0))
        combined.paste(logo_image, logo_pos, logo_image)
        
        return combined
    
    def _add_text_to_qrcode(self, qr_image: Image.Image, text: str, text_color: str, text_position: str = 'bottom', text_font_size: Optional[int] = None) -> Image.Image:
        """
        在二维码上添加文本
        
        Args:
            qr_image: 二维码图像
            text: 文本内容
            text_color: 文本颜色
            text_position: 文本位置 ('top' 或 'bottom')
            text_font_size: 文本字体大小
            
        Returns:
            PIL.Image: 添加文本后的二维码图像
        """
        try:
            from PIL import ImageDraw, ImageFont
            
            # 使用用户指定的字体大小，如果没有指定则使用默认值
            if text_font_size is not None:
                font_size = max(8, min(text_font_size, 50))  # 限制在8-50之间
            else:
                font_size = max(12, min(qr_image.size) // 20)  # 默认值
            
            try:
                # 尝试使用系统字体
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                # 使用默认字体
                font = ImageFont.load_default()
            
            # 计算文本尺寸
            draw = ImageDraw.Draw(qr_image)
            text_width, text_height = draw.textsize(text, font=font)
            
            # 创建新图像（增加空间）
            qr_width, qr_height = qr_image.size
            padding = 10
            new_height = qr_height + text_height + padding * 2
            new_image = Image.new('RGBA', (qr_width, new_height), (255, 255, 255, 255))
            
            # 根据文本位置确定二维码和文本的位置
            if text_position == 'top':
                # 粘贴二维码（在文本下方）
                new_image.paste(qr_image, (0, text_height + padding * 2))
                # 添加文本（在顶部）
                draw = ImageDraw.Draw(new_image)
                text_pos = ((qr_width - text_width) // 2, padding)
                draw.text(text_pos, text, fill=text_color, font=font)
            else:  # bottom
                # 粘贴二维码（在顶部）
                new_image.paste(qr_image, (0, 0))
                # 添加文本（在底部）
                draw = ImageDraw.Draw(new_image)
                text_pos = ((qr_width - text_width) // 2, qr_height + padding)
                draw.text(text_pos, text, fill=text_color, font=font)
            
            return new_image
            
        except Exception as e:
            app_logger.warning(f"添加文本失败: {str(e)}，返回不带文本的二维码")
            return qr_image
    
    def generate_qrcode(self, data: str, options: Optional[Dict[str, Any]] = None) -> Optional[Image.Image]:
        """
        生成二维码图像
        
        Args:
            data: 二维码数据
            options: 生成选项
            
        Returns:
            Optional[Image.Image]: 生成的二维码图像，失败则返回None
            
        Raises:
            ValueError: 数据验证失败
            RuntimeError: 生成失败
        """
        try:
            # 验证数据
            if not data:
                raise ValueError("二维码数据不能为空")
            
            # 合并选项
            gen_options = self.default_options.copy()
            if options:
                gen_options.update(options)
            
            # 验证选项参数
            self._validate_qrcode_options(gen_options)
            
            # 创建二维码实例
            qr = qrcode.QRCode(
                version=1,
                error_correction=gen_options['error_correction'],
                box_size=gen_options['box_size'],
                border=gen_options['border'],
            )
            
            # 添加数据
            qr.add_data(data)
            qr.make(fit=True)
            
            # 创建二维码图像
            qr_image = qr.make_image(fill_color=gen_options['fill_color'], back_color=gen_options['back_color'])
            
            # 转换为RGBA模式以支持透明度
            qr_image = qr_image.convert('RGBA')
            
            # 添加Logo
            if gen_options.get('logo_path') and os.path.exists(gen_options['logo_path']):
                # 处理logo_size参数，如果是元组则取第一个值
                logo_size = gen_options.get('logo_size')
                if logo_size and isinstance(logo_size, tuple):
                    logo_size = logo_size[0]
                
                logo_image = self._load_logo(gen_options['logo_path'], logo_size)
                if logo_image:
                    qr_image = self._add_logo_to_qrcode(qr_image, logo_image)
            
            # 添加文本
            if gen_options.get('text'):
                text_position = gen_options.get('text_position', 'bottom')
                text_font_size = gen_options.get('text_font_size')
                qr_image = self._add_text_to_qrcode(
                    qr_image, 
                    gen_options['text'], 
                    gen_options.get('text_color', 'black'),
                    text_position,
                    text_font_size
                )
            
            app_logger.info(f"成功生成二维码: {data}")
            return qr_image
            
        except ValueError as ve:
            app_logger.error(f"二维码生成参数错误: {str(ve)}")
            raise ve
        except RuntimeError as re:
            app_logger.error(f"二维码生成运行时错误: {str(re)}")
            raise re
        except Exception as e:
            error_msg = f"生成二维码时发生未知错误: {str(e)}"
            app_logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _validate_qrcode_options(self, options: Dict[str, Any]) -> None:
        """
        验证二维码生成选项参数
        
        Args:
            options: 生成选项字典
            
        Raises:
            ValueError: 参数验证失败
        """
        # 验证纠错级别
        error_correction = options.get('error_correction', self.default_options['error_correction'])
        valid_error_corrections = [level['value'] for level in self.ERROR_CORRECTION_LEVELS.values()]
        if error_correction not in valid_error_corrections:
            raise ValueError("无效的纠错级别")
        
        # 验证二维码大小
        box_size = options.get('box_size', self.default_options['box_size'])
        if not isinstance(box_size, int) or box_size < 1 or box_size > 50:
            raise ValueError("二维码大小必须是1到50之间的整数")
        
        # 验证边框大小
        border = options.get('border', self.default_options['border'])
        if not isinstance(border, int) or border < 0 or border > 20:
            raise ValueError("边框大小必须是0到20之间的整数")
        
        # 验证颜色
        fill_color = options.get('fill_color', self.default_options['fill_color'])
        back_color = options.get('back_color', self.default_options['back_color'])
        text_color = options.get('text_color', 'black')
        
        try:
            from PIL import ImageColor
            ImageColor.getrgb(fill_color)
            ImageColor.getrgb(back_color)
            ImageColor.getrgb(text_color)
            
            if fill_color.lower() == back_color.lower():
                raise ValueError("前景色和背景色不能相同")
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise ValueError(f"无效的颜色值: {str(e)}")
        
        # 验证Logo大小
        logo_size = options.get('logo_size')
        if logo_size is not None:
            # 如果是元组，取第一个值
            if isinstance(logo_size, tuple):
                logo_size = logo_size[0]
            
            if not isinstance(logo_size, int) or logo_size < 10 or logo_size > 200:
                raise ValueError("Logo大小必须是10到200之间的整数")
    
    def _load_logo(self, logo_path: str, logo_size: Optional[int] = None) -> Optional[Image.Image]:
        """
        加载Logo图像
        
        Args:
            logo_path: Logo路径
            logo_size: Logo大小
            
        Returns:
            Optional[Image.Image]: Logo图像，失败则返回None
        """
        try:
            if not os.path.exists(logo_path):
                app_logger.warning(f"Logo文件不存在: {logo_path}")
                return None
            
            logo_image = Image.open(logo_path)
            logo_image = logo_image.convert('RGBA')
            
            if logo_size:
                logo_image = logo_image.resize((logo_size, logo_size), Image.LANCZOS)
            
            return logo_image
        except Exception as e:
            app_logger.error(f"加载Logo失败: {str(e)}")
            return None
    
    def save_qrcode(self, data: str, file_path: str, options: Optional[Dict[str, Any]] = None) -> bool:
        """
        保存二维码到文件
        
        Args:
            data: 二维码数据
            file_path: 保存路径
            options: 生成选项
            
        Returns:
            bool: 是否成功保存
            
        Raises:
            ValueError: 参数验证失败
            OSError: 文件操作失败
            RuntimeError: 生成失败
        """
        try:
            # 验证参数
            if not data:
                raise ValueError("二维码数据不能为空")
            
            if not file_path:
                raise ValueError("保存路径不能为空")
            
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
            
            # 生成二维码图像
            qr_image = self.generate_qrcode(data, options)
            if qr_image is None:
                raise RuntimeError("二维码图像生成失败，返回为空")
            
            # 保存图像
            try:
                qr_image.save(file_path)
                
                # 验证文件是否保存成功
                if not os.path.exists(file_path):
                    raise RuntimeError("二维码文件保存失败")
                
                # 检查文件大小
                file_size = os.path.getsize(file_path)
                if file_size == 0:
                    raise RuntimeError("保存的二维码文件为空")
                
                app_logger.info(f"二维码保存成功: {file_path} (大小: {file_size} 字节)")
                return True
                
            except Exception as e:
                raise RuntimeError(f"保存二维码图像失败: {str(e)}")
            
        except ValueError as ve:
            app_logger.error(f"二维码保存参数错误: {str(ve)}")
            raise ve
        except OSError as oe:
            app_logger.error(f"二维码保存文件系统错误: {str(oe)}")
            raise oe
        except RuntimeError as re:
            app_logger.error(f"二维码保存运行时错误: {str(re)}")
            raise re
        except Exception as e:
            error_msg = f"保存二维码时发生未知错误: {str(e)}"
            app_logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def batch_generate_qrcodes(self, data_list: list, output_dir: str, 
                              file_prefix: str = 'qrcode', file_format: str = 'PNG',
                              options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        批量生成二维码
        
        Args:
            data_list (list): 二维码数据列表
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
                
                # 生成并保存二维码
                if self.save_qrcode(data, file_path, options):
                    result['success'] += 1
                    app_logger.info(f"批量生成二维码成功: {file_path}")
                else:
                    result['failed'] += 1
                    result['errors'].append(f"生成二维码失败: {data[:50]}{'...' if len(data) > 50 else ''}")
                    
            except Exception as e:
                result['failed'] += 1
                error_msg = f"生成二维码时出错: {data[:50]}{'...' if len(data) > 50 else ''}, 错误: {str(e)}"
                result['errors'].append(error_msg)
                app_logger.error(error_msg)
        
        app_logger.info(f"批量生成二维码完成: 成功{result['success']}个, 失败{result['failed']}个")
        return result