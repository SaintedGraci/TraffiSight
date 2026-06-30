<nav class="top-navbar">
    <div class="container-fluid">
        <div class="d-flex align-items-center justify-content-between w-100">
            <div>
                <button class="btn btn-link d-md-none text-dark" type="button" onclick="toggleSidebar()">
                    <i class="bi bi-list fs-4"></i>
                </button>
            </div>

            <div class="d-flex align-items-center gap-3">
                <!-- Notifications -->
                <div class="dropdown">
                    <button class="btn btn-link text-dark position-relative" type="button" data-bs-toggle="dropdown">
                        <i class="bi bi-bell fs-5"></i>
                        <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" style="font-size: 10px;">
                            3
                        </span>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end" style="min-width: 300px;">
                        <li class="px-3 py-2 border-bottom">
                            <strong>Notifications</strong>
                        </li>
                        <li><a class="dropdown-item py-2" href="#"><small>New violation detected</small></a></li>
                        <li><a class="dropdown-item py-2" href="#"><small>Video analysis complete</small></a></li>
                        <li><a class="dropdown-item py-2" href="#"><small>System update available</small></a></li>
                    </ul>
                </div>

                <!-- User Dropdown -->
                <div class="dropdown">
                    <button class="btn btn-link text-dark text-decoration-none d-flex align-items-center gap-2" type="button" id="userDropdown" data-bs-toggle="dropdown">
                        <div class="d-flex align-items-center gap-2">
                            <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 36px; height: 36px; font-weight: 600;">
                                {{ strtoupper(substr(Auth::user()->name, 0, 1)) }}
                            </div>
                            <div class="text-start d-none d-md-block">
                                <div style="font-size: 14px; font-weight: 600; line-height: 1.2;">{{ Auth::user()->name }}</div>
                                <div style="font-size: 12px; color: #64748b;">{{ Auth::user()->roles->first()->name ?? 'User' }}</div>
                            </div>
                        </div>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                        <li>
                            <a class="dropdown-item" href="{{ route('profile.edit') }}">
                                <i class="bi bi-person"></i> Profile
                            </a>
                        </li>
                        <li><hr class="dropdown-divider"></li>
                        <li>
                            <form method="POST" action="{{ route('logout') }}">
                                @csrf
                                <button type="submit" class="dropdown-item text-danger">
                                    <i class="bi bi-box-arrow-right"></i> Logout
                                </button>
                            </form>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</nav>

<script>
function toggleSidebar() {
    document.querySelector('.sidebar').classList.toggle('show');
}
</script>
