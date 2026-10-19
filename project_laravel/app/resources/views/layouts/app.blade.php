<!DOCTYPE html>
<html lang="es" data-bs-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>@yield('title', 'Tareas')@auth · {{ auth()->user()->name }}@endauth</title>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700&family=Nunito+Sans:wght@400;600;700&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
    <link href="{{ asset('css/app.css') }}" rel="stylesheet">

    {{-- Aplicar el tema guardado ANTES del primer render para evitar parpadeo --}}
    <script>
        (function () {
            const theme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-bs-theme', theme);
        })();
    </script>
</head>
<body>
    <nav class="navbar navbar-expand navbar-dark navbar-app mb-4">
        <div class="container">
            <a class="navbar-brand" href="{{ route('tasks.index') }}">
                <i class="bi bi-check2-square me-1"></i> Gestor de Tareas
            </a>

            <div class="d-flex align-items-center gap-2">
                @auth
                    <span class="navbar-text text-white-50 d-none d-sm-inline">
                        <i class="bi bi-person-circle me-1"></i> {{ auth()->user()->name }}
                    </span>
                    <form action="{{ route('logout') }}" method="POST" class="d-inline">
                        @csrf
                        <button type="submit" class="btn btn-sm btn-theme" title="Cerrar sesión">
                            <i class="bi bi-box-arrow-right"></i>
                        </button>
                    </form>
                @endauth
                <button type="button" id="theme-toggle" class="btn btn-sm btn-theme" title="Cambiar tema">
                    <i class="bi bi-moon-stars" id="theme-icon"></i>
                </button>
            </div>
        </div>
    </nav>

    <main class="container pb-5">
        {{-- Mensajes flash --}}
        @if (session('success'))
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                {{ session('success') }}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
            </div>
        @endif

        @yield('content')
    </main>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Alternar tema y persistir la preferencia
        document.getElementById('theme-toggle').addEventListener('click', function () {
            const html = document.documentElement;
            const next = html.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';

            html.setAttribute('data-bs-theme', next);
            localStorage.setItem('theme', next);
            updateThemeIcon(next);
        });

        function updateThemeIcon(theme) {
            const icon = document.getElementById('theme-icon');
            icon.classList.toggle('bi-moon-stars', theme === 'light');
            icon.classList.toggle('bi-sun', theme === 'dark');
        }

        updateThemeIcon(document.documentElement.getAttribute('data-bs-theme'));
    </script>
    @stack('scripts')
</body>
</html>
