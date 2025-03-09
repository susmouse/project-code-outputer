from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QCheckBox, QSpinBox, QTextEdit,
                            QFileDialog)
from PyQt5.QtCore import Qt
from generator import FileTreeTextGenerator

class TreeGeneratorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("目录树生成器")
        self.setWindowState(Qt.WindowMaximized)  # 默认最大化窗口
        
        # 主控件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        
        # 路径输入
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("目录路径:"))
        self.path_input = QLineEdit()
        path_layout.addWidget(self.path_input)
        self.browse_button = QPushButton("浏览...")
        path_layout.addWidget(self.browse_button)
        layout.addLayout(path_layout)
        
        # 正则表达式过滤
        regex_layout = QHBoxLayout()
        regex_layout.addWidget(QLabel("正则过滤:"))
        self.regex_input = QLineEdit()
        self.regex_input.setPlaceholderText("输入正则表达式，匹配的文件将不显示")
        regex_layout.addWidget(self.regex_input)
        layout.addLayout(regex_layout)
        
        # 选项
        options_layout = QHBoxLayout()
        
        # 第一列
        col1 = QVBoxLayout()
        self.all_files_check = QCheckBox("显示隐藏文件")
        self.dirs_first_check = QCheckBox("目录优先")
        self.dirs_only_check = QCheckBox("仅显示目录")
        col1.addWidget(self.all_files_check)
        col1.addWidget(self.dirs_first_check)
        col1.addWidget(self.dirs_only_check)
        
        # 第二列
        col2 = QVBoxLayout()
        self.sizes_check = QCheckBox("显示文件大小")
        self.reverse_check = QCheckBox("反向排序")
        self.trailing_slash_check = QCheckBox("目录添加斜杠")
        self.trailing_slash_check.setChecked(True)
        col2.addWidget(self.sizes_check)
        col2.addWidget(self.reverse_check)
        col2.addWidget(self.trailing_slash_check)
        
        # 第三列
        col3 = QVBoxLayout()
        self.ascii_check = QCheckBox("使用ASCII字符")
        self.ignore_gitignore_check = QCheckBox("使用.gitignore")
        self.ignore_gitignore_check.setChecked(True)
        self.show_content_check = QCheckBox("显示文件内容")
        self.max_depth_label = QLabel("最大深度:")
        self.max_depth_spin = QSpinBox()
        self.max_depth_spin.setRange(1, 100)
        self.max_depth_spin.setValue(10)
        col3.addWidget(self.ascii_check)
        col3.addWidget(self.ignore_gitignore_check)
        col3.addWidget(self.show_content_check)
        col3.addWidget(self.max_depth_label)
        col3.addWidget(self.max_depth_spin)
        
        options_layout.addLayout(col1)
        options_layout.addLayout(col2)
        options_layout.addLayout(col3)
        layout.addLayout(options_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("生成目录树")
        self.copy_button = QPushButton("复制结果")
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.copy_button)
        layout.addLayout(button_layout)
        
        # 结果展示
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)
        
        main_widget.setLayout(layout)
        
        # 连接信号
        self.generate_button.clicked.connect(self.generate_tree)
        self.browse_button.clicked.connect(self.browse_directory)
        self.copy_button.clicked.connect(self.copy_result)
        
    def browse_directory(self):
        """打开目录选择对话框"""
        directory = QFileDialog.getExistingDirectory(self, "选择目录")
        if directory:
            self.path_input.setText(directory)

    def copy_result(self):
        """复制结果到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.result_text.toPlainText())

    def generate_tree(self):
        path = self.path_input.text()
        if not path:
            return
            
        options = {
            'all_files': self.all_files_check.isChecked(),
            'dirs_first': self.dirs_first_check.isChecked(),
            'dirs_only': self.dirs_only_check.isChecked(),
            'sizes': self.sizes_check.isChecked(),
            'max_depth': self.max_depth_spin.value(),
            'reverse': self.reverse_check.isChecked(),
            'trailing_slash': self.trailing_slash_check.isChecked(),
            'ascii': self.ascii_check.isChecked(),
            'use_gitignore': self.ignore_gitignore_check.isChecked(),
            'regex_filter': self.regex_input.text().strip() or None
        }
        
        generator = FileTreeTextGenerator(options)
        try:
            tree = generator.generate(path)
            self.result_text.setPlainText(tree)
        except Exception as e:
            self.result_text.setPlainText(f"错误: {str(e)}")

if __name__ == '__main__':
    app = QApplication([])
    window = TreeGeneratorGUI()
    window.show()
    app.exec_()
