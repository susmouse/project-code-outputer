import os
import re
from pathlib import Path
from typing import List, Dict, Any
from humanize import naturalsize
from fnmatch import fnmatch
from utils import is_path_excluded, sort_contents

# 默认选项
DEFAULT_OPTIONS = {
    # 是否显示隐藏文件
    'all_files': False,
    # 是否目录优先
    'dirs_first': False,
    # 是否仅显示目录
    'dirs_only': False,
    # 是否显示文件大小
    'sizes': False,
    # 忽略的文件模式
    'exclude': [],
    # 最大深度
    'max_depth': float('inf'),
    # 是否反向排序
    'reverse': False,
    # 是否在目录后添加斜杠
    'trailing_slash': False,
    # 是否使用ASCII字符
    'ascii': False
}

# 组成文件树的默认符号
SYMBOLS_ANSI = {
    'BRANCH': '├── ',
    'EMPTY': '',
    'INDENT': '    ',
    'LAST_BRANCH': '└── ',
    'VERTICAL': '│   '
}

# 组成文件树的ASCII符号
SYMBOLS_ASCII = {
    'BRANCH': '|-- ',
    'EMPTY': '',
    'INDENT': '    ',
    'LAST_BRANCH': '`-- ',
    'VERTICAL': '|   '
}

# 默认忽略的文件模式
EXCLUDED_PATTERNS = [re.compile(r'\.DS_Store')]

class FileTreeTextGenerator:
    def __init__(self, options: Dict[str, Any]):
        self.options = {**DEFAULT_OPTIONS, **options}
        self.ignore_patterns = []

    def _is_binary(self, path: Path) -> bool:
        """检查文件是否是二进制文件"""
        try:
            with open(path, 'rb') as f:
                return b'\x00' in f.read(1024)
        except:
            return True

    def _get_file_content(self, path: Path) -> str:
        """获取文件内容，如果是二进制文件则返回提示"""
        if self._is_binary(path):
            return f"{path} 可能是二进制文件，无法输出内容"
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            return f"{path} 可能是二进制文件，无法输出内容"
        except Exception as e:
            return f"无法读取文件内容: {str(e)}"

    def generate(self, path: str) -> str:
        path = Path(path)
        if self.options.get('use_gitignore', True):
            self._load_gitignore(path)
        
        tree_lines = self._print(path.name, path, 0, '', self.options)
        result = '\n'.join(tree_lines)
        
        if self.options.get('show_content', False):
            # 收集所有文件路径
            files = []
            self._collect_files(path, files, self.options)
            
            # 添加文件内容
            if files:
                result += "\n\n---\n\n"
                for file_path in files:
                    relative_path = file_path.relative_to(path)
                    extension = file_path.suffix.lstrip('.') or 'text'
                    content = self._get_file_content(file_path)
                    
                    result += f"**{relative_path}**\n\n```{extension}\n{content}\n```\n\n---\n\n"
        
        return result

    def _collect_files(self, path: Path, files: list, options: Dict[str, Any]):
        """递归收集所有符合条件的文件路径"""
        if path.is_file():
            if not is_path_excluded(path, EXCLUDED_PATTERNS + options['exclude'], self.ignore_patterns):
                files.append(path)
            return
        
        if path.is_dir():
            try:
                contents = sort_contents(os.listdir(path), path, options)
                if not options['all_files']:
                    contents = [c for c in contents if not self._is_hidden(c)]
                
                for content in contents:
                    self._collect_files(path / content, files, options)
            except (PermissionError, FileNotFoundError):
                pass

    def __init__(self, options: Dict[str, Any]):
        self.options = {**DEFAULT_OPTIONS, **options}
        self.ignore_patterns = []
        self._gitignore_cache = {}
        # 确保show_content选项被正确传递
        if 'show_content' not in self.options:
            self.options['show_content'] = False

    def _load_gitignore(self, path: Path):
        """递归加载.gitignore文件中的忽略规则，带缓存"""
        # 检查缓存
        cache_key = str(path.resolve())
        if cache_key in self._gitignore_cache:
            self.ignore_patterns.extend(self._gitignore_cache[cache_key])
            return
            
        # 如果当前路径已经在忽略模式中，则不再递归
        if any(fnmatch(str(path), pattern) for pattern in self.ignore_patterns):
            return
            
        # 加载当前目录的.gitignore
        gitignore_path = path / '.gitignore'
        patterns = []
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # 将.gitignore模式转换为正则表达式
                            pattern = line.rstrip('/')
                            if pattern.startswith('/'):
                                pattern = pattern[1:]
                            else:
                                pattern = '**/' + pattern
                            patterns.append(pattern)
            except (IOError, UnicodeDecodeError):
                pass
                
        # 更新缓存
        self._gitignore_cache[cache_key] = patterns
        self.ignore_patterns.extend(patterns)
        
        # 递归加载子目录的.gitignore
        try:
            for item in path.iterdir():
                if item.is_dir():
                    self._load_gitignore(item)
        except (PermissionError, FileNotFoundError):
            pass

    def _is_hidden(self, filename: str) -> bool:
        """
        * 检查文件名是否是隐藏文件
        * @param filename 要检查的文件名
        * @return 如果是隐藏文件则返回True，否则返回False
        """
        return filename.startswith('.')

    def _print(self, filename: str, path: Path, current_depth: int, preceding_symbols: str, options: Dict[str, Any], is_last: bool = False) -> List[str]:
        is_dir = path.is_dir()
        is_file = not is_dir

        lines = []
        symbols = SYMBOLS_ASCII if options['ascii'] else SYMBOLS_ANSI

        # 检查路径是否应该被排除
        if is_path_excluded(path, EXCLUDED_PATTERNS + options['exclude'], self.ignore_patterns):
            return lines

        # Handle directories only
        if is_file and options['dirs_only']:
            return lines

        # Handle max depth
        if current_depth > options['max_depth']:
            return lines

        # Build current line
        line = [preceding_symbols]
        if current_depth >= 1:
            line.append(symbols['LAST_BRANCH'] if is_last else symbols['BRANCH'])

        if is_file and options['sizes']:
            file_size = path.stat().st_size
            line.append(naturalsize(file_size).replace(' ', ''))
            line.append(' ')

        line.append(filename)
        if is_dir and options['trailing_slash']:
            line.append('/')
        lines.append(''.join(line))

        if is_file:
            return lines

        # 获取并排序目录内容
        contents = sort_contents(os.listdir(path), path, options)
        
        # 如果不需要显示隐藏文件
        if not options['all_files']:
            contents = [c for c in contents if not self._is_hidden(c)]
            
        # 如果设置了正则过滤
        if options['regex_filter']:
            import re
            try:
                pattern = re.compile(options['regex_filter'])
                # 匹配正则的文件不显示
                contents = [c for c in contents if not pattern.search(c)]
            except re.error:
                # 如果正则表达式无效，忽略过滤
                pass

        for i, content in enumerate(contents):
            is_current_last = i == len(contents) - 1
            new_lines = self._print(
                content,
                path / content,
                current_depth + 1,
                preceding_symbols + (symbols['INDENT'] if is_last else symbols['VERTICAL']),
                options,
                is_current_last
            )
            lines.extend(new_lines)

        return lines
