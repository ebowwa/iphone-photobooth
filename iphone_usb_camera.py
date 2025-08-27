#!/usr/bin/env python3
"""
iPhone USB Camera Interface
Uses the iPhone as a webcam when connected via USB
"""

import cv2
import numpy as np
import datetime
import os
import time
from typing import Optional
import argparse


class iPhoneUSBCamera:
    def __init__(self, output_dir: str = "recordings"):
        """
        Initialize iPhone USB camera interface
        
        Args:
            output_dir: Directory to save recordings and screenshots
        """
        self.output_dir = output_dir
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_recording = False
        self.video_writer: Optional[cv2.VideoWriter] = None
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Video settings
        self.fps = 30
        self.frame_width = 1920
        self.frame_height = 1080
        
    def find_iphone_camera(self) -> int:
        """Find the iPhone camera index"""
        print("Searching for iPhone camera...")
        
        # Try different camera indices
        for index in range(10):
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                # Check if this might be the iPhone
                width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                
                # Read a test frame
                ret, frame = cap.read()
                cap.release()
                
                if ret and width > 640 and height > 480:
                    print(f"Found camera at index {index}: {int(width)}x{int(height)}")
                    
                    # Try to determine if it's the iPhone
                    # iPhones typically offer higher resolutions
                    if width >= 1280 or height >= 720:
                        response = input(f"Is this your iPhone camera? (y/n): ")
                        if response.lower() == 'y':
                            return index
            else:
                cap.release()
                
        return -1
        
    def connect(self, camera_index: Optional[int] = None) -> bool:
        """Connect to iPhone camera"""
        if camera_index is None:
            camera_index = self.find_iphone_camera()
            if camera_index == -1:
                print("Could not find iPhone camera. Make sure:")
                print("1. iPhone is connected via USB")
                print("2. You've trusted this computer on your iPhone")
                print("3. The camera is not being used by another app")
                return False
        
        print(f"Connecting to camera at index {camera_index}...")
        
        # Set up video capture
        self.cap = cv2.VideoCapture(camera_index)
        
        if not self.cap.isOpened():
            print("Failed to open camera")
            return False
        
        # Try to set optimal resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        # Set buffer size for lower latency
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Get actual stream properties
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        if self.fps <= 0:
            self.fps = 30  # Default fallback
            
        print(f"Connected! Camera info: {self.frame_width}x{self.frame_height} @ {self.fps}fps")
        return True
        
    def start_recording(self) -> bool:
        """Start recording the stream"""
        if self.is_recording:
            print("Already recording!")
            return False
            
        # Generate filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"recording_{timestamp}.mp4")
        
        # Set up video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(
            filename, 
            fourcc, 
            self.fps, 
            (self.frame_width, self.frame_height)
        )
        
        if not self.video_writer.isOpened():
            print("Failed to initialize video writer")
            self.video_writer = None
            return False
            
        self.is_recording = True
        print(f"Recording started: {filename}")
        return True
        
    def stop_recording(self):
        """Stop recording"""
        if not self.is_recording:
            print("Not currently recording")
            return
            
        self.is_recording = False
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        print("Recording stopped")
        
    def take_screenshot(self, frame):
        """Take a screenshot of current frame"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"screenshot_{timestamp}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Screenshot saved: {filename}")
        
    def run(self):
        """Main run loop"""
        if not self.cap or not self.cap.isOpened():
            print("Camera not connected. Attempting to connect...")
            if not self.connect():
                return
        
        window_name = "iPhone Camera (USB)"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        print("\nControls:")
        print("  SPACE - Start/Stop recording")
        print("  S     - Take screenshot")
        print("  F     - Toggle fullscreen")
        print("  R     - Reset camera connection")
        print("  Q/ESC - Quit")
        print("\nPress any key in the video window to activate controls")
        
        fullscreen = False
        
        while True:
            ret, frame = self.cap.read()
            
            if not ret:
                print("Failed to read frame. Press 'R' to reconnect or 'Q' to quit")
                key = cv2.waitKey(1000) & 0xFF
                if key == ord('q') or key == 27:
                    break
                elif key == ord('r'):
                    self.cap.release()
                    if self.connect():
                        continue
                continue
            
            # Add overlay information
            display_frame = frame.copy()
            
            # Add recording indicator
            if self.is_recording:
                cv2.circle(display_frame, (30, 30), 10, (0, 0, 255), -1)
                cv2.putText(display_frame, "REC", (50, 35), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Add timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(display_frame, timestamp, (10, self.frame_height - 20),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Add resolution info
            info_text = f"{self.frame_width}x{self.frame_height} @ {self.fps:.0f}fps"
            cv2.putText(display_frame, info_text, (self.frame_width - 200, 30),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Display frame
            cv2.imshow(window_name, display_frame)
            
            # Write frame if recording
            if self.is_recording and self.video_writer:
                self.video_writer.write(frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == 27:  # Q or ESC
                break
            elif key == ord(' '):  # Space - Toggle recording
                if self.is_recording:
                    self.stop_recording()
                else:
                    self.start_recording()
            elif key == ord('s'):  # S - Screenshot
                self.take_screenshot(frame)
            elif key == ord('f'):  # F - Fullscreen toggle
                fullscreen = not fullscreen
                if fullscreen:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, 
                                        cv2.WINDOW_FULLSCREEN)
                else:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, 
                                        cv2.WINDOW_NORMAL)
            elif key == ord('r'):  # R - Reset connection
                print("Resetting camera connection...")
                self.cap.release()
                time.sleep(1)
                if not self.connect():
                    break
                    
        self.cleanup()
        
    def cleanup(self):
        """Clean up resources"""
        print("\nShutting down...")
        
        # Stop recording if active
        if self.is_recording:
            self.stop_recording()
            
        # Release resources
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        
        print("Cleanup complete")


def main():
    parser = argparse.ArgumentParser(description="iPhone USB Camera Interface")
    parser.add_argument(
        "--camera",
        type=int,
        default=None,
        help="Camera index (will auto-detect if not specified)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="recordings",
        help="Output directory for recordings (default: recordings)"
    )
    
    args = parser.parse_args()
    
    print("iPhone USB Camera Interface")
    print("=" * 40)
    print(f"Output Directory: {args.output}")
    print("=" * 40)
    
    camera = iPhoneUSBCamera(args.output)
    
    if args.camera is not None:
        if not camera.connect(args.camera):
            print("Failed to connect to specified camera")
            return
    else:
        if not camera.connect():
            return
    
    try:
        camera.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        camera.cleanup()
    except Exception as e:
        print(f"Error: {e}")
        camera.cleanup()


if __name__ == "__main__":
    main()