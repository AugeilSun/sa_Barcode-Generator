"""
批量处理功能模块
提供批量生成条形码和二维码的功能
"""

import os
import csv
import json
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Union
from utils.logger import app_logger
from utils.file_handler import FileHandler
from core.barcode_generator import BarcodeGenerator
from core.qrcode_generator import QRCodeGenerator


class BatchProcessor:
    """批量处理器类"""
    
    def __init__(self):
        """初始化批量处理器"""
        self.barcode_generator = BarcodeGenerator()
        self.qrcode_generator = QRCodeGenerator()
        app_logger.info("批量处理器初始化完成")
    
    def read_data_from_file(self, file_path: str, data_column: str = None) -> Tuple[bool, List[str], str]:
        """
        从文件中读取数据
        
        Args:
            file_path (str): 文件路径
            data_column (str): 数据列名（对于CSV文件）
            
        Returns:
            Tuple[bool, List[str], str]: (是否成功, 数据列表, 错误信息)
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件格式不支持或文件为空
            OSError: 文件读取错误
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"数据文件不存在: {file_path}")
            
            # 检查文件是否可读
            if not os.access(file_path, os.R_OK):
                raise OSError(f"文件不可读: {file_path}")
            
            # 获取文件扩展名
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # 根据文件类型读取数据
            if file_ext == '.csv':
                return self._read_csv_file_with_column(file_path, data_column)
            elif file_ext == '.txt':
                return self._read_txt_file_enhanced(file_path)
            elif file_ext == '.json':
                return self._read_json_file_enhanced(file_path, data_column)
            elif file_ext in ['.xls', '.xlsx']:
                return self._read_excel_file_with_column(file_path, data_column)
            else:
                raise ValueError(f"不支持的文件格式: {file_ext}")
                
        except FileNotFoundError:
            error_msg = f"文件不存在: {file_path}"
            app_logger.error(error_msg)
            return False, [], error_msg
        except ValueError:
            error_msg = f"文件格式错误: {file_path}"
            app_logger.error(error_msg)
            return False, [], error_msg
        except OSError:
            error_msg = f"文件读取错误: {file_path}"
            app_logger.error(error_msg)
            return False, [], error_msg
        except Exception as e:
            error_msg = f"读取文件时发生未知错误: {str(e)}"
            app_logger.error(error_msg)
            return False, [], error_msg
    
    def _read_csv_file_with_column(self, file_path: str, data_column: str = None) -> Tuple[bool, List[str], str]:
        """
        读取CSV文件（增强版）
        
        Args:
            file_path (str): 文件路径
            data_column (str): 数据列名
            
        Returns:
            Tuple[bool, List[str], str]: (是否成功, 数据列表, 错误信息)
        """
        try:
            # 尝试使用UTF-8编码读取
            try:
                df = pd.read_csv(file_path)
            except UnicodeDecodeError:
                # 如果UTF-8失败，尝试GBK编码
                df = pd.read_csv(file_path, encoding='gbk')
                app_logger.info(f"使用GBK编码读取CSV文件: {file_path}")
            
            # 检查DataFrame是否为空
            if df.empty:
                raise ValueError("CSV文件为空")
            
            # 如果指定了列名，使用指定列
            if data_column and data_column in df.columns:
                data_list = df[data_column].dropna().astype(str).tolist()
            else:
                # 否则使用第一列
                data_list = df.iloc[:, 0].dropna().astype(str).tolist()
            
            if not data_list:
                raise ValueError("CSV文件没有有效数据")
            
            app_logger.info(f"从CSV文件读取数据成功: {len(data_list)}条记录")
            return True, data_list, ""
            
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise OSError(f"读取CSV文件失败: {str(e)}")
    
    def _read_txt_file_enhanced(self, file_path: str) -> Tuple[bool, List[str], str]:
        """
        读取文本文件（增强版）
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            Tuple[bool, List[str], str]: (是否成功, 数据列表, 错误信息)
        """
        try:
            # 尝试使用UTF-8编码读取
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data_list = [line.strip() for line in f.readlines() if line.strip()]
            except UnicodeDecodeError:
                # 如果UTF-8失败，尝试GBK编码
                with open(file_path, 'r', encoding='gbk') as f:
                    data_list = [line.strip() for line in f.readlines() if line.strip()]
                app_logger.info(f"使用GBK编码读取文本文件: {file_path}")
            
            if not data_list:
                raise ValueError("文本文件为空或只包含空行")
            
            app_logger.info(f"从文本文件读取数据成功: {len(data_list)}条记录")
            return True, data_list, ""
            
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise OSError(f"读取文本文件失败: {str(e)}")
    
    def _read_json_file_enhanced(self, file_path: str, data_column: str = None) -> Tuple[bool, List[str], str]:
        """
        读取JSON文件（增强版）
        
        Args:
            file_path (str): 文件路径
            data_column (str): 数据列名
            
        Returns:
            Tuple[bool, List[str], str]: (是否成功, 数据列表, 错误信息)
        """
        try:
            # 尝试使用UTF-8编码读取
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
            except UnicodeDecodeError:
                # 如果UTF-8失败，尝试GBK编码
                with open(file_path, 'r', encoding='gbk') as f:
                    json_data = json.load(f)
                app_logger.info(f"使用GBK编码读取JSON文件: {file_path}")
            
            # 处理不同格式的JSON数据
            if isinstance(json_data, list):
                # 如果是列表，直接使用
                data_list = [str(item) for item in json_data if item]
            elif isinstance(json_data, dict):
                # 如果是字典，尝试找到包含数据的列表
                if data_column and data_column in json_data:
                    data_list = [str(item) for item in json_data[data_column] if item]
                else:
                    # 使用第一个值为列表的键
                    for key, value in json_data.items():
                        if isinstance(value, list):
                            data_list = [str(item) for item in value if item]
                            break
                    else:
                        raise ValueError("JSON文件中未找到有效的数据列表")
            else:
                raise ValueError("不支持的JSON格式")
            
            if not data_list:
                raise ValueError("JSON文件没有有效数据")
            
            app_logger.info(f"从JSON文件读取数据成功: {len(data_list)}条记录")
            return True, data_list, ""
            
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON格式错误: {str(e)}")
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise OSError(f"读取JSON文件失败: {str(e)}")
    
    def _read_excel_file_with_column(self, file_path: str, data_column: str = None) -> Tuple[bool, List[str], str]:
        """
        读取Excel文件（增强版）
        
        Args:
            file_path (str): 文件路径
            data_column (str): 数据列名
            
        Returns:
            Tuple[bool, List[str], str]: (是否成功, 数据列表, 错误信息)
        """
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            # 检查DataFrame是否为空
            if df.empty:
                raise ValueError("Excel文件为空")
            
            # 如果指定了列名，使用指定列
            if data_column and data_column in df.columns:
                data_list = df[data_column].dropna().astype(str).tolist()
            else:
                # 否则使用第一列
                data_list = df.iloc[:, 0].dropna().astype(str).tolist()
            
            if not data_list:
                raise ValueError("Excel文件没有有效数据")
            
            app_logger.info(f"从Excel文件读取数据成功: {len(data_list)}条记录")
            return True, data_list, ""
            
        except ImportError:
            raise ValueError("未安装pandas或openpyxl库，无法读取Excel文件")
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise OSError(f"读取Excel文件失败: {str(e)}")
    
    def batch_generate_barcodes(self, data_source: Union[str, List[str]], output_dir: str, barcode_type: str,
                               file_prefix: str = 'barcode', file_format: str = 'PNG',
                               data_column: str = None, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        批量生成条形码
        
        Args:
            data_source (str): 数据源（文件路径或直接数据列表）
            output_dir (str): 输出目录
            barcode_type (str): 条形码类型
            file_prefix (str): 文件名前缀
            file_format (str): 文件格式
            data_column (str): 数据列名（对于CSV文件）
            options (Optional[Dict[str, Any]]): 生成选项
            
        Returns:
            Dict[str, Any]: 批量生成结果
            
        Raises:
            ValueError: 参数验证失败
            FileNotFoundError: 文件不存在
            OSError: 文件操作失败
            RuntimeError: 处理失败
        """
        try:
            # 验证参数
            if not output_dir:
                raise ValueError("输出目录不能为空")
            
            if not barcode_type:
                raise ValueError("条形码类型不能为空")
            
            # 确保输出目录存在
            if not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir, exist_ok=True)
                    app_logger.info(f"创建输出目录: {output_dir}")
                except OSError as e:
                    raise OSError(f"无法创建输出目录 {output_dir}: {str(e)}")
            
            # 验证目录是否可写
            if not os.access(output_dir, os.W_OK):
                raise OSError(f"输出目录 {output_dir} 不可写")
            
            # 获取数据
            if isinstance(data_source, str) and os.path.isfile(data_source):
                # 数据源是文件路径
                success, data_list, error_msg = self.read_data_from_file(data_source, data_column)
                if not success:
                    raise ValueError(f"读取数据文件失败: {error_msg}")
            elif isinstance(data_source, list):
                # 数据源是直接的数据列表
                data_list = data_source
            else:
                raise ValueError(f"无效的数据源类型，期望文件路径字符串或数据列表，得到: {type(data_source)}")
            
            if not data_list:
                raise ValueError("没有可处理的数据")
            
            app_logger.info(f"开始批量生成条形码: 类型={barcode_type}, 数据量={len(data_list)}")
            
            # 批量生成条形码
            result = self.barcode_generator.batch_generate_barcodes(
                barcode_type, data_list, output_dir, file_prefix, file_format, options
            )
            
            # 记录处理结果
            app_logger.info(f"批量条形码处理完成: 成功={result.get('success', 0)}, 失败={result.get('failed', 0)}")
            
            return result
            
        except ValueError as ve:
            app_logger.error(f"批量条形码处理参数错误: {str(ve)}")
            raise ve
        except FileNotFoundError as fnfe:
            app_logger.error(f"批量条形码处理文件不存在: {str(fnfe)}")
            raise fnfe
        except OSError as oe:
            app_logger.error(f"批量条形码处理文件系统错误: {str(oe)}")
            raise oe
        except RuntimeError as re:
            app_logger.error(f"批量条形码处理运行时错误: {str(re)}")
            raise re
        except Exception as e:
            error_msg = f"批量条形码处理时发生未知错误: {str(e)}"
            app_logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def batch_generate_qrcodes(self, data_source: Union[str, List[str]], output_dir: str,
                             file_prefix: str = 'qrcode', file_format: str = 'PNG',
                             data_column: str = None, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        批量生成二维码
        
        Args:
            data_source (Union[str, List[str]]): 数据源（文件路径或直接数据列表）
            output_dir (str): 输出目录
            file_prefix (str): 文件名前缀
            file_format (str): 文件格式
            data_column (str): 数据列名（对于CSV文件）
            options (Optional[Dict[str, Any]]): 生成选项
            
        Returns:
            Dict[str, Any]: 批量生成结果
            
        Raises:
            ValueError: 参数验证失败
            FileNotFoundError: 文件不存在
            OSError: 文件操作失败
            RuntimeError: 处理失败
        """
        try:
            # 验证参数
            if not output_dir:
                raise ValueError("输出目录不能为空")
            
            # 确保输出目录存在
            if not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir, exist_ok=True)
                    app_logger.info(f"创建输出目录: {output_dir}")
                except OSError as e:
                    raise OSError(f"无法创建输出目录 {output_dir}: {str(e)}")
            
            # 验证目录是否可写
            if not os.access(output_dir, os.W_OK):
                raise OSError(f"输出目录 {output_dir} 不可写")
            
            # 获取数据
            if isinstance(data_source, list):
                # 数据源是直接的数据列表
                data_list = data_source
                app_logger.info(f"使用数据列表，共 {len(data_list)} 条数据")
            elif isinstance(data_source, str) and os.path.isfile(data_source):
                # 数据源是文件路径
                success, data_list, error_msg = self.read_data_from_file(data_source, data_column)
                if not success:
                    raise ValueError(f"读取数据文件失败: {error_msg}")
                app_logger.info(f"从文件 {data_source} 读取了 {len(data_list)} 条数据")
            else:
                raise ValueError(f"无效的数据源类型，期望文件路径字符串或数据列表，得到: {type(data_source)}")
            
            if not data_list:
                raise ValueError("没有可处理的数据")
            
            app_logger.info(f"开始批量生成二维码: 数据量={len(data_list)}")
            
            # 批量生成二维码
            result = self.qrcode_generator.batch_generate_qrcodes(
                data_list, output_dir, file_prefix, file_format, options
            )
            
            # 记录处理结果
            app_logger.info(f"批量二维码处理完成: 成功={result.get('success', 0)}, 失败={result.get('failed', 0)}")
            
            return result
            
        except ValueError as ve:
            app_logger.error(f"批量二维码处理参数错误: {str(ve)}")
            raise ve
        except FileNotFoundError as fnfe:
            app_logger.error(f"批量二维码处理文件不存在: {str(fnfe)}")
            raise fnfe
        except OSError as oe:
            app_logger.error(f"批量二维码处理文件系统错误: {str(oe)}")
            raise oe
        except RuntimeError as re:
            app_logger.error(f"批量二维码处理运行时错误: {str(re)}")
            raise re
        except Exception as e:
            error_msg = f"批量二维码处理时发生未知错误: {str(e)}"
            app_logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def create_batch_report(self, results: Dict[str, Any], output_path: str) -> bool:
        """
        创建批量处理报告
        
        Args:
            results (Dict[str, Any]): 批量处理结果
            output_path (str): 报告输出路径
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 确保目录存在
            dir_path = os.path.dirname(output_path)
            if dir_path and not FileHandler.ensure_dir_exists(dir_path):
                return False
            
            # 创建报告内容
            report = []
            report.append("# 批量生成报告")
            report.append(f"生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            report.append("## 生成结果统计")
            report.append(f"- 成功生成: {results.get('success', 0)} 个")
            report.append(f"- 生成失败: {results.get('failed', 0)} 个")
            report.append("")
            
            # 如果有错误，添加错误信息
            errors = results.get('errors', [])
            if errors:
                report.append("## 错误信息")
                for i, error in enumerate(errors, 1):
                    report.append(f"{i}. {error}")
                report.append("")
            
            # 保存报告
            report_content = "\n".join(report)
            return FileHandler.save_file(output_path, report_content)
            
        except Exception as e:
            app_logger.error(f"创建批量处理报告失败: {str(e)}")
            return False
    
    def _get_output_filename(self, data_item, index, output_dir, file_prefix, file_format):
        """
        获取输出文件名
        
        Args:
            data_item: 数据项
            index: 索引
            output_dir: 输出目录
            file_prefix: 文件前缀
            file_format: 文件格式
            
        Returns:
            str: 输出文件路径
            
        Raises:
            ValueError: 参数无效
            OSError: 文件路径错误
        """
        try:
            # 验证参数
            if not data_item or not isinstance(data_item, str):
                raise ValueError("数据项不能为空且必须是字符串")
            
            if not output_dir or not isinstance(output_dir, str):
                raise ValueError("输出目录不能为空且必须是字符串")
            
            if not file_prefix or not isinstance(file_prefix, str):
                raise ValueError("文件前缀不能为空且必须是字符串")
            
            if not file_format or not isinstance(file_format, str):
                raise ValueError("文件格式不能为空且必须是字符串")
            
            # 清理数据项，移除不适合作为文件名的字符
            safe_data_item = re.sub(r'[\\/*?:"<>|]', "", str(data_item)).strip()
            
            # 如果清理后数据项为空，使用索引
            if not safe_data_item:
                safe_data_item = f"data_{index+1}"
            
            # 限制文件名长度
            max_filename_length = 100
            if len(safe_data_item) > max_filename_length:
                safe_data_item = safe_data_item[:max_filename_length]
            
            # 构建文件名
            if file_prefix:
                filename = f"{file_prefix}_{safe_data_item}.{file_format}"
            else:
                filename = f"{safe_data_item}.{file_format}"
            
            # 构建完整路径
            output_path = os.path.join(output_dir, filename)
            
            # 检查路径长度（Windows限制）
            if len(output_path) > 260:
                # 如果路径太长，缩短文件名
                safe_data_item = safe_data_item[:30]
                if file_prefix:
                    filename = f"{file_prefix}_{safe_data_item}.{file_format}"
                else:
                    filename = f"{safe_data_item}.{file_format}"
                output_path = os.path.join(output_dir, filename)
                
                if len(output_path) > 260:
                    # 如果仍然太长，使用更短的文件名
                    filename = f"{index+1}.{file_format}"
                    output_path = os.path.join(output_dir, filename)
            
            return output_path
            
        except Exception as e:
            if isinstance(e, (ValueError, OSError)):
                raise e
            # 如果发生其他错误，返回一个基于索引的文件名
            try:
                filename = f"{index+1}.{file_format}"
                return os.path.join(output_dir, filename)
            except:
                # 最后的备用方案
                return os.path.join(os.getcwd(), f"{index+1}.{file_format}")
    
    def _create_html_report(self, output_dir, results, total_count, success_count, failed_count, process_type):
        """
        创建HTML报告
        
        Args:
            output_dir: 输出目录
            results: 处理结果列表
            total_count: 总数
            success_count: 成功数
            failed_count: 失败数
            process_type: 处理类型 (barcode 或 qrcode)
            
        Raises:
            ValueError: 参数无效
            OSError: 文件操作错误
        """
        try:
            # 验证参数
            if not output_dir or not isinstance(output_dir, str):
                raise ValueError("输出目录不能为空且必须是字符串")
            
            if not isinstance(results, list):
                raise ValueError("处理结果必须是列表")
            
            if not isinstance(total_count, int) or total_count < 0:
                raise ValueError("总数必须是非负整数")
            
            if not isinstance(success_count, int) or success_count < 0:
                raise ValueError("成功数必须是非负整数")
            
            if not isinstance(failed_count, int) or failed_count < 0:
                raise ValueError("失败数必须是非负整数")
            
            if not process_type or not isinstance(process_type, str):
                raise ValueError("处理类型不能为空且必须是字符串")
            
            # 确保输出目录存在
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # 检查输出目录是否可写
            if not os.access(output_dir, os.W_OK):
                raise OSError(f"输出目录不可写: {output_dir}")
            
            # 获取当前时间
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 创建HTML报告内容
            html_content = f"""
            <!DOCTYPE html>
            <html lang="zh-CN">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>批量{'条形码' if process_type == 'barcode' else '二维码'}生成报告</title>
                <style>
                    body {{
                        font-family: 'Microsoft YaHei', Arial, sans-serif;
                        margin: 0;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    .container {{
                        max-width: 1200px;
                        margin: 0 auto;
                        background-color: white;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                    }}
                    h1 {{
                        color: #333;
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .summary {{
                        display: flex;
                        justify-content: space-around;
                        margin-bottom: 30px;
                        flex-wrap: wrap;
                    }}
                    .summary-item {{
                        text-align: center;
                        padding: 15px;
                        background-color: #f8f9fa;
                        border-radius: 6px;
                        min-width: 120px;
                        margin: 5px;
                    }}
                    .summary-number {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #007bff;
                    }}
                    .summary-label {{
                        color: #666;
                        margin-top: 5px;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 20px;
                    }}
                    th, td {{
                        padding: 12px;
                        text-align: left;
                        border-bottom: 1px solid #ddd;
                    }}
                    th {{
                        background-color: #f8f9fa;
                        font-weight: bold;
                    }}
                    .success {{
                        color: #28a745;
                    }}
                    .failed {{
                        color: #dc3545;
                    }}
                    .footer {{
                        margin-top: 30px;
                        text-align: center;
                        color: #666;
                        font-size: 14px;
                    }}
                    .status-success {{
                        background-color: #d4edda;
                        color: #155724;
                    }}
                    .status-failed {{
                        background-color: #f8d7da;
                        color: #721c24;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>批量{'条形码' if process_type == 'barcode' else '二维码'}生成报告</h1>
                    
                    <div class="summary">
                        <div class="summary-item">
                            <div class="summary-number">{total_count}</div>
                            <div class="summary-label">总数</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-number success">{success_count}</div>
                            <div class="summary-label">成功</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-number failed">{failed_count}</div>
                            <div class="summary-label">失败</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-number">{success_count/total_count*100 if total_count > 0 else 0:.1f}%</div>
                            <div class="summary-label">成功率</div>
                        </div>
                    </div>
                    
                    <h2>详细结果</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>序号</th>
                                <th>数据</th>
                                <th>文件名</th>
                                <th>状态</th>
                                <th>错误信息</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            # 添加结果行
            for i, result in enumerate(results, 1):
                status = "成功" if result['success'] else "失败"
                status_class = "status-success" if result['success'] else "status-failed"
                error_msg = result.get('error', '') if not result['success'] else ""
                
                html_content += f"""
                            <tr>
                                <td>{i}</td>
                                <td>{result.get('data', '')}</td>
                                <td>{result.get('filename', '')}</td>
                                <td class="{status_class}">{status}</td>
                                <td>{error_msg}</td>
                            </tr>
                """
            
            # 添加HTML结尾
            html_content += f"""
                        </tbody>
                    </table>
                    
                    <div class="footer">
                        <p>报告生成时间: {now}</p>
                        <p>输出目录: {output_dir}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # 写入HTML文件
            report_path = os.path.join(output_dir, f"batch_{process_type}_report.html")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            app_logger.info(f"HTML报告已生成: {report_path}")
            
        except Exception as e:
            if isinstance(e, (ValueError, OSError)):
                raise e
            raise OSError(f"创建HTML报告时发生错误: {str(e)}")
    
    def get_supported_file_formats(self) -> Dict[str, str]:
        """
        获取支持的文件格式
        
        Returns:
            Dict[str, str]: 支持的文件格式及描述
        """
        return {
            '.csv': 'CSV文件 (逗号分隔值)',
            '.txt': '文本文件 (每行一个数据)',
            '.json': 'JSON文件'
        }
    
    def get_csv_columns(self, file_path: str) -> Tuple[bool, List[str], str]:
        """
        获取CSV文件的列名
        
        Args:
            file_path (str): CSV文件路径
            
        Returns:
            Tuple[bool, List[str], str]: (是否成功, 列名列表, 错误信息)
        """
        try:
            if not os.path.isfile(file_path):
                return False, [], "文件不存在"
            
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext != '.csv':
                return False, [], "不是CSV文件"
            
            # 读取CSV文件的第一行获取列名
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                columns = next(reader, [])
            
            app_logger.info(f"获取CSV列名成功: {columns}")
            return True, columns, ""
            
        except Exception as e:
            error_msg = f"获取CSV列名失败: {str(e)}"
            app_logger.error(error_msg)
            return False, [], error_msg