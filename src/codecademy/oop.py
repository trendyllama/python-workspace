"""Object-oriented programming examples."""


class School:
    """

    Example:
    >>> s = School("Hill", "High", 100)
    >>> s.name
    'Hill'
    >>> s.level
    'High'
    >>> s.number_of_students
    100
    >>> s.__repr__()
    'A High school named Hill with 100 students'
    """

    def __init__(self, name: str, level: str, number_of_students: int):
        self.name = name
        self.level = level
        self.number_of_students = number_of_students

    def __repr__(self):
        return f"A {self.level} school named {self.name} with {self.number_of_students} students"


class PrimarySchool(School):
    """
    Example:
    >>> p = PrimarySchool("Wyndcroft", 500, "Parents only")
    >>> p.name
    'Wyndcroft'
    >>> p.level
    'primary'
    >>> p.number_of_students
    500
    """

    def __init__(self, name: str, number_of_students: int, pickup_policy: str):
        super().__init__(name, "primary", number_of_students)
        self.pickupPolicy = pickup_policy

    def get_pp(self):
        return self.pickupPolicy

    def __repr__(self):
        return super().__repr__()


class HighSchool(School):
    """

    Example:
    >>> h = HighSchool("Lawrenceville", 100, ["Soccer", "Track", "Hockey"])
    >>> h.name
    'Lawrenceville'
    >>> h.level
    'High'
    >>> h.number_of_students
    100
    >>> h.sports_teams
    ['Soccer', 'Track', 'Hockey']
    >>> h.__repr__()
    "We offer ['Soccer', 'Track', 'Hockey'] as extra ciricular sports"
    """

    def __init__(self, name: str, number_of_students: int, sports_teams: list[str]):
        super().__init__(name, "High", number_of_students)
        self.sports_teams = sports_teams

    def get_st(self):
        return self.sports_teams

    def __repr__(self):
        return f"We offer {self.sports_teams} as extra ciricular sports"
