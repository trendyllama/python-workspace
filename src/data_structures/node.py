"""
- only contains the Node class
"""

from typing import Self


class Node[T]:
    """
    - codecademy implementation of a node
    """

    def __init__(
        self,
        value: T,
        next_node: Self | None = None,
        prev_node: Self | None = None,
    ) -> None:
        self.value = value
        self.next_node = next_node
        self.previous_node = prev_node

    def __str__(self) -> str:
        return f"Node(value={self.value})"
