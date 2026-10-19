@extends('layouts.app')

@section('title', 'Iniciar sesión')

@section('content')
<div class="row justify-content-center align-items-center" style="min-height: 70vh;">
    <div class="col-12 col-sm-8 col-md-6 col-lg-4">
        <div class="card shadow-sm border-0">
            <div class="card-body p-4 p-md-5">
                <div class="text-center mb-4">
                    <div class="login-logo mx-auto mb-3">
                        <i class="bi bi-check2-square"></i>
                    </div>
                    <h1 class="h4 mb-1">Gestor de Tareas</h1>
                    <p class="task-meta mb-0">Inicia sesión para continuar</p>
                </div>

                <form action="{{ route('login.attempt') }}" method="POST" novalidate>
                    @csrf

                    <div class="mb-3">
                        <label for="email" class="form-label">Correo electrónico</label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-envelope"></i></span>
                            <input type="email" name="email" id="email" value="{{ old('email') }}"
                                   class="form-control @error('email') is-invalid @enderror"
                                   placeholder="tu@correo.com" required autofocus>
                            @error('email')
                                <div class="invalid-feedback">{{ $message }}</div>
                            @enderror
                        </div>
                    </div>

                    <div class="mb-3">
                        <label for="password" class="form-label">Contraseña</label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-lock"></i></span>
                            <input type="password" name="password" id="password"
                                   class="form-control @error('password') is-invalid @enderror"
                                   placeholder="••••••••" required>
                            @error('password')
                                <div class="invalid-feedback">{{ $message }}</div>
                            @enderror
                        </div>
                    </div>

                    <div class="form-check mb-4">
                        <input type="checkbox" name="remember" id="remember" value="1" class="form-check-input">
                        <label for="remember" class="form-check-label task-meta">Mantener sesión abierta</label>
                    </div>

                    <button type="submit" class="btn btn-brand w-100">
                        <i class="bi bi-box-arrow-in-right me-1"></i> Ingresar
                    </button>
                </form>
            </div>
        </div>

        <p class="text-center task-meta mt-3 mb-0">
            <i class="bi bi-shield-check me-1"></i> Usuario demo: <strong>demo@taskapp.com</strong> · <strong>demo1234</strong>
        </p>
    </div>
</div>
@endsection
