@extends('layouts.app')

@section('title', 'Nueva tarea')

@section('content')
<h1 class="h3 mb-3"><i class="bi bi-plus-circle me-2"></i>Nueva tarea</h1>

@include('tasks.form', [
    'action' => route('tasks.store'),
    'submitLabel' => 'Crear tarea',
])
@endsection
