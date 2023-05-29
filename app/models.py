from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    region = Column(String)
    origin_coord = Column(Geometry(geometry_type='POINT', srid=4326))
    destination_coord = Column(Geometry(geometry_type='POINT', srid=4326))
    datetime = Column(DateTime)
    datasource = Column(String)

class GroupedTrip(Base):
    __tablename__ = "grouped_trips"

    id = Column(Integer, primary_key=True, index=True)
    region = Column(String)
    origin_coord = Column(Geometry(geometry_type='POINT', srid=4326))
    destination_coord = Column(Geometry(geometry_type='POINT', srid=4326))
    time_group = Column(Integer)
    average_hour = Column(Float)
    count = Column(Integer)

