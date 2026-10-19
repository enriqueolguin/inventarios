<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, Helvetica, sans-serif; background-color: #eef4f3; margin: 0; padding: 24px; }
        .container { max-width: 560px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #d3dedb; }
        .header { background: linear-gradient(135deg, #0f766e, #0891b2); color: #ffffff; padding: 24px; text-align: center; }
        .header h1 { margin: 0; font-size: 20px; }
        .body { padding: 24px; color: #0f172a; }
        .button { display: inline-block; background: #0d9488; color: #ffffff; text-decoration: none; padding: 10px 22px; border-radius: 50rem; font-weight: bold; margin-top: 12px; }
        .meta { background: #eef4f3; border-radius: 8px; padding: 12px 16px; margin: 16px 0; }
        .meta p { margin: 4px 0; font-size: 14px; }
        .muted { color: #55657a; font-size: 13px; }
        .footer { padding: 16px 24px; border-top: 1px solid #d3dedb; }
    </style>
    <title></title>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔄 Cambio de estado</h1>
        </div>
        <div class="body">
            <p>Hola <strong>{{ $recipient->name }}</strong>,</p>

            <p><strong>{{ $actor->name }}</strong> cambió el estado de la tarea <strong>{{ $task->title }}</strong>
                de <strong>{{ ucfirst($oldStatus) }}</strong> a <strong>{{ ucfirst($task->status) }}</strong>.</p>

            <div class="meta">
                <p><strong>Responsable:</strong> {{ $task->responsible->name }}</p>
                <p><strong>Asignada por:</strong> {{ $task->assignedBy->name }}</p>
                <p><strong>Estado anterior:</strong> {{ ucfirst($oldStatus) }}</p>
                <p><strong>Estado nuevo:</strong> {{ ucfirst($task->status) }}</p>
            </div>

            <a class="button" href="{{ url('/tasks/' . $task->id) }}">Ver tarea</a>
            <p class="muted">Si el botón no funciona, copia esta URL en tu navegador:<br>{{ url('/tasks/' . $task->id) }}</p>
        </div>
        <div class="footer">
            <p class="muted">Este es un mensaje automático del Gestor de Tareas. No respondas a este correo.</p>
        </div>
    </div>
</body>
</html>
