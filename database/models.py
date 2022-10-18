from datetime import datetime

from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy import DateTime, Integer, BigInteger, String, Float
from sqlalchemy import create_engine, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, nullable=False)
    city = Column(String, nullable=False)
    connection_date = Column(DateTime, default=datetime.now, nullable=False)
    reports = relationship('WeatherReport', backref='report', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return self.tg_id


class WeatherReport(Base):
    __tablename__ = 'weather_reports'
    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey('Users.id'), nullable=False)
    date = Column(DateTime, default=datetime.now, nullable=False)
    temp = Column(Float, nullable=False)
    feels_like = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    presuare_mm = Column(Float, nullable=False)
    city = Column(String, nullable=False)

    def __repr__(self):
        return self.city


# Создаем движок
engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres', echo=True)
Base.metadata.create_all(engine)

# Создаем сессию
Session = sessionmaker(bind=engine)
session = Session()
