import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication,
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


class FileTreeItem(QTreeWidgetItem):
    def __init__(self, path, parent=None):
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

    def sort_key(self, p):
        """排序函数，文件夹排在前面，其余按首字母排序"""
        return (p.is_file(), p.name.lower())


class FileMergeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("项目文件输出工具")
        self.setGeometry(100, 100, 1000, 800)
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setLayout(main_layout)

        self.setup_project_selector(main_layout)
        self.setup_file_tree_and_preview(main_layout)
        self.setup_export_buttons(main_layout)

        # 添加样式表
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #0078D4;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                font-family: 'Microsoft YaHei', Courier, monospace;
                margin: 4px 2px;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #004578;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QTreeWidget {
                background-color: white;
                border: 1px solid #ccc;
                padding: 10px;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #ccc;
                padding: 10px;
                font-family: 'Times New Roman', Courier, monospace;
                font-size: 14px;
                color: #333;
            }
        """
        )

    def setup_project_selector(self, layout):
        button_layout = QHBoxLayout()
        browse_button = QPushButton("选择项目根目录", self)
        browse_button.clicked.connect(self.browse_project)
        button_layout.addWidget(browse_button)

        self.project_label = QLabel("未选择项目根目录")
        button_layout.addWidget(self.project_label)

        layout.addLayout(button_layout)

    def setup_file_tree_and_preview(self, layout):
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

    def browse_project(self):
        directory = QFileDialog.getExistingDirectory(self, "选择项目根目录")
        if directory:
            self.project_label.setText(directory)
            self.file_tree.clear()
            root_item = FileTreeItem(directory)
            self.file_tree.addTopLevelItem(root_item)

    def handle_item_changed(self, item, column):
        if item.checkState(column) == Qt.Checked:
            self.check_children(item, True)
        elif item.checkState(column) == Qt.Unchecked:
            self.check_children(item, False)
        self.check_parents(item)

    def check_children(self, item, checked):
        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, Qt.Checked if checked else Qt.Unchecked)
            self.check_children(child, checked)

    def check_parents(self, item):
        parent = item.parent()
        if parent:
            all_checked = all(
                parent.child(i).checkState(0) == Qt.Checked
                for i in range(parent.childCount())
            )
            all_unchecked = all(
                parent.child(i).checkState(0) == Qt.Unchecked
                for i in range(parent.childCount())
            )
            if all_checked:
                parent.setCheckState(0, Qt.Checked)
            elif all_unchecked:
                parent.setCheckState(0, Qt.Unchecked)
            else:
                parent.setCheckState(0, Qt.PartiallyChecked)
            self.check_parents(parent)

    def preview_selected_files(self):
        if not self.file_tree.topLevelItem(0):
            self.alert("提示", "没有选择项目根目录。")
            return
        selected_files = self.get_selected_files(self.file_tree.topLevelItem(0))
        if not selected_files:
            self.alert("提示", "没有选择任何文件。")
            return

        preview_content = self.get_files_content(selected_files)
        self.preview_text.setPlainText(preview_content)

    def get_selected_files(self, item):
        files = []
        if item.checkState(0) == Qt.Checked and item.path.is_file():
            files.append(item.path)
        for i in range(item.childCount()):
            child = item.child(i)
            files.extend(self.get_selected_files(child))
        return files

    def get_files_content(self, files):
        file_structure = {}
        root_path = self.file_tree.topLevelItem(0).path
        for file in files:
            relative_path = file.relative_to(root_path)
            parts = relative_path.parts
            current_level = file_structure
            for part in parts[:-1]:
                current_level = current_level.setdefault(part, {})
            current_level[parts[-1]] = file

        def print_tree(tree, indent=""):
            content = ""
            for i, (key, value) in enumerate(tree.items()):
                connector = "└── " if i == len(tree) - 1 else "├── "
                if isinstance(value, dict):
                    content += indent + connector + key + "\n"
                    content += print_tree(
                        value, indent + ("    " if i == len(tree) - 1 else "│   ")
                    )
                else:
                    content += indent + connector + key + "\n"
            return content

        def print_files_content(tree, path=""):
            content = ""
            for key, value in tree.items():
                new_path = os.path.join(path, key)
                if isinstance(value, dict):
                    content += print_files_content(value, new_path)
                else:
                    relative_path = os.path.relpath(value, root_path)
                    content += f"**.\\{relative_path}**\n\n"
                    extension = Path(value).suffix.lower()
                    language = self.get_language_by_extension(extension)
                    content += f"```{language}\n"
                    try:
                        with open(value, "r", encoding="utf-8") as f:
                            file_content = f.read()
                        content += file_content
                    except UnicodeDecodeError:
                        content += "（无法读取文件内容 - 可能是二进制文件）"
                    content += "\n```\n\n\n---\n\n"
            return content

        structure_output = print_tree(file_structure)
        content_output = print_files_content(file_structure)
        return f"项目结构：\n\n{structure_output}\n---\n\n{content_output}"

    def get_language_by_extension(self, extension):
        """根据文件后缀名返回对应的语言标签"""
        extension_mapping = {
            ".py": "python",
            ".md": "markdown",
            ".js": "javascript",
            # 添加更多的扩展名映射
        }
        type = extension_mapping.get(extension, "")
        # 匹配不上的话去掉点号返回后缀名
        if not type:
            type = extension.lstrip(".")
        return type

    def export_files(self, file_type):
        content = self.preview_text.toPlainText()
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"保存文件", "", f"{file_type.upper()}文件 (*.{file_type})"
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)

    def alert(self, title, message):
        # 创建并显示消息框
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)  # 设置图标类型
        msg.setText(message)  # 设置消息文本
        msg.setWindowTitle(title)  # 设置窗口标题
        msg.setStandardButtons(QMessageBox.Ok)  # 设置标准按钮
        msg.exec_()  # 显示消息框


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setStyle("Fusion")
    window = FileMergeApp()
    window.show()
    sys.exit(app.exec_())
