#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from typing import Dict, List, Optional
from PyQt5.QtCore import Qt


class CollectionManager:
    """集合管理器"""
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        # 确保user-data目录存在
        user_data_dir = os.path.join(workspace_dir, 'user-data')
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
        self.collections_file = os.path.join(user_data_dir, 'collections.json')
        
    def load_collections(self) -> List[Dict]:
        """加载集合数据"""
        if not os.path.exists(self.collections_file):
            return []
            
        try:
            with open(self.collections_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
            
    def save_collections(self, collections: List[Dict]) -> bool:
        """保存集合数据"""
        try:
            with open(self.collections_file, 'w', encoding='utf-8') as f:
                json.dump(collections, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
            
    def find_request_by_name(self, name: str, collections: List[Dict]) -> Optional[Dict]:
        """根据名称查找请求"""
        def search_in_collection(collection):
            for item in collection.get('children', []):
                if item.get('type') == 'request' and item.get('name') == name:
                    return item.get('request')
                elif item.get('type') == 'collection':
                    result = search_in_collection(item)
                    if result:
                        return result
            return None
            
        for collection in collections:
            result = search_in_collection(collection)
            if result:
                return result
        return None
        
    def serialize_collections(self, tree_items) -> List[Dict]:
        """序列化集合树"""
        def serialize_item(item):
            if item.childCount() == 0:  # request
                req_data = item.data(0, Qt.UserRole)
                if not req_data:
                    return None  # 未保存的request不导出
                return {
                    'name': item.text(0),
                    'type': 'request',
                    'request': req_data
                }
            else:
                # Collection节点，即使没有子项也要保存
                children = []
                for i in range(item.childCount()):
                    child_result = serialize_item(item.child(i))
                    if child_result:
                        children.append(child_result)
                return {
                    'name': item.text(0),
                    'type': 'collection',
                    'children': children
                }
                
        data = []
        for i in range(tree_items.topLevelItemCount()):
            node = serialize_item(tree_items.topLevelItem(i))
            if node:
                data.append(node)
        return data 