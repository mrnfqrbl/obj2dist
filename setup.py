import setuptools

from setuptools import setup, find_packages

setup(
    name="class2dist",        # 库名
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic",  # Pydantic 数据模型库

    ],
    python_requires=">=3.7",
    description="给任意对象添加可序列化能力的包装器",
    author="null",
    url="null",
)