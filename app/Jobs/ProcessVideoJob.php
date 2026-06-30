<?php

namespace App\Jobs;

use App\Models\Video;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Process;

class ProcessVideoJob implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    /**
     * The number of seconds the job can run before timing out.
     *
     * @var int
     */
    public $timeout = 3600; // 1 hour for large videos

    /**
     * The number of times the job may be attempted.
     *
     * @var int
     */
    public $tries = 3;

    /**
     * The video instance.
     *
     * @var \App\Models\Video
     */
    protected $video;

    /**
     * Create a new job instance.
     */
    public function __construct(Video $video)
    {
        $this->video = $video;
    }

    /**
     * Execute the job.
     */
    public function handle(): void
    {
        Log::info("Starting video processing", ['video_id' => $this->video->id]);

        // Update status to processing
        $this->video->update([
            'status' => 'processing'
        ]);

        try {
            // Get paths
            $pythonPath = $this->getPythonPath();
            $scriptPath = base_path('python_ai/main.py');
            $videoPath = storage_path('app/public/' . $this->video->filepath);

            // Check if Python script exists
            if (!file_exists($scriptPath)) {
                throw new \Exception("Python script not found at: {$scriptPath}");
            }

            // Check if video file exists
            if (!file_exists($videoPath)) {
                throw new \Exception("Video file not found at: {$videoPath}");
            }

            Log::info("Running Python analysis", [
                'video_id' => $this->video->id,
                'python' => $pythonPath,
                'script' => $scriptPath,
                'video' => $videoPath
            ]);

            // Run Python script with complete analysis
            $command = sprintf(
                '"%s" "%s" analyze -i "%s" --video-id %d',
                $pythonPath,
                $scriptPath,
                $videoPath,
                $this->video->id
            );

            // Execute command
            $output = [];
            $returnCode = 0;
            
            // Change to python_ai directory before running
            $pythonDir = base_path('python_ai');
            $oldDir = getcwd();
            chdir($pythonDir);
            
            exec($command . ' 2>&1', $output, $returnCode);
            
            // Change back to original directory
            chdir($oldDir);

            Log::info("Python script output", [
                'return_code' => $returnCode,
                'output' => implode("\n", $output)
            ]);

            // Check for success
            if ($returnCode === 0) {
                // Try to load results from output
                $this->loadResults();

                Log::info("Video processing completed successfully", [
                    'video_id' => $this->video->id
                ]);
            } else {
                throw new \Exception("Python script failed with code {$returnCode}: " . implode("\n", $output));
            }

        } catch (\Exception $e) {
            Log::error("Video processing failed", [
                'video_id' => $this->video->id,
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            $this->video->update([
                'status' => 'failed'
            ]);

            throw $e;
        }
    }

    /**
     * Load results from Python output
     */
    protected function loadResults(): void
    {
        // Get output directory
        $videoBasename = pathinfo($this->video->filename, PATHINFO_FILENAME);
        $outputDir = base_path("python_ai/output/{$videoBasename}");
        $resultsFile = "{$outputDir}/detection_results.json";

        if (file_exists($resultsFile)) {
            $results = json_decode(file_get_contents($resultsFile), true);

            if ($results) {
                $this->video->update([
                    'analysis_result' => json_encode($results),
                    'analyzed_at' => now(),
                    'status' => 'completed'
                ]);

                Log::info("Results loaded and saved", [
                    'video_id' => $this->video->id,
                    'detections' => $results['total_detections'] ?? 0
                ]);
            } else {
                throw new \Exception("Failed to parse results JSON");
            }
        } else {
            // Mark as completed even without results file
            $this->video->update([
                'analyzed_at' => now(),
                'status' => 'completed'
            ]);

            Log::warning("Results file not found, marking as completed", [
                'video_id' => $this->video->id,
                'expected_file' => $resultsFile
            ]);
        }
    }

    /**
     * Get Python executable path
     */
    protected function getPythonPath(): string
    {
        // Try virtual environment first
        $venvPython = base_path('python_ai/venv/Scripts/python.exe');
        if (file_exists($venvPython)) {
            return $venvPython;
        }

        // Fallback to system Python
        return 'python';
    }

    /**
     * Handle a job failure.
     */
    public function failed(\Throwable $exception): void
    {
        Log::error("Video processing job failed permanently", [
            'video_id' => $this->video->id,
            'error' => $exception->getMessage()
        ]);

        $this->video->update([
            'status' => 'failed'
        ]);
    }
}
