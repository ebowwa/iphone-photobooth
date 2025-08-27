#!/usr/bin/env python3
"""List all available cameras"""

import cv2

def list_cameras():
    """List all available camera devices"""
    print("Scanning for available cameras...\n")
    
    available_cameras = []
    
    for index in range(10):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            print(f"Camera {index}:")
            print(f"  Resolution: {width}x{height}")
            print(f"  FPS: {fps}")
            
            # Try to get backend name
            backend = cap.getBackendName()
            print(f"  Backend: {backend}")
            
            available_cameras.append(index)
            cap.release()
            print()
    
    if not available_cameras:
        print("No cameras found!")
    else:
        print(f"Found {len(available_cameras)} camera(s): {available_cameras}")
        
        # If iPhone is connected via Continuity Camera, it usually appears as index 0 or 1
        if len(available_cameras) > 0:
            print("\nTo use a camera, run:")
            print(f"  python iphone_usb_camera.py --camera {available_cameras[0]}")
    
    return available_cameras

if __name__ == "__main__":
    list_cameras()