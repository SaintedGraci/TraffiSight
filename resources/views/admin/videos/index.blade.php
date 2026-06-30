@extends('layouts.admin')

@section('title', 'Video Management')

@section('content')
<div class="page-header">
    <div class="d-flex justify-content-between align-items-center">
        <div>
            <h1>Video Management</h1>
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="{{ route('admin.dashboard') }}">Dashboard</a></li>
                    <li class="breadcrumb-item active">Videos</li>
                </ol>
            </nav>
        </div>
        <div>
            <a href="{{ route('admin.videos.create') }}" class="btn btn-primary">
                <i class="bi bi-upload"></i> Upload Video
            </a>
        </div>
    </div>
</div>

@if(session('success'))
<div class="alert alert-success alert-dismissible fade show" role="alert">
    <i class="bi bi-check-circle"></i> {{ session('success') }}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
@endif

@if(session('error'))
<div class="alert alert-danger alert-dismissible fade show" role="alert">
    <i class="bi bi-exclamation-triangle"></i> {{ session('error') }}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
@endif

<!-- Statistics Cards -->
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card">
            <div class="card-body text-center">
                <h4 class="text-primary">{{ $statistics['total'] }}</h4>
                <p class="mb-0 text-muted">Total Videos</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body text-center">
                <h4 class="text-secondary">{{ $statistics['pending'] }}</h4>
                <p class="mb-0 text-muted">Pending</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body text-center">
                <h4 class="text-info">{{ $statistics['processing'] }}</h4>
                <p class="mb-0 text-muted">Processing</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body text-center">
                <h4 class="text-success">{{ $statistics['completed'] }}</h4>
                <p class="mb-0 text-muted">Completed</p>
            </div>
        </div>
    </div>
</div>

<!-- Filters -->
<div class="card mb-4">
    <div class="card-body">
        <form method="GET" action="{{ route('admin.videos.index') }}" class="row g-3">
            <div class="col-md-4">
                <input type="text" class="form-control" name="search" placeholder="Search by title..." value="{{ request('search') }}">
            </div>
            <div class="col-md-3">
                <select name="status" class="form-select">
                    <option value="">All Status</option>
                    <option value="pending" {{ request('status') == 'pending' ? 'selected' : '' }}>Pending</option>
                    <option value="processing" {{ request('status') == 'processing' ? 'selected' : '' }}>Processing</option>
                    <option value="completed" {{ request('status') == 'completed' ? 'selected' : '' }}>Completed</option>
                    <option value="failed" {{ request('status') == 'failed' ? 'selected' : '' }}>Failed</option>
                </select>
            </div>
            <div class="col-md-2">
                <button type="submit" class="btn btn-primary w-100">
                    <i class="bi bi-search"></i> Filter
                </button>
            </div>
            <div class="col-md-2">
                <a href="{{ route('admin.videos.index') }}" class="btn btn-secondary w-100">
                    <i class="bi bi-x-circle"></i> Clear
                </a>
            </div>
        </form>
    </div>
</div>

<!-- Videos Grid -->
<div class="row">
    @forelse($videos as $video)
    <div class="col-md-4 mb-4">
        <div class="card h-100">
            <div class="position-relative">
                @if($video->thumbnail_url)
                    <img src="{{ $video->thumbnail_url }}" class="card-img-top" alt="{{ $video->title }}" style="height: 200px; object-fit: cover;">
                @else
                    <div class="bg-secondary d-flex align-items-center justify-content-center" style="height: 200px;">
                        <i class="bi bi-camera-video text-white" style="font-size: 4rem;"></i>
                    </div>
                @endif
                <span class="position-absolute top-0 end-0 m-2 badge bg-{{ $video->status_color }}">
                    {{ $video->status_name }}
                </span>
            </div>
            <div class="card-body">
                <h5 class="card-title">{{ Str::limit($video->title, 40) }}</h5>
                <p class="card-text text-muted small mb-2">
                    {{ Str::limit($video->description, 80) ?: 'No description' }}
                </p>
                <div class="small text-muted mb-2">
                    <i class="bi bi-person"></i> {{ $video->uploader->name }}<br>
                    <i class="bi bi-calendar"></i> {{ $video->created_at->format('M d, Y') }}<br>
                    <i class="bi bi-file-earmark"></i> {{ $video->filesize_human }}<br>
                    @if($video->duration)
                        <i class="bi bi-clock"></i> {{ $video->duration_human }}
                    @endif
                </div>
            </div>
            <div class="card-footer bg-white">
                <div class="d-flex justify-content-between align-items-center">
                    <a href="{{ route('admin.videos.show', $video) }}" class="btn btn-sm btn-primary">
                        <i class="bi bi-eye"></i> View Details
                    </a>
                    @if($video->isProcessing())
                    <span class="badge bg-info">
                        <i class="bi bi-hourglass-split"></i> Processing...
                    </span>
                    @elseif($video->status == 'completed')
                    <span class="badge bg-success">
                        <i class="bi bi-check-circle"></i> Analyzed
                    </span>
                    @else
                    <span class="badge bg-secondary">
                        <i class="bi bi-clock"></i> Pending
                    </span>
                    @endif
                </div>
            </div>
        </div>
    </div>
    @empty
    <div class="col-12">
        <div class="card">
            <div class="card-body text-center py-5">
                <i class="bi bi-camera-video-off text-muted" style="font-size: 4rem;"></i>
                <h4 class="mt-3 text-muted">No Videos Found</h4>
                <p class="text-muted">Upload your first traffic video to get started.</p>
                <a href="{{ route('admin.videos.create') }}" class="btn btn-primary mt-3">
                    <i class="bi bi-upload"></i> Upload Video
                </a>
            </div>
        </div>
    </div>
    @endforelse
</div>

<!-- Pagination -->
@if($videos->hasPages())
<div class="mt-4">
    {{ $videos->links() }}
</div>
@endif
@endsection
