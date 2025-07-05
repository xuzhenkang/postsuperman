#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QObject, pyqtSignal
import requests
import json
import time
import threading


class RequestWorker(QObject):
    """请求工作线程 - 使用threading版本"""
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
        self._stop_flag = False
        self._thread = None
        
    def stop(self):
        """停止请求"""
        try:
            print("RequestWorker: 设置停止标志")
            self._stop_flag = True
            print("RequestWorker: 停止标志已设置")
        except Exception as e:
            print(f"RequestWorker.stop() 出错: {e}")
        
    def start(self):
        """启动请求线程"""
        try:
            print("RequestWorker: 启动请求线程")
            self._thread = threading.Thread(target=self.run)
            self._thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
            self._thread.start()
        except Exception as e:
            print(f"RequestWorker.start() 出错: {e}")
        
    def run(self):
        """执行请求"""
        try:
            print("RequestWorker: 开始执行请求")
            if self._stop_flag:
                print("RequestWorker: 请求被停止")
                self.stopped.emit()
                return
                
            # 构建请求参数
            request_kwargs = {
                'url': self.url,
                'method': self.method,
                'timeout': None  # 无超时限制，一直等待服务器响应
            }
            
            # 添加参数
            if self.params:
                request_kwargs['params'] = {p['key']: p['value'] for p in self.params if p.get('key')}
                
            # 添加头部
            if self.headers:
                request_kwargs['headers'] = {h['key']: h['value'] for h in self.headers if h.get('key')}
                
            # 添加数据
            if self.data:
                request_kwargs['data'] = self.data
            elif self.json_data:
                request_kwargs['json'] = self.json_data
            elif self.files:
                request_kwargs['files'] = self.files
                
            # 发送请求前再次检查停止标志
            if self._stop_flag:
                print("RequestWorker: 请求发送前被停止")
                self.stopped.emit()
                return
                
            print(f"RequestWorker: 发送请求 {self.method} {self.url}")
            
            # 使用requests发送请求
            response = requests.request(**request_kwargs)
            
            # 请求完成后立即检查停止标志
            if self._stop_flag:
                print("RequestWorker: 请求完成后被停止")
                self.stopped.emit()
                return
                
            print(f"RequestWorker: 请求完成，状态码 {response.status_code}")
            
            # 构建响应数据
            result = {
                'status_code': response.status_code,
                'status_text': f"{response.status_code} {response.reason}",
                'headers': dict(response.headers),
                'body': response.text,
                'url': response.url,
                'elapsed': response.elapsed.total_seconds()
            }
            
            self.finished.emit(result)
            
        except requests.exceptions.RequestException as e:
            if not self._stop_flag:
                print(f"RequestWorker: 请求异常 {e}")
                self.error.emit(str(e))
            else:
                print("RequestWorker: 请求异常但已停止")
                self.stopped.emit()
        except Exception as e:
            if not self._stop_flag:
                print(f"RequestWorker: 意外错误 {e}")
                self.error.emit(f"Unexpected error: {str(e)}")
            else:
                print("RequestWorker: 意外错误但已停止")
                self.stopped.emit()
        finally:
            print("RequestWorker: 线程执行完成")

    def __del__(self):
        """析构函数，确保资源清理"""
        try:
            if hasattr(self, '_thread') and self._thread and self._thread.is_alive():
                print("RequestWorker: 析构时检测到线程还在运行")
                self._stop_flag = True
        except Exception as e:
            print(f"RequestWorker.__del__ 出错: {e}")
    
    def cleanup(self):
        """手动清理资源"""
        try:
            print("RequestWorker: 手动清理资源")
            self._stop_flag = True
            if hasattr(self, '_thread') and self._thread:
                self._thread = None
        except Exception as e:
            print(f"RequestWorker.cleanup 出错: {e}") 