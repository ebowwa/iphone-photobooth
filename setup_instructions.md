# iPhone as Webcam using RTSP

## Setup Instructions

### Step 1: Install iPhone RTSP App

Install one of these RTSP streaming apps on your iPhone:
- **LARIX Broadcaster** (Free, recommended)
- **IPCams** 
- **Live:Air Solo**

### Step 2: Configure iPhone App

For LARIX Broadcaster:
1. Open the app
2. Tap Settings (gear icon)
3. Go to "Connections" 
4. Tap "+" to add new connection
5. Select "RTSP server"
6. Note the RTSP URL (usually `rtsp://[iPhone-IP]:554/live`)
7. Start broadcasting

### Step 3: Find Your iPhone's IP Address

On iPhone:
1. Go to Settings → Wi-Fi
2. Tap the (i) next to your connected network
3. Note the IP Address

### Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run the Receiver

Basic usage:
```bash
python rtsp_receiver.py --url rtsp://[iPhone-IP]:554/live
```

Example with custom settings:
```bash
python rtsp_receiver.py --url rtsp://192.168.1.100:554/live --output my_recordings
```

## Controls

When the video window is active:
- **SPACE** - Start/Stop recording
- **S** - Take screenshot
- **F** - Toggle fullscreen
- **Q/ESC** - Quit

## Tips

1. **Best Quality**: In your iPhone RTSP app, set:
   - Resolution: 1920x1080 (or highest available)
   - Bitrate: 4000-8000 kbps
   - FPS: 30 or 60

2. **Low Latency**: Ensure both devices are on the same Wi-Fi network

3. **Stable Connection**: Use 5GHz Wi-Fi if available

## Troubleshooting

- **Connection Failed**: Verify the IP address and that both devices are on same network
- **Black Screen**: Check that the iPhone app is actively broadcasting
- **High Latency**: Reduce video quality settings in the iPhone app
- **Choppy Video**: Lower the bitrate or resolution in iPhone app settings

## Output Files

- **Recordings**: Saved as MP4 files in the `recordings` folder
- **Screenshots**: Saved as JPG files in the same folder
- **Naming**: Files are timestamped (YYYYMMDD_HHMMSS format)