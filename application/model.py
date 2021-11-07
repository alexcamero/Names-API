from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, select, Enum
from sqlalchemy.orm import registry, relationship, Session
import click
from flask import current_app, g
from flask.cli import with_appcontext

import config

engine = create_engine(f"mysql+pymysql://{config.DATABASE_USER}:{config.DATABASE_PASSWORD}@{config.DATABASE_HOST}/{config.DATABASE_NAME}?charset=utf8mb4")

"""

metadata_obj = MetaData()

user_table = Table("user_account",
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('name', String(30)),
    Column('fullname', String)
)

address_table = Table(
    "address",
    metadata_obj,
    Column('id', Integer, primary_key = True),
    Column('user_id', ForeignKey('user_account.id'), nullable = False),
    Column('email_address', String, nullable = False)
)

metadata_obj.create_all(engine)

"""

mapper_registry = registry()
Base = mapper_registry.generate_base()

class Name(Base):
    __tablename__ = 'name'

    id = Column(Integer, primary_key = True)
    name = Column(String(50))

    data = relationship("Data", back_populates = "name")

    def __repr__(self):
        return self.name

class Location(Base):
    __tablename__ = 'location'

    id = Column(Integer, primary_key = True)
    name = Column(String(100))

    data = relationship("Data", back_populates = "location")

    def __repr__(self):
        return self.name

class Data(Base):
    __tablename__ = 'data'

    id = Column(Integer, primary_key = True)
    name_id = Column(Integer, ForeignKey('name.id'))
    location_id = Column(Integer, ForeignKey('location.id'))
    year = Column(Integer)
    value = Column(Integer)
    sex = Column(Enum('F','M'))

    name = relationship("Name", back_populates = "data")
    location = relationship("Location", back_populates = "data")

    def __repr__(self):
        return f"Data(year = {self.year}, location = {self.location!r}, name = {self.name!r}, sex = {self.sex!r}, count = {self.value})"




mapper_registry.metadata.create_all(engine)

"""

sandy = User(name = "sandy", fullname = "Sandy Cheeks")
sunny_lane = Address(email_address="sl@sl.com", user=sandy)

print(sandy)
print(sunny_lane)
print(sandy.addresses)

new_place = Address(email_address="sollll@sl.com", user=sandy)
print(sandy.addresses)
print(new_place)
print(new_place.user)
gell = User(name = "gell", fullname = "Gell Cheeks", addresses = [sunny_lane])
print(gell.addresses)
print(sunny_lane.user)
print(sandy.addresses)
print(new_place.user)
"""
