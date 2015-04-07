from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

from sqlalchemy import Table, Column, ForeignKey, String, Integer, Date
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative  import declarative_base


#config and init seccion
engine = create_engine("postgresql+psycopg2://silpy:silpypass@localhost/silpy")
Session = sessionmaker(bind=engine)

#model section
Base = declarative_base()

association_table = Table('parlamentario_camara', Base.metadata,
    Column('parlamentario_id', Integer, ForeignKey('parlamentario.id')),
    Column('camara_id', Integer, ForeignKey('camara.id'))
)

class Parlamentario(Base):
    #Member of parliament
    __tablename__ = 'parlamentario'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    partido = Column(String)#TODO: extract from name
    camaras = relationship("Camara",
                           secondary=association_table,
                           backref="parlamentarios")
    
class Camara(Base):
    #camara alta o baja en un periodo dado
    __tablename__ = 'camara'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    periodo = periodo = Column(String)#Column(DateTime)
    

class Comision(Base):
    __tablename__ = 'comision'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    folder = Column(String)#unique, maybe primary key


class Proyecto(Base):
    __tablename__ = 'projecto'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
session = Session()
# ed_user = User(name='ed', fullname='Ed Jones', password='edspassword')
# session.add(ed_user)
# our_user = session.query(User).filter_by(name='ed').first() 
#session.commit()
#print our_user
