# Endfield-AI

《明日方舟：终末地》AI游戏助手 - 解放双手，拥抱AI （正在开发中...）

## 项目简介

Endfield-AI 是一个游戏自动化控制框架，专为《明日方舟：终末地》设计。项目采用模块化架构，提供完整的工具链，方便扩展和定制。

## 功能特性

- 🎮 游戏窗口自动识别和管理
- 🖱️ 鼠标和键盘自动化控制
- 📸 屏幕捕获和图像识别
- 🔍 模板匹配和目标检测
- ⚙️ 灵活的配置管理系统
- 📝 完善的日志记录系统

## 项目结构

```
Endfield-AI/
├── src/                    # 源代码目录
│   ├── core/              # 核心模块
│   ├── actions/           # 动作模块
│   ├── detection/         # 检测模块
│   └── utils/             # 工具模块
├── config/                # 配置文件
├── tests/                 # 测试代码
├── docs/                  # 项目文档
├── logs/                  # 日志文件（自动生成）
├── main.py               # 主入口文件
└── requirements.txt      # 项目依赖
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置设置

编辑 `config/config.json` 文件，设置游戏窗口标题等参数。

### 3. 运行程序

```bash
python main.py
```

## 模块说明

### 核心模块 (core)
- **GameController**: 游戏自动化控制器，统一管理自动化流程

### 动作模块 (actions)
- **BaseAction**: 动作基类
- **ClickAction**: 鼠标点击动作
- **KeyAction**: 键盘按键动作

### 检测模块 (detection)
- **ImageMatcher**: 图像匹配和模板识别
- **ScreenCapture**: 屏幕和窗口图像捕获

### 工具模块 (utils)
- **Logger**: 日志管理
- **ConfigManager**: 配置管理
- **InputController**: 输入控制
- **WindowManager**: 窗口管理
- **ImageUtils**: 图像处理
- **Timer**: 定时器工具

## 使用示例

### 基本使用

```python
from src.core.game_controller import GameController

controller = GameController()
controller.start()
# ... 执行自动化逻辑 ...
controller.stop()
```

### 执行点击动作

```python
from src.actions.click_action import ClickAction

click_action = ClickAction()
click_action.execute(x=100, y=200, button="left")
```

## 开发状态

项目目前处于基础架构搭建阶段，各模块框架已就绪，等待具体功能实现。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
