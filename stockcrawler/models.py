from sqlalchemy import CHAR, Column, DateTime, SMALLINT, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Company(Base):
    __tablename__ = 'Company'

    Guid = Column(CHAR(36, 'utf8_unicode_ci'), primary_key=True)
    Name = Column(String(50, 'utf8_unicode_ci'))
    StockID = Column(SMALLINT(6))
    CreateDate = Column(DateTime)
    CreateUser = Column(String(255, 'utf8_unicode_ci'))
