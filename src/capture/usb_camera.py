#!/usr/bin/env python3
"""
iPhone Camera with Audio Recording
Captures both video and audio from iPhone when connected
"""

import cv2
import numpy as np
import datetime
import os
import time
import threading
import queue
import subprocess
import tempfile
from typing import Optional
import argparse
import pyaudio
import wave


class iPhoneCameraWithAudio:
    def __init__(self, output_dir: str = "recordings"):
        """
        Initialize iPhone camera with audio interface
        
        Args:
            output_dir: Directory to save recordings and screenshots
        """
        self.output_dir = output_dir
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_recording = False
        self.video_writer: Optional[cv2.VideoWriter] = None
        
        # Audio recording components
        self.audio = pyaudio.PyAudio()
        self.audio_stream = None
        self.audio_frames = []
        self.audio_thread = None
        self.audio_recording = False
        
        # Temporary files for sync
        self.temp_video_file = None
        self.temp_audio_file = None
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Video settings
        self.fps = 30
        self.frame_width = 1920
        self.frame_height = 1080
        
        # Audio settings
        self.audio_format = pyaudio.paInt16
        self.channels = 1  # Mono (most Mac mics are mono)
        self.sample_rate = 44100
        self.chunk_size = 1024
        
    def list_audio_devices(self):
        """List all available audio devices"""
        print("\nAvailable audio devices:")
        info = self.audio.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        
        iphone_device_index = None
        
        for i in range(num_devices):
            device_info = self.audio.get_device_info_by_host_api_device_index(0, i)
            if device_info.get('maxInputChannels') > 0:
                device_name = device_info.get('name')
                print(f"  {i}: {device_name} (Channels: {device_info.get('maxInputChannels')})")
                
                # Try to identify iPhone microphone
                if 'iPhone' in device_name or 'iOS' in device_name or 'Continuity' in device_name:
                    iphone_device_index = i
                    print(f"     ^ Detected as iPhone microphone")
        
        return iphone_device_index
    
    def setup_audio(self, device_index: Optional[int] = None):
        """Setup audio recording stream"""
        if device_index is None:
            # Try to auto-detect iPhone microphone
            device_index = self.list_audio_devices()
            
            if device_index is None:
                # Use default microphone
                print("\nUsing default microphone (iPhone not detected in audio devices)")
                device_index = None
            else:
                print(f"\nUsing iPhone microphone at index {device_index}")
        
        try:
            self.audio_stream = self.audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size
            )
            print("Audio stream initialized successfully")
            return True
        except Exception as e:
            print(f"Failed to initialize audio: {e}")
            print("Will record video only")
            return False
    
    def record_audio(self):
        """Record audio in a separate thread"""
        if not self.audio_stream:
            return
            
        self.audio_frames = []
        while self.audio_recording:
            try:
                data = self.audio_stream.read(self.chunk_size, exception_on_overflow=False)
                self.audio_frames.append(data)
            except Exception as e:
                print(f"Audio recording error: {e}")
                break
    
    def save_audio(self, filename):
        """Save recorded audio to WAV file"""
        if not self.audio_frames:
            return None
            
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.audio_format))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(self.audio_frames))
        wf.close()
        
        return filename
    
    def merge_audio_video(self, video_file, audio_file, output_file):
        """Merge audio and video files using ffmpeg"""
        print("Merging audio and video...")
        
        # Check if ffmpeg is available
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ffmpeg not found. Installing via brew...")
            subprocess.run(['brew', 'install', 'ffmpeg'], check=True)
        
        # Merge audio and video
        cmd = [
            'ffmpeg',
            '-i', video_file,
            '-i', audio_file,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            '-y',  # Overwrite output
            output_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"Successfully created: {output_file}")
            
            # Clean up temporary files
            os.remove(video_file)
            os.remove(audio_file)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to merge audio/video: {e}")
            print(f"Video saved as: {video_file}")
            if audio_file and os.path.exists(audio_file):
                print(f"Audio saved as: {audio_file}")
            return False
    
    def find_iphone_camera(self) -> int:
        """Find the iPhone camera index"""
        print("Searching for cameras...")
        
        for index in range(10):
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                
                ret, frame = cap.read()
                cap.release()
                
                if ret:
                    print(f"Camera {index}: {int(width)}x{int(height)}")
                    
                    # Higher resolution cameras are likely external/iPhone
                    if width >= 1920 or height >= 1080:
                        return index
        
        # Default to first camera if no high-res found
        return 0
    
    def connect(self, camera_index: Optional[int] = None) -> bool:
        """Connect to iPhone camera"""
        if camera_index is None:
            camera_index = self.find_iphone_camera()
        
        print(f"Connecting to camera at index {camera_index}...")
        
        self.cap = cv2.VideoCapture(camera_index)
        
        if not self.cap.isOpened():
            print("Failed to open camera")
            return False
        
        # Try to set optimal resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Get actual properties
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        
        print(f"Connected! Camera: {self.frame_width}x{self.frame_height} @ {self.fps}fps")
        
        # Setup audio
        self.setup_audio()
        
        return True
    
    def start_recording(self) -> bool:
        """Start recording video and audio"""
        if self.is_recording:
            print("Already recording!")
            return False
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create temporary files for video and audio
        self.temp_video_file = os.path.join(self.output_dir, f"temp_video_{timestamp}.mp4")
        self.temp_audio_file = os.path.join(self.output_dir, f"temp_audio_{timestamp}.wav")
        self.final_output_file = os.path.join(self.output_dir, f"recording_{timestamp}.mp4")
        
        # Start video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(
            self.temp_video_file,
            fourcc,
            self.fps,
            (self.frame_width, self.frame_height)
        )
        
        if not self.video_writer.isOpened():
            print("Failed to initialize video writer")
            return False
        
        # Start audio recording thread if audio is available
        if self.audio_stream:
            self.audio_recording = True
            self.audio_thread = threading.Thread(target=self.record_audio)
            self.audio_thread.start()
            print(f"Recording started (with audio): {self.final_output_file}")
        else:
            print(f"Recording started (video only): {self.temp_video_file}")
        
        self.is_recording = True
        return True
    
    def stop_recording(self):
        """Stop recording and merge audio/video"""
        if not self.is_recording:
            print("Not currently recording")
            return
        
        self.is_recording = False
        
        # Stop video recording
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        
        # Stop audio recording
        if self.audio_recording:
            self.audio_recording = False
            if self.audio_thread:
                self.audio_thread.join()
            
            # Save audio
            if self.audio_frames:
                self.save_audio(self.temp_audio_file)
                
                # Merge audio and video
                self.merge_audio_video(
                    self.temp_video_file,
                    self.temp_audio_file,
                    self.final_output_file
                )
            else:
                # No audio frames, just rename video
                os.rename(self.temp_video_file, self.final_output_file)
                print(f"Recording saved (video only): {self.final_output_file}")
        else:
            # Video only recording
            final_file = self.temp_video_file.replace('temp_video_', 'recording_')
            os.rename(self.temp_video_file, final_file)
            print(f"Recording saved: {final_file}")
        
        print("Recording stopped")
    
    def take_screenshot(self, frame):
        """Take a screenshot"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"screenshot_{timestamp}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Screenshot saved: {filename}")
    
    def run(self):
        """Main run loop"""
        if not self.cap or not self.cap.isOpened():
            if not self.connect():
                return
        
        window_name = "iPhone Camera (with Audio)"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        print("\nControls:")
        print("  SPACE - Start/Stop recording (video + audio)")
        print("  S     - Take screenshot")
        print("  F     - Toggle fullscreen")
        print("  R     - Reset camera connection")
        print("  Q/ESC - Quit")
        
        fullscreen = False
        
        while True:
            ret, frame = self.cap.read()
            
            if not ret:
                print("Failed to read frame")
                time.sleep(0.1)
                continue
            
            # Add overlay
            display_frame = frame.copy()
            
            # Recording indicator
            if self.is_recording:
                cv2.circle(display_frame, (30, 30), 10, (0, 0, 255), -1)
                cv2.putText(display_frame, "REC", (50, 35),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Show if audio is being recorded
                if self.audio_stream:
                    cv2.putText(display_frame, "Audio: ON", (50, 60),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(display_frame, timestamp, (10, self.frame_height - 20),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Resolution info
            info_text = f"{self.frame_width}x{self.frame_height} @ {self.fps:.0f}fps"
            cv2.putText(display_frame, info_text, (self.frame_width - 200, 30),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow(window_name, display_frame)
            
            # Write frame if recording
            if self.is_recording and self.video_writer:
                self.video_writer.write(frame)
            
            # Handle keyboard
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
            elif key == ord('f'):  # F - Fullscreen
                fullscreen = not fullscreen
                if fullscreen:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,
                                        cv2.WINDOW_FULLSCREEN)
                else:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,
                                        cv2.WINDOW_NORMAL)
            elif key == ord('r'):  # R - Reset
                print("Resetting connection...")
                self.cleanup()
                time.sleep(1)
                if not self.connect():
                    break
        
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("\nShutting down...")
        
        # Stop recording
        if self.is_recording:
            self.stop_recording()
        
        # Close audio stream
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        
        # Close camera
        if self.cap:
            self.cap.release()
        
        # Close audio
        self.audio.terminate()
        
        # Close windows
        cv2.destroyAllWindows()
        
        print("Cleanup complete")


def main():
    parser = argparse.ArgumentParser(description="iPhone Camera with Audio Recording")
    parser.add_argument("--camera", type=int, default=None, help="Camera index")
    parser.add_argument("--audio", type=int, default=None, help="Audio device index")
    parser.add_argument("--output", type=str, default="recordings", help="Output directory")
    
    args = parser.parse_args()
    
    print("iPhone Camera with Audio Recording")
    print("=" * 40)
    
    camera = iPhoneCameraWithAudio(args.output)
    
    if args.camera is not None:
        camera.connect(args.camera)
    else:
        camera.connect()
    
    try:
        camera.run()
    except KeyboardInterrupt:
        print("\nInterrupted")
        camera.cleanup()
    except Exception as e:
        print(f"Error: {e}")
        camera.cleanup()


if __name__ == "__main__":
    main()