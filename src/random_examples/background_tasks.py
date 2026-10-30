import threading
from collections import deque
from collections.abc import Callable

type DeadLetterState = list[tuple[str, int, BaseException]]

class BackgroundTaskManager:
    """
    A simple background task manager that allows you to add tasks to a queue and run them in the background.
    """

    def __init__(self, max_attempts: int, backoff_secs: float) -> None:
        self.tasks: deque[Callable[[], None]] = deque()
        self.dead_letter: deque[tuple[Callable[[], None], int, BaseException]] = deque()
        self.max_attempts: int = max_attempts
        self.backoff_secs: float = backoff_secs
        self._stop_event = threading.Event()
        self.main_thread: threading.Thread | None = None
        self.dead_letter_thread: threading.Thread | None = None

    def put_task(self, task: Callable[[], None]) -> None:
        """
        Add a task to the queue.

        :param task: A callable representing the task to be executed.
        """
        self.tasks.append(task)


    def _run_main_loop(self) -> None:
        """
        Run the main loop that executes tasks in the queue.
        """
        while not self._stop_event.is_set():
            if self.tasks:
                task: Callable[[], None] = self.tasks.popleft()
                try:
                    task()
                except Exception as e:  # noqa: BLE001
                    print(f"Error running task: {e}")
                    if not self._stop_event.is_set():
                        self.dead_letter.append((task, 1, e))
                        self._stop_event.wait(self.backoff_secs)
            else:
                break

    def _run_dead_letter_loop(self) -> None:
        """
        Run the loop that executes tasks in the dead letter queue.
        """
        while not self._stop_event.is_set():
            if self.dead_letter:
                task, attempts, _ = self.dead_letter.popleft()

                if attempts > self.max_attempts:
                    print(f"Task {task} exceeded max attempts. Discarding.")
                    continue

                try:
                    task()
                except Exception as e:
                    print(f"Error running dead letter task: {e}")
                    if not self._stop_event.is_set():
                        self.dead_letter.append((task, attempts + 1, e))
                        self._stop_event.wait(self.backoff_secs)
            else:
                break




    def run_tasks(self):
        """
        Run all tasks in the queue.
        """

        self.main_thread = threading.Thread(target=self._run_main_loop)
        self.dead_letter_thread = threading.Thread(target=self._run_dead_letter_loop)
        self.main_thread.start()
        self.dead_letter_thread.start()


    def close(self) -> DeadLetterState:
        """
        Close the task manager and clean up resources.
        """
        self._stop_event.set()
        self.tasks.clear()

        dead_letter_state: list[tuple[str, int, BaseException]] = []
        for task, attempts, exception in self.dead_letter:
            dead_letter_state.append((str(task), attempts, exception))

        self.dead_letter.clear()


        current_thread: threading.Thread = threading.current_thread()
        for thread in (self.main_thread, self.dead_letter_thread):
            if thread is not None and thread is not current_thread and thread.ident is not None:
                thread.join()

        return dead_letter_state
