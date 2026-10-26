from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str

# 1. The Abstract Repository Interface
class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    def add(self, user: User) -> None:
        pass

# 2. A Concrete Implementation (e.g., for testing or local development)
class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._users: list[User] = []

    def get_by_id(self, user_id: int) -> User | None:
        return next((u for u in self._users if u.id == user_id), None)

    def add(self, user: User) -> None:
        self._users.append(user)

# 3. The Business Logic (Service Layer)
class UserService:
    def __init__(self, repo: UserRepository):
        self.repo: UserRepository = repo

    def register_user(self, user_id: int, name: str) -> User:
        user = User(id=user_id, name=name)
        self.repo.add(user)
        return user

# Usage
repo = InMemoryUserRepository()
service = UserService(repo)

service.register_user(1, "Alice")
user: User | None = repo.get_by_id(1)

assert user is not None

print(f"Found user: {user.name}")
