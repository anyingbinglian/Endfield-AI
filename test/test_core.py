"""测试 InteractionCore 功能的测试脚本。

使用记事本窗口来测试截图、图像识别、鼠标键盘操作等功能。
运行前请确保已打开记事本窗口。
"""

import sys
import os
import time
from datetime import datetime

import cv2

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 直接导入并使用 WINDOW_CONFIG（已在 config.py 中设置为测试配置）
from interaction.core import InteractionCore
from interaction.constants import NORMAL_CHANNELS, FOUR_CHANNELS
from core.logging import get_logger

logger = get_logger(__name__)


def test_capture():
    """测试截图功能。"""
    print("\n=== 测试截图功能 ===")
    core = InteractionCore(force_1920x1080=False)  # 使用实际窗口尺寸
    
    # 创建保存目录
    save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test", "screenshots")
    os.makedirs(save_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # 测试全屏截图
        print("1. 测试全屏截图...")
        img = core.capture()
        print(f"   截图成功！尺寸: {img.shape}")
        # 保存全屏截图
        if img.shape[2] == 4:
            img_save = img[:, :, :3]  # BGRA转BGR
        else:
            img_save = img
        filepath = os.path.join(save_dir, f"01_fullscreen_{timestamp}.jpg")
        cv2.imwrite(filepath, img_save)
        print(f"   已保存到: {filepath}")
        
        # 测试区域截图
        print("2. 测试区域截图...")
        from core.types import Rect
        region = Rect(x=100, y=100, width=200, height=200)
        img_region = core.capture(region=region)
        print(f"   区域截图成功！尺寸: {img_region.shape}")
        # 保存区域截图
        if img_region.shape[2] == 4:
            img_region_save = img_region[:, :, :3]
        else:
            img_region_save = img_region
        filepath = os.path.join(save_dir, f"02_region_{timestamp}.jpg")
        cv2.imwrite(filepath, img_region_save)
        print(f"   已保存到: {filepath}")
        
        # 测试不同通道模式
        print("3. 测试不同通道模式...")
        img_bgr = core.capture(channel_mode=NORMAL_CHANNELS)
        print(f"   BGR模式: {img_bgr.shape}")
        filepath = os.path.join(save_dir, f"03_bgr_{timestamp}.jpg")
        cv2.imwrite(filepath, img_bgr)
        print(f"   已保存到: {filepath}")
        
        img_bgra = core.capture(channel_mode=FOUR_CHANNELS)
        print(f"   BGRA模式: {img_bgra.shape}")
        # BGRA需要转换为BGR才能保存为JPG
        img_bgra_save = img_bgra[:, :, :3]
        filepath = os.path.join(save_dir, f"04_bgra_{timestamp}.jpg")
        cv2.imwrite(filepath, img_bgra_save)
        print(f"   已保存到: {filepath}")
        
        # 测试缓存
        print("4. 测试截图缓存...")
        start_time = time.time()
        img1 = core.capture(use_cache=True)
        time1 = time.time() - start_time
        
        start_time = time.time()
        img2 = core.capture(use_cache=True)
        time2 = time.time() - start_time
        
        print(f"   首次截图耗时: {time1:.4f}秒")
        print(f"   缓存截图耗时: {time2:.4f}秒")
        print(f"   缓存是否生效: {time2 < time1}")
        # 保存缓存测试截图
        if img1.shape[2] == 4:
            img1_save = img1[:, :, :3]
        else:
            img1_save = img1
        filepath = os.path.join(save_dir, f"05_cache_first_{timestamp}.jpg")
        cv2.imwrite(filepath, img1_save)
        print(f"   首次截图已保存到: {filepath}")
        
        print(f"\n所有截图已保存到: {save_dir}")
        print("✓ 截图功能测试通过！")
        return True
    except Exception as e:
        print(f"✗ 截图功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mouse_operations():
    """测试鼠标操作功能。"""
    print("\n=== 测试鼠标操作功能 ===")
    core = InteractionCore(force_1920x1080=False)
    
    try:
        print("1. 测试鼠标移动...")
        # 移动到窗口中心
        img = core.capture()
        center_x = img.shape[1] // 2
        center_y = img.shape[0] // 2
        print(f"   移动到窗口中心: ({center_x}, {center_y})")
        core.move_to(center_x, center_y)
        time.sleep(0.5)
        
        print("2. 测试左键点击...")
        core.left_click()
        time.sleep(0.3)
        
        print("3. 测试右键点击...")
        core.right_click()
        time.sleep(0.3)
        
        print("4. 测试移动并点击...")
        core.move_and_click((center_x + 100, center_y + 100), button='left')
        time.sleep(0.3)
        
        print("✓ 鼠标操作功能测试通过！")
        return True
    except Exception as e:
        print(f"✗ 鼠标操作功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_keyboard_operations():
    """测试键盘操作功能。"""
    print("\n=== 测试键盘操作功能 ===")
    core = InteractionCore(force_1920x1080=False)
    
    try:
        print("1. 测试按键按下和释放...")
        core.key_down('a')
        time.sleep(0.1)
        core.key_up('a')
        time.sleep(0.2)
        
        print("2. 测试按键按下（完整操作）...")
        core.key_press('b')
        time.sleep(0.2)
        
        print("3. 测试冻结和解冻按键...")
        core.freeze_key('c', state='down')
        time.sleep(0.1)
        core.unfreeze_key('c')
        time.sleep(0.2)
        
        print("✓ 键盘操作功能测试通过！")
        return True
    except Exception as e:
        print(f"✗ 键盘操作功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_image_matching():
    """测试图像识别功能。"""
    print("\n=== 测试图像识别功能 ===")
    core = InteractionCore(force_1920x1080=False)
    
    try:
        # 先截取一张图片作为模板
        print("1. 截取模板图片...")
        img = core.capture()
        # 截取一个小区域作为模板
        from core.types import Rect
        template_region = Rect(
            x=img.shape[1] // 4,
            y=img.shape[0] // 4,
            width=100,
            height=100
        )
        template = core.capture(region=template_region)
        print(f"   模板尺寸: {template.shape}")
        
        # 测试图片是否存在
        print("2. 测试图片是否存在...")
        exists = core.check_image_exists(template, threshold=0.8)
        print(f"   图片是否存在: {exists}")
        
        # 测试查找图片位置
        print("3. 测试查找图片位置...")
        position = core.find_image_position(template, threshold=0.8)
        if position:
            print(f"   找到图片位置: {position}")
        else:
            print("   未找到图片位置（可能因为窗口内容变化）")
        
        # 测试查找边界框
        print("4. 测试查找边界框...")
        bbox = core.find_image_bounding_box(template, threshold=0.8)
        if bbox:
            print(f"   找到边界框: {bbox}")
        else:
            print("   未找到边界框（可能因为窗口内容变化）")
        
        print("✓ 图像识别功能测试通过！")
        return True
    except Exception as e:
        print(f"✗ 图像识别功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_utility_functions():
    """测试辅助功能。"""
    print("\n=== 测试辅助功能 ===")
    core = InteractionCore(force_1920x1080=False)
    
    try:
        print("1. 测试延迟功能...")
        start_time = time.time()
        core.delay(0.5)
        elapsed = time.time() - start_time
        print(f"   延迟0.5秒，实际耗时: {elapsed:.3f}秒")
        
        print("2. 测试保存快照...")
        core.save_snapshot(reason="test")
        print("   快照已保存到 logs 文件夹")
        
        print("✓ 辅助功能测试通过！")
        return True
    except Exception as e:
        print(f"✗ 辅助功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试。"""
    print("=" * 60)
    print("InteractionCore 功能测试")
    print("=" * 60)
    print("\n提示：请确保已打开记事本（Notepad）窗口")
    print("等待 3 秒后开始测试...\n")
    time.sleep(3)
    
    results = []
    
    # 运行各项测试
    # results.append(("截图功能", test_capture()))
    # results.append(("鼠标操作", test_mouse_operations()))
    # results.append(("键盘操作", test_keyboard_operations()))
    # results.append(("图像识别", test_image_matching()))
    results.append(("辅助功能", test_utility_functions()))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name:20s}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n总计: {passed}/{total} 项测试通过")
    print("\n测试完成！")


if __name__ == "__main__":
    main()

