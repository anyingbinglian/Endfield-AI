"""交互核心模块。

提供统一的交互接口，整合截图、图像识别、鼠标键盘操作等功能。
"""

import inspect
import random
import threading
import time
from typing import Optional, Tuple, Union

import cv2
import numpy as np

from core.logging import get_logger
from core.types import Point, Rect
from interaction.capture import WindowsCapture
from interaction.constants import (
    BACKGROUND_CHANNELS,
    FOUR_CHANNELS,
    IMG_BOOL,
    IMG_BOOLRATE,
    IMG_POSI,
    IMG_RATE,
    NORMAL_CHANNELS,
    UI_CHANNELS,
)
from interaction.decorators import before_operation
from interaction.image_matcher import crop_image, match_image
from interaction.input_controller import InteractionNormal

logger = get_logger(__name__)


class InteractionCore:
    """交互核心类。
    
    整合截图、图像识别、鼠标键盘操作等功能，提供统一的交互接口。
    默认支持 1920x1080 分辨率。
    """

    # 截图缓存最大间隔（秒）
    RECAPTURE_LIMIT = 0.5

    def __init__(self):
        """初始化交互核心类。"""
        logger.info("InteractionCore 初始化")
        
        # 初始化组件
        self._screenshot_capture = WindowsCapture(max_fps=30)
        self._input_controller = InteractionNormal()
        
        # 线程安全锁
        self._operation_lock = threading.Lock()
        
        # 按键状态跟踪
        self._key_status: dict[str, bool] = {}
        self._key_freeze: dict[str, bool] = {}
        
        # 配置
        self._wheel_delta = 120
        self._default_delay_time = 0.05
        self._debug_mode = False
        self._is_borderless_window = False

    # ========== 截图功能 ==========

    def capture(
        self,
        region: Optional[Rect] = None,
        channel_mode: int = NORMAL_CHANNELS,
        use_cache: bool = False,
    ) -> np.ndarray:
        """截取窗口图像。
        
        Args:
            region: 可选的截图区域（窗口内坐标），如果为 None 则截取全屏
            channel_mode: 通道模式
                - NORMAL_CHANNELS (0): 返回3通道BGR
                - BACKGROUND_CHANNELS (1): 返回背景通道（处理透明）
                - UI_CHANNELS (2): 返回UI通道（处理透明）
                - FOUR_CHANNELS (3): 返回4通道BGRA
            use_cache: 是否使用截图缓存，默认 False
            
        Returns:
            截图图像数组（numpy.ndarray）
        """
        recapture_limit = self.RECAPTURE_LIMIT if use_cache else 0.0
        ret = self._screenshot_capture.capture(recapture_limit=recapture_limit)
        
        # 裁剪区域（如果需要）
        if region is not None:
            ret = crop_image(ret, region)
        
        # 处理通道模式
        if ret.shape[2] == 3:
            # 已经是3通道，直接返回
            pass
        elif channel_mode == NORMAL_CHANNELS:
            # 返回3通道BGR
            ret = ret[:, :, :3]
        elif channel_mode == BACKGROUND_CHANNELS:
            # 返回背景通道
            ret = self._convert_png_to_jpg(ret, bg_color='black', channel='bg')
        elif channel_mode == UI_CHANNELS:
            # 返回UI通道
            ret = self._convert_png_to_jpg(ret, bg_color='black', channel='ui')
        elif channel_mode == FOUR_CHANNELS:
            # 返回4通道BGRA
            return ret
        
        return ret

    def _convert_png_to_jpg(
        self,
        png: np.ndarray,
        bg_color: str = 'black',
        channel: str = 'bg',
        alpha_threshold: int = 50,
    ) -> np.ndarray:
        """将4通道PNG转换为3通道JPG。
        
        Args:
            png: 4通道图片（BGRA）
            bg_color: 背景颜色，'black' 或 'white'
            channel: 提取通道，'bg'（背景）或 'ui'（UI）
            alpha_threshold: 透明通道阈值，默认 50
            
        Returns:
            3通道图片（BGR）
        """
        if bg_color == 'black':
            bg_col = 0
        else:
            bg_col = 255
        
        jpg = png[:, :, :3].copy()
        
        if channel == 'bg':
            # 提取背景：alpha > threshold 的区域
            over_item_list = png[:, :, 3] > alpha_threshold
        else:
            # 提取UI：alpha < threshold 的区域
            over_item_list = png[:, :, 3] < alpha_threshold
        
        jpg[:, :, 0][over_item_list] = bg_col
        jpg[:, :, 1][over_item_list] = bg_col
        jpg[:, :, 2][over_item_list] = bg_col
        
        return jpg

    # ========== 图像识别功能 ==========

    def check_image_exists(
        self,
        template: np.ndarray,
        region: Optional[Rect] = None,
        threshold: float = 0.8,
        use_cache: bool = False,
        return_mode: int = IMG_BOOL,
    ) -> Union[bool, float]:
        """检测图片是否存在。
        
        Args:
            template: 模板图片（numpy数组）
            region: 可选的搜索区域（窗口内坐标），如果为 None 则在整个窗口搜索
            threshold: 匹配阈值（0.0-1.0），默认 0.8
            use_cache: 是否使用截图缓存，默认 False
            return_mode: 返回模式
                - IMG_BOOL (4): 返回布尔值
                - IMG_BOOLRATE (5): 如果匹配成功返回分数，否则返回False
                - IMG_RATE (0): 返回相似度分数
                
        Returns:
            根据 return_mode 返回不同的结果
        """
        cap = self.capture(region=region, channel_mode=NORMAL_CHANNELS, use_cache=use_cache)
        
        matching_rate = match_image(cap, template, return_mode=IMG_RATE)
        
        if return_mode == IMG_BOOL:
            return matching_rate >= threshold
        elif return_mode == IMG_BOOLRATE:
            if matching_rate >= threshold:
                return matching_rate
            else:
                return False
        elif return_mode == IMG_RATE:
            return matching_rate
        else:
            raise ValueError(f"不支持的返回模式: {return_mode}")

    def find_image_position(
        self,
        template: np.ndarray,
        region: Optional[Rect] = None,
        threshold: float = 0.8,
        use_cache: bool = False,
    ) -> Optional[Tuple[int, int]]:
        """查找图片位置。
        
        Args:
            template: 模板图片（numpy数组）
            region: 可选的搜索区域（窗口内坐标），如果为 None 则在整个窗口搜索
            threshold: 匹配阈值（0.0-1.0），默认 0.8
            use_cache: 是否使用截图缓存，默认 False
            
        Returns:
            如果找到匹配，返回位置坐标 (x, y)，否则返回 None
        """
        cap = self.capture(region=region, channel_mode=NORMAL_CHANNELS, use_cache=use_cache)
        
        matching_rate, position = match_image(cap, template, return_mode=IMG_POSI)
        
        if matching_rate >= threshold:
            # 如果指定了区域，需要加上区域的偏移量
            if region is not None:
                x_offset = region.x
                y_offset = region.y
                return (position[0] + x_offset, position[1] + y_offset)
            else:
                return position
        else:
            return None

    def find_image_bounding_box(
        self,
        template: np.ndarray,
        region: Optional[Rect] = None,
        threshold: float = 0.8,
        use_cache: bool = False,
    ) -> Optional[Rect]:
        """查找图片边界框。
        
        Args:
            template: 模板图片（numpy数组）
            region: 可选的搜索区域（窗口内坐标），如果为 None 则在整个窗口搜索
            threshold: 匹配阈值（0.0-1.0），默认 0.8
            use_cache: 是否使用截图缓存，默认 False
            
        Returns:
            如果找到匹配，返回边界框 Rect，否则返回 None
        """
        position = self.find_image_position(template, region, threshold, use_cache)
        
        if position is None:
            return None
        
        x, y = position
        h, w = template.shape[:2]
        
        return Rect(x=x, y=y, width=w, height=h)

    def click_if_image_exists(
        self,
        template: np.ndarray,
        region: Optional[Rect] = None,
        threshold: float = 0.8,
        use_cache: bool = False,
        button: str = 'left',
    ) -> bool:
        """检测到图片后自动点击。
        
        Args:
            template: 模板图片（numpy数组）
            region: 可选的搜索区域（窗口内坐标），如果为 None 则在整个窗口搜索
            threshold: 匹配阈值（0.0-1.0），默认 0.8
            use_cache: 是否使用截图缓存，默认 False
            button: 鼠标按键，'left' 或 'right'，默认 'left'
            
        Returns:
            如果找到并点击了图片返回 True，否则返回 False
        """
        position = self.find_image_position(template, region, threshold, use_cache)
        
        if position is None:
            return False
        
        # 计算点击位置（模板中心）
        h, w = template.shape[:2]
        center_x = position[0] + w // 2
        center_y = position[1] + h // 2
        
        self.move_and_click((center_x, center_y), button=button)
        return True

    # ========== OCR功能（占位） ==========

    def ocr_single_line(self, region: Rect, text_template: str) -> str:
        """OCR单行文字识别（占位）。
        
        Args:
            region: 识别区域
            text_template: 文字模板（占位参数）
            
        Returns:
            识别的文字（当前返回空字符串）
        """
        # TODO: 实现 OCR 功能
        logger.warning("OCR功能尚未实现")
        return ""

    def ocr_lines(self, region: Rect, text_template: str) -> list[str]:
        """OCR多行文字识别（占位）。
        
        Args:
            region: 识别区域
            text_template: 文字模板（占位参数）
            
        Returns:
            识别的文字列表（当前返回空列表）
        """
        # TODO: 实现 OCR 功能
        logger.warning("OCR功能尚未实现")
        return []

    def check_text_exists(self, text_template: str, region: Optional[Rect] = None) -> bool:
        """检测文字是否存在（占位）。
        
        Args:
            text_template: 文字模板
            region: 可选的搜索区域
            
        Returns:
            如果找到文字返回 True，否则返回 False（当前总是返回 False）
        """
        # TODO: 实现 OCR 功能
        logger.warning("OCR功能尚未实现")
        return False

    # ========== 鼠标操作 ==========

    @before_operation()
    def left_click(self) -> None:
        """左键单击。"""
        self._operation_lock.acquire()
        try:
            self._input_controller.left_click()
        finally:
            self._operation_lock.release()

    @before_operation()
    def left_down(self) -> None:
        """按下左键（保持按下状态）。"""
        self._operation_lock.acquire()
        try:
            self._input_controller.left_down()
        finally:
            self._operation_lock.release()

    @before_operation()
    def left_up(self) -> None:
        """释放左键。"""
        self._operation_lock.acquire()
        try:
            self._input_controller.left_up()
        finally:
            self._operation_lock.release()

    @before_operation()
    def left_double_click(self, dt: float = 0.05) -> None:
        """左键双击。
        
        Args:
            dt: 两次点击之间的间隔时间（秒），默认 0.05
        """
        self._operation_lock.acquire()
        try:
            self._input_controller.left_double_click(dt)
        finally:
            self._operation_lock.release()

    @before_operation()
    def right_click(self) -> None:
        """右键单击。"""
        self._operation_lock.acquire()
        try:
            self._input_controller.right_click()
        finally:
            self._operation_lock.release()
        self.delay(0.05)

    @before_operation()
    def middle_click(self) -> None:
        """中键单击。"""
        self._operation_lock.acquire()
        try:
            self._input_controller.middle_click()
        finally:
            self._operation_lock.release()

    @before_operation(print_log=False)
    def move_to(self, x: int, y: int, relative: bool = False) -> None:
        """移动鼠标到指定坐标。
        
        Args:
            x: 目标 x 坐标（窗口内坐标）
            y: 目标 y 坐标（窗口内坐标）
            relative: 如果为 True，则相对于当前位置移动
        """
        self._operation_lock.acquire()
        try:
            self._input_controller.move_to(
                x, y, relative=relative, is_borderless_window=self._is_borderless_window
            )
        finally:
            self._operation_lock.release()

    @before_operation()
    def move_and_click(
        self,
        position: Point,
        button: str = 'left',
        delay: float = 0.3,
    ) -> None:
        """移动鼠标到指定位置并点击。
        
        Args:
            position: 目标位置坐标 (x, y)
            button: 鼠标按键，'left' 或 'right'，默认 'left'
            delay: 移动后等待时间（秒），默认 0.3
        """
        self._operation_lock.acquire()
        try:
            x, y = position
            self._input_controller.move_to(
                int(x), int(y), relative=False, is_borderless_window=self._is_borderless_window
            )
            time.sleep(delay)
            
            if button == 'left':
                self._input_controller.left_click()
            else:
                self._input_controller.right_click()
        finally:
            self._operation_lock.release()

    @before_operation()
    def drag(self, origin_pos: Point, target_pos: Point, button: str = 'left') -> None:
        """拖拽操作。
        
        Args:
            origin_pos: 起始位置 (x, y)
            target_pos: 目标位置 (x, y)
            button: 鼠标按键，'left' 或 'right'，默认 'left'
        """
        self._operation_lock.acquire()
        try:
            # 移动到起始位置
            self._input_controller.move_to(
                origin_pos[0], origin_pos[1],
                relative=False, is_borderless_window=self._is_borderless_window
            )
            
            # 按下鼠标
            if button == 'left':
                self._input_controller.left_down()
            else:
                self._input_controller.right_click()  # 右键拖拽使用右键
            
            # 移动到目标位置
            self._input_controller.move_to(
                target_pos[0], target_pos[1],
                relative=False, is_borderless_window=self._is_borderless_window
            )
            
            # 释放鼠标
            if button == 'left':
                self._input_controller.left_up()
        finally:
            self._operation_lock.release()

    # ========== 键盘操作 ==========

    @before_operation()
    def key_down(self, key: str) -> None:
        """按下键盘按键（保持按下状态）。
        
        Args:
            key: 按键名称（如 'w', 'space', 'esc'）
        """
        self._operation_lock.acquire()
        try:
            self._input_controller.key_down(key)
            self._key_status[key] = True
        finally:
            self._operation_lock.release()

    @before_operation()
    def key_up(self, key: str) -> None:
        """释放键盘按键。
        
        Args:
            key: 按键名称（如 'w', 'space', 'esc'）
        """
        self._operation_lock.acquire()
        try:
            self._input_controller.key_up(key)
            self._key_status[key] = False
        finally:
            self._operation_lock.release()

    @before_operation()
    def key_press(self, key: str) -> None:
        """按下并释放键盘按键（完整的按键操作）。
        
        Args:
            key: 按键名称（如 'w', 'space', 'esc'）
        """
        self._operation_lock.acquire()
        try:
            self._input_controller.key_press(key)
            self._key_status[key] = False
        finally:
            self._operation_lock.release()

    @before_operation()
    def freeze_key(self, key: str, state: str = 'down') -> None:
        """冻结按键状态。
        
        保存当前按键状态，然后设置为指定状态。
        
        Args:
            key: 按键名称
            state: 要设置的状态，'down' 或 'up'，默认 'down'
        """
        self._operation_lock.acquire()
        try:
            self._key_freeze[key] = self._key_status.get(key, False)
            if state == 'down':
                self._input_controller.key_down(key)
            else:
                self._input_controller.key_up(key)
        finally:
            self._operation_lock.release()

    @before_operation()
    def unfreeze_key(self, key: str) -> None:
        """解冻按键状态。
        
        恢复冻结前的按键状态。
        
        Args:
            key: 按键名称
        """
        self._operation_lock.acquire()
        try:
            original_state = self._key_freeze.get(key, False)
            if original_state:
                self._input_controller.key_down(key)
            else:
                self._input_controller.key_up(key)
        finally:
            self._operation_lock.release()

    # ========== 辅助功能 ==========

    def delay(
        self,
        seconds: Union[float, str],
        randomize: bool = False,
        comment: str = '',
    ) -> None:
        """延迟一段时间。
        
        Args:
            seconds: 延迟时间（秒）或关键字（'animation' 或 '2animation'）
            randomize: 是否启用随机延迟，默认 False
            comment: 日志注释，默认 ''
        """
        # 处理关键字
        if seconds == "animation":
            time.sleep(0.3)
            return
        if seconds == "2animation":
            time.sleep(0.6)
            return
        
        # 获取调用者信息
        frame = inspect.currentframe()
        func_name = ""
        if frame and frame.f_back:
            func_name = inspect.getframeinfo(frame.f_back)[2]
        
        # 随机延迟
        if randomize:
            random_offset = random.randint(-10, 10)
            random_offset = random_offset * seconds * 0.02
            actual_delay = seconds + random_offset
            if seconds > 0.2:
                logger.debug(
                    f"延迟: {seconds} 秒，随机: {actual_delay:.3f} 秒 | "
                    f"调用函数: {func_name} | 注释: {comment}"
                )
            time.sleep(actual_delay)
        else:
            if seconds > 0.2:
                logger.debug(
                    f"延迟: {seconds} 秒 | 调用函数: {func_name} | 注释: {comment}"
                )
            time.sleep(seconds)

    def wait_until_stable(
        self,
        threshold: float = 0.9995,
        timeout: float = 10.0,
        additional_break_func: Optional[callable] = None,
    ) -> None:
        """等待画面稳定。
        
        通过比较连续截图来判断画面是否稳定。
        
        Args:
            threshold: 相似度阈值（0.0-1.0），默认 0.9995
            timeout: 超时时间（秒），默认 10.0
            additional_break_func: 额外的中断函数，如果返回 True 则中断等待
        """
        timeout_timer = time.time() + timeout
        last_cap = self.capture()
        
        start_time = time.time()
        stable_timer = 0.0
        stable_duration = 0.25  # 稳定持续时间（秒）
        stable_count = 3  # 需要连续稳定3次
        
        while True:
            time.sleep(0.1)
            
            # 检查超时
            if time.time() > timeout_timer:
                logger.warning("等待画面稳定超时")
                break
            
            # 获取当前截图并比较
            curr_img = self.capture()
            similarity = match_image(last_cap, curr_img, return_mode=IMG_RATE)
            
            if self._debug_mode:
                logger.debug(f"画面相似度: {similarity}")
            
            if similarity > threshold:
                # 画面稳定
                stable_timer += 0.1
                if stable_timer >= stable_duration * stable_count:
                    if self._debug_mode:
                        logger.debug(f"画面稳定，等待时间: {time.time() - start_time:.2f} 秒")
                    break
            else:
                # 画面不稳定，重置计时器
                stable_timer = 0.0
            
            last_cap = curr_img.copy()
            
            # 检查额外的中断条件
            if additional_break_func and additional_break_func():
                logger.debug("等待画面稳定中断：额外条件满足")
                break

    def save_snapshot(self, reason: str = '') -> None:
        """保存截图快照。
        
        Args:
            reason: 保存原因（用于文件名）
        """
        img = self.capture(channel_mode=FOUR_CHANNELS)
        if img.shape[2] == 4:
            img = img[:, :, :3]
        
        import os
        from datetime import datetime
        
        # 创建日志目录
        log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{reason}_{timestamp}.jpg" if reason else f"snapshot_{timestamp}.jpg"
        filepath = os.path.join(log_dir, filename)
        
        cv2.imwrite(filepath, img)
        logger.warning(f"截图快照已保存: {filepath}")
