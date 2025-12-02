# 文件路径: 可序列化库/可序列化基类.py
# 流程原理: 单人项目可控对象序列化库，支持继承、包装器和依赖传递三种模式，递归序列化常用类型，特殊类型由外部传入处理函数，可选择是否序列化可调用对象

import datetime
from dataclasses import is_dataclass, asdict
from typing import Any, Dict, Type, Callable
from enum import Enum

from prompt_toolkit.key_binding.bindings.named_commands import self_insert
from pydantic import BaseModel
import types

# ===========================
# 核心递归函数
# ===========================
def _递归序列化(
        v: Any,
        类型处理: Dict[Type, Callable[[Any], Any]],
        序列化可调用对象: bool = False
) -> Any:
    # 可调用对象处理
    if callable(v):
        if 类型处理:
            # 遍历可调用对象类型处理
            for t, func in 类型处理.items():
                if isinstance(v, t):
                    return func(v)
        # 默认处理
        if 序列化可调用对象:
            return repr(v)
        else:
            return None

    # 可序列化基类或已有转字典方法
    if hasattr(v, "转字典") and callable(v.转字典):
        return v.转字典()

    # Pydantic BaseModel
    elif isinstance(v, BaseModel):
        return _递归序列化(v.dict(), 类型处理, 序列化可调用对象)

    # dataclass 对象
    elif is_dataclass(v):
        return _递归序列化(asdict(v), 类型处理, 序列化可调用对象)

    # dict
    elif isinstance(v, dict):
        return {kk: _递归序列化(vv, 类型处理, 序列化可调用对象) for kk, vv in v.items()}

    # list/tuple/set/frozenset
    elif isinstance(v, (list, tuple, set, frozenset)):
        return [_递归序列化(vv, 类型处理, 序列化可调用对象) for vv in v]

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
    def 转字典(
            self,
            类型处理: Dict[Type, Callable[[Any], Any]] = None,
            序列化可调用对象: bool = False
    ) -> Dict[str, Any]:
        类型处理 = 类型处理 or {}

        # 判断是类还是实例
        if isinstance(self, type):
            print("self 是类")
            # self 是类
            属性字典 = {
                k: v for k, v in vars(self).items()
                if not k.startswith("__")  # 过滤内置属性
            }
        else:
            print("self 是实例")
            # self 是实例
            属性字典 = vars(self)

        # 递归序列化每个属性
        return {
            k: _递归序列化(v, 类型处理, 序列化可调用对象)
            for k, v in 属性字典.items()
        }

# ===========================
# 2. 包装器模式
# ===========================
def 可序列化包装器(
        类型处理: Dict[Type, Callable[[Any], Any]] = None,
        序列化可调用对象: bool = False
):
    类型处理 = 类型处理 or {}
    def 装饰器(cls):
        def 转字典(self) -> Dict[str, Any]:
            return {k: _递归序列化(v, 类型处理, 序列化可调用对象) for k, v in vars(self).items()}
        setattr(cls, "转字典", 转字典)
        return cls
    return 装饰器

# ===========================
# 3. 依赖传递模式
# ===========================
def 序列化对象(
        obj: Any,
        类型处理: Dict[Type, Callable[[Any], Any]] = None,
        序列化可调用对象: bool = False
) -> Dict[str, Any]:
    """
    对任意对象实例进行序列化，不修改类
    """
    类型处理 = 类型处理 or {}
    return {k: _递归序列化(v, 类型处理, 序列化可调用对象) for k, v in vars(obj).items()}

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
    def 函数处理(函数: types.FunctionType) -> str:
        return 函数()
    # 继承模式
    class 文件资源继承(可序列化基类):
        def __init__(self, 名称: str, 内容: bytes):
            self.名称 = 名称
            self.内容 = 内容
            self.可执行 = lambda : "aaaaaaa"  # 测试函数

    f1 = 文件资源继承("继承文件", b"\x01\x02")
    print(f1.转字典({bytes: bytes_to_hex, types.FunctionType: 函数处理}, True))  # 默认不序列化可调用对象

    # 包装器模式
    @可序列化包装器({bytes: bytes_to_hex, types.FunctionType: 函数处理}, True)
    class 文件资源包装:
        def __init__(self, 名称: str, 内容: bytes):
            self.名称 = 名称
            self.内容 = 内容
            self.方法 = lambda : "bbbbbbb"  # 测试函数

    f2 = 文件资源包装("包装文件", b"\x03\x04")
    print(f2.转字典())

    # 依赖传递模式
    class 文件资源普通:
        def __init__(self, 名称: str, 内容: bytes):
            self.名称 = 名称
            self.内容 = 内容
            self.func = lambda: "test"

    f3 = 文件资源普通("普通文件", b"\x05\x06")
    print(序列化对象(f3, {bytes: bytes_to_hex, types.FunctionType: 函数处理}, True))
