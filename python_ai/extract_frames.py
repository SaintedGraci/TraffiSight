"""Extract frames with fake detections"""
import cv2
import sys
import random
import os
import json

def extract_with_detections(video_path, output_dir, max_frames=20):
    """Extract frames and add detection boxes"""
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"ERROR: Could not open video: {video_path}")
        return False
    
    # Check if video has valid dimensions
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    if width < 100 or height < 100:
        print(f"ERROR: Invalid video dimensions: {width}x{height}")
        cap.release()
        return False
    
    os.makedirs(output_dir, exist_ok=True)
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    interval = max(1, total_frames // max_frames)
    
    frame_num = 0
    saved = 0
    violations = []
    
    # Traffic light state tracking
    traffic_light_state = 'GREEN'  # Start with green
    frames_since_light_change = 0
    
    # Track vehicle positions across frames to detect actual red light running
    vehicles_in_frame = []
    
    while saved < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_num % interval == 0:
            h, w = frame.shape[:2]
            
            # Change traffic light state periodically
            frames_since_light_change += 1
            if frames_since_light_change > 3:  # Change every ~3 frames (more frequent RED)
                frames_since_light_change = 0
                # More RED lights for more violations
                if traffic_light_state == 'GREEN':
                    traffic_light_state = random.choices(['GREEN', 'YELLOW', 'RED'], weights=[30, 20, 50])[0]
                elif traffic_light_state == 'YELLOW':
                    traffic_light_state = 'RED'  # Always go RED after YELLOW
                elif traffic_light_state == 'RED':
                    traffic_light_state = random.choices(['RED', 'GREEN'], weights=[60, 40])[0]  # Stay RED longer
            
            # Map traffic light colors
            light_color_map = {
                'RED': (0, 0, 255),
                'YELLOW': (0, 255, 255),
                'GREEN': (0, 255, 0)
            }
            light_color = light_color_map[traffic_light_state]
            
            # Add vehicles (green boxes) - ALWAYS show vehicles
            num_vehicles = random.randint(2, 4)
            current_frame_vehicles = []
            
            for i in range(num_vehicles):
                if w > 250:
                    x = random.randint(50, max(51, w - 200))
                    y = random.randint(max(h//2, 50), max(51, h - 150))
                    bw = random.randint(80, min(150, w - x - 10))
                    bh = random.randint(60, min(120, h - y - 10))
                    
                    # Vehicle is moving (simulate movement)
                    is_moving = random.random() > 0.3  # 70% are moving
                    
                    current_frame_vehicles.append({
                        'x': x, 'y': y, 'w': bw, 'h': bh,
                        'moving': is_moving
                    })
                    
                    # Normal vehicle - green box
                    cv2.rectangle(frame, (x, y), (x+bw, y+bh), (0, 255, 0), 3)
                    cv2.putText(frame, 'Vehicle', (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Detect violations - ONLY if light is RED AND vehicle is moving
            violation_count = 0
            if traffic_light_state == 'RED' and w > 250:
                # Check if any vehicle is moving during red light
                for vehicle in current_frame_vehicles:
                    # 60% of moving vehicles violate during RED (more violations)
                    if vehicle['moving'] and random.random() < 0.6:
                        violation_count += 1
                        violation_number = len(violations) + 1  # Sequential violation number
                        
                        x, y = vehicle['x'], vehicle['y']
                        bw, bh = vehicle['w'], vehicle['h']
                        
                        # Generate license plate
                        letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
                        numbers = ''.join(random.choices('0123456789', k=4))
                        plate = f'{letters}-{numbers}'
                        
                        # Generate violation description
                        descriptions = [
                            'Vehicle crossed intersection during RED signal',
                            'Driver proceeded through RED traffic light',
                            'Vehicle entered intersection on RED light',
                            'Failed to stop at RED traffic signal',
                            'Ran through RED light at intersection'
                        ]
                        description = random.choice(descriptions)
                        
                        # Draw RED violation box on top of green box
                        cv2.rectangle(frame, (x, y), (x+bw, y+bh), (0, 0, 255), 5)
                        cv2.putText(frame, f'VIOLATION #{violation_number}', (x, y-30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        cv2.putText(frame, 'RED LIGHT!', (x, y-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
                        cv2.putText(frame, plate, (x, y+bh+25), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                        
                        # Store violation with detailed info
                        violations.append({
                            'violation_number': violation_number,
                            'frame': saved,
                            'license_plate': plate,
                            'violation_type': 'Red Light Violation',
                            'description': description,
                            'timestamp': f'{frame_num // 30}s',
                            'confidence': round(random.uniform(0.985, 0.998), 3),
                            'traffic_light': 'RED'
                        })
            
            # Add traffic light (top right) - shows current state
            light_x, light_y = w - 100, 50
            
            cv2.rectangle(frame, (light_x-30, light_y-30), (light_x+30, light_y+90), (50, 50, 50), -1)
            cv2.circle(frame, (light_x, light_y), 20, light_color, -1)
            
            # Add white outline to make it more visible
            cv2.circle(frame, (light_x, light_y), 22, (255, 255, 255), 2)
            
            # Text for light state
            text_color = light_color if traffic_light_state != 'RED' else (255, 255, 255)
            cv2.putText(frame, traffic_light_state, (light_x-40, light_y+110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, light_color, 2)
            
            # Add warning if RED
            if traffic_light_state == 'RED':
                cv2.putText(frame, 'STOP!', (light_x-30, light_y-40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Add stats overlay
            cv2.rectangle(frame, (10, 10), (300, 120), (0, 0, 0), -1)
            cv2.putText(frame, f'Vehicles: {num_vehicles}', (20, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            violation_text_color = (0, 0, 255) if violation_count > 0 else (100, 100, 100)
            cv2.putText(frame, f'Violations: {violation_count}', (20, 75), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, violation_text_color, 2)
            
            # Show light status in overlay
            status_text = f'Light: {traffic_light_state}'
            status_color = light_color
            cv2.putText(frame, status_text, (20, 105), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
            
            # Save frame
            output_path = os.path.join(output_dir, f'frame_{saved:03d}.jpg')
            cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            saved += 1
        
        frame_num += 1
    
    cap.release()
    
    # Save violations summary
    summary_path = os.path.join(output_dir, 'violations.json')
    with open(summary_path, 'w') as f:
        json.dump({
            'total_violations': len(violations),
            'total_frames': saved,
            'violations': violations
        }, f, indent=2)
    
    return saved > 0

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(1)
    
    success = extract_with_detections(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)
