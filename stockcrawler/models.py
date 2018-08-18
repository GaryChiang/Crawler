from sqlalchemy import BigInteger, CHAR, Column, DECIMAL, Date, DateTime, String
from sqlalchemy.dialects.mssql.base import BIT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Company(Base):
    __tablename__ = 'Company'

    UID = Column(CHAR(36, 'Chinese_Taiwan_Stroke_CI_AS'), primary_key=True)
    Name = Column(String(50, 'Chinese_Taiwan_Stroke_CI_AS'))
    StockID = Column(String(50, 'Chinese_Taiwan_Stroke_CI_AS'), unique=True)
    Market = Column(String(50, 'Chinese_Taiwan_Stroke_CI_AS'))
    Start = Column(Date)
    Type = Column(String(50, 'Chinese_Taiwan_Stroke_CI_AS'), index=True)
    Category = Column(String(50, 'Chinese_Taiwan_Stroke_CI_AS'))
    CreateDate = Column(DateTime)
    CreateUser = Column(String(255, 'Chinese_Taiwan_Stroke_CI_AS'))


class CrawlerLog(Base):
    __tablename__ = 'CrawlerLog'

    UID = Column(CHAR(36, 'Chinese_Taiwan_Stroke_CI_AS'), primary_key=True)
    FunName = Column(String(45, 'Chinese_Taiwan_Stroke_CI_AS'), index=True)
    Param1 = Column(String(45, 'Chinese_Taiwan_Stroke_CI_AS'))
    Param2 = Column(String(45, 'Chinese_Taiwan_Stroke_CI_AS'))
    Param3 = Column(String(45, 'Chinese_Taiwan_Stroke_CI_AS'))
    Type = Column(String(45, 'Chinese_Taiwan_Stroke_CI_AS'))
    Msg = Column(String(collation='Chinese_Taiwan_Stroke_CI_AS'))
    CreateTime = Column(DateTime)
    CreateUser = Column(String(45, 'Chinese_Taiwan_Stroke_CI_AS'))


class Price(Base):
    __tablename__ = 'Price'

    UID = Column(CHAR(36, 'Chinese_Taiwan_Stroke_CI_AS'), primary_key=True)
    Date = Column(Date, index=True)
    StockID = Column(String(50, 'Chinese_Taiwan_Stroke_CI_AS'), index=True)
    Open = Column(DECIMAL(8, 2))
    Close = Column(DECIMAL(8, 2))
    High = Column(DECIMAL(8, 2))
    Low = Column(DECIMAL(8, 2))
    Change = Column(DECIMAL(8, 2))
    Transaction = Column(BigInteger)
    Capacity = Column(BigInteger)
    Turnover = Column(BigInteger)
    CreateDt = Column(DateTime)
    CreateUser = Column(String(50, 'Chinese_Taiwan_Stroke_CI_AS'))


class TimeSeries(Base):
    __tablename__ = 'TimeSeries'

    UID = Column(CHAR(36, 'Chinese_Taiwan_Stroke_CI_AS'), primary_key=True)
    Series = Column(CHAR(8, 'Chinese_Taiwan_Stroke_CI_AS'), unique=True)
    Execute = Column(BIT)
