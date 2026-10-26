import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession


def test_sqlalchemy_dependency_is_importable() -> None:
    assert hasattr(sa, "Column")
    assert AsyncSession is not None
