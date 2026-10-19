@extends('layouts.app')

@section('title', 'Editar tarea')

@section('content')
<h1 class="h3 mb-3"><i class="bi bi-pencil-square me-2"></i>Editar tarea</h1>

@include('tasks.form', [
    'action' => route('tasks.update', $task),
    'submitLabel' => 'Guardar cambios',
])
@endsection
