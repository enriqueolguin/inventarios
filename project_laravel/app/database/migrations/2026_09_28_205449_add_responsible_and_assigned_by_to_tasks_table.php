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
        Schema::table('tasks', function (Blueprint $table) {
            // default('') requerido por SQLite al añadir NOT NULL a una tabla existente
            $table->string('responsible')->default('')->after('title');
            $table->string('assigned_by')->default('')->after('responsible');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('tasks', function (Blueprint $table) {
            $table->dropColumn(['responsible', 'assigned_by']);
        });
    }
};
