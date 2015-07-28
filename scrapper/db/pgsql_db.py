from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

from sqlalchemy import Table, Column, ForeignKey, String, Integer, Date, CLOB
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative  import declarative_base

#config and init seccion
#engine = create_engine("postgresql+psycopg2://silpy:silpypass@localhost/silpy")
engine = create_engine('sqlite:///silpy.db')
DBSession = sessionmaker(bind=engine)

#model section
Base = declarative_base()

# association_table = Table('member_chamber', Base.metadata,
#     Column('member_id', Integer, ForeignKey('member.id')),
#     Column('chamber_id', Integer, ForeignKey('chamber.id'))
# )

class Member(Base):
    #u'index', u'committees', u'name', u'img',
    #u'phone', u'projects_body_param', u'rulings',
    #u'cv', u'email', u'link', u'party', u'_id', u'id', u'projects']

    #Member of parliament
    __tablename__ = 'member'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    party = Column(String)#TODO: extract from name
    email = Column(String)
    phone = Column(String)
    cv = Column(CLOB)
    # chamber = relationship("Chamber",
    #                        secondary=association_table,
    #                        backref="members")
    #projects relation
    #image location
    #committees relation

    
class Chamber(Base):
    #camara alta o baja en un periodo dado
    __tablename__ = 'chamber'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    period = period = Column(String)#Column(DateTime) move to a table?
    

class Committee(Base):
    __tablename__ = 'committee'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    folder = Column(String)#unique, maybe primary key


class Project(Base):
    __tablename__ = 'project'
#    'description', 'title', 'expediente', 'data', 'ingreso', 'stage'
    id = Column(Integer, primary_key=True)
    name = Column(String)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


from mongo_db import SilpyMongoClient
mongo_client = SilpyMongoClient()
session = DBSession()

senator = mongo_client.get_senador()

senators = [senator]

def save_senators(senators):
    print 'saving'
    for s in senators:
        print 'saving members %s to sql database' %(s['name'])
        m = Member()
        m.id = ['id']
        m.name = s['name']
        if 'phone' in s:
            m.phone = s['phone']
        m.img = s['img']
#        m.cv = s['cv']
        if 'email' in s:
            m.email = s['email']

        print m
            #        m.party = s['party']

        # s['projects']
        # s['committees']
        # s['rulings']
        # s['link']
        # s['projects_body_param']
        session.add(m)
        session.commit()

save_senators(senators)
#print our_user
