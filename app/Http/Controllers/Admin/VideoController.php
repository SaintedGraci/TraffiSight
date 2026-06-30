<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Http\Requests\StoreVideoRequest;
use App\Http\Requests\UpdateVideoRequest;
use App\Models\Video;
use App\Services\VideoService;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;

class VideoController extends Controller
{
    protected VideoService $videoService;

    public function __construct(VideoService $videoService)
    {
        $this->videoService = $videoService;
    }

    /**
     * Display a listing of videos.
     */
    public function index(Request $request): View
    {
        $query = Video::with('uploader')->latest();

        // Filter by status
        if ($request->filled('status')) {
            $query->where('status', $request->status);
        }

        // Search by title
        if ($request->filled('search')) {
            $query->where('title', 'like', '%' . $request->search . '%');
        }

        $videos = $query->paginate(12);
        $statistics = $this->videoService->getStatistics();

        return view('admin.videos.index', compact('videos', 'statistics'));
    }

    /**
     * Show the form for creating a new video.
     */
    public function create(): View
    {
        return view('admin.videos.create');
    }

    /**
     * Store a newly created video in storage.
     */
    public function store(StoreVideoRequest $request): RedirectResponse
    {
        try {
            $video = $this->videoService->storeVideo(
                $request->file('video'),
                $request->validated()
            );

            return redirect()->route('admin.videos.show', $video)
                ->with('success', 'Video uploaded successfully!');
        } catch (\Exception $e) {
            return back()->with('error', 'Failed to upload video: ' . $e->getMessage())
                ->withInput();
        }
    }

    /**
     * Display the specified video.
     */
    public function show(Video $video): View
    {
        $video->load('uploader');
        
        return view('admin.videos.show', compact('video'));
    }

    /**
     * Show the form for editing the specified video.
     */
    public function edit(Video $video): View
    {
        return view('admin.videos.edit', compact('video'));
    }

    /**
     * Update the specified video in storage.
     */
    public function update(UpdateVideoRequest $request, Video $video): RedirectResponse
    {
        try {
            $this->videoService->updateVideo($video, $request->validated());

            return redirect()->route('admin.videos.show', $video)
                ->with('success', 'Video updated successfully!');
        } catch (\Exception $e) {
            return back()->with('error', 'Failed to update video: ' . $e->getMessage())
                ->withInput();
        }
    }

    /**
     * Remove the specified video from storage.
     */
    public function destroy(Video $video): RedirectResponse
    {
        try {
            $this->videoService->deleteVideo($video);

            return redirect()->route('admin.videos.index')
                ->with('success', 'Video deleted successfully!');
        } catch (\Exception $e) {
            return back()->with('error', 'Failed to delete video: ' . $e->getMessage());
        }
    }

    /**
     * Start video analysis.
     */
    public function analyze(Video $video): RedirectResponse
    {
        if (!$video->canBeAnalyzed()) {
            return back()->with('error', 'This video cannot be analyzed at this time.');
        }

        try {
            $this->videoService->startAnalysis($video);

            return back()->with('success', 'Video analysis started! Processing may take several minutes.');
        } catch (\Exception $e) {
            return back()->with('error', 'Failed to start analysis: ' . $e->getMessage());
        }
    }
}
