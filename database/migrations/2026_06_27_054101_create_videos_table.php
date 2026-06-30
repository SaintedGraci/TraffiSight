<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('videos', function (Blueprint $table) {
            $table->id();
            $table->string('title');
            $table->text('description')->nullable();
            $table->string('filename'); // Original filename
            $table->string('filepath'); // Stored file path
            $table->string('thumbnail')->nullable(); // Thumbnail image path
            $table->unsignedBigInteger('filesize'); // File size in bytes
            $table->integer('duration')->nullable(); // Duration in seconds
            $table->string('resolution')->nullable(); // e.g., 1920x1080
            $table->decimal('fps', 8, 2)->nullable(); // Frames per second
            $table->string('format')->nullable(); // Video format (mp4, avi, etc.)
            $table->enum('status', ['pending', 'processing', 'completed', 'failed'])->default('pending');
            $table->text('analysis_result')->nullable(); // JSON result from Python AI
            $table->timestamp('analyzed_at')->nullable();
            $table->foreignId('uploaded_by')->constrained('users')->onDelete('cascade');
            $table->timestamps();
            
            // Indexes for better performance
            $table->index('status');
            $table->index('uploaded_by');
            $table->index('created_at');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('videos');
    }
};
