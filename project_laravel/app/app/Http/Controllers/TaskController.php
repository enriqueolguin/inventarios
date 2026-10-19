<?php

namespace App\Http\Controllers;

use App\Mail\TaskAssignedMail;
use App\Mail\TaskStatusChangedMail;
use App\Models\Task;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Mail;

class TaskController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        $status = $request->query('status');

        $tasks = Task::query()
            ->with(['responsible', 'assignedBy'])
            ->when($status, fn ($query) => $query->where('status', $status))
            ->latest()
            ->paginate(10)
            ->withQueryString();

        $counts = [
            'todas' => Task::count(),
            'pendiente' => Task::where('status', 'pendiente')->count(),
            'completada' => Task::where('status', 'completada')->count(),
        ];

        return view('tasks.index', compact('tasks', 'status', 'counts'));
    }

    /**
     * Show the form for creating a new resource.
     */
    public function create()
    {
        return view('tasks.create', [
            'task' => new Task(),
            'statuses' => $this->statuses(),
            'users' => User::orderBy('name')->get(['id', 'name', 'email']),
        ]);
    }

    /**
     * Store a newly created task and notify both users by email.
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'title' => 'required|string|max:255',
            'responsible_id' => 'required|exists:users,id',
            'assigned_by_id' => 'required|exists:users,id',
            'description' => 'nullable|string',
            'status' => 'required|in:pendiente,completada',
            'due_date' => 'nullable|date',
        ]);

        $task = Task::create($validated);

        $this->notifyAssignment($task);

        return redirect()
            ->route('tasks.index')
            ->with('success', 'Tarea creada correctamente. Se notificó por correo a los involucrados.');
    }

    /**
     * Display the specified resource.
     */
    public function show(Task $task)
    {
        return view('tasks.show', [
            'task' => $task->load(['responsible', 'assignedBy']),
        ]);
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(Task $task)
    {
        return view('tasks.edit', [
            'task' => $task,
            'statuses' => $this->statuses(),
            'users' => User::orderBy('name')->get(['id', 'name', 'email']),
        ]);
    }

    /**
     * Update the task and notify on status change.
     */
    public function update(Request $request, Task $task)
    {
        $validated = $request->validate([
            'title' => 'required|string|max:255',
            'responsible_id' => 'required|exists:users,id',
            'assigned_by_id' => 'required|exists:users,id',
            'description' => 'nullable|string',
            'status' => 'required|in:pendiente,completada',
            'due_date' => 'nullable|date',
        ]);

        $oldStatus = $task->status;
        $task->update($validated);

        if ($task->status !== $oldStatus) {
            $this->notifyStatusChange($task, $oldStatus);
        }

        return redirect()
            ->route('tasks.index')
            ->with('success', 'Tarea actualizada correctamente.');
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Task $task)
    {
        $task->delete();

        return redirect()
            ->route('tasks.index')
            ->with('success', 'Tarea eliminada correctamente.');
    }

    /**
     * Allowed status values.
     */
    private function statuses(): array
    {
        return ['pendiente', 'completada'];
    }

    /**
     * Send assignment emails to responsible and assigner (no duplicates).
     */
    private function notifyAssignment(Task $task): void
    {
        $assigner = $task->assignedBy;

        $recipients = collect([$task->responsible, $assigner])
            ->filter()
            ->unique('id');

        foreach ($recipients as $recipient) {
            Mail::to($recipient->email)->send(
                new TaskAssignedMail($task, $recipient, $assigner)
            );
        }
    }

    /**
     * Send status change emails to responsible and assigner (no duplicates).
     */
    private function notifyStatusChange(Task $task, string $oldStatus): void
    {
        $actor = auth()->user();

        $recipients = collect([$task->responsible, $task->assignedBy])
            ->filter()
            ->unique('id');

        foreach ($recipients as $recipient) {
            Mail::to($recipient->email)->send(
                new TaskStatusChangedMail($task, $recipient, $actor, $oldStatus)
            );
        }
    }
}
