from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import registry, relationship

engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)

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

mapper_registry = registry()
Base = mapper_registry.generate_base()

class User(Base):
    __tablename__ = 'user_account'

    id = Column(Integer, primary_key = True)
    name = Column(String(30))
    fullname = Column(String)

    addresses = relationship("Address", back_populates = "user")

    def __repr__(self):
        return f"User(id = {self.id!r}, name = {self.name!r}, fullname = {self.fullname!r})"

class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key = True)
    email_address = Column(String, nullable = False)
    user_id = Column(Integer, ForeignKey('user_account.id'))

    user = relationship("User", back_populates = "addresses")

    def __repr__(self):
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"

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

