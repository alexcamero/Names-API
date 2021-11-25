from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import registry, relationship

mapper_registry = registry()
Base = mapper_registry.generate_base()

class Name(Base):
    __tablename__ = 'name'

    id = Column(Integer, primary_key = True)
    name = Column(String(50), unique = True)

    data = relationship("Data", back_populates = "name")

    def __repr__(self):
        return self.name

class Location(Base):
    __tablename__ = 'location'

    id = Column(Integer, primary_key = True)
    name = Column(String(100), unique = True)

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