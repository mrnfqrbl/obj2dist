# 文件路径: 可序列化库/可序列化基类.py
# 流程原理: 单人项目可控对象序列化库，支持继承、包装器和依赖传递三种模式，递归序列化常用类型，特殊类型由外部传入处理函数

import datetime
from dataclasses import is_dataclass, asdict
from typing import Any, Dict, Type, Callable
from enum import Enum
from pydantic import BaseModel

# ===========================
# 核心递归函数
# ===========================
def _递归序列化(v: Any, 类型处理: Dict[Type, Callable[[Any], Any]]) -> Any:
    # 可序列化基类或已有转字典方法
    if hasattr(v, "转字典") and callable(v.转字典):
        return v.转字典()

    # Pydantic BaseModel
    elif isinstance(v, BaseModel):
        return _递归序列化(v.dict(), 类型处理)

    # dataclass 对象
    elif is_dataclass(v):
        return _递归序列化(asdict(v), 类型处理)

    # dict
    elif isinstance(v, dict):
        return {kk: _递归序列化(vv, 类型处理) for kk, vv in v.items()}

    # list/tuple/set/frozenset
    elif isinstance(v, (list, tuple, set, frozenset)):
        return [_递归序列化(vv, 类型处理) for vv in v]

    # Enum
    elif isinstance(v, Enum):
        return v.value

    # datetime/date
    elif isinstance(v, (datetime.datetime, datetime.date)):
        return v.isoformat()

    # 原子类型
    elif isinstance(v, (str, int, float, bool, type(None))):
        return v

    # 调用外部类型处理
    for t, func in 类型处理.items():
        if isinstance(v, t):
            return func(v)

    # 未处理类型返回 None
    return None

# ===========================
# 1. 继承模式
# ===========================
class 可序列化基类:
    def 转字典(self, 类型处理: Dict[Type, Callable[[Any], Any]] = None) -> Dict[str, Any]:
        类型处理 = 类型处理 or {}
        return {k: _递归序列化(v, 类型处理) for k, v in vars(self).items()}

# ===========================
# 2. 包装器模式
# ===========================
def 可序列化包装器(类型处理: Dict[Type, Callable[[Any], Any]] = None):
    类型处理 = 类型处理 or {}
    def 装饰器(cls):
        def 转字典(self) -> Dict[str, Any]:
            return {k: _递归序列化(v, 类型处理) for k, v in vars(self).items()}
        setattr(cls, "转字典", 转字典)
        return cls
    return 装饰器

# ===========================
# 3. 依赖传递模式
# ===========================
def 序列化对象(obj: Any, 类型处理: Dict[Type, Callable[[Any], Any]] = None) -> Dict[str, Any]:
    """
    对任意对象实例进行序列化，不修改类
    """
    类型处理 = 类型处理 or {}
    return {k: _递归序列化(v, 类型处理) for k, v in vars(obj).items()}

# ===========================
# 示例用法
# ===========================
__all__ = [
    "可序列化基类",
    "可序列化包装器",
    "序列化对象"
]


if __name__ == "__main__":
    # 自定义类型处理函数
    def bytes_to_hex(b: bytes) -> str:
        return b.hex()

    # 继承模式
    class 文件资源继承(可序列化基类):
        def __init__(self, 名称: str, 内容: bytes):
            self.名称 = 名称
            self.内容 = 内容

    f1 = 文件资源继承("继承文件", b"\x01\x02")
    print(f1.转字典({bytes: bytes_to_hex}))

    # 包装器模式
    @可序列化包装器({bytes: bytes_to_hex})
    class 文件资源包装:
        def __init__(self, 名称: str, 内容: bytes):
            self.名称 = 名称
            self.内容 = 内容

    f2 = 文件资源包装("包装文件", b"\x03\x04")
    print(f2.转字典())

    # 依赖传递模式
    class 文件资源普通:
        def __init__(self, 名称: str, 内容: bytes):
            self.名称 = 名称
            self.内容 = 内容

    f3 = 文件资源普通("普通文件", b"\x05\x06")
    print(序列化对象(f3, {bytes: bytes_to_hex}))
