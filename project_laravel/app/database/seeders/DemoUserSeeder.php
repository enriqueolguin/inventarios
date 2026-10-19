<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class DemoUserSeeder extends Seeder
{
    /**
     * Demo users, all with the same password.
     */
    public function run(): void
    {
        $users = [
            ['name' => 'Demo', 'email' => 'demo@taskapp.com'],
            ['name' => 'Ana Torres', 'email' => 'ana@taskapp.com'],
            ['name' => 'Luis Ramírez', 'email' => 'luis@taskapp.com'],
            ['name' => 'María López', 'email' => 'maria@taskapp.com'],
        ];

        foreach ($users as $user) {
            User::updateOrCreate(
                ['email' => $user['email']],
                ['name' => $user['name'], 'password' => Hash::make('demo1234')],
            );
        }
    }
}
