from PyQt5.QtWidgets import QTreeWidget
from PyQt5.QtCore import Qt
import os
import json

class CollectionTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._main_window = None  # 运行时注入

    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        if event.source() == self:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """拖拽移动事件"""
        if event.source() == self:
            # 获取拖拽的目标项
            target_item = self.itemAt(event.pos())
            
            if target_item:
                # 简单验证：确保有目标项
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event):
        """拖拽放置事件"""
        if event.source() != self:
            event.ignore()
            return
            
        # 获取拖拽的目标项
        target_item = self.itemAt(event.pos())
        
        if not target_item:
            event.ignore()
            return
        
        # 让Qt完成默认的拖拽操作
        super().dropEvent(event)
        
        # 拖拽后处理 - 直接保存，不依赖复杂的键值匹配
        if self._main_window and event.isAccepted():
            try:
                # 强制保存所有数据
                self._main_window.save_all()
                self._main_window.log_info(f'拖拽完成并立即保存')
                
                # 更新所有Tab标签路径 - 重新扫描整个树结构
                self._main_window.update_all_tabs_after_drag()
                
                # 验证保存是否成功
                user_data_dir = os.path.join(self._main_window._workspace_dir, 'user-data')
                collections_path = os.path.join(user_data_dir, 'collections.json')
                
                if os.path.exists(collections_path):
                    with open(collections_path, 'r', encoding='utf-8') as f:
                        saved_data = json.load(f)
                    
                    # 统计保存的数据
                    collections_count = 0
                    requests_count = 0
                    
                    def count_items(items):
                        nonlocal collections_count, requests_count
                        for item in items:
                            if item.get('type') == 'collection':
                                collections_count += 1
                                if 'children' in item:
                                    count_items(item['children'])
                            elif item.get('type') == 'request':
                                requests_count += 1
                    
                    count_items(saved_data)
                    
                    self._main_window.log_info(f'✅ 拖拽持久化成功: {collections_count} 个集合, {requests_count} 个请求')
                    
                    # 显示状态栏提示（如果有的话）
                    if hasattr(self._main_window, 'statusBar'):
                        self._main_window.statusBar().showMessage(f'拖拽完成并已保存', 3000)
                else:
                    self._main_window.log_warning('❌ collections.json 文件未找到，保存可能失败')
                    if hasattr(self._main_window, 'statusBar'):
                        self._main_window.statusBar().showMessage('保存失败：文件未创建', 3000)
                        
            except Exception as e:
                self._main_window.log_error(f'❌ 拖拽后保存失败: {e}')
                if hasattr(self._main_window, 'statusBar'):
                    self._main_window.statusBar().showMessage(f'保存失败: {str(e)}', 3000)
    
    def _find_item_by_key(self, item_key):
        """根据键找到对应的QTreeWidgetItem"""
        if not item_key:
            return None
        
        # 解析键
        path_part = item_key.split(':')[0]
        path_parts = path_part.split('/')
        
        # 从根开始查找
        for i in range(self.topLevelItemCount()):
            top_item = self.topLevelItem(i)
            if top_item.text(0) == path_parts[0]:
                if len(path_parts) == 1:
                    return top_item
                else:
                    return self._find_item_recursive(top_item, path_parts[1:])
        
        return None
    
    def _find_item_recursive(self, parent_item, path_parts):
        """递归查找项"""
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            if child.text(0) == path_parts[0]:
                if len(path_parts) == 1:
                    return child
                else:
                    return self._find_item_recursive(child, path_parts[1:])
        
        return None

    def _is_valid_drop(self, source_item, target_item):
        """验证拖拽规则"""
        def is_collection(item):
            # Collection：有子项或者是顶级项（没有父项）
            return item.parent() is None or item.childCount() >= 0
            
        def is_request(item):
            # Request：没有子项且有父项
            return item.childCount() == 0 and item.parent() is not None
            
        source_is_collection = is_collection(source_item)
        source_is_request = is_request(source_item)
        target_is_collection = is_collection(target_item)
        target_is_request = is_request(target_item)
        
        # 验证拖拽规则
        if source_is_collection and target_is_collection:
            # Collection可以拖拽到Collection下
            return True
        elif source_is_request and target_is_collection:
            # Request可以拖拽到Collection下
            return True
        elif source_is_collection and target_is_request:
            # Collection不能拖拽到Request下
            return False
        elif source_is_request and target_is_request:
            # Request不能拖拽到Request下
            return False
        else:
            # 其他情况不允许拖拽
            return False

    def _is_child_of(self, parent, child):
        """检查child是否是parent的子项"""
        for i in range(parent.childCount()):
            if parent.child(i) == child:
                return True
            if self._is_child_of(parent.child(i), child):
                return True
        return False 