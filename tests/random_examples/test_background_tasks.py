import threading

from random_examples.background_tasks import BackgroundTaskManager, DeadLetterState


def test_run_tasks_executes_queued_tasks():
    manager = BackgroundTaskManager(max_attempts=2, backoff_secs=0)
    completed: list[str] = []
    tasks_completed = threading.Event()

    def complete_second_task():
        completed.append("second")
        tasks_completed.set()

    with manager:
        manager.put_task(lambda: completed.append("first"))
        manager.put_task(complete_second_task)

        assert tasks_completed.wait(timeout=1)

    assert completed == ["first", "second"]
    assert not manager.tasks
    assert manager.main_thread is not None
    assert not manager.main_thread.is_alive()
    assert manager.dead_letter_thread is not None
    assert not manager.dead_letter_thread.is_alive()


def test_run_tasks_retries_failed_task_until_max_attempts():
    manager = BackgroundTaskManager(max_attempts=2, backoff_secs=0)
    attempts = 0
    max_attempts_reached = threading.Event()

    def failing_task():
        nonlocal attempts
        attempts += 1
        if attempts == len(tasks) * (manager.max_attempts + 1):
            max_attempts_reached.set()
        raise RuntimeError

    tasks = [failing_task, failing_task]

    with manager:
        for task in tasks:
            manager.put_task(task)
        assert max_attempts_reached.wait(timeout=1)

    assert attempts == len(tasks) * (manager.max_attempts + 1)
    assert not manager.dead_letter


def test_close_returns_and_clears_queued_dead_letters():
    manager = BackgroundTaskManager(max_attempts=2, backoff_secs=0)

    def pending_task():
        pass

    error = RuntimeError()
    manager.put_task(pending_task)
    manager.dead_letter.append((pending_task, 1, error))

    dead_letter_state: DeadLetterState = manager.close()

    assert dead_letter_state == [(str(pending_task), 1, error)]
    assert not manager.tasks
    assert not manager.dead_letter


def test_close_stops_and_joins_both_worker_threads():
    manager = BackgroundTaskManager(max_attempts=3, backoff_secs=10)
    task_started = threading.Event()
    release_task = threading.Event()
    retry_started = threading.Event()

    def blocking_task():
        task_started.set()
        release_task.wait()

    def failing_task():
        retry_started.set()
        raise RuntimeError

    manager.put_task(blocking_task)
    manager.dead_letter.append((failing_task, 1, RuntimeError()))
    runner = threading.Thread(target=manager.run_tasks)
    runner.start()

    assert task_started.wait(timeout=1)
    assert retry_started.wait(timeout=1)

    closer = threading.Thread(target=manager.close)
    closer.start()
    release_task.set()

    closer.join(timeout=1)
    runner.join(timeout=1)

    assert not closer.is_alive()
    assert not runner.is_alive()
    assert manager.main_thread is not None
    assert not manager.main_thread.is_alive()
    assert manager.dead_letter_thread is not None
    assert not manager.dead_letter_thread.is_alive()
