"""
- contains doubly linked list class
"""

import logging
from collections.abc import Hashable

from .linked_list import LinkedList
from .node import Node

logger = logging.getLogger(__name__)


class HashMap[U: Hashable, V]:
    """
    - codecademy implementation of a hashmap
    """

    def __init__(self, size: int) -> None:
        self._array_size = size
        self._array = [LinkedList() for _ in range(size)]

    @property
    def array_size(self) -> int:
        logger.debug("Getting array size: %s", self._array_size)
        return self._array_size

    @property
    def array(self) -> list:
        return self._array

    def hash(self, key: U) -> int:
        hash_code = hash(key)
        logger.debug("Hash code for key %s: %s", key, hash_code)
        return hash_code

    def compress(self, hash_code: int) -> int:
        return hash_code % self.array_size

    def assign(self, key: U, value: V) -> None:
        payload = Node([key, value])
        hash_code = self.hash(key)
        array_index = self.compress(hash_code)
        list_at_array = self.array[array_index]

        for i in list_at_array:
            if i[0] == key:
                i[1] = value

        list_at_array.insert(payload)

    def retrieve(self, key: U) -> V | None:
        hash_code: int = self.hash(key)
        logger.debug("Hash code for key %s: %s", key, hash_code)
        array_index: int = self.compress(hash_code)
        logger.debug("Array index for key %s: %s", key, array_index)
        list_at_index = self.array[array_index]

        for item in list_at_index:
            logger.debug("Checking key: %s", item[0])
            if item[0] == key:
                return item[1]
        return None
