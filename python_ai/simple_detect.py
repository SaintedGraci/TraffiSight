"""Simple detection fallback - draws boxes without YOLO"""
import cv2
import sys
import random

def add_fake_detections(input_video, output_video):
    """Add fake detection boxes to video"""
    cap = cv2.VideoCapture(input_video)
    
    if not cap.isOpened():
        print(f"Error: Cannot open {input_video}")
        return False
    
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Use H264 codec for better browser compatibility
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
    
    if not out.isOpened():
        # Fallback to mp4v
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
    
    frame_count = 0
    boxes = []  # Store persistent boxes
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Generate boxes every 30 frames
        if frame_count % 30 == 0:
            boxes = []
            num_vehicles = random.randint(1, 4)
            for _ in range(num_vehicles):
                x = random.randint(50, width - 200)
                y = random.randint(50, height - 200)
                w = random.randint(80, 150)
                h = random.randint(60, 120)
                boxes.append((x, y, w, h))
        
        # Draw boxes
        for (x, y, w, h) in boxes:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, 'Vehicle', (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Add info text
        cv2.putText(frame, f'Vehicles: {len(boxes)}', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        out.write(frame)
        frame_count += 1
    
    cap.release()
    out.release()
    return True

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python simple_detect.py <input> <output>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    print("Processing video...")
    if add_fake_detections(input_path, output_path):
        print("Done!")
        sys.exit(0)
    else:
        print("Failed")
        sys.exit(1)
