"""
主窗口UI模块
实现主要的用户界面和交互逻辑
"""

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
        layout.addLayout(button_layout)

    def setup_file_tree_and_preview(self, layout):
        """设置文件树和预览区域"""
        content_layout = QHBoxLayout()

        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabel("项目文件")
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
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f5f6fa;
            }
            
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 10px 25px;
                font-size: 14px;
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
                border-radius: 4px;
                min-width: 100px;
                margin: 4px;
                transition: background-color 0.3s;
            }
            
            QPushButton:hover {
                background-color: #357abd;
            }
            
            QPushButton:pressed {
                background-color: #2d6da3;
            }
            
            QLabel {
                font-size: 14px;
                color: #2c3e50;
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
                padding: 5px;
            }
            
            QTreeWidget {
                background-color: white;
                border: 1px solid #e1e1e1;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
                selection-background-color: #e8f0fe;
                selection-color: #2c3e50;
            }
            
            QTreeWidget::item {
                padding: 5px;
                border-radius: 4px;
            }
            
            QTreeWidget::item:hover {
                background-color: #f8f9fa;
            }
            
            QTreeWidget::item:selected {
                background-color: #e8f0fe;
                color: #2c3e50;
            }
            
            QTextEdit {
                background-color: white;
                border: 1px solid #e1e1e1;
                border-radius: 6px;
                padding: 15px;
                font-family: 'Consolas', 'Source Code Pro', monospace;
                font-size: 14px;
                color: #2c3e50;
                selection-background-color: #4a90e2;
                selection-color: white;
            }
            
            QScrollBar:vertical {
                border: none;
                background-color: #f5f6fa;
                width: 10px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #c1c1c1;
                border-radius: 5px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #a8a8a8;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar:horizontal {
                border: none;
                background-color: #f5f6fa;
                height: 10px;
                margin: 0px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #c1c1c1;
                border-radius: 5px;
                min-width: 20px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #a8a8a8;
            }
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            """
        )

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

    def preview_selected_files(self):
        """预览选中的文件"""
        if not self.file_tree.topLevelItem(0):
            self.alert("提示", "没有选择项目根目录。")
            return
        selected_files = self.get_selected_files(self.file_tree.topLevelItem(0))
        if not selected_files:
            self.alert("提示", "没有选择任何文件。")
            return

        root_path = self.file_tree.topLevelItem(0).path
        file_structure = generate_file_structure(selected_files, root_path)
        structure_output = print_tree_structure(file_structure)
        content_output = generate_files_content(file_structure, root_path)

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
