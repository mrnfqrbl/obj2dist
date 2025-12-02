import setuptools

from setuptools import setup, find_packages

setup(
    name="obj2dict",        # 库名
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "pydantic",  # Pydantic 数据模型库

    ],
    python_requires=">=3.7",
    description="给任意对象添加可序列化能力的包装器",
    author="null",
    url="null",
)