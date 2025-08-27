# iPhone Photobooth

Use your iPhone as a high-quality webcam for Mac via USB or RTSP streaming.

## Features

- 📹 High-quality video capture (up to 1920x1080)
- 🎤 Audio recording support
- 💾 Record videos (MP4 format)
- 📸 Take screenshots
- 🖥️ Fullscreen mode
- 🔄 Auto-reconnection
- 🎬 Real-time preview with recording indicator

## Installation

1. Install dependencies:
```bash
# Create virtual environment
uv venv
source .venv/bin/activate

# Install Python packages
uv pip install -r requirements.txt

# Install system dependencies (if needed)
brew install portaudio  # For audio support
brew install ffmpeg     # For audio/video merging
```

## Usage

### USB Connection (Continuity Camera)

For iPhone with iOS 16+ connected via USB:

```bash
# Run with auto-detection
python iphone_camera_with_audio.py

# Or specify camera index
python iphone_camera_with_audio.py --camera 0
```

### RTSP Streaming

For wireless streaming using RTSP:

1. Install LARIX Broadcaster (or similar) on iPhone
2. Configure RTSP server in the app
3. Run the receiver:

```bash
python rtsp_receiver.py --url rtsp://[iPhone-IP]:554/live
```

## Controls

- **SPACE** - Start/Stop recording
- **S** - Take screenshot
- **F** - Toggle fullscreen
- **R** - Reset connection (USB mode)
- **Q/ESC** - Quit

## Files

- `iphone_camera_with_audio.py` - USB camera with audio recording
- `iphone_usb_camera.py` - Basic USB camera interface
- `rtsp_receiver.py` - RTSP stream receiver
- `list_cameras.py` - Utility to list available cameras

## Output

All recordings and screenshots are saved to the `recordings/` folder with timestamps.

## Requirements

- macOS
- Python 3.9+
- iPhone with iOS 16+ (for Continuity Camera)
- USB cable or Wi-Fi connection

## License

MIT