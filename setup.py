"""
Endfield-AI 项目安装配置
"""
from setuptools import setup, find_packages
from pathlib import Path

# 读取 README 文件
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="endfield-ai",
    version="0.1.0",
    description="明日方舟终末地游戏自动化助手",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="anyingbinglian",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "Pillow>=10.0.0",
        "pywin32>=306; sys_platform == 'win32'",
        "pyautogui>=0.9.54",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "console_scripts": [
            "endfield-ai=main:main",
        ],
    },
)

