@extends('layouts.app')

@section('title', 'Detalle de tarea')

@section('content')
<div class="d-flex justify-content-between align-items-center mb-3">
    <h1 class="h3 mb-0"><i class="bi bi-card-text me-2"></i>Detalle de tarea</h1>
    <div>
        <a href="{{ route('tasks.edit', $task) }}" class="btn btn-brand">
            <i class="bi bi-pencil me-1"></i> Editar
        </a>
        <a href="{{ route('tasks.index') }}" class="btn btn-outline-secondary">Volver</a>
    </div>
</div>

<div class="card shadow-sm">
    <div class="card-body">
        <h2 class="h5">{{ $task->title }}</h2>

        <p class="mb-2">
        @if ($task->status === 'completada')
            <span class="badge badge-completada">Completada</span>
        @else
            <span class="badge badge-pendiente">Pendiente</span>
        @endif
        </p>

        <div class="row mb-3">
            <div class="col-md-6">
                <span class="task-meta d-block">Responsable</span>
                <strong><i class="bi bi-person-check me-1"></i>{{ $task->responsible?->name ?? '—' }}</strong>
            </div>
            <div class="col-md-6">
                <span class="task-meta d-block">Asignado por</span>
                <strong><i class="bi bi-person-badge me-1"></i>{{ $task->assignedBy?->name ?? '—' }}</strong>
            </div>
        </div>

        @if ($task->description)
            <p class="text-secondary mb-3">{{ $task->description }}</p>
        @endif

        <ul class="list-unstyled task-meta mb-0">
            <li><i class="bi bi-calendar3 me-1"></i> Fecha límite: {{ $task->due_date?->format('d/m/Y') ?? 'Sin fecha límite' }}</li>
            <li><i class="bi bi-clock-history me-1"></i> Creada: {{ $task->created_at?->format('d/m/Y H:i') }}</li>
            <li><i class="bi bi-arrow-repeat me-1"></i> Actualizada: {{ $task->updated_at?->format('d/m/Y H:i') }}</li>
        </ul>
    </div>
</div>
@endsection
