import configparser
from sqlalchemy import create_engine
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import (
    relationship,
)

cp = configparser.ConfigParser()
cp.read('site.cfg');

(db_name, db_user, db_pass) = map(lambda x: cp.get('db', x), ('db', 'user', 'pass'))
conn_string = 'mysql+mysqlconnector://{db_user}:{db_pass}@/{db_name}?unix_socket=/var/lib/mysql/mysql.sock'

engine = create_engine(conn_string.format(db_user=db_user, db_pass=db_pass, db_name=db_name),
                       echo=False, pool_recycle=7200)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class BaseMixin:
    def to_dict(self):
        return dict((self, getattr(self, col)) for col in self.__table__.columns.keys())


class User(BaseMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(75), nullable=False)
    hash = Column(String(32), nullable=False, index=True, unique=True)
    name = Column(String(64), nullable=False)
    presence = Column(Integer) # 0-100
    V = Column(Integer)
    S = Column(Integer)
    D = Column(Integer)
    L = Column(Integer)
    first_visit = Column(Boolean)
    viewed_comments = relationship("CommentViews")
    viewed_bodies = relationship("BodyViews")
    comments = relationship("Comment", backref="user")

    def presence(self):
        return [(d, getattr(self,d)) for d in "VSDL"]

    def to_dict(self):
        return {
            'name': self.name,
            'presence' : (
                ('V', self.V),
                ('S', self.S),
                ('D', self.D),
                ('L', self.L),
            ),
            'answer': not (self.S is None and self.V is None and self.D is None and self.L is None)
        }


class Comment(BaseMixin, Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(140))
    comment = Column(Text)
    created = Column(DateTime, index=True)
    updated = Column(DateTime)
    last_response = Column(DateTime, index=True)
    original = Column(Integer, ForeignKey('comments.id'), index=True)
    replies = relationship("Comment")

class Body(BaseMixin, Base):
    __tablename__ = 'bodies'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created = Column(DateTime)
    body = Column(Text)


class BodyViews(BaseMixin, Base):
    __tablename__ = 'body_views'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    body_id = Column(Integer, ForeignKey('bodies.id'), primary_key=True)

class CommentViews(BaseMixin, Base):
    __tablename__ = 'comment_views'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    comment_id = Column(Integer, ForeignKey('comments.id'), primary_key=True)

def to_dict(model):
    return model.to_dict()

def create_all():
    Base.metadata.create_all(engine)
    
