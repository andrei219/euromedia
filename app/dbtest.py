

from sqlalchemy import create_engine, event, insert, select, update, delete, and_
from sqlalchemy.sql import func, exists
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine('mysql+mysqlconnector://root:hnq#4506@localhost:3306/appdb', echo=True) 


Session = scoped_session(sessionmaker(bind=engine, autoflush=False))
session = Session() 

from datetime import datetime

from sqlalchemy import ( 
    Table, Column, Integer, String, Enum, DateTime, 
    ForeignKey, UniqueConstraint, SmallInteger, Boolean, LargeBinary,
    Date, CheckConstraint, Numeric
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref


Base = declarative_base()


class Parent(Base):

    __tablename__ = 'parents'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    children = relationship('Child', backref='parent', \
        cascade='delete-orphan, save-update, delete')

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"{class_name}(id={self.id}, name='{self.name}')"

    def __init__(self, name):
        self.name = name 

class Child(Base):

    __tablename__ = 'children'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('parents.id'))
    name = Column(String(50), nullable=False)


    def __init__(self, name):
        self.name = name 

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"{class_name}(id={self.id}, parent_id = {self.parent_id}, name='{self.name}')"


def inspect(object):

    print(object)

    from sqlalchemy import inspect
    insp = inspect(object)
    for state in ['transient', 'pending','persistent', 'deleted', 'detached']:
        print('{:>10}:{}'.format(state, getattr(insp, state)))


from sqlalchemy import event

@event.listens_for(session, 'transient_to_pending')
def object_is_pending(session, object):
    print('new pending %s' %object)


@event.listens_for(Base, "init", propagate=True)
def intercept_init(instance, args, kwargs):
    print("new transient: %s" % instance)


@event.listens_for(session, "pending_to_persistent")
def intercept_pending_to_persistent(session, object_):
    print("pending to persistent: %s" % object_)


@event.listens_for(session, "pending_to_transient")
def intercept_pending_to_transient(session, object_):
    print("pending to transient: %s" % object_)


@event.listens_for(session, "loaded_as_persistent")
def intercept_loaded_as_persistent(session, object_):
    print("object loaded into persistent state: %s" % object_)


@event.listens_for(session, "persistent_to_deleted")
def intercept_persistent_to_deleted(session, object_):
    print("object was DELETEd, is now in deleted state: %s" % object_)


@event.listens_for(session, "deleted_to_detached")
def intercept_deleted_to_detached(session, object_):
    print("deleted to detached: %s" % object_)


@event.listens_for(session, "persistent_to_detached")
def intercept_persistent_to_detached(session, object_):
    print("object became detached: %s" % object_)



@event.listens_for(session, "detached_to_persistent")
def intercept_detached_to_persistent(session, object_):
    print("object became persistent again: %s" % object_)


@event.listens_for(session, "deleted_to_persistent")
def intercept_deleted_to_persistent(session, object_):
    print("deleted to persistent: %s" % object_)

Base.metadata.create_all(engine) 

if __name__ == '__main__':

    p = Parent('p1')

    p.children.append(Child('c1'))  
    p.children.append(Child('c2'))
    p.children.append(Child('c3'))

    session.add(p)

    session.commit() 