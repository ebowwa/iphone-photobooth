#!/usr/bin/env python3
"""
iPhone Photobooth - Main Application
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from capture.usb_camera import iPhoneCameraWithAudio
from capture.rtsp_stream import RTSPReceiver
from utils.device_finder import list_cameras


def main():
    parser = argparse.ArgumentParser(
        description="iPhone Photobooth - High-quality camera capture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # USB camera with audio
  python main.py usb
  
  # RTSP streaming
  python main.py rtsp --url rtsp://192.168.1.100:554/live
  
  # List available cameras
  python main.py list
        """
    )
    
    subparsers = parser.add_subparsers(dest='mode', help='Operation mode')
    
    # USB mode
    usb_parser = subparsers.add_parser('usb', help='USB/Continuity Camera mode')
    usb_parser.add_argument('--camera', type=int, default=None, 
                           help='Camera index (auto-detect if not specified)')
    usb_parser.add_argument('--output', type=str, default='outputs/recordings',
                           help='Output directory')
    
    # RTSP mode
    rtsp_parser = subparsers.add_parser('rtsp', help='RTSP streaming mode')
    rtsp_parser.add_argument('--url', type=str, required=True,
                            help='RTSP URL (e.g., rtsp://192.168.1.100:554/live)')
    rtsp_parser.add_argument('--output', type=str, default='outputs/recordings',
                            help='Output directory')
    
    # List cameras
    list_parser = subparsers.add_parser('list', help='List available cameras')
    
    args = parser.parse_args()
    
    if not args.mode:
        parser.print_help()
        print("\n✨ Quick start: python main.py usb")
        return
    
    try:
        if args.mode == 'usb':
            print("🎥 Starting USB Camera Mode...")
            camera = iPhoneCameraWithAudio(args.output)
            if args.camera is not None:
                camera.connect(args.camera)
            else:
                camera.connect()
            camera.run()
            
        elif args.mode == 'rtsp':
            print("📡 Starting RTSP Streaming Mode...")
            receiver = RTSPReceiver(args.url, args.output)
            receiver.run()
            
        elif args.mode == 'list':
            print("🔍 Scanning for cameras...")
            list_cameras()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()