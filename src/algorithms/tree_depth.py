"""
- algos for trees
"""

from collections import deque

from src.data_structures.tree_node import TreeNode


def breadth_first_search[T](
    tree_node: TreeNode[T] | None, value: TreeNode[T]
) -> TreeNode[T] | None:
    """Return the matching node using breadth-first traversal, or ``None``."""

    if tree_node is None:
        return None

    queue = deque([tree_node])

    while queue:
        current_node = queue.popleft()

        if current_node == value:
            return current_node

        if current_node.left_child:
            queue.append(current_node.left_child)
        if current_node.right_child:
            queue.append(current_node.right_child)

    return None


def depth_first_search[T](
    tree_node: TreeNode[T] | None, value: T
) -> TreeNode[T] | None:
    """

    Examples:

    """

    msg = "This function is not implemented yet."
    raise NotImplementedError(msg)


def build_bst[T](my_list: list[T]) -> TreeNode[T] | None:
    """
    - helper function to build trees

    Examples:
    >>> my_list = [1, 2, 3, 4, 5]
    >>> tree = build_bst(my_list)
    >>> tree.value
    3
    >>> tree.left_child.value
    2
    >>> tree.right_child.value
    5
    """
    if len(my_list) == 0:
        return None

    mid_idx: int = len(my_list) // 2
    mid_val = my_list[mid_idx]

    tree_node: TreeNode[T] = TreeNode(mid_val)
    tree_node.left_child = build_bst(my_list[:mid_idx])
    tree_node.right_child = build_bst(my_list[mid_idx + 1 :])

    return tree_node
