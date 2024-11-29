"""
文件树节点模型模块
用于表示文件树中的文件和目录项
"""

from pathlib import Path
from PyQt5.QtWidgets import QTreeWidgetItem, QApplication
from PyQt5.QtCore import Qt


class FileTreeItem(QTreeWidgetItem):
    """
    文件树节点类
    用于在树形视图中展示文件和目录，支持复选框选择

    属性:
        path: Path对象，表示文件或目录的路径
    """

    def __init__(self, path, parent=None):
        """
        初始化文件树节点

        参数:
            path: 文件或目录的路径
            parent: 父节点，默认为None
        """
        super().__init__(parent)
        self.path = Path(path)
        self.setText(0, self.path.name)
        self.setCheckState(0, Qt.Unchecked)

        if self.path.is_dir():
            self.setIcon(
                0, QApplication.style().standardIcon(QApplication.style().SP_DirIcon)
            )
            self.addChildren(
                [
                    FileTreeItem(child, self)
                    for child in sorted(self.path.iterdir(), key=self.sort_key)
                ]
            )
        else:
            self.setIcon(
                0, QApplication.style().standardIcon(QApplication.style().SP_FileIcon)
            )

    @staticmethod
    def sort_key(p):
        """
        文件排序键函数

        参数:
            p: Path对象

        返回:
            tuple: (是否为文件, 小写文件名)，用于确保目录排在文件前面
        """
        return (p.is_file(), p.name.lower())
