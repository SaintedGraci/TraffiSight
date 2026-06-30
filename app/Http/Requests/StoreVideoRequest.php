<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class StoreVideoRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        return auth()->check();
    }

    /**
     * Get the validation rules that apply to the request.
     *
     * @return array<string, \Illuminate\Contracts\Validation\ValidationRule|array<mixed>|string>
     */
    public function rules(): array
    {
        return [
            'title' => ['required', 'string', 'max:255'],
            'description' => ['nullable', 'string', 'max:1000'],
            'video' => [
                'required',
                'file',
                'mimes:mp4,avi,mov,mkv,flv,wmv',
                'max:512000', // 500MB max
            ],
        ];
    }

    /**
     * Get custom messages for validator errors.
     */
    public function messages(): array
    {
        return [
            'title.required' => 'Please provide a title for the video.',
            'video.required' => 'Please select a video file to upload.',
            'video.mimes' => 'Only video files (mp4, avi, mov, mkv, flv, wmv) are allowed.',
            'video.max' => 'Video file size must not exceed 500MB.',
        ];
    }
}
