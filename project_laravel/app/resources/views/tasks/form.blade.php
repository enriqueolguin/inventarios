<form action="{{ $action }}" method="POST" class="card shadow-sm">
    @csrf
    @if (isset($task) && $task->exists)
        @method('PUT')
    @endif

    <div class="card-body">
        <div class="mb-3">
            <label for="title" class="form-label">Título <span class="text-danger">*</span></label>
            <input type="text" name="title" id="title"
                   value="{{ old('title', $task->title ?? '') }}"
                   class="form-control @error('title') is-invalid @enderror"
                   maxlength="255" required autofocus>
            @error('title')
                <div class="invalid-feedback">{{ $message }}</div>
            @enderror
        </div>

        <div class="row">
            <div class="col-md-6 mb-3">
                <label for="responsible_id" class="form-label">Responsable <span class="text-danger">*</span></label>
                <select name="responsible_id" id="responsible_id"
                        class="form-select @error('responsible_id') is-invalid @enderror" required>
                    <option value="">Selecciona un usuario…</option>
                    @foreach ($users as $user)
                        <option value="{{ $user->id }}" @selected(old('responsible_id', $task->responsible_id) == $user->id)>
                            {{ $user->name }} ({{ $user->email }})
                        </option>
                    @endforeach
                </select>
                @error('responsible_id')
                    <div class="invalid-feedback">{{ $message }}</div>
                @enderror
            </div>

            <div class="col-md-6 mb-3">
                <label for="assigned_by_id" class="form-label">Asignado por <span class="text-danger">*</span></label>
                <select name="assigned_by_id" id="assigned_by_id"
                        class="form-select @error('assigned_by_id') is-invalid @enderror" required>
                    <option value="">Selecciona un usuario…</option>
                    @foreach ($users as $user)
                        <option value="{{ $user->id }}" @selected(old('assigned_by_id', $task->assigned_by_id ?? auth()->id()) == $user->id)>
                            {{ $user->name }} ({{ $user->email }})
                        </option>
                    @endforeach
                </select>
                @error('assigned_by_id')
                    <div class="invalid-feedback">{{ $message }}</div>
                @enderror
            </div>
        </div>

        <div class="mb-3">
            <label for="description" class="form-label">Descripción</label>
            <textarea name="description" id="description" rows="4"
                      class="form-control @error('description') is-invalid @enderror">{{ old('description', $task->description ?? '') }}</textarea>
            @error('description')
                <div class="invalid-feedback">{{ $message }}</div>
            @enderror
        </div>

        <div class="row">
            <div class="col-md-6 mb-3">
                <label for="status" class="form-label">Estado</label>
                <select name="status" id="status"
                        class="form-select @error('status') is-invalid @enderror">
                    @foreach ($statuses as $value)
                        <option value="{{ $value }}" @selected(old('status', $task->status ?? 'pendiente') === $value)>
                            {{ ucfirst($value) }}
                        </option>
                    @endforeach
                </select>
                @error('status')
                    <div class="invalid-feedback">{{ $message }}</div>
                @enderror
            </div>

            <div class="col-md-6 mb-3">
                <label for="due_date" class="form-label">Fecha límite</label>
                <input type="date" name="due_date" id="due_date"
                       value="{{ old('due_date', $task->due_date?->format('Y-m-d')) }}"                       class="form-control @error('due_date') is-invalid @enderror">
            @error('due_date')
                <div class="invalid-feedback">{{ $message }}</div>
            @enderror
        </div>
        </div>
    </div>

    <div class="card-footer d-flex justify-content-between">
        <a href="{{ route('tasks.index') }}" class="btn btn-outline-secondary">
            <i class="bi bi-arrow-left me-1"></i> Volver
        </a>
        <button type="submit" class="btn btn-brand">
            <i class="bi bi-check-lg me-1"></i> {{ $submitLabel }}
        </button>
    </div>
</form>
