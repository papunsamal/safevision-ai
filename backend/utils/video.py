import cv2
import os
import numpy as np  # ✅ FIX: Added missing import for type hints
from typing import Generator, Tuple, List, Dict
from ..config import settings
from .logger import get_logger

logger = get_logger("video_utils")


def open_video(path: str) -> cv2.VideoCapture:
    """
    Safely opens a video file using OpenCV.
    Raises FileNotFoundError if path doesn't exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Video file not found at: {path}")
    
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video file: {path}")
        
    return cap


def get_frame_count(cap: cv2.VideoCapture) -> int:
    """Returns total number of frames in the video."""
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # Fallback for streams or corrupted headers where count might be 0/-1
    return max(count, 1) 


def sample_frames(
    cap: cv2.VideoCapture, 
    every_n: int = 10, 
    max_frames: int = 50
) -> Generator[Tuple[int, np.ndarray], None, None]:
    """
    Yields sampled frames from a VideoCapture object.
    
    Args:
        cap: OpenCV VideoCapture object.
        every_n: Sample every N-th frame (e.g., 10 means 1st, 11th, 21st...).
                 Lower value = more accurate but slower. Higher = faster but less precise.
        max_frames: Safety limit to prevent infinite loops on live streams/corrupt files.
    
    Yields:
        Tuple[frame_index, frame_image]
    """
    frame_idx = 0
    yielded_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Check safety limits
            if yielded_count >= max_frames:
                logger.warning(f"Max frames ({max_frames}) reached. Stopping sampling.")
                break
                
            # Yield only selected frames based on interval
            if frame_idx % every_n == 0:
                yield frame_idx, frame
                yielded_count += 1
                
            frame_idx += 1
            
    except Exception as e:
        logger.error(f"Error during frame sampling: {e}")
    finally:
        # Ensure resources are released even if loop breaks early
        pass # Cap release handled by caller usually, but good practice here too if needed
        
def to_percent_boxes(dets: List[Dict], width: int, height: int) -> List[Dict]:
    """
    Converts absolute pixel coordinates [x1,y1,x2,y2] to percentage-based 
    relative coordinates suitable for CSS positioning in React frontend.
    
    Returns list of dicts with keys: x, y, w, h (percentages).
    """
    percent_dets = []
    for d in dets:
        x1, y1, x2, y2 = d["bbox"]
        
        # Calculate width and height in pixels first
        box_w = abs(x2 - x1)
        box_h = abs(y2 - y1)
        
        # Convert to percentages relative to original video dimensions
        pct_x = (min(x1, x2) / width) * 100
        pct_y = (min(y1, y2) / height) * 100
        pct_w = (box_w / width) * 100
        pct_h = (box_h / height) * 100
        
        # Clamp values between 0-100 just in case of edge cases
        pct_x = max(0, min(pct_x, 100))
        pct_y = max(0, min(pct_y, 100))
        pct_w = max(0, min(pct_w, 100))
        pct_h = max(0, min(pct_h, 100))
        
        percent_dets.append({
            "label": d["label"],
            "confidence": d["confidence"],
            "x": round(pct_x, 2),
            "y": round(pct_y, 2),
            "w": round(pct_w, 2),
            "h": round(pct_h, 2),
            # Keep original bbox for backend calculations if needed later
            "_original_bbox": d["bbox"] 
        })
        
    return percent_dets