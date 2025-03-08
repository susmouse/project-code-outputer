"""
文件处理工具模块
提供文件内容读取和导出相关的功能
"""

from pathlib import Path
import json

EXTENSION_MAPPING = {}
try:
    with open("./config.json", "r", encoding="utf-8") as config_file:
        EXTENSION_MAPPING = json.load(config_file).get("extension_mapping", {})
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading config: {e}")
    EXTENSION_MAPPING = {}


def get_language_by_extension(extension):
    """
    * 根据文件扩展名返回对应的语言标识
    * @param extension 文件扩展名（包含点号）
    * @return str 语言标识符
    """
    type = EXTENSION_MAPPING.get(extension, "")
    # 未找到匹配的扩展名，使用扩展名本身
    if not type:
        type = extension.lstrip(".")
    return type


def generate_file_structure(files, root_path):
    """
    * 生成文件结构树
    * @param files 文件路径列表
    * @param root_path 项目根路径
    * @return dict 文件结构树字典
    """
    file_structure = {}
    for file in files:
        relative_path = file.relative_to(root_path)
        parts = relative_path.parts
        current_level = file_structure
        for part in parts[:-1]:
            current_level = current_level.setdefault(part, {})
        current_level[parts[-1]] = file
    return file_structure


def print_tree_structure(tree, indent=""):
    """
    * 生成树形结构的文本表示
    * @param tree 文件结构树字典
    * @param indent 缩进字符串
    * @return str 格式化的树形结构文本
    """
    content = ""
    for i, (key, value) in enumerate(tree.items()):
        connector = "└── " if i == len(tree) - 1 else "├── "
        if isinstance(value, dict):
            content += indent + connector + key + "\n"
            content += print_tree_structure(
                value, indent + ("    " if i == len(tree) - 1 else "│   ")
            )
        else:
            content += indent + connector + key + "\n"
    return content


def generate_files_content(tree, root_path, path=""):
    """
    * 生成文件内容的文本表示
    * @param tree 文件结构树字典
    * @param root_path 项目根路径
    * @param path 当前路径
    * @return str 格式化的文件内容文本
    """
    content = ""
    for key, value in tree.items():
        new_path = Path(path) / key
        if isinstance(value, dict):
            content += generate_files_content(value, root_path, new_path)
        else:
            relative_path = Path(value).relative_to(root_path)
            content += f"下面是 **.\\{relative_path}** 文件的内容：\n\n"
            extension = value.suffix.lower()
            language = get_language_by_extension(extension)
            content += f"```{language}\n"
            try:
                with open(value, "r", encoding="utf-8") as f:
                    file_content = f.read()
                content += file_content
            except UnicodeDecodeError:
                content += "（无法读取该文件内容 - 可能是二进制文件）"
            content += "\n```\n\n---\n\n"
    return content
