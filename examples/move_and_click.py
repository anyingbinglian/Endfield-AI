"""简单示例：移动鼠标到窗口中心并点击。

这个示例演示了基本的输入和截图功能：
1. 查找游戏窗口
2. 移动鼠标到窗口中心
3. 点击鼠标
4. 截取屏幕图像
"""

from core.logging import get_logger
from input.foreground import ForegroundInput
from input.screenshot import ScreenCapture

logger = get_logger(__name__)


def main() -> None:
    """演示基本的输入和截图功能。"""
    # 初始化输入控制器和截图工具
    # 它们会自动查找游戏窗口
    input_ctrl = ForegroundInput()
    screen = ScreenCapture()

    # 获取窗口信息并计算中心点
    win = input_ctrl.window
    cx = win.width // 2  # 窗口中心 x 坐标
    cy = win.height // 2  # 窗口中心 y 坐标
    logger.info("准备点击窗口中心位置 (%s, %s)", cx, cy)

    # 移动鼠标到中心并点击
    input_ctrl.move_to(cx, cy)
    input_ctrl.click()
    logger.info("已点击窗口中心")

    # 截取一张屏幕图像
    img = screen.grab()
    logger.info("截图完成，图像尺寸: %s (高度, 宽度, 通道数)", img.shape)


if __name__ == "__main__":
    main()

