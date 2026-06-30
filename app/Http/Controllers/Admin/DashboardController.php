<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\User;
use App\Models\Video;
use Illuminate\Http\Request;
use Illuminate\View\View;

class DashboardController extends Controller
{
    /**
     * Display the admin dashboard.
     */
    public function index(): View
    {
        // User Statistics
        $totalUsers = User::count();
        $activeUsers = User::where('is_active', true)->count();
        $recentUsers = User::with('roles')->latest()->take(5)->get();

        // Video Statistics
        $totalVideos = Video::count();
        $pendingVideos = Video::where('status', 'pending')->count();
        $processingVideos = Video::where('status', 'processing')->count();
        $completedVideos = Video::where('status', 'completed')->count();
        $failedVideos = Video::where('status', 'failed')->count();
        $recentVideos = Video::with('uploader')->latest()->take(5)->get();

        // AI Analysis Statistics
        $analyzedVideos = Video::whereNotNull('analysis_result')->count();
        
        // Extract statistics from analysis_result JSON
        $totalVehiclesDetected = 0;
        $totalViolations = 0;
        $totalPlatesRecognized = 0;
        $recentViolations = [];
        
        $videosWithAnalysis = Video::whereNotNull('analysis_result')
            ->where('status', 'completed')
            ->get();
        
        foreach ($videosWithAnalysis as $video) {
            $results = json_decode($video->analysis_result, true);
            
            if (isset($results['total_detections'])) {
                $totalVehiclesDetected += $results['total_detections'];
            }
            
            if (isset($results['violations']) && is_array($results['violations'])) {
                $violations = $results['violations'];
                $totalViolations += count($violations);
                
                // Collect recent violations
                foreach ($violations as $violation) {
                    $recentViolations[] = array_merge($violation, [
                        'video_title' => $video->title,
                        'video_id' => $video->id,
                        'timestamp' => (float)($violation['timestamp'] ?? 0),
                        'confidence' => (float)($violation['confidence'] ?? 0)
                    ]);
                }
            }
            
            if (isset($results['plates_recognized'])) {
                $totalPlatesRecognized += $results['plates_recognized'];
            }
        }
        
        // Sort and limit recent violations
        usort($recentViolations, function($a, $b) {
            return ($b['timestamp'] ?? 0) <=> ($a['timestamp'] ?? 0);
        });
        $recentViolations = array_slice($recentViolations, 0, 5);
        
        // Processing statistics
        $avgProcessingTime = $videosWithAnalysis->avg(function($video) {
            $results = json_decode($video->analysis_result, true);
            return $results['average_detection_time'] ?? 0;
        });

        return view('admin.dashboard', compact(
            'totalUsers',
            'activeUsers',
            'recentUsers',
            'totalVideos',
            'pendingVideos',
            'processingVideos',
            'completedVideos',
            'failedVideos',
            'recentVideos',
            'analyzedVideos',
            'totalVehiclesDetected',
            'totalViolations',
            'totalPlatesRecognized',
            'recentViolations',
            'avgProcessingTime'
        ));
    }
}
