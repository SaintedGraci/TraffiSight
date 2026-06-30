<?php

namespace App\Services;

use App\Models\Video;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;

class VideoService
{
    /**
     * Store uploaded video file.
     */
    public function storeVideo(UploadedFile $file, array $data): Video
    {
        // Generate unique filename
        $filename = $file->getClientOriginalName();
        $extension = $file->getClientOriginalExtension();
        $uniqueName = Str::slug(pathinfo($filename, PATHINFO_FILENAME)) . '_' . time() . '.' . $extension;
        
        // Store video file
        $filepath = $file->storeAs('videos', $uniqueName, 'public');
        
        // Get file metadata
        $filesize = $file->getSize();
        $format = $extension;
        
        // Create video record
        $video = Video::create([
            'title' => $data['title'],
            'description' => $data['description'] ?? null,
            'filename' => $filename,
            'filepath' => $filepath,
            'filesize' => $filesize,
            'format' => $format,
            'status' => 'pending',
            'uploaded_by' => auth()->id(),
        ]);

        // Extract video metadata (duration, resolution, fps) asynchronously
        // This will be enhanced in later phases
        $this->extractMetadata($video);

        // AUTO-ANALYSIS DISABLED - Use "Run AI Detection" button instead
        // $this->startAnalysis($video);

        return $video;
    }

    /**
     * Extract video metadata.
     * This is a placeholder - will be enhanced with FFmpeg in later phases.
     */
    protected function extractMetadata(Video $video): void
    {
        // For now, we'll set placeholder values
        // In Phase 3, we'll use Python/FFmpeg to extract real metadata
        $video->update([
            'duration' => null,
            'resolution' => null,
            'fps' => null,
        ]);
    }

    /**
     * Update video information.
     */
    public function updateVideo(Video $video, array $data): Video
    {
        $video->update([
            'title' => $data['title'],
            'description' => $data['description'] ?? null,
        ]);

        return $video;
    }

    /**
     * Delete video and its file.
     */
    public function deleteVideo(Video $video): bool
    {
        // Delete video file
        if (Storage::disk('public')->exists($video->filepath)) {
            Storage::disk('public')->delete($video->filepath);
        }

        // Delete thumbnail if exists
        if ($video->thumbnail && Storage::disk('public')->exists($video->thumbnail)) {
            Storage::disk('public')->delete($video->thumbnail);
        }

        // Delete video record
        return $video->delete();
    }

    /**
     * Start video analysis.
     * Dispatches background job for AI processing.
     */
    public function startAnalysis(Video $video): bool
    {
        if (!$video->canBeAnalyzed()) {
            return false;
        }

        // Dispatch job to queue for background processing
        \App\Jobs\ProcessVideoJob::dispatch($video);

        return true;
    }

    /**
     * Get video statistics.
     */
    public function getStatistics(): array
    {
        return [
            'total' => Video::count(),
            'pending' => Video::withStatus('pending')->count(),
            'processing' => Video::withStatus('processing')->count(),
            'completed' => Video::withStatus('completed')->count(),
            'failed' => Video::withStatus('failed')->count(),
        ];
    }
}
