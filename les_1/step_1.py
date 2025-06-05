from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from tabulate import tabulate

db_url = 'database.db'

engine = create_engine(f'sqlite:///{db_url}')
Base = declarative_base()


class People(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    age = Column(Integer)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id}, {self.name!r}, {self.age})'

    @property
    def is_adult(self):
        return self.age >= 18

    @property
    def greating(self):
        return f'Hello, {self.name}'

    @classmethod
    def display(cls, session):
        people = session.query(cls).all()
        people = [(p, p.is_adult, p.greating) for p in people]
        header = ['Obyekt', 'is_adult', 'greating']
        print(tabulate(people, header, tablefmt='simple_grid'))
        return people

    def save(self, session):
        session.add(self)
        session.commit()

    @classmethod
    def delete(cls, session, id_):
        obj = session.query(cls).filter(id_ == cls.id).first()
        if obj:
            session.delete(obj)
            session.commit()
            return True
        return False


Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()
print(session.query(People).all())
# p1 = People(name="Vali", age=25)
# p2 = People(name="Ali", age=17)
# p3 = People(name="Sardor", age=30)

# session.add_all([p1, p2, p3])

# print(People.display(session))
# p1 = People(name="Vali", age=25)
# p1.save(session)
# People.delete(session, 3)
