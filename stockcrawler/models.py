from sqlalchemy import CHAR, Column, Date, DateTime, Float, INTEGER, String, Text, BIGINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Company(Base):
    __tablename__ = 'Company'

    UID = Column(CHAR(36), primary_key=True)
    Name = Column(String(50))
    StockID = Column(String(50), unique=True)
    Market = Column(String(50))
    Start = Column(Date)
    Type = Column(String(50), index=True)
    Category = Column(String(50))
    CreateDate = Column(DateTime)
    CreateUser = Column(String(255))


class CrawlerLog(Base):
    __tablename__ = 'CrawlerLog'

    UID = Column(CHAR(36), primary_key=True)
    FunName = Column(String(45), index=True)
    Param1 = Column(String(45))
    Param2 = Column(String(45))
    Param3 = Column(String(45))
    Type = Column(String(45))
    Msg = Column(Text)
    CreateTime = Column(DateTime)
    CreateUser = Column(String(45))


class Price(Base):
    __tablename__ = 'Price'

    UID = Column(CHAR(36), primary_key=True)
    Date = Column(Date, index=True)
    StockID = Column(String(50), index=True)
    Open = Column(Float)
    Close = Column(Float)
    High = Column(Float)
    Low = Column(Float)
    Change = Column(Float)
    Transaction = Column(INTEGER)
    Capacity = Column(INTEGER)
    Turnover = Column(BIGINT)
    CreateDt = Column(DateTime)
    CreateUser = Column(String(50))


class TimeSeries(Base):
    __tablename__ = 'TimeSeries'

    UID = Column(CHAR(36), primary_key=True)
    Series = Column(CHAR(6), unique=True)
