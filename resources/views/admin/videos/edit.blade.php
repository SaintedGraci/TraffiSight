@extends('layouts.admin')

@section('title', 'Edit Video')

@section('content')
<div class="page-header">
    <h1>Edit Video</h1>
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="{{ route('admin.dashboard') }}">Dashboard</a></li>
            <li class="breadcrumb-item"><a href="{{ route('admin.videos.index') }}">Videos</a></li>
            <li class="breadcrumb-item"><a href="{{ route('admin.videos.show', $video) }}">{{ Str::limit($video->title, 20) }}</a></li>
            <li class="breadcrumb-item active">Edit</li>
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
                <h5 class="mb-0">Edit Video Information</h5>
            </div>
            <div class="card-body">
                <form action="{{ route('admin.videos.update', $video) }}" method="POST">
                    @csrf
                    @method('PUT')

                    <div class="mb-3">
                        <label for="title" class="form-label">
                            Title <span class="text-danger">*</span>
                        </label>
                        <input type="text" 
                               class="form-control @error('title') is-invalid @enderror" 
                               id="title" 
                               name="title" 
                               value="{{ old('title', $video->title) }}" 
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
                                  rows="5">{{ old('description', $video->description) }}</textarea>
                        @error('description')
                            <div class="invalid-feedback">{{ $message }}</div>
                        @enderror
                    </div>

                    <div class="alert alert-info">
                        <i class="bi bi-info-circle"></i> 
                        <strong>Note:</strong> You can only edit the title and description. 
                        To change the video file, please delete this video and upload a new one.
                    </div>

                    <div class="d-flex justify-content-end gap-2">
                        <a href="{{ route('admin.videos.show', $video) }}" class="btn btn-secondary">
                            <i class="bi bi-x-circle"></i> Cancel
                        </a>
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-save"></i> Update Video
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <div class="col-md-4">
        <!-- Video Preview -->
        <div class="card mb-3">
            <div class="card-header bg-white">
                <h6 class="mb-0">Current Video</h6>
            </div>
            <div class="card-body p-0">
                <video controls class="w-100">
                    <source src="{{ $video->video_url }}" type="video/{{ $video->format }}">
                </video>
            </div>
            <div class="card-footer bg-white">
                <small class="text-muted">
                    <i class="bi bi-file-earmark"></i> {{ $video->filename }}<br>
                    <i class="bi bi-hdd"></i> {{ $video->filesize_human }}<br>
                    <i class="bi bi-clock"></i> {{ $video->duration_human }}
                </small>
            </div>
        </div>

        <!-- Video Details -->
        <div class="card">
            <div class="card-header bg-white">
                <h6 class="mb-0">Video Details</h6>
            </div>
            <div class="card-body">
                <small>
                    <strong>Status:</strong><br>
                    <span class="badge bg-{{ $video->status_color }} mb-2">{{ $video->status_name }}</span><br>
                    
                    <strong>Uploaded By:</strong><br>
                    {{ $video->uploader->name }}<br>
                    
                    <strong>Uploaded At:</strong><br>
                    {{ $video->created_at->format('M d, Y H:i') }}<br>
                    
                    <strong>Last Modified:</strong><br>
                    {{ $video->updated_at->format('M d, Y H:i') }}
                </small>
            </div>
        </div>
    </div>
</div>
@endsection
