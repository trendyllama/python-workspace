import pytest

from src.algorithms.tree_depth import (
    breadth_first_search,
    build_bst,
    depth_first_search,
)
from src.data_structures.tree_node import TreeNode


def test_breadth_first_search_finds_root_and_children() -> None:
    root = TreeNode(4)
    left_child = TreeNode(2)
    right_child = TreeNode(6)
    root.add_child(left_child, "left")
    root.add_child(right_child, "right")

    assert breadth_first_search(root, root) is root
    assert breadth_first_search(root, left_child) is left_child
    assert breadth_first_search(root, right_child) is right_child


def test_breadth_first_search_returns_none_for_empty_or_missing_nodes() -> None:
    root = TreeNode(4)
    root.add_child(TreeNode(2), "left")

    assert breadth_first_search(None, root) is None
    assert breadth_first_search(root, TreeNode(8)) is None


def test_build_bst_returns_none_for_empty_list() -> None:
    assert build_bst([]) is None


def test_build_bst_builds_balanced_tree() -> None:
    root = build_bst([1, 2, 3, 4, 5])

    assert root is not None
    assert root.value == 3
    assert root.left_child is not None
    assert root.left_child.value == 2
    assert root.left_child.left_child is not None
    assert root.left_child.left_child.value == 1
    assert root.left_child.right_child is None
    assert root.right_child is not None
    assert root.right_child.value == 5
    assert root.right_child.left_child is not None
    assert root.right_child.left_child.value == 4
    assert root.right_child.right_child is None


def test_depth_first_search_is_not_implemented() -> None:
    with pytest.raises(NotImplementedError, match="not implemented"):
        depth_first_search(TreeNode(1), 1)
