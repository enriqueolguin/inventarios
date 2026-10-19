@extends('layouts.app')

@section('title', 'Listado de tareas')

@section('content')
<div class="d-flex justify-content-between align-items-center mb-3">
    <h1 class="h3 mb-0"><i class="bi bi-list-task me-2"></i>Tareas</h1>
    <a href="{{ route('tasks.create') }}" class="btn btn-brand">
        <i class="bi bi-plus-lg me-1"></i> Nueva tarea
    </a>
</div>

<div class="card shadow-sm">
    <div class="card-header py-3">
        <div class="filter-tabs" role="group" aria-label="Filtrar por estado">
            <a href="{{ route('tasks.index') }}" class="filter-tab {{ $status === null ? 'active active-all' : '' }}">
                <i class="bi bi-list-ul"></i> Todas
                <span class="count">{{ $counts['todas'] }}</span>
            </a>
            <a href="{{ route('tasks.index', ['status' => 'pendiente']) }}" class="filter-tab {{ $status === 'pendiente' ? 'active active-pendiente' : '' }}">
                <i class="bi bi-hourglass-split"></i> Pendientes
                <span class="count">{{ $counts['pendiente'] }}</span>
            </a>
            <a href="{{ route('tasks.index', ['status' => 'completada']) }}" class="filter-tab {{ $status === 'completada' ? 'active active-completada' : '' }}">
                <i class="bi bi-check2-circle"></i> Completadas
                <span class="count">{{ $counts['completada'] }}</span>
            </a>
        </div>
    </div>

    <div class="card-body p-0">
        @if ($tasks->isEmpty())
            <div class="text-center empty-state py-5">
                <i class="bi bi-inbox display-4 d-block mb-2"></i>
                No hay tareas @if($status) con estado «{{ $status }}» @endif
            </div>
        @else
            <table class="table table-hover align-middle mb-0">
                <thead>
                    <tr>
                        <th>Título</th>
                        <th>Responsable</th>
                        <th>Estado</th>
                        <th>Fecha límite</th>
                        <th class="text-end">Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach ($tasks as $task)
                        <tr>
                            <td>
                                <strong>{{ $task->title }}</strong>
                                @if ($task->description)
                                    <small class="d-block text-muted text-truncate" style="max-width: 420px;">
                                        {{ $task->description }}
                                    </small>
                                @endif
                            </td>
                            <td>
                                <i class="bi bi-person-check me-1"></i>{{ $task->responsible?->name ?? '—' }}
                                <small class="d-block task-meta">
                                    <i class="bi bi-person-badge me-1"></i>Asignó: {{ $task->assignedBy?->name ?? '—' }}
                                </small>
                            </td>
                            <td>
                                @if ($task->status === 'completada')
                                    <span class="badge badge-completada">Completada</span>
                                @else
                                    <span class="badge badge-pendiente">Pendiente</span>
                                @endif
                            </td>
                            <td>{{ $task->due_date?->format('d/m/Y') ?? '—' }}</td>
                            <td class="text-end">
                                <a href="{{ route('tasks.show', $task) }}" class="btn btn-sm btn-outline-secondary" title="Ver">
                                    <i class="bi bi-eye"></i>
                                </a>
                                <a href="{{ route('tasks.edit', $task) }}" class="btn btn-sm btn-outline-brand" title="Editar">
                                    <i class="bi bi-pencil"></i>
                                </a>
                                <form action="{{ route('tasks.destroy', $task) }}" method="POST" class="d-inline"
                                      onsubmit="return confirm('¿Eliminar esta tarea?')">
                                    @csrf
                                    @method('DELETE')
                                    <button type="submit" class="btn btn-sm btn-outline-danger" title="Eliminar">
                                        <i class="bi bi-trash"></i>
                                    </button>
                                </form>
                            </td>
                        </tr>
                    @endforeach
                </tbody>
            </table>
        @endif
    </div>

    @if ($tasks->hasPages())
        <div class="card-footer">
            {{ $tasks->links() }}
        </div>
    @endif
</div>
@endsection
