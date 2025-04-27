#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MinerU Web UI 工具类

这个模块提供了一些辅助功能，用于支持web UI应用程序。
"""

import os
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Callable, Optional
from loguru import logger


class ParallelProcessor:
    """并行处理器类，支持并行处理文件以提高效率"""
    
    def __init__(self, max_workers: int = None):
        """
        初始化并行处理器
        
        Args:
            max_workers: 最大工作线程数，默认为None（由系统决定）
        """
        # 如果未指定，使用CPU核心数的2倍
        if max_workers is None:
            import multiprocessing
            max_workers = multiprocessing.cpu_count() * 2
            
        self.max_workers = max_workers
        logger.info(f"初始化并行处理器，最大工作线程数: {max_workers}")
    
    def process_items(self, 
                      items: List[Any], 
                      process_func: Callable[[Any], Any],
                      callback: Optional[Callable[[Any, Any], None]] = None) -> List[Any]:
        """
        并行处理多个项目
        
        Args:
            items: 需要处理的项目列表
            process_func: 处理单个项目的函数，接收一个项目作为参数
            callback: 回调函数，在每个项目处理完成后调用，接收原始项目和处理结果
            
        Returns:
            处理结果列表
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 创建futures
            future_to_item = {
                executor.submit(process_func, item): item for item in items
            }
            
            # 处理结果
            for future in future_to_item:
                try:
                    result = future.result()
                    results.append(result)
                    
                    # 如果有回调函数，调用它
                    if callback:
                        item = future_to_item[future]
                        callback(item, result)
                        
                except Exception as e:
                    logger.error(f"处理项目时出错: {e}")
        
        return results


class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def get_file_type(file_path: str) -> str:
        """
        获取文件类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件类型（pdf、docx、image等）
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return 'pdf'
        elif ext in ['.doc', '.docx']:
            return 'docx'
        elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
            return 'image'
        else:
            return 'unknown'
    
    @staticmethod
    def ensure_dir(directory: str) -> str:
        """
        确保目录存在，如果不存在则创建
        
        Args:
            directory: 目录路径
            
        Returns:
            目录路径
        """
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        return directory
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """
        清理文件名，移除不合法字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            清理后的文件名
        """
        # 移除不合法字符
        illegal_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in illegal_chars:
            filename = filename.replace(char, '_')
        return filename


class ProgressTracker:
    """进度跟踪器，用于跟踪任务处理进度"""
    
    def __init__(self, total: int, description: str = "处理进度"):
        """
        初始化进度跟踪器
        
        Args:
            total: 任务总数
            description: 进度描述
        """
        self.total = total
        self.current = 0
        self.description = description
        self.lock = threading.Lock()
        
    def update(self, increment: int = 1) -> Dict[str, Any]:
        """
        更新进度
        
        Args:
            increment: 增量值
            
        Returns:
            包含进度信息的字典
        """
        with self.lock:
            self.current += increment
            progress = min(self.current / self.total, 1.0)
            percentage = progress * 100
            
            logger.info(f"{self.description}: {percentage:.2f}% ({self.current}/{self.total})")
            
            return {
                "current": self.current,
                "total": self.total,
                "progress": progress,
                "percentage": percentage
            }
    
    def get_progress(self) -> Dict[str, Any]:
        """
        获取当前进度信息
        
        Returns:
            包含进度信息的字典
        """
        with self.lock:
            progress = min(self.current / self.total, 1.0)
            percentage = progress * 100
            
            return {
                "current": self.current,
                "total": self.total,
                "progress": progress,
                "percentage": percentage
            } 