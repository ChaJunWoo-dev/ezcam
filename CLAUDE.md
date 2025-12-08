# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EZCAM is a PyQt6-based desktop application for AI-powered webcam background removal. The application provides real-time background removal using MediaPipe's selfie segmentation, with a "transparent mode" that allows the processed video to be overlaid on other applications.

## Development Commands

### Environment Setup
```bash
pip install -r requirements.txt
```

### Run Application
```bash
python main.py
```

## Architecture

### Application Entry Point
- [main.py](main.py) - Simple entry point that initializes QApplication and shows MainApp window
- [main_window.py](main_window.py) - Contains `MainApp` class with UI layout (currently a skeleton implementation)

### Complete Implementation Reference
- [backup.py](backup.py) - Contains the full working implementation (`CameraApp` class) with all features including:
  - Camera detection and management
  - MediaPipe selfie segmentation integration
  - Dual video display (original + background-removed)
  - Transparent overlay mode with frameless window
  - Real-time background threshold adjustment

**Important**: The actual working code is in [backup.py](backup.py). The [main_window.py](main_window.py) file contains only basic UI structure without camera/segmentation functionality.

### UI Architecture

#### Styling System
The application uses modular QSS (Qt StyleSheets) loaded from the `styles/` directory:
- [styles/base.qss](styles/base.qss) - Base window and label styles, including video display areas
- [styles/button.qss](styles/button.qss) - Button styles including close/minimize button variants
- [styles/combo.qss](styles/combo.qss) - ComboBox dropdown styles
- [styles/slider.qss](styles/slider.qss) - QSlider styles for threshold control

Stylesheets are loaded and concatenated in `load_stylesheet()` method.

#### Window Behavior
- Frameless window with custom title bar (minimize/close buttons)
- Always-on-top behavior
- Custom drag handling for window movement
- Window dragging implemented via `mousePressEvent`, `mouseMoveEvent`, `mouseReleaseEvent`

### Key Components (from backup.py reference)

#### Camera Management
- Automatic camera detection (scans indices 0-9)
- Camera resolution detection and display
- OpenCV VideoCapture integration

#### Background Removal Pipeline
1. Capture frame from camera (BGR format)
2. Convert BGR → RGB for MediaPipe processing
3. Process through MediaPipe SelfieSegmentation (model_selection=1)
4. Extract segmentation mask (0-1 float values)
5. Apply threshold based on slider value (0.1-1.0)
6. Create binary mask and alpha channel
7. Convert to BGRA with transparency

#### Transparent Mode
When enabled:
- Window becomes frameless overlay (WindowStaysOnTopHint)
- All UI controls hidden except processed video
- Background set to transparent via WA_TranslucentBackground
- Mouse wheel resizing support
- Drag-to-move functionality
- 'T' key toggle shortcut

#### Frame Display
- Converts OpenCV frames to QImage/QPixmap
- Handles both BGR (3-channel) and BGRA (4-channel with alpha)
- Scales to fit QLabel dimensions while maintaining aspect ratio

## Important Implementation Notes

1. **Segmentation Readiness**: The app waits for 5 valid frames before enabling transparent mode to ensure stable background removal

2. **Mask Validation**: Checks if mask mean > 0.01 to verify person detection before allowing transparent mode

3. **Logging**: Configured to write to both `app.log` file and console with timestamp and level info

4. **Qt Image Format**: Use `QImage.Format.Format_RGBA8888` for transparent frames, not RGB888

5. **Event Processing**: Multiple `QCoreApplication.processEvents()` calls needed when toggling transparent mode to ensure proper window composition

## Code Organization Pattern

When adding features:
- Keep UI initialization in `init_ui()` method
- Use separate methods for distinct functionality (e.g., `detect_cameras()`, `remove_background()`)
- Store UI elements as instance variables for later access/modification
- Use QTimer for frame updates (33ms interval ≈ 30 FPS)
- Release resources properly in `closeEvent()`
