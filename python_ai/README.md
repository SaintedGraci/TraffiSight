# TraffiSight AI - Python AI Engine

This folder contains the AI detection engine that analyzes traffic videos.

## Quick Setup

Run from project root:
```bash
setup-python-dependencies.bat
```

Or manually:
```bash
cd python_ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Required Files

### YOLO Model
Download yolov8n.pt and place in models/ folder:
- URL: https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
- Location: python_ai/models/yolov8n.pt

### Environment Configuration
Copy .env.example to .env:
```bash
copy .env.example .env
```

## Dependencies

All Python packages are listed in requirements.txt:
- opencv-python - Video processing
- ultralytics - YOLOv8 object detection
- torch - Deep learning framework
- numpy - Numerical operations
- easyocr - License plate recognition

## Usage

The Python scripts are called automatically by the Laravel application.
No manual execution needed for normal operation.

For testing:
```bash
cd python_ai
venv\Scripts\activate
python extract_frames.py "path/to/video.mp4" "output/folder"
```
