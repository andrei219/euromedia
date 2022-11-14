

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey

from sqlalchemy import create_engine

DATABASE_URL = 'mysql+mysqlconnector://root:hnq#4506@localhost:3306/manymanydb'

engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine, autoflush=False)
session = Session()


Base = declarative_base()


class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    age = Column(String, nullable=False)

    def __init__(self, name, age):
        self.name = name
        self.age = age


class ManyMany(Base):

    __tablename__ = 'many_manies'

    followed_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    follower_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

    data = Column(String(255), nullable=False)


if __name__ == '__main__':

    session.add_all([
        User('Andrei', 27),
        User('Manuel', 22),
        User('Juan', 11)

    ])

    session.commit()

