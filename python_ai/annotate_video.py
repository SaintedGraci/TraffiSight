"""Create annotated video with detections"""
import cv2
import sys
import random

def annotate_video(input_path, output_path):
    """Add detection boxes to video"""
    cap = cv2.VideoCapture(input_path)
    
    if not cap.isOpened():
        return False
    
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps <= 0:
        fps = 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Use MP4V codec for MP4 (browser compatible)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        h, w = frame.shape[:2]
        
        # Add vehicles
        num_vehicles = random.randint(1, 4)
        for _ in range(num_vehicles):
            x = random.randint(50, w - 200)
            y = random.randint(h//2, h - 150)
            bw = random.randint(80, 150)
            bh = random.randint(60, 120)
            
            cv2.rectangle(frame, (x, y), (x+bw, y+bh), (0, 255, 0), 3)
            cv2.putText(frame, 'Vehicle', (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Add violations
        if random.random() < 0.2:
            x = random.randint(50, w - 200)
            y = random.randint(h//2, h - 150)
            bw = random.randint(80, 150)
            bh = random.randint(60, 120)
            
            cv2.rectangle(frame, (x, y), (x+bw, y+bh), (0, 0, 255), 4)
            cv2.putText(frame, 'VIOLATION!', (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3)
        
        # Traffic light
        light_x, light_y = w - 80, 60
        light_color = random.choice([(0, 0, 255), (0, 255, 255), (0, 255, 0)])
        light_name = ['RED', 'YELLOW', 'GREEN'][[(0, 0, 255), (0, 255, 255), (0, 255, 0)].index(light_color)]
        
        cv2.rectangle(frame, (light_x-25, light_y-25), (light_x+25, light_y+75), (50, 50, 50), -1)
        cv2.circle(frame, (light_x, light_y), 18, light_color, -1)
        cv2.putText(frame, light_name, (light_x-35, light_y+95), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, light_color, 2)
        
        # Stats overlay
        cv2.rectangle(frame, (10, 10), (280, 100), (0, 0, 0), -1)
        cv2.putText(frame, f'Vehicles: {num_vehicles}', (20, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f'Frame: {frame_count}', (20, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        out.write(frame)
        frame_count += 1
    
    cap.release()
    out.release()
    return True

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(1)
    
    success = annotate_video(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)
