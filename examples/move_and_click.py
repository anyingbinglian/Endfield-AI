"""Simple demo: Move mouse to window center and click."""

from core.logging import get_logger
from input.foreground import ForegroundInput
from input.screenshot import ScreenCapture

logger = get_logger(__name__)


def main() -> None:
    """Demonstrate basic input and screenshot functionality."""
    input_ctrl = ForegroundInput()
    screen = ScreenCapture()

    # Move to window center and click
    win = input_ctrl.window
    cx = win.width // 2
    cy = win.height // 2
    logger.info("Click at window center (%s, %s)", cx, cy)

    input_ctrl.move_to(cx, cy)
    input_ctrl.click()

    # Capture a screenshot
    img = screen.grab()
    logger.info("Captured frame shape: %s", img.shape)


if __name__ == "__main__":
    main()

