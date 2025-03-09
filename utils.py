from pathlib import Path
from typing import List, Dict, Any
from fnmatch import fnmatch

def is_path_excluded(path: Path, exclude_patterns: List[str], ignore_patterns: List[str]) -> bool:
    """
    * 检查路径是否应该被排除
    * @param path 要检查的路径对象
    * @param exclude_patterns 排除的正则表达式模式列表
    * @param ignore_patterns 忽略的.gitignore模式列表
    * @return 如果路径应该被排除则返回True，否则返回False
    """
    try:
        relative_path = str(path.relative_to(path.parent.parent)) if path.parent.parent else path.name
        # 先检查正则表达式
        if any(pattern.match(str(path)) for pattern in exclude_patterns):
            return True
        # 使用更高效的路径匹配
        path_str = str(path)
        return any(path_str.endswith(pattern.lstrip('**/')) or 
                  fnmatch(path_str, pattern) 
                  for pattern in ignore_patterns)
    except Exception:
        return False

def sort_contents(contents: List[str], path: Path, options: Dict[str, Any]) -> List[str]:
    """
    * 对目录内容进行排序
    * @param contents 目录内容列表
    * @param path 当前路径对象
    * @param options 排序选项字典
    * @return 排序后的内容列表
    """
    # 按名称排序（忽略大小写）
    sorted_contents = sorted(contents, key=lambda x: x.lower())
    
    # 如果需要反向排序
    if options['reverse']:
        sorted_contents.reverse()
    
    # 如果只需要目录
    if options['dirs_only']:
        sorted_contents = [c for c in sorted_contents if (path / c).is_dir()]
    
    # 如果目录优先
    if options['dirs_first']:
        dirs = [c for c in sorted_contents if (path / c).is_dir()]
        files = [c for c in sorted_contents if not (path / c).is_dir()]
        sorted_contents = dirs + files
    
    return sorted_contents
