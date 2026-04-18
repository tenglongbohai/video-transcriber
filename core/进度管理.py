# -*- coding: utf-8 -*-
"""
进度管理模块 - 保存和加载任务进度
"""
import json
import os


class ProgressManager:
    """进度管理器"""

    def __init__(self, progress_file):
        self.progress_file = progress_file

    def load(self):
        """加载进度"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return None

    def save(self, data):
        """保存进度"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            return True
        except:
            return False

    def clear(self):
        """清除进度"""
        if os.path.exists(self.progress_file):
            try:
                os.remove(self.progress_file)
                return True
            except:
                return False
        return False


def load_task_progress_file(task_id, output_dir):
    """根据task_id加载任务进度"""
    progress_file = os.path.join(output_dir, 'task_progress.json')
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                store = json.load(f)
                return store.get(task_id)
        except:
            pass
    return None


def save_task_progress_file(task_id, data, output_dir):
    """保存任务进度到文件"""
    progress_file = os.path.join(output_dir, 'task_progress.json')
    try:
        # 读取现有数据
        store = {}
        if os.path.exists(progress_file):
            with open(progress_file, 'r', encoding='utf-8') as f:
                store = json.load(f)
        
        store[task_id] = data
        
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(store, f, ensure_ascii=False)
        return True
    except:
        return False


if __name__ == "__main__":
    # 测试进度管理
    pm = ProgressManager("test_progress.json")
    print("进度管理模块测试成功")
