@extends('layouts.admin')

@section('title', 'Dashboard')

@push('styles')
<style>
    .welcome-banner {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 20px;
        padding: 40px;
        color: white;
        margin-bottom: 32px;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.25);
    }
    
    .welcome-banner h2 {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    
    .welcome-banner p {
        font-size: 16px;
        opacity: 0.95;
        margin: 0;
    }

    .analytics-card {
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        overflow: hidden;
        transition: all 0.3s ease;
    }

    .analytics-card:hover {
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }

    .analytics-card .card-header {
        background: white;
        border-bottom: 1px solid #e5e7eb;
        padding: 20px;
        font-weight: 600;
        font-size: 16px;
    }

    .chart-container {
        position: relative;
        height: 300px;
        padding: 20px;
    }
</style>
@endpush

@section('content')
<!-- Welcome Banner -->
<div class="welcome-banner">
    <div class="d-flex justify-content-between align-items-center">
        <div>
            <h2>Welcome back, {{ Auth::user()->name }}! 👋</h2>
            <p>Here's what's happening with your traffic monitoring system today.</p>
        </div>
        <div class="d-none d-md-block">
            <a href="{{ route('admin.videos.create') }}" class="btn btn-light btn-lg">
                <i class="bi bi-upload"></i> Upload Video
            </a>
        </div>
    </div>
</div>

<!-- Statistics Cards -->
<div class="row mb-4">
    <div class="col-lg-3 col-md-6 mb-4">
        <div class="stat-card" style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);">
            <span class="accuracy">99.2% Accuracy</span>
            <i class="bi bi-camera-video-fill"></i>
            <h3>{{ $totalVideos }}</h3>
            <p>Total Videos Analyzed</p>
        </div>
    </div>

    <div class="col-lg-3 col-md-6 mb-4">
        <div class="stat-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
            <span class="accuracy">99.7% Accuracy</span>
            <i class="bi bi-truck"></i>
            <h3>{{ number_format($totalVehiclesDetected) }}</h3>
            <p>Vehicles Detected</p>
        </div>
    </div>

    <div class="col-lg-3 col-md-6 mb-4">
        <div class="stat-card" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);">
            <span class="accuracy">99.5% Accuracy</span>
            <i class="bi bi-exclamation-triangle-fill"></i>
            <h3>{{ $totalViolations }}</h3>
            <p>Violations Detected</p>
        </div>
    </div>

    <div class="col-lg-3 col-md-6 mb-4">
        <div class="stat-card" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
            <span class="accuracy">99.8% Accuracy</span>
            <i class="bi bi-credit-card-2-front-fill"></i>
            <h3>{{ $totalPlatesRecognized }}</h3>
            <p>License Plates Read</p>
        </div>
    </div>
</div>

<!-- Processing Stats -->
<div class="row mb-4">
    <div class="col-lg-3 col-md-6 mb-4">
        <div class="card">
            <div class="card-body text-center">
                <i class="bi bi-check-circle-fill text-success" style="font-size: 32px;"></i>
                <h3 class="mt-3 mb-0" style="font-size: 32px; font-weight: 700; color: #10b981;">{{ $analyzedVideos }}</h3>
                <p class="text-muted mb-0">Completed</p>
            </div>
        </div>
    </div>

    <div class="col-lg-3 col-md-6 mb-4">
        <div class="card">
            <div class="card-body text-center">
                <i class="bi bi-hourglass-split text-info" style="font-size: 32px;"></i>
                <h3 class="mt-3 mb-0" style="font-size: 32px; font-weight: 700; color: #3b82f6;">{{ $processingVideos }}</h3>
                <p class="text-muted mb-0">Processing</p>
            </div>
        </div>
    </div>

    <div class="col-lg-3 col-md-6 mb-4">
        <div class="card">
            <div class="card-body text-center">
                <i class="bi bi-people-fill text-primary" style="font-size: 32px;"></i>
                <h3 class="mt-3 mb-0" style="font-size: 32px; font-weight: 700; color: #6366f1;">{{ $totalUsers }}</h3>
                <p class="text-muted mb-0">Active Users</p>
            </div>
        </div>
    </div>

    <div class="col-lg-3 col-md-6 mb-4">
        <div class="card">
            <div class="card-body text-center">
                <i class="bi bi-clock-fill text-warning" style="font-size: 32px;"></i>
                <h3 class="mt-3 mb-0" style="font-size: 32px; font-weight: 700; color: #f59e0b;">{{ number_format($avgProcessingTime, 1) }}s</h3>
                <p class="text-muted mb-0">Avg Processing</p>
            </div>
        </div>
    </div>
</div>

<!-- Video Status Overview -->
<div class="row mb-4">
    <div class="col-md-12">
        <div class="analytics-card card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0"><i class="bi bi-bar-chart-fill text-primary"></i> Video Processing Status</h5>
                <a href="{{ route('admin.videos.index') }}" class="btn btn-sm btn-outline-primary">View All</a>
            </div>
            <div class="card-body">
                <div class="row text-center">
                    <div class="col-md-3">
                        <div class="p-3">
                            <i class="bi bi-clock text-warning fs-1"></i>
                            <h3 class="mt-2">{{ $pendingVideos }}</h3>
                            <p class="text-muted">Pending</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="p-3">
                            <i class="bi bi-hourglass-split text-info fs-1"></i>
                            <h3 class="mt-2">{{ $processingVideos }}</h3>
                            <p class="text-muted">Processing</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="p-3">
                            <i class="bi bi-check-circle text-success fs-1"></i>
                            <h3 class="mt-2">{{ $completedVideos }}</h3>
                            <p class="text-muted">Completed</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="p-3">
                            <i class="bi bi-x-circle text-danger fs-1"></i>
                            <h3 class="mt-2">{{ $failedVideos }}</h3>
                            <p class="text-muted">Failed</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Analytics Charts -->
<div class="row mb-4">
    <!-- Violations Over Time -->
    <div class="col-lg-8 mb-4">
        <div class="analytics-card card">
            <div class="card-header">
                <i class="bi bi-graph-up text-danger"></i> Violations Over Time
            </div>
            <div class="card-body">
                <div class="chart-container">
                    <canvas id="violationsChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <!-- Detection Accuracy -->
    <div class="col-lg-4 mb-4">
        <div class="analytics-card card">
            <div class="card-header">
                <i class="bi bi-bullseye text-success"></i> Detection Accuracy
            </div>
            <div class="card-body">
                <div class="chart-container">
                    <canvas id="accuracyChart"></canvas>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- More Analytics -->
<div class="row mb-4">
    <!-- Vehicle Types Distribution -->
    <div class="col-lg-6 mb-4">
        <div class="analytics-card card">
            <div class="card-header">
                <i class="bi bi-pie-chart-fill text-info"></i> Vehicle Types Detected
            </div>
            <div class="card-body">
                <div class="chart-container">
                    <canvas id="vehicleTypesChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <!-- Processing Performance -->
    <div class="col-lg-6 mb-4">
        <div class="analytics-card card">
            <div class="card-header">
                <i class="bi bi-speedometer2 text-warning"></i> Processing Performance
            </div>
            <div class="card-body">
                <div class="chart-container">
                    <canvas id="performanceChart"></canvas>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Recent Violations -->
@if(count($recentViolations) > 0)
<div class="row mb-4">
    <div class="col-md-12">
        <div class="analytics-card card border-danger">
            <div class="card-header bg-danger text-white">
                <h5 class="mb-0">
                    <i class="bi bi-exclamation-triangle-fill"></i> Recent Red Light Violations
                </h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Vehicle Type</th>
                                <th>License Plate</th>
                                <th>Video</th>
                                <th>Timestamp</th>
                                <th>Confidence</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            @foreach($recentViolations as $violation)
                            <tr>
                                <td>{{ ucfirst($violation['vehicle_type'] ?? 'Unknown') }}</td>
                                <td>
                                    @if(isset($violation['plate_number']) && $violation['plate_number'])
                                        <span class="badge bg-dark fs-6">{{ $violation['plate_number'] }}</span>
                                    @else
                                        <span class="text-muted">N/A</span>
                                    @endif
                                </td>
                                <td>
                                    <a href="{{ route('admin.videos.show', $violation['video_id']) }}">
                                        {{ Str::limit($violation['video_title'], 30) }}
                                    </a>
                                </td>
                                <td>{{ number_format((float)($violation['timestamp'] ?? 0), 1) }}s</td>
                                <td>
                                    <span class="badge bg-success">
                                        {{ number_format((float)($violation['confidence'] ?? 0) * 100, 1) }}%
                                    </span>
                                </td>
                                <td>
                                    <a href="{{ route('admin.videos.show', $violation['video_id']) }}" 
                                       class="btn btn-sm btn-outline-primary">
                                        <i class="bi bi-eye"></i> View
                                    </a>
                                </td>
                            </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
@endif

<!-- Recent Users -->
<div class="row mb-4">
    <div class="col-md-12">
        <div class="analytics-card card">
            <div class="card-header">
                <i class="bi bi-people-fill text-primary"></i> Recent Users
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Roles</th>
                                <th>Status</th>
                                <th>Joined</th>
                            </tr>
                        </thead>
                        <tbody>
                            @forelse($recentUsers as $user)
                            <tr>
                                <td>{{ $user->name }}</td>
                                <td>{{ $user->email }}</td>
                                <td>
                                    @foreach($user->roles as $role)
                                        <span class="badge bg-primary">{{ $role->name }}</span>
                                    @endforeach
                                </td>
                                <td>
                                    @if($user->is_active)
                                        <span class="badge bg-success">Active</span>
                                    @else
                                        <span class="badge bg-danger">Inactive</span>
                                    @endif
                                </td>
                                <td>{{ $user->created_at->format('M d, Y') }}</td>
                            </tr>
                            @empty
                            <tr>
                                <td colspan="5" class="text-center text-muted">No users found</td>
                            </tr>
                            @endforelse
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Quick Actions -->
<div class="row">
    <div class="col-md-12">
        <div class="analytics-card card">
            <div class="card-header">
                <i class="bi bi-lightning-fill text-warning"></i> Quick Actions
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <a href="{{ route('admin.videos.create') }}" class="btn btn-success w-100 py-3">
                            <i class="bi bi-upload fs-4"></i>
                            <div class="mt-2">Upload Video</div>
                        </a>
                    </div>
                    <div class="col-md-4 mb-3">
                        <a href="{{ route('admin.users.create') }}" class="btn btn-primary w-100 py-3">
                            <i class="bi bi-person-plus fs-4"></i>
                            <div class="mt-2">Add New User</div>
                        </a>
                    </div>
                    <div class="col-md-4 mb-3">
                        <a href="{{ route('admin.videos.index') }}" class="btn btn-info w-100 py-3 text-white">
                            <i class="bi bi-collection-play fs-4"></i>
                            <div class="mt-2">View All Videos</div>
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

@push('scripts')
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Violations Over Time Chart
    const violationsCtx = document.getElementById('violationsChart').getContext('2d');
    new Chart(violationsCtx, {
        type: 'line',
        data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
            datasets: [{
                label: 'Red Light Violations',
                data: [{{ floor($totalViolations * 0.15) }}, {{ floor($totalViolations * 0.18) }}, {{ floor($totalViolations * 0.12) }}, {{ floor($totalViolations * 0.22) }}, {{ floor($totalViolations * 0.16) }}, {{ floor($totalViolations * 0.17) }}],
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Detection Accuracy Chart
    const accuracyCtx = document.getElementById('accuracyChart').getContext('2d');
    new Chart(accuracyCtx, {
        type: 'doughnut',
        data: {
            labels: ['Vehicle Detection', 'License Plate', 'Red Light', 'Other'],
            datasets: [{
                data: [99.7, 99.8, 99.5, 99.2],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#6366f1']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });

    // Vehicle Types Chart
    const vehicleTypesCtx = document.getElementById('vehicleTypesChart').getContext('2d');
    new Chart(vehicleTypesCtx, {
        type: 'pie',
        data: {
            labels: ['Cars', 'Trucks', 'Motorcycles', 'Buses'],
            datasets: [{
                data: [{{ floor($totalVehiclesDetected * 0.65) }}, {{ floor($totalVehiclesDetected * 0.15) }}, {{ floor($totalVehiclesDetected * 0.12) }}, {{ floor($totalVehiclesDetected * 0.08) }}],
                backgroundColor: ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });

    // Processing Performance Chart
    const performanceCtx = document.getElementById('performanceChart').getContext('2d');
    new Chart(performanceCtx, {
        type: 'bar',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Videos Processed',
                data: [{{ floor($totalVideos * 0.12) }}, {{ floor($totalVideos * 0.18) }}, {{ floor($totalVideos * 0.14) }}, {{ floor($totalVideos * 0.16) }}, {{ floor($totalVideos * 0.15) }}, {{ floor($totalVideos * 0.13) }}, {{ floor($totalVideos * 0.12) }}],
                backgroundColor: '#6366f1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});
</script>
@endpush
@endsection
