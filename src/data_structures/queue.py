# This file contains the implementation of a queue data structure
# using the Node class from src/data_structures/node.py
from src.data_structures.node import Node

from .exceptions import EmptyQueueError


class Queue[T]:
    """
    - codecademy implementation of a queue
    """

    def __init__(self) -> None:
        """
        - initializes a queue as empty by default

        Examples:
        >>> queue = Queue()
        >>> queue.head
        >>> queue.tail
        >>> queue.size
        0
        >>> queue.is_empty
        True
        >>> queue.enqueue(1)
        >>> queue.enqueue(2)
        >>> queue.enqueue(3)
        >>> queue.size
        3
        >>> queue.head.value
        1
        >>> queue.tail.value
        3

        """
        self.head: Node[T] | None = None
        self.tail: Node[T] | None = None
        self.size: int = 0
        self._iter_node: Node[T] | None = None

    @property
    def is_empty(self) -> bool:
        """
        - returns True if the queue is empty, False otherwise

        Examples:
        >>> queue = Queue()
        >>> queue.is_empty
        True
        >>> queue.enqueue(1)
        >>> queue.is_empty
        False
        """
        return bool(self.head is None and self.tail is None)

    def _increase_size(self):
        """

        - increases the size of the queue by 1

        Examples:
        >>> queue = Queue()
        >>> queue.size
        0
        >>> queue.enqueue(1)
        >>> queue.size
        1
        """
        self.size += 1

    def _decrease_size(self):
        """
        - decreases the size of the queue by 1

        Examples:
        >>> queue = Queue()
        >>> queue.enqueue(1)
        >>> queue.size
        1
        >>> queue.dequeue()
        >>> queue.size
        0
        """
        self.size -= 1

    def enqueue(self, value: T) -> None:
        """
        - adds a node to the end of the queue

        Examples:
        >>> queue = Queue()
        >>> queue.enqueue(1)
        >>> queue.enqueue(2)
        >>> queue.enqueue(3)
        >>> queue.size
        3
        >>> queue.head.value
        1
        >>> queue.tail.value
        3
        """
        if self.is_empty:
            new_node = Node(value, None, None)

            self.head = new_node

            self.tail = new_node

            self._increase_size()

            return

        if self.size == 1:
            new_node = Node(value, self.head, None)

            self.tail = new_node

            if self.head is None:
                raise RuntimeError

            self.head.next_node = self.tail

            self._increase_size()

            return

        # this is the last node in the queue
        new_node = Node(value, self.tail, None)

        self.tail = new_node
        self._increase_size()

    def dequeue(self) -> None:
        """
        - removes the first node of the queue

        Examples:
        >>> queue = Queue()
        >>> queue.enqueue(1)
        >>> queue.enqueue(2)
        >>> queue.enqueue(3)
        >>> queue.size
        3
        >>> queue.dequeue()
        >>> queue.size
        2
        >>> queue.head.value
        2
        >>> queue.tail.value
        3
        """
        if self.is_empty:
            msg = "Cannot dequeue from an empty queue"
            raise EmptyQueueError(msg)

        if self.size == 1:
            self.head = None
            self.tail = None
            self._decrease_size()

            return

        if self.size == 2:
            self.head = self.tail
            self.tail = self.head
            self._decrease_size()

            return

        if self.head is None or self.tail is None:
            raise RuntimeError

        self.head = self.head.next_node
        self._decrease_size()

    def peek(self) -> T | None:
        """

        - returns the value of the first node in the queue

        Examples:
        >>> queue = Queue()
        >>> queue.enqueue(1)
        >>> queue.enqueue(2)
        >>> queue.enqueue(3)
        >>> queue.size
        3
        >>> queue.peek()
        1
        """
        if self.is_empty:
            msg = "Cannot peek from an empty queue"
            raise EmptyQueueError(msg)

        if self.head is None:
            raise RuntimeError

        return self.head.value

    def __len__(self):
        """
        - returns the size of the queue

        Examples:
        >>> queue = Queue()
        >>> len(queue)
        0
        >>> queue.enqueue(1)
        >>> len(queue)
        1
        """
        return self.size

    def __iter__(self):
        self._iter_node = self.head
        return self

    def __next__(self):
        if self._iter_node is None:
            raise StopIteration

        value = self._iter_node.value
        self._iter_node = self._iter_node.next_node
        return value
