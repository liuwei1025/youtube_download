"""
线程管理模块
"""

import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


class ThreadSafeProgress:
    """线程安全的进度条包装类"""
    def __init__(self, total=None, desc=None, unit=None):
        self.lock = threading.Lock()
        if HAS_TQDM:
            self.progress = tqdm(total=total, desc=desc, unit=unit)
        else:
            self.progress = None
            self.current = 0
            self.total = total
            self.desc = desc

    def update(self, n=1):
        with self.lock:
            if self.progress:
                self.progress.update(n)
            else:
                self.current += n
                if self.desc:
                    print(f"{self.desc}: {self.current}/{self.total}")

    def set_postfix_str(self, text):
        with self.lock:
            if self.progress:
                self.progress.set_postfix_str(text)
            else:
                print(f"{text}")

    def close(self):
        with self.lock:
            if self.progress:
                self.progress.close()


class ThreadPoolManager:
    """线程池管理器"""
    def __init__(self, max_workers=3):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.progress_lock = threading.Lock()
        self.results_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.executor.shutdown(wait=True)
        if exc_type:
            self.logger.error(f"线程池执行出错: {exc_val}")
            return False
        return True

    def wait_for_results(self, futures_dict: Dict[str, Any]) -> Dict[str, Any]:
        """等待并收集所有任务的结果"""
        results = {}
        try:
            if isinstance(futures_dict, dict):
                for key, future in futures_dict.items():
                    try:
                        results[key] = future.result()
                    except Exception as e:
                        self.logger.error(f"任务 {key} 执行失败: {e}")
                        results[key] = None
            else:  # List of futures
                for future in as_completed(futures_dict):
                    try:
                        result = future.result()
                        with self.results_lock:
                            if isinstance(result, dict):
                                results.update(result)
                            else:
                                results[id(future)] = result
                    except Exception as e:
                        self.logger.error(f"任务执行失败: {e}")
        except Exception as e:
            self.logger.error(f"等待任务结果时出错: {e}")
        return results

