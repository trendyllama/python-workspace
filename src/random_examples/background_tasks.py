import threading
import time
from collections import deque
from collections.abc import Callable
from types import TracebackType
from typing import Self

type DeadLetterState = list[tuple[str, int, BaseException]]


class BackgroundTaskManager:
    """
    A background task manager whose context starts workers and closes them on exit.
    """

    def __init__(
        self,
        max_attempts: int,
        backoff_secs: float,
        empty_queue_polling_interval: float = 0.01,
    ) -> None:
        self.tasks: deque[Callable[[], None]] = deque()
        self.dead_letter: deque[tuple[Callable[[], None], int, BaseException]] = deque()
        self.max_attempts: int = max_attempts
        self.backoff_secs: float = backoff_secs
        self._stop_event = threading.Event()
        self._lifecycle_lock = threading.Lock()
        self.main_thread: threading.Thread | None = None
        self.dead_letter_thread: threading.Thread | None = None
        self.main_lock = threading.Lock()
        self.dead_letter_lock = threading.Lock()
        self.empty_queue_polling_interval: float = empty_queue_polling_interval

    def __enter__(self) -> Self:
        self.run_tasks()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def put_task(self, task: Callable[[], None]) -> None:
        """
        Add a task to the queue.

        :param task: A callable representing the task to be executed.
        """
        with self.main_lock:
            self.tasks.append(task)

    def _run_main_loop(self) -> None:
        """
        Run the main loop that executes tasks in the queue.
        """
        while not self._stop_event.is_set():
            with self.main_lock:
                task = self.tasks.popleft() if self.tasks else None
            if task is None:
                time.sleep(self.empty_queue_polling_interval)
                continue

            try:
                task()
            except Exception as exc:  # noqa: BLE001
                print(f"Error running task: {exc}")
                if not self._stop_event.is_set():
                    with self.dead_letter_lock:
                        self.dead_letter.append((task, 1, exc))
                    if self.backoff_secs > 0:
                        self._stop_event.wait(self.backoff_secs)

    def _run_dead_letter_loop(self) -> None:
        """
        Run the loop that executes tasks in the dead letter queue.
        """
        while not self._stop_event.is_set():
            with self.dead_letter_lock:
                dead_letter_task = (
                    self.dead_letter.popleft() if self.dead_letter else None
                )
            if dead_letter_task is None:
                time.sleep(self.empty_queue_polling_interval)
                continue

            task, attempts, _ = dead_letter_task

            if attempts > self.max_attempts:
                print(f"Task {task} exceeded max attempts. Discarding.")
                continue

            try:
                task()
            except Exception as retry_exc:  # noqa: BLE001
                print(f"Error running dead letter task: {retry_exc}")
                if not self._stop_event.is_set():
                    with self.dead_letter_lock:
                        self.dead_letter.append((task, attempts + 1, retry_exc))
                    if self.backoff_secs > 0:
                        self._stop_event.wait(self.backoff_secs)

    def run_tasks(self) -> None:
        """
        Run the task loops in the background until the manager is closed.
        """
        with self._lifecycle_lock:
            threads = (self.main_thread, self.dead_letter_thread)
            if any(thread is not None and thread.is_alive() for thread in threads):
                return

            self._stop_event.clear()
            self.main_thread = threading.Thread(target=self._run_main_loop)
            self.dead_letter_thread = threading.Thread(
                target=self._run_dead_letter_loop
            )
            self.main_thread.start()
            self.dead_letter_thread.start()

    def close(self) -> DeadLetterState:
        """
        Close the task manager and clean up resources.
        """
        self._stop_event.set()

        with self.main_lock:
            self.tasks.clear()

        dead_letter_state: list[tuple[str, int, BaseException]] = []
        with self.dead_letter_lock:
            for task, attempts, exception in self.dead_letter:
                dead_letter_state.append((str(task), attempts, exception))
            self.dead_letter.clear()

        current_thread: threading.Thread = threading.current_thread()
        for thread in (self.main_thread, self.dead_letter_thread):
            if (
                thread is not None
                and thread is not current_thread
                and thread.ident is not None
            ):
                thread.join()

        return dead_letter_state
