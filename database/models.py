from sqlalchemy import Column, Integer, String, Boolean, func, Table, UniqueConstraint, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())  # Исправлено на 'created_at'
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    totp_secret = Column(String, nullable=True)
    confirmed = Column(Boolean, default=False)

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
