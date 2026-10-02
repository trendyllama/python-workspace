"""
- contains stack class and exceptions related to the stack
"""

from src.data_structures.exceptions import EmptyStackError, StackOverflowError
from src.data_structures.node import Node


class Stack[T]:
    """
    - codecademy implementation of a stack
    """

    def __init__(self) -> None:
        """
        - initializes a stack as empty by default

        Examples:
        >>> stack = Stack()
        >>> stack.head
        >>> stack.size
        0
        >>> stack.is_empty
        True
        >>> stack.push(1)
        >>> stack.push(2)
        >>> stack.push(3)
        >>> stack.size
        3
        >>> stack.head.value
        3
        >>> stack.head.next_node.value
        2
        >>> stack.head.next_node.next_node.value
        1
        """
        self.size: int = 0
        self.head: Node[T] | None = None
        self.limit: int = 1000
        self._iter_node: Node[T] | None = None

    def _increase_size(self) -> None:
        self.size += 1

    def _decrease_size(self) -> None:
        self.size -= 1

    def push(self, value: T) -> None:
        """
        - adds a node to the top of the stack

        Examples:
        >>> stack = Stack()
        >>> stack.push(1)
        >>> stack.push(2)
        >>> stack.push(3)
        >>> stack.size
        3
        >>> stack.head.value
        3
        """

        if self.is_empty:
            self.head = Node(value, None)
            self._increase_size()
            return

        if self.has_space:
            item = Node(value, self.head)

            self.head = item
            self._increase_size()
            return

        raise StackOverflowError

    def pop(self) -> None:
        """
        - removes the top node of the stack

        Examples:
        >>> stack = Stack()
        >>> stack.push(1)
        >>> stack.push(2)
        >>> stack.push(3)
        >>> stack.size
        3
        >>> stack.pop()
        >>> stack.size
        2
        >>> stack.head.value
        2
        """

        if self.is_empty:
            raise EmptyStackError

        if self.size == 1:
            self.head = None
            self.size = 0
            return

        if self.head is None:
            raise RuntimeError

        self.head = self.head.next_node
        self._decrease_size()

        return

    def peek(self) -> T | None:
        """
        - returns the value of the Node at the top of the stack

        Examples:
        >>> stack = Stack()
        >>> stack.push(1)
        >>> stack.push(2)
        >>> stack.push(3)
        >>> stack.size
        3
        >>> stack.peek()
        3
        """

        if self.head is None:
            raise RuntimeError

        if not self.is_empty:
            return self.head.value

        raise EmptyStackError

    @property
    def has_space(self) -> bool:
        """
        - returns True if the stack has space to add a new node

        Examples:
        >>> stack = Stack()
        >>> stack.has_space
        True
        >>> for i in range(1000):
        ...     stack.push(i)
        >>> stack.size
        1000
        >>> stack.has_space
        False
        """
        return self.limit > self.size

    @property
    def is_empty(self) -> bool:
        """
        - returns True if the stack is empty

        Examples:
        >>> stack = Stack()
        >>> stack.is_empty
        True
        >>> stack.push(1)
        >>> stack.is_empty
        False
        """
        return self.size == 0

    def __iter__(self):
        """
        - returns an iterator for the stack

        Examples:
        >>> stack = Stack()
        >>> stack.push(1)
        >>> stack.push(2)
        >>> stack.push(3)
        >>> for value in stack:
        ...     print(value)
        3
        2
        1
        """
        self._iter_node = self.head
        return self

    def __next__(self):
        """

        - returns the next value in the stack


        """

        if self._iter_node is None:
            raise StopIteration
        value = self._iter_node.value
        self._iter_node = self._iter_node.next_node
        return value

    def __str__(self) -> str:
        """
        - returns the string representation of the stack

        Examples:
        >>> stack = Stack()
        >>> stack.push(1)
        >>> stack.push(2)
        >>> stack.push(3)
        >>> print(stack)
        3 -> 2 -> 1
        """
        return " -> ".join(map(str, self))

    def __len__(self) -> int:
        """
        - returns the length of the stack

        Examples:
        >>> stack = Stack()
        >>> stack.push(1)
        >>> stack.push(2)
        >>> stack.push(3)
        >>> len(stack)
        3
        """
        return self.size
