<?php

namespace Database\Seeders;

use App\Models\Role;
use Illuminate\Database\Seeder;

class RoleSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $roles = [
            [
                'name' => 'Administrator',
                'slug' => 'admin',
                'description' => 'Full system access with all permissions',
            ],
            [
                'name' => 'Operator',
                'slug' => 'operator',
                'description' => 'Can upload and analyze videos',
            ],
            [
                'name' => 'Viewer',
                'slug' => 'viewer',
                'description' => 'Can only view reports and violations',
            ],
        ];

        foreach ($roles as $role) {
            Role::firstOrCreate(
                ['slug' => $role['slug']],
                $role
            );
        }

        $this->command->info('Roles created successfully!');
    }
}
