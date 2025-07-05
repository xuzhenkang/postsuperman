#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import multiprocessing as mp
import requests
import json
import time
import os
import sys
from PyQt5.QtCore import QObject, pyqtSignal, QTimer


def run_request_process(method, url, params, headers, data, json_data, files, result_queue, error_queue, stop_event):
    """在子进程中执行请求的独立函数"""
    try:
        # 构建请求参数
        request_kwargs = {
            'url': url,
            'method': method,
            'timeout': 30  # 可以设置更长的超时，因为可以强制kill
        }
        
        # 添加参数
        if params:
            request_kwargs['params'] = {p['key']: p['value'] for p in params if p.get('key')}
            
        # 添加头部
        if headers:
            request_kwargs['headers'] = {h['key']: h['value'] for h in headers if h.get('key')}
            
        # 添加数据
        if data:
            request_kwargs['data'] = data
        elif json_data:
            request_kwargs['json'] = json_data
        elif files:
            request_kwargs['files'] = files
        
        # 检查停止标志
        if stop_event.is_set():
            return
            
        # 发送请求
        response = requests.request(**request_kwargs)
        
        # 请求完成后再次检查停止标志
        if stop_event.is_set():
            return
            
        # 构建响应数据
        result = {
            'status_code': response.status_code,
            'status_text': f"{response.status_code} {response.reason}",
            'headers': dict(response.headers),
            'body': response.text,
            'url': response.url,
            'elapsed': response.elapsed.total_seconds()
        }
        
        result_queue.put(result)
        
    except requests.exceptions.RequestException as e:
        if not stop_event.is_set():
            error_queue.put(str(e))
    except Exception as e:
        if not stop_event.is_set():
            error_queue.put(f"Unexpected error: {str(e)}")


class MultiprocessRequestWorker(QObject):
    """多进程请求工作器"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    stopped = pyqtSignal()
    
    def __init__(self, method, url, params, headers, data, json_data, files):
        super().__init__()
        self.method = method
        self.url = url
        self.params = params
        self.headers = headers
        self.data = data
        self.json_data = json_data
        self.files = files
        self._process = None
        self._stop_flag = False
        self._timer = None
        
    def stop(self):
        """停止请求 - 强制kill子进程"""
        self._stop_flag = True
        if self._process and self._process.is_alive():
            try:
                self._process.terminate()  # 先尝试优雅终止
                self._process.join(timeout=0.5)  # 最多等0.5秒
                if self._process.is_alive():
                    self._process.kill()  # 强制kill
                    self._process.join(timeout=0.1)
            except Exception as e:
                print(f"停止进程时出错: {e}")
            finally:
                self._process = None
        if self._timer:
            self._timer.stop()
            self._timer = None
        # 重置状态
        self._stop_flag = False
        
    def start_request(self):
        """启动请求进程"""
        try:
            # 创建进程间通信对象
            result_queue = mp.Queue()
            error_queue = mp.Queue()
            stop_event = mp.Event()
            
            # 创建子进程
            self._process = mp.Process(
                target=run_request_process,
                args=(self.method, self.url, self.params, self.headers, 
                      self.data, self.json_data, self.files, 
                      result_queue, error_queue, stop_event)
            )
            
            # 启动进程
            self._process.start()
            
            # 创建定时器轮询结果
            self._timer = QTimer()
            self._timer.timeout.connect(self._create_check_callback(result_queue, error_queue, stop_event))
            self._timer.start(50)  # 每50ms检查一次
            
        except Exception as e:
            self.error.emit(f"启动请求进程失败: {str(e)}")
            
    def _create_check_callback(self, result_queue, error_queue, stop_event):
        """创建检查回调函数"""
        def check_callback():
            self._check_result(result_queue, error_queue, stop_event)
        return check_callback
            
    def _check_result(self, result_queue, error_queue, stop_event):
        """检查进程结果"""
        # 检查停止标志
        if self._stop_flag:
            stop_event.set()
            self.stop()
            self.stopped.emit()
            return
        
        # 检查进程是否还活着
        if self._process and not self._process.is_alive():
            # 进程已结束，检查是否有结果
            try:
                if not result_queue.empty():
                    result = result_queue.get_nowait()
                    self.finished.emit(result)
                    self.stop()
                    return
            except:
                pass
                
            try:
                if not error_queue.empty():
                    error_msg = error_queue.get_nowait()
                    self.error.emit(error_msg)
                    self.stop()
                    return
            except:
                pass
            
            # 如果没有结果且进程已结束，可能是被停止的
            if self._stop_flag:
                self.stopped.emit()
            else:
                self.error.emit("请求进程意外结束")
            self.stop()
            return
        
        # 检查是否有结果
        try:
            if not result_queue.empty():
                result = result_queue.get_nowait()
                self.finished.emit(result)
                self.stop()
                return
        except:
            pass
        
        try:
            if not error_queue.empty():
                error_msg = error_queue.get_nowait()
                self.error.emit(error_msg)
                self.stop()
                return
        except:
            pass 