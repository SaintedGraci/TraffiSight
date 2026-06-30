# TraffiSight AI - API and Libraries Documentation

## Backend APIs and Libraries

### Laravel Framework (PHP)
Version: 11.x

Purpose: Web application framework for backend logic, routing, and database management.

Key Features Used:
- MVC architecture
- Authentication system
- Database migrations and ORM (Eloquent)
- File storage management
- Job queues for background processing

### Laravel Breeze
Purpose: Simple authentication scaffolding with login, registration, and password reset.

Why Used: Provides secure, ready-to-use authentication without building from scratch.

### MySQL Database
Version: 8.0+

Purpose: Relational database for storing users, videos, and analysis results.

Tables:
- users: User accounts and authentication
- videos: Video metadata and processing status
- roles: User role management
- role_user: User-role relationships

### Tailwind CSS
Version: 3.x

Purpose: Utility-first CSS framework for modern, responsive UI design.

Why Used: Fast development of professional-looking interfaces without writing custom CSS.

## Frontend Libraries

### Bootstrap 5
Version: 5.3

Purpose: UI components and responsive grid system.

Why Used: Quick implementation of cards, buttons, modals, and navigation.

### Bootstrap Icons
Version: 1.11

Purpose: Icon library for UI elements.

Why Used: Consistent, scalable icons throughout the application.

### Chart.js
Version: 4.4.0

Purpose: JavaScript charting library for data visualization.

Why Used: Creates interactive analytics charts on dashboard (violations over time, accuracy metrics, vehicle types distribution).

### Alpine.js (included in Laravel Breeze)
Purpose: Lightweight JavaScript framework for interactive components.

Why Used: Simple reactivity for dropdowns, modals, and form interactions.

## Python AI Libraries

### OpenCV (cv2)
Version: Latest

Purpose: Computer vision library for video processing and image manipulation.

Why Used:
- Video frame extraction
- Image preprocessing
- Drawing bounding boxes and annotations
- Video codec handling

### Ultralytics YOLO
Version: Latest

Purpose: State-of-the-art object detection model.

Model Used: YOLOv8n (nano variant)

Why Used:
- Real-time vehicle detection
- High accuracy (99%+ in optimal conditions)
- Fast inference speed
- Pre-trained on COCO dataset including vehicles

### NumPy
Purpose: Numerical computing library for array operations.

Why Used:
- Image array manipulation
- Mathematical calculations for tracking
- Performance optimization

### PyYAML
Purpose: YAML parser for configuration files.

Why Used: Loading AI model settings from config.yaml file.

## Detection Algorithms

### Traffic Light State Simulation
Purpose: Simulates realistic traffic light cycles (RED/YELLOW/GREEN).

How It Works:
- RED phase: 8 seconds
- YELLOW phase: 2 seconds  
- GREEN phase: 10 seconds
- Cycles repeat throughout video

Why Used: Enables red light violation detection by tracking light state during vehicle movement.

### Violation Detection Logic
Purpose: Identifies vehicles crossing intersection during red light.

How It Works:
1. Track traffic light state
2. Detect vehicles using YOLO
3. Monitor vehicle movement across frames
4. Flag violation when: light is RED AND vehicle is moving
5. Generate violation report with timestamp and confidence

### License Plate Recognition (Simulated)
Purpose: Extracts license plate numbers from violation frames.

Current Implementation: Generates realistic placeholder plates (ABC-1234 format).

Why Used: Provides violation evidence for enforcement purposes.

## File Processing Flow

1. User uploads video through web interface
2. Laravel stores file in storage/app/public/videos/
3. Video record created in database with "pending" status
4. User clicks "Start Analysis"
5. AJAX call triggers Python script execution
6. Python script:
   - Loads video with OpenCV
   - Extracts 20 frames evenly distributed
   - Runs YOLO detection on each frame
   - Tracks traffic light state
   - Identifies violations during red light
   - Generates annotated frames with bounding boxes
   - Saves frames to storage/app/public/detections/{video_id}/
   - Creates violations.json with detailed results
7. Laravel loads results and updates database
8. Frontend displays violations table and frame gallery
9. Dashboard analytics automatically updated

## Security Features

### Authentication
- Bcrypt password hashing
- Session-based authentication
- CSRF protection on all forms
- Password reset functionality

### Authorization
- Role-based access control (Admin/Operator)
- Middleware protection on admin routes
- File upload validation

### File Security
- Allowed video formats: mp4, avi, mov, mkv
- Maximum file size: 100MB (configurable in php.ini)
- Files stored outside public web root
- Unique filenames to prevent conflicts

## Performance Optimizations

### Database
- Indexed columns for faster queries (status, user_id, created_at)
- JSON storage for analysis results (flexible, no schema changes needed)

### File Processing
- Frames extracted at intervals (not every frame)
- 20 frames per video provides good balance of speed and accuracy
- Results cached (re-uses existing analysis if available)

### Frontend
- Assets compiled and minified with Vite
- Chart.js loaded from CDN for faster initial load
- Lazy loading of detection frames

## System Architecture

```
User Browser
    |
    v
Laravel Application (PHP)
    |
    +-- Authentication & Authorization
    |
    +-- Video Upload & Management
    |
    +-- Database (MySQL)
    |
    +-- Triggers Python Script
         |
         v
    Python AI Engine
         |
         +-- YOLO Detection
         |
         +-- Traffic Light Simulation
         |
         +-- Violation Detection
         |
         +-- Frame Annotation
         |
         v
    Results Saved to Storage
         |
         v
    Laravel Loads Results
         |
         v
    Dashboard Analytics Updated
```

## API Endpoints

### Authentication
- POST /login - User login
- POST /register - User registration
- POST /logout - User logout
- POST /forgot-password - Password reset request

### Video Management
- GET /admin/videos - List all videos
- POST /admin/videos - Upload new video
- GET /admin/videos/{id} - View video details
- DELETE /admin/videos/{id} - Delete video

### AI Detection
- POST /admin/videos/{id}/detect-realtime - Run AI analysis
  Returns: JSON with frame URLs and violations data

### Dashboard
- GET /admin/dashboard - Analytics overview

## Configuration Files

### .env
Database credentials, app settings, file upload limits

### python_ai/config/config.yaml
YOLO model settings, detection thresholds, frame extraction parameters

### config/filesystems.php
Storage disk configuration

### config/queue.php
Background job processing settings
