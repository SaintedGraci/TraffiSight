@extends('layouts.admin')

@section('title', 'Video Analysis')

@push('styles')
<style>
    .video-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 32px;
        color: white;
        margin-bottom: 32px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.25);
    }
    
    .video-header h1 {
        font-size: 28px;
        font-weight: 600;
        margin-bottom: 8px;
        color: white;
    }
    
    .video-header p {
        opacity: 0.95;
        margin: 0;
    }
    
    .analysis-card {
        background: white;
        border-radius: 16px;
        padding: 0;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        overflow: hidden;
    }
    
    .card-header-custom {
        background: #f9fafb;
        border-bottom: 1px solid #e5e7eb;
        padding: 20px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .card-header-custom h5 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
        color: #111827;
    }
    
    .btn-analyze {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 500;
        font-size: 14px;
        transition: all 0.3s;
        box-shadow: 0 4px 6px -1px rgba(102, 126, 234, 0.3);
    }
    
    .btn-analyze:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px -1px rgba(102, 126, 234, 0.4);
        color: white;
    }
    
    .btn-analyze:disabled {
        opacity: 0.6;
        transform: none;
    }
    
    .loading-state {
        text-align: center;
        padding: 60px 20px;
    }
    
    .loading-state .spinner {
        width: 48px;
        height: 48px;
        border: 4px solid #e5e7eb;
        border-top-color: #667eea;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        margin: 0 auto;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .loading-state p {
        margin-top: 20px;
        color: #6b7280;
        font-size: 15px;
    }
    
    .violation-panel {
        background: white;
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid #fee2e2;
        box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.1);
    }
    
    .violation-header {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        padding: 20px 24px;
        color: white;
    }
    
    .violation-header h5 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .violation-count {
        background: rgba(255, 255, 255, 0.25);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
    }
    
    .violation-table {
        margin: 0;
    }
    
    .violation-table thead {
        background: #fef2f2;
    }
    
    .violation-table thead th {
        border: none;
        padding: 16px 24px;
        font-size: 13px;
        font-weight: 600;
        color: #991b1b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .violation-table tbody td {
        padding: 16px 24px;
        vertical-align: middle;
        border-bottom: 1px solid #fee2e2;
    }
    
    .violation-table tbody tr:last-child td {
        border-bottom: none;
    }
    
    .violation-table tbody tr:hover {
        background: #fef2f2;
    }
    
    .plate-badge {
        background: #111827;
        color: white;
        padding: 8px 16px;
        border-radius: 6px;
        font-family: 'Courier New', monospace;
        font-weight: 600;
        font-size: 15px;
        letter-spacing: 1px;
    }
    
    .violation-badge {
        background: #fee2e2;
        color: #991b1b;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
    }
    
    .frame-badge {
        background: #f3f4f6;
        color: #374151;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 13px;
    }
    
    .info-box {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        margin-bottom: 24px;
    }
    
    .info-box h5 {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 12px;
        color: white;
    }
    
    .info-box ul {
        margin: 0;
        padding-left: 20px;
    }
    
    .info-box li {
        margin-bottom: 8px;
        font-size: 14px;
        line-height: 1.6;
    }
    
    .frame-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 20px;
        padding: 24px;
    }
    
    .frame-card {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e5e7eb;
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .frame-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px -4px rgba(0, 0, 0, 0.15);
        border-color: #667eea;
    }
    
    .frame-card img {
        width: 100%;
        height: 200px;
        object-fit: cover;
        display: block;
    }
    
    .frame-card-body {
        padding: 12px 16px;
        background: #f9fafb;
        text-align: center;
    }
    
    .frame-card-body small {
        color: #6b7280;
        font-weight: 500;
        font-size: 13px;
    }
    
    .original-video {
        text-align: center;
        padding: 24px;
    }
    
    .original-video video {
        max-height: 500px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .original-video p {
        margin-top: 16px;
        color: #6b7280;
        font-size: 14px;
    }
    
    .success-alert {
        background: #d1fae5;
        border: 1px solid #6ee7b7;
        color: #065f46;
        border-radius: 12px;
        padding: 16px 20px;
        display: flex;
        align-items: center;
        gap: 12px;
        font-weight: 500;
    }
</style>
@endpush

@section('content')
<!-- Header -->
<div class="video-header">
    <div class="d-flex justify-content-between align-items-start">
        <div>
            <h1>{{ Str::limit($video->title, 50) }}</h1>
            <p>{{ $video->description ?: 'Advanced traffic violation detection and analysis' }}</p>
        </div>
        <div class="d-flex gap-2">
            <a href="{{ route('admin.videos.edit', $video) }}" class="btn btn-light">
                <i class="bi bi-pencil"></i> Edit
            </a>
            <form action="{{ route('admin.videos.destroy', $video) }}" method="POST" class="d-inline" onsubmit="return confirm('Delete this video?');">
                @csrf
                @method('DELETE')
                <button type="submit" class="btn btn-light text-danger">
                    <i class="bi bi-trash"></i>
                </button>
            </form>
        </div>
    </div>
</div>

<!-- Main Analysis Section -->
<div class="analysis-card mb-4">
    <div class="card-header-custom">
        <h5><i class="bi bi-cpu"></i> Detection Analysis</h5>
        <button id="detectBtn" class="btn-analyze" onclick="runAIDetection()">
            <i class="bi bi-play-circle-fill"></i> Start Analysis
        </button>
    </div>
    
    <div class="card-body p-0">
        <!-- Loading State -->
        <div id="loadingMsg" style="display: none;">
            <div class="loading-state">
                <div class="spinner"></div>
                <p>Analyzing video and detecting violations...</p>
            </div>
        </div>
        
        <!-- Results Container -->
        <div id="framesContainer" style="display: none;">
            <!-- Results will be inserted here -->
        </div>
        
        <!-- Original Video -->
        <div id="originalVideo" class="original-video">
            <video controls class="w-100">
                <source src="{{ $video->video_url }}" type="video/{{ $video->format }}">
            </video>
            <p>Click "Start Analysis" to detect traffic violations in this video</p>
        </div>
    </div>
</div>

<script>
function runAIDetection() {
    const btn = document.getElementById('detectBtn');
    const loading = document.getElementById('loadingMsg');
    const frames = document.getElementById('framesContainer');
    const original = document.getElementById('originalVideo');
    
    original.style.display = 'none';
    loading.style.display = 'block';
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Analyzing...';
    
    fetch('{{ route("admin.videos.detect.realtime", $video) }}', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': '{{ csrf_token() }}'
        }
    })
    .then(response => response.json())
    .then(data => {
        loading.style.display = 'none';
        
        console.log('Detection data:', data); // DEBUG
        console.log('Violations:', data.violations); // DEBUG
        
        if (data.success && data.frames) {
            let html = '';
            
            // Success message
            html += `<div class="p-4"><div class="success-alert"><i class="bi bi-check-circle-fill fs-5"></i><span>${data.message}</span></div></div>`;
            
            // Violations summary - CHECK IF EXISTS
            if (data.violations && data.violations.violations && Array.isArray(data.violations.violations) && data.violations.violations.length > 0) {
                console.log('Rendering violations table with', data.violations.violations.length, 'violations'); // DEBUG
                
                html += `
                    <div class="px-4 pb-4">
                        <div class="violation-panel">
                            <div class="violation-header">
                                <h5>
                                    <i class="bi bi-exclamation-triangle-fill"></i>
                                    Violations Detected
                                    <span class="violation-count ms-2">${data.violations.total_violations}</span>
                                </h5>
                            </div>
                            <div class="table-responsive">
                                <table class="table violation-table mb-0">
                                    <thead>
                                        <tr>
                                            <th>#</th>
                                            <th>FRAME</th>
                                            <th>TIME</th>
                                            <th>DESCRIPTION</th>
                                            <th>LICENSE PLATE</th>
                                            <th>CONFIDENCE</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                `;
                
                data.violations.violations.forEach(v => {
                    const confidence = (v.confidence * 100).toFixed(1);
                    const confidenceColor = confidence >= 99 ? '#10b981' : confidence >= 95 ? '#f59e0b' : '#ef4444';
                    
                    html += `
                        <tr>
                            <td><span class="badge bg-danger" style="font-size: 14px; padding: 8px 12px;">#${v.violation_number}</span></td>
                            <td><span class="frame-badge">Frame ${v.frame + 1}</span></td>
                            <td><strong>${v.timestamp}</strong></td>
                            <td style="max-width: 300px;"><em>${v.description}</em></td>
                            <td><span class="plate-badge">${v.license_plate}</span></td>
                            <td><span class="badge" style="background: ${confidenceColor}; color: white; font-size: 13px;">${confidence}%</span></td>
                        </tr>
                    `;
                });
                
                html += `
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                `;
            } else {
                console.log('NO VIOLATIONS FOUND OR INVALID DATA'); // DEBUG
                console.log('violations object:', data.violations); // DEBUG
            }
            
            // Info box
            html += `
                <div class="px-4 pb-4">
                    <div class="info-box">
                        <h5><i class="bi bi-info-circle-fill"></i> Detection Features</h5>
                        <ul>
                            <li><strong style="color: #86efac;">Green boxes</strong> indicate normal vehicles being tracked</li>
                            <li><strong style="color: #fca5a5;">Red boxes</strong> indicate traffic violations detected</li>
                            <li>License plates are extracted and displayed for violations</li>
                            <li>Traffic light status shown in top-right corner</li>
                            <li>Real-time vehicle count displayed in top-left</li>
                        </ul>
                    </div>
                </div>
            `;
            
            // Frames grid
            html += '<div class="frame-grid">';
            data.frames.forEach((url, index) => {
                html += `
                    <div class="frame-card" onclick="showFullImage('${url}')">
                        <img src="${url}" alt="Frame ${index + 1}">
                        <div class="frame-card-body">
                            <small>Frame ${index + 1}</small>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            
            frames.innerHTML = html;
            frames.style.display = 'block';
            
            btn.innerHTML = '<i class="bi bi-check-circle-fill"></i> Analysis Complete';
            btn.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
        } else {
            alert('Detection failed: ' + (data.message || 'Unknown error'));
            original.style.display = 'block';
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-play-circle-fill"></i> Start Analysis';
        }
    })
    .catch(error => {
        loading.style.display = 'none';
        original.style.display = 'block';
        alert('Error: ' + error);
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-play-circle-fill"></i> Start Analysis';
    });
}

function showFullImage(url) {
    window.open(url, '_blank');
}
</script>
@endsection
