@extends('layouts.admin')

@section('title', 'Upload Video')

@section('content')
<div class="page-header">
    <h1>Upload Video</h1>
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="{{ route('admin.dashboard') }}">Dashboard</a></li>
            <li class="breadcrumb-item"><a href="{{ route('admin.videos.index') }}">Videos</a></li>
            <li class="breadcrumb-item active">Upload</li>
        </ol>
    </nav>
</div>

@if(session('error'))
<div class="alert alert-danger alert-dismissible fade show" role="alert">
    <i class="bi bi-exclamation-triangle"></i> {{ session('error') }}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
@endif

<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header bg-white">
                <h5 class="mb-0">Video Information</h5>
            </div>
            <div class="card-body">
                <form action="{{ route('admin.videos.store') }}" method="POST" enctype="multipart/form-data" id="uploadForm">
                    @csrf

                    <div class="mb-4">
                        <label for="video" class="form-label">
                            Video File <span class="text-danger">*</span>
                        </label>
                        <input type="file" 
                               class="form-control @error('video') is-invalid @enderror" 
                               id="video" 
                               name="video" 
                               accept="video/mp4,video/avi,video/quicktime,video/x-matroska,video/x-flv,video/x-ms-wmv"
                               required>
                        <small class="text-muted">
                            Supported formats: MP4, AVI, MOV, MKV, FLV, WMV (Max: 500MB)
                        </small>
                        @error('video')
                            <div class="invalid-feedback">{{ $message }}</div>
                        @enderror
                        
                        <!-- Upload Progress -->
                        <div class="progress mt-3" id="uploadProgress" style="display: none;">
                            <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 0%"></div>
                        </div>
                        <small id="uploadStatus" class="text-muted"></small>
                    </div>

                    <div class="mb-3">
                        <label for="title" class="form-label">
                            Title <span class="text-danger">*</span>
                        </label>
                        <input type="text" 
                               class="form-control @error('title') is-invalid @enderror" 
                               id="title" 
                               name="title" 
                               value="{{ old('title') }}" 
                               placeholder="e.g., Main Street Intersection - Morning Rush Hour"
                               required>
                        @error('title')
                            <div class="invalid-feedback">{{ $message }}</div>
                        @enderror
                    </div>

                    <div class="mb-3">
                        <label for="description" class="form-label">Description</label>
                        <textarea class="form-control @error('description') is-invalid @enderror" 
                                  id="description" 
                                  name="description" 
                                  rows="4"
                                  placeholder="Optional: Add details about the video location, time, or any special notes...">{{ old('description') }}</textarea>
                        @error('description')
                            <div class="invalid-feedback">{{ $message }}</div>
                        @enderror
                    </div>

                    <div class="d-flex justify-content-end gap-2">
                        <a href="{{ route('admin.videos.index') }}" class="btn btn-secondary">
                            <i class="bi bi-x-circle"></i> Cancel
                        </a>
                        <button type="submit" class="btn btn-primary" id="submitBtn">
                            <i class="bi bi-upload"></i> Upload Video
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <div class="col-md-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h6 class="mb-0"><i class="bi bi-info-circle"></i> Upload Guidelines</h6>
            </div>
            <div class="card-body">
                <h6 class="fw-bold">Supported Formats:</h6>
                <ul class="small">
                    <li>MP4 (recommended)</li>
                    <li>AVI</li>
                    <li>MOV</li>
                    <li>MKV</li>
                    <li>FLV</li>
                    <li>WMV</li>
                </ul>

                <h6 class="fw-bold mt-3">Requirements:</h6>
                <ul class="small">
                    <li>Maximum file size: 500MB</li>
                    <li>Minimum resolution: 720p recommended</li>
                    <li>Clear view of traffic and vehicles</li>
                    <li>Stable camera position</li>
                </ul>

                <h6 class="fw-bold mt-3">Tips for Best Results:</h6>
                <ul class="small">
                    <li>Use high-quality video recordings</li>
                    <li>Ensure good lighting conditions</li>
                    <li>Keep camera steady</li>
                    <li>Capture clear license plates</li>
                    <li>Include traffic signals in frame</li>
                </ul>
            </div>
        </div>
    </div>
</div>
@endsection

@push('scripts')
<script>
document.getElementById('video').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const fileSize = (file.size / 1024 / 1024).toFixed(2); // Convert to MB
        const fileName = file.name;
        
        // Auto-fill title if empty
        if (!document.getElementById('title').value) {
            const titleWithoutExt = fileName.substring(0, fileName.lastIndexOf('.')) || fileName;
            document.getElementById('title').value = titleWithoutExt;
        }
        
        // Show file info
        document.getElementById('uploadStatus').textContent = `Selected: ${fileName} (${fileSize} MB)`;
    }
});

document.getElementById('uploadForm').addEventListener('submit', function(e) {
    const submitBtn = document.getElementById('submitBtn');
    const progress = document.getElementById('uploadProgress');
    
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Uploading...';
    progress.style.display = 'block';
    
    // Simulate progress (real progress tracking would require AJAX)
    let width = 0;
    const interval = setInterval(function() {
        if (width >= 90) {
            clearInterval(interval);
        } else {
            width += 10;
            progress.querySelector('.progress-bar').style.width = width + '%';
        }
    }, 500);
});
</script>
@endpush
