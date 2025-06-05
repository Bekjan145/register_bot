from sqlalchemy import (create_engine, Column, Integer, String,
                        Text, ForeignKey)

from data.config import db_user, password, host, port, db_name
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

pg_url = f"postgresql+psycopg2://{db_user}:{password}@{host}:{port}/{db_name}"
engine = create_engine(pg_url)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    age = Column(Integer)
    posts = relationship('Post', back_populates='user', cascade="all, delete-orphan")

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id}, {self.name!r})'


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, unique=True)
    content = Column(Text)
    user_id = Column(Integer,  ForeignKey('users.id'))

    user = relationship('User', back_populates='posts')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id}, {self.title!r})'


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# user1 = User(name='Alex')
# session.add(user1)
# session.commit()
# post1 = Post(title='My 5 day', content='My 5 day content', user_id=user1.id)
# post2 = Post(title='My 6 day', content='My 6 day content', user_id=user1.id)
#
# session.add_all([post1, post2])
# session.commit()

#
# users = session.query(User).all()
#
# for user in users:
#     print(f"{user.name}: {user.posts}")


# posts = session.query(Post).all()
#
# for post in posts:
#     print(f"{post.title}: {post.user}")


# user = session.query(User).filter_by(name='Ali').first()

