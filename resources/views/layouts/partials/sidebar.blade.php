<div class="sidebar">
    <div class="sidebar-header">
        <h4>🚦 TraffiSight AI</h4>
    </div>

    <div class="sidebar-menu">
        <div class="menu-label">Main</div>
        
        <a href="{{ route('admin.dashboard') }}" class="menu-item {{ request()->routeIs('admin.dashboard') ? 'active' : '' }}">
            <i class="bi bi-grid-fill"></i>
            <span>Dashboard</span>
        </a>

        <div class="menu-label">Management</div>

        <a href="{{ route('admin.videos.index') }}" class="menu-item {{ request()->routeIs('admin.videos.*') ? 'active' : '' }}">
            <i class="bi bi-camera-video-fill"></i>
            <span>Videos</span>
        </a>

        <a href="{{ route('admin.users.index') }}" class="menu-item {{ request()->routeIs('admin.users.*') ? 'active' : '' }}">
            <i class="bi bi-people-fill"></i>
            <span>Users</span>
        </a>

        <div class="menu-label">System</div>

        <a href="#" class="menu-item">
            <i class="bi bi-gear-fill"></i>
            <span>Settings</span>
        </a>
    </div>
</div>
