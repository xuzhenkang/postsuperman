from PyQt5.QtWidgets import QTreeWidget
from PyQt5.QtCore import Qt

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
            # 获取拖拽的源项和目标项
            source_item = self.currentItem()
            target_item = self.itemAt(event.pos())
            
            if source_item and target_item and source_item != target_item:
                # 验证拖拽规则
                if self._is_valid_drop(source_item, target_item):
                    event.acceptProposedAction()
                else:
                    event.ignore()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event):
        """拖拽放置事件"""
        if event.source() != self:
            event.ignore()
            return
            
        # 获取拖拽的源项和目标项
        source_item = self.currentItem()
        target_item = self.itemAt(event.pos())
        
        if not source_item or not target_item or source_item == target_item:
            event.ignore()
            return
            
        # 验证拖拽规则
        if not self._is_valid_drop(source_item, target_item):
            event.ignore()
            return
            
        # 检查是否拖拽到自己的子项
        if self._is_child_of(source_item, target_item):
            event.ignore()
            return
            
        # 拖拽前记录状态
        parent_map_before = self._main_window._get_parent_map() if self._main_window else {}
        
        # 让Qt完成默认的拖拽操作
        super().dropEvent(event)
        
        # 拖拽后处理
        if self._main_window and event.isAccepted():
            parent_map_after = self._main_window._get_parent_map()
            moved_items = []
            
            # 找出被移动的项
            for item, parent_before in parent_map_before.items():
                parent_after = parent_map_after.get(item, None)
                if parent_before != parent_after:
                    moved_items.append(item)
            
            # 处理被移动的项
            if moved_items:
                moved_item = moved_items[0]
                self._main_window.log_info(f'检测到拖拽: {moved_item.text(0)}')
                
                # 更新Tab路径
                old_paths = self._main_window.get_item_paths_for_tabs(moved_item)
                self._main_window.update_tabs_after_drag(moved_item, old_paths)
                
                # 保存到collections.json
                self._main_window.save_all()
                self._main_window.log_info(f'拖拽完成: {moved_item.text(0)}')

    def _is_valid_drop(self, source_item, target_item):
        """验证拖拽规则"""
        def is_collection(item):
            return item.childCount() > 0
            
        def is_request(item):
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
            # 其他情况（如顶级项）不允许拖拽
            return False

    def _is_child_of(self, parent, child):
        """检查child是否是parent的子项"""
        for i in range(parent.childCount()):
            if parent.child(i) == child:
                return True
            if self._is_child_of(parent.child(i), child):
                return True
        return False 