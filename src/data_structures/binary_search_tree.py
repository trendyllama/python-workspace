"""

If the new value is less than the root node's value
  If a left child node does not exist
    Create a new BinarySearchTree with the new value and updated depth and assign it to the left pointer
  Else
    Recursively call .insert() on the left child node
Else
  If a right child node does not exist
    Create a new BinarySearchTree with the new value and updated depth and assign it to the right pointer
  Else
    Recursively call .insert() on the right child node

Insert 50
50 < 100, left child node doesn't exist, create a left child node with value 50 and depth 2

    ==> 100
       /
      50

Insert 125
125 > 100, right child node doesn't exist, create a right child node with value 125 and depth 2

    ==> 100
       /   \
      50    125

Insert 75
75 < 100, left child node with value 50 exists, recursively insert at left child

    ==> 100
       /   \
      50    125

75 > 50, right child node doesn't exist, create a right child node with value 75 and depth 3

        100
       /   \
  ==> 50    125
       \
       75

Insert 25
25 < 100, left child node with value 50 exists, recursively insert at left child

    ==> 100
       /   \
      50    125
        \
        75

25 < 50, left child node doesn't exist, create a left child node with value 25 and depth 3

        100
       /   \
  ==> 50    125
     /  \
    25  75


"""

import logging
import random
from typing import Any, Protocol


class IsOrdered(Protocol):
    def __lt__(self, other: Any, /) -> bool: ...
    def __eq__(self, other: object, /) -> bool: ...
    def __ge__(self, other: Any, /) -> bool: ...
    def __gt__(self, other: Any, /) -> bool: ...


logger = logging.getLogger(__name__)


class BinarySearchTree[T: IsOrdered]:
    def __init__(self, value: T, depth: int = 1):
        self.value = value
        self.depth = depth
        self.left = None
        self.right = None

    def insert(self, value: T):
        if value < self.value:
            if self.left is None:
                self.left = BinarySearchTree(value, self.depth + 1)
                logger.info(
                    "Tree node %s added to the left of %s at depth %s",
                    value,
                    self.value,
                    self.depth + 1,
                )
            else:
                self.left.insert(value)
        else:
            match self.right:
                case None:
                    self.right = BinarySearchTree(value, self.depth + 1)
                    logger.info(
                        "Tree node %s added to the right of %s at depth %s",
                        value,
                        self.value,
                        self.depth + 1,
                    )
                case _:
                    self.right.insert(value)

    def get_node_by_value(self, value: T):
        if self.value == value:
            return self
        elif (self.left is not None) and (value < self.value):
            return self.left.get_node_by_value(value)
        elif (self.right is not None) and (value >= self.value):
            return self.right.get_node_by_value(value)
        else:
            return None

    def depth_first_traversal(self):
        if self.left is not None:
            self.left.depth_first_traversal()

        logger.info("Depth=%s, Value=%s", self.depth, self.value)

        if self.right is not None:
            self.right.depth_first_traversal()


if __name__ == "__main__":
    # Example usage
    logger.info("Creating Binary Search Tree rooted at value 100:")
    tree = BinarySearchTree[int](100)

    for _x in range(10):
        tree.insert(random.randint(0, 100))

    logger.info("logger.infoing the inorder depth-first traversal:")
    tree.depth_first_traversal()
