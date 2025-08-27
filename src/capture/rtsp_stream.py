#!/usr/bin/env python3
"""
iPhone RTSP Stream Receiver
Receives RTSP stream from iPhone and provides display/recording capabilities
"""

import cv2
import numpy as np
import datetime
import os
import threading
import queue
import time
from typing import Optional, Tuple
import argparse


class RTSPReceiver:
    def __init__(self, rtsp_url: str, output_dir: str = "recordings"):
        """
        Initialize RTSP receiver
        
        Args:
            rtsp_url: RTSP stream URL from iPhone
            output_dir: Directory to save recordings
        """
        self.rtsp_url = rtsp_url
        self.output_dir = output_dir
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_recording = False
        self.video_writer: Optional[cv2.VideoWriter] = None
        self.frame_queue = queue.Queue(maxsize=30)
        self.recording_thread: Optional[threading.Thread] = None
        self.display_thread: Optional[threading.Thread] = None
        self.stop_threads = threading.Event()
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Video settings
        self.fps = 30
        self.frame_width = 1920
        self.frame_height = 1080
        
    def connect(self) -> bool:
        """Connect to RTSP stream"""
        print(f"Connecting to RTSP stream: {self.rtsp_url}")
        
        # Set up video capture with optimal settings for RTSP
        self.cap = cv2.VideoCapture(self.rtsp_url)
        
        # Set buffer size to reduce latency
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Try to set optimal resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        if not self.cap.isOpened():
            print("Failed to connect to RTSP stream")
            return False
            
        # Get actual stream properties
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        if self.fps <= 0:
            self.fps = 30  # Default fallback
            
        print(f"Connected! Stream info: {self.frame_width}x{self.frame_height} @ {self.fps}fps")
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
        
    def capture_frames(self):
        """Capture frames from RTSP stream (runs in thread)"""
        while not self.stop_threads.is_set():
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    # Add frame to queue for display
                    if not self.frame_queue.full():
                        self.frame_queue.put(frame)
                    
                    # Write frame if recording
                    if self.is_recording and self.video_writer:
                        self.video_writer.write(frame)
                else:
                    print("Failed to read frame, attempting reconnection...")
                    time.sleep(1)
                    self.connect()
            else:
                time.sleep(0.1)
                
    def display_frames(self):
        """Display frames with overlay info (runs in thread)"""
        window_name = "iPhone Camera Stream"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        while not self.stop_threads.is_set():
            try:
                frame = self.frame_queue.get(timeout=1)
                
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
                
                cv2.imshow(window_name, display_frame)
                
            except queue.Empty:
                continue
                
    def run(self):
        """Main run loop"""
        if not self.connect():
            return
            
        # Start capture thread
        self.capture_thread = threading.Thread(target=self.capture_frames)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        
        # Start display thread
        self.display_thread = threading.Thread(target=self.display_frames)
        self.display_thread.daemon = True
        self.display_thread.start()
        
        print("\nControls:")
        print("  SPACE - Start/Stop recording")
        print("  S     - Take screenshot")
        print("  F     - Toggle fullscreen")
        print("  Q/ESC - Quit")
        print("\nPress any key in the video window to activate controls")
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == 27:  # Q or ESC
                break
            elif key == ord(' '):  # Space
                if self.is_recording:
                    self.stop_recording()
                else:
                    self.start_recording()
            elif key == ord('s'):  # S - Screenshot
                self.take_screenshot()
            elif key == ord('f'):  # F - Fullscreen toggle
                self.toggle_fullscreen()
                
        self.cleanup()
        
    def take_screenshot(self):
        """Take a screenshot of current frame"""
        try:
            if not self.frame_queue.empty():
                frame = self.frame_queue.queue[-1]  # Get last frame without removing
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(self.output_dir, f"screenshot_{timestamp}.jpg")
                cv2.imwrite(filename, frame)
                print(f"Screenshot saved: {filename}")
        except:
            print("Failed to take screenshot")
            
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        window_name = "iPhone Camera Stream"
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, 
                            cv2.WINDOW_FULLSCREEN)
        
    def cleanup(self):
        """Clean up resources"""
        print("\nShutting down...")
        
        # Stop threads
        self.stop_threads.set()
        
        # Stop recording if active
        if self.is_recording:
            self.stop_recording()
            
        # Release resources
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        
        print("Cleanup complete")


def main():
    parser = argparse.ArgumentParser(description="iPhone RTSP Stream Receiver")
    parser.add_argument(
        "--url",
        type=str,
        default="rtsp://192.168.1.100:554/live",
        help="RTSP URL (default: rtsp://192.168.1.100:554/live)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="recordings",
        help="Output directory for recordings (default: recordings)"
    )
    
    args = parser.parse_args()
    
    print("iPhone RTSP Stream Receiver")
    print("=" * 40)
    print(f"RTSP URL: {args.url}")
    print(f"Output Directory: {args.output}")
    print("=" * 40)
    
    receiver = RTSPReceiver(args.url, args.output)
    
    try:
        receiver.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        receiver.cleanup()
    except Exception as e:
        print(f"Error: {e}")
        receiver.cleanup()


if __name__ == "__main__":
    main()