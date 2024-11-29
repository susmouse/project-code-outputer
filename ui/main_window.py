"""
主窗口UI模块
实现主要的用户界面和交互逻辑
"""

import json

# 文件树黑名单（控制完整输出文件树时，不显示在文件树的文件）
BLACK_LIST = []
try:
    with open("./config.jsonc", "r", encoding="utf-8") as config_file:
        BLACK_LIST = json.load(config_file).get("black_list", [])
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading config: {e}")
    BLACK_LIST = []

from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTreeWidget,
    QFileDialog,
    QTreeWidgetItem,
    QTextEdit,
    QPushButton,
    QLabel,
    QMessageBox,
    QCheckBox,
)
from PyQt5.QtCore import Qt

from models.file_tree_item import FileTreeItem
from utils.file_utils import (
    generate_file_structure,
    print_tree_structure,
    generate_files_content,
)


class FileMergeApp(QMainWindow):
    """
    文件合并应用主窗口类
    实现项目文件的选择、预览和导出功能
    """

    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        self.setWindowTitle("项目文件输出工具")
        self.setGeometry(100, 100, 1000, 800)
        self.show_complete_tree = False  # 添加开关状态变量
        self.initUI()

    def initUI(self):
        """初始化用户界面"""
        main_layout = QVBoxLayout()
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setLayout(main_layout)

        self.setup_project_selector(main_layout)
        self.setup_file_tree_and_preview(main_layout)
        self.setup_export_buttons(main_layout)
        self.apply_styles()

    def setup_project_selector(self, layout):
        """设置项目选择器部分"""
        button_layout = QHBoxLayout()
        browse_button = QPushButton("选择项目根目录", self)
        browse_button.clicked.connect(self.browse_project)
        button_layout.addWidget(browse_button)

        self.project_label = QLabel("未选择项目根目录")
        button_layout.addWidget(self.project_label)

        # 添加显示完整树的复选框
        self.complete_tree_checkbox = QCheckBox("显示完整文件树", self)
        self.complete_tree_checkbox.setChecked(self.show_complete_tree)
        self.complete_tree_checkbox.stateChanged.connect(self.toggle_tree_mode)
        button_layout.addWidget(self.complete_tree_checkbox)

        layout.addLayout(button_layout)

    def setup_file_tree_and_preview(self, layout):
        """设置文件树和预览区域"""
        content_layout = QHBoxLayout()

        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabel("请选择要输出内容的文件：")
        self.file_tree.itemChanged.connect(self.handle_item_changed)
        content_layout.addWidget(self.file_tree)

        preview_layout = QVBoxLayout()
        preview_label = QLabel("预览")
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(preview_label)
        preview_layout.addWidget(self.preview_text)

        content_layout.addLayout(preview_layout)
        layout.addLayout(content_layout)

    def setup_export_buttons(self, layout):
        """设置导出按钮"""
        button_layout = QHBoxLayout()

        preview_button = QPushButton("预览", self)
        preview_button.clicked.connect(self.preview_selected_files)
        button_layout.addWidget(preview_button)

        export_txt_button = QPushButton("导出TXT", self)
        export_txt_button.clicked.connect(lambda: self.export_files("txt"))
        button_layout.addWidget(export_txt_button)

        export_md_button = QPushButton("导出MD", self)
        export_md_button.clicked.connect(lambda: self.export_files("md"))
        button_layout.addWidget(export_md_button)

        layout.addLayout(button_layout)

    def apply_styles(self):
        """应用界面样式"""

        # 读取当前目录下`style.css`文件的内容
        with open("ui/style.css", "r", encoding="utf-8") as file:
            style = file.read()

        self.setStyleSheet(style)

    def browse_project(self):
        """浏览并选择项目目录"""
        directory = QFileDialog.getExistingDirectory(self, "选择项目根目录")
        if directory:
            self.project_label.setText(directory)
            self.file_tree.clear()
            root_item = FileTreeItem(directory)
            self.file_tree.addTopLevelItem(root_item)

    def handle_item_changed(self, item, column):
        """处理文件树项选中状态变化"""
        if item.checkState(column) == Qt.Checked:
            self.check_children(item, True)
        elif item.checkState(column) == Qt.Unchecked:
            self.check_children(item, False)
        self.check_parents(item)

    def check_children(self, item, checked):
        """递归设置子项的选中状态"""
        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, Qt.Checked if checked else Qt.Unchecked)
            self.check_children(child, checked)

    def check_parents(self, item):
        """更新父项的选中状态"""
        parent = item.parent()
        if parent:
            children_states = [
                parent.child(i).checkState(0) for i in range(parent.childCount())
            ]
            if all(state == Qt.Checked for state in children_states):
                parent.setCheckState(0, Qt.Checked)
            elif all(state == Qt.Unchecked for state in children_states):
                parent.setCheckState(0, Qt.Unchecked)
            else:
                parent.setCheckState(0, Qt.PartiallyChecked)
            self.check_parents(parent)

    def get_selected_files(self, item):
        """获取选中的文件列表"""
        files = []
        if item.checkState(0) == Qt.Checked and item.path.is_file():
            files.append(item.path)
        for i in range(item.childCount()):
            child = item.child(i)
            files.extend(self.get_selected_files(child))
        return files

    def get_all_files(self, item):
        """获取项目中的所有文件列表，排除黑名单中的文件和目录"""
        files = []
        if item.path.is_file() and not any(
            item.path.match(pattern) for pattern in BLACK_LIST
        ):
            files.append(item.path)
        elif item.path.is_dir() and not any(
            item.path.match(pattern) for pattern in BLACK_LIST
        ):
            for i in range(item.childCount()):
                child = item.child(i)
                files.extend(self.get_all_files(child))
        return files

    def toggle_tree_mode(self, state):
        """切换文件树显示模式"""
        self.show_complete_tree = bool(state)
        # if self.file_tree.topLevelItem(0):
        #     self.preview_selected_files()

    def preview_selected_files(self):
        """预览选中的文件"""
        if not self.file_tree.topLevelItem(0):
            self.alert("提示", "没有选择项目根目录。")
            return

        # 获取根目录项
        root_item = self.file_tree.topLevelItem(0)
        root_path = root_item.path

        # 根据开关状态决定使用哪种方式获取文件
        if self.show_complete_tree:
            files_for_structure = self.get_all_files(root_item)
        else:
            files_for_structure = self.get_selected_files(root_item)

        if not files_for_structure:
            self.alert("提示", "没有选择任何文件。")
            return

        # 生成文件树结构
        file_structure = generate_file_structure(files_for_structure, root_path)
        structure_output = print_tree_structure(file_structure)

        # 只为选中的文件生成内容
        selected_files = self.get_selected_files(root_item)
        selected_file_structure = generate_file_structure(selected_files, root_path)
        content_output = generate_files_content(selected_file_structure, root_path)

        self.preview_text.setPlainText(
            f"项目结构：\n\n{structure_output}\n---\n\n{content_output}"
        )

    def export_files(self, file_type):
        """导出文件内容"""
        content = self.preview_text.toPlainText()
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"保存文件", "", f"{file_type.upper()}文件 (*.{file_type})"
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)

    def alert(self, title, message):
        """显示警告对话框"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
