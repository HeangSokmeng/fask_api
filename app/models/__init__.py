from sqlalchemy.orm import declarative_base

from .base_migration import BaseMixin

Base = declarative_base(cls=BaseMixin)
