# Endfield-AI 文档

## 项目结构

```
Endfield-AI/
├── src/                    # 源代码目录
│   ├── core/              # 核心模块
│   │   └── game_controller.py    # 游戏控制器
│   ├── actions/           # 动作模块
│   │   ├── base_action.py        # 动作基类
│   │   ├── click_action.py       # 点击动作
│   │   └── key_action.py         # 键盘动作
│   ├── detection/         # 检测模块
│   │   ├── image_matcher.py      # 图像匹配
│   │   └── screen_capture.py     # 屏幕捕获
│   └── utils/             # 工具模块
│       ├── logger.py              # 日志工具
│       ├── config_manager.py      # 配置管理
│       ├── input_controller.py   # 输入控制
│       ├── window_manager.py      # 窗口管理
│       ├── image_utils.py         # 图像处理
│       └── timer.py              # 定时器
├── config/                # 配置文件目录
│   └── config.json        # 主配置文件
├── tests/                 # 测试目录
├── docs/                  # 文档目录
├── logs/                  # 日志目录（自动生成）
├── main.py               # 主入口文件
├── requirements.txt      # 项目依赖
└── README.md             # 项目说明
```

## 模块说明

### 核心模块 (core)
- **GameController**: 游戏自动化控制器，统一管理自动化流程

### 动作模块 (actions)
- **BaseAction**: 所有动作的基类，定义了动作的基本接口
- **ClickAction**: 鼠标点击动作
- **KeyAction**: 键盘按键动作

### 检测模块 (detection)
- **ImageMatcher**: 图像匹配和模板识别
- **ScreenCapture**: 屏幕和窗口图像捕获

### 工具模块 (utils)
- **Logger**: 统一的日志管理系统
- **ConfigManager**: 配置文件管理
- **InputController**: 鼠标和键盘控制
- **WindowManager**: 窗口查找和管理
- **ImageUtils**: 图像处理工具
- **Timer**: 延迟和定时功能

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

### 使用配置管理

```python
from src.utils.config_manager import ConfigManager

config = ConfigManager()
window_title = config.get("game.window_title")
config.set("game.auto_focus", True)
config.save_config()
```

## 开发指南

1. 所有动作类应继承 `BaseAction` 并实现 `execute` 和 `validate` 方法
2. 使用 `Logger` 进行日志记录
3. 配置项通过 `ConfigManager` 统一管理
4. 图像处理使用 `ImageUtils` 和 `ImageMatcher`
5. 输入控制使用 `InputController`

## TODO

- [ ] 实现具体的图像识别算法
- [ ] 实现鼠标键盘控制逻辑
- [ ] 实现窗口管理功能
- [ ] 添加更多游戏动作类型
- [ ] 实现任务调度系统

