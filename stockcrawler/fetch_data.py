from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import twstock

# information
driver = 'mysql+pymysql'
user = 'vi0x734y298pbme8'
password = 'x566hqmy6u54ufms'
host = 'a5s42n4idx9husyc.cbetxkdyhwsb.us-east-1.rds.amazonaws.com'
port = '3306'
database = 'wwzwm8iuvtquwkj6'

connect_info = '{0}://{1}:{2}@{3}:{4}/{5}'.format(driver, user, password, host, port, database)

# create_engine("数据库类型+数据库驱动://数据库用户名:数据库密码@IP地址:端口/数据库"，其他参数)
engine = create_engine(connect_info)
Session = sessionmaker(bind=engine)
# Session.configure(bind=engine)  # once engine is available
session = Session()


def fetch_company():
    twse = twstock.twse  # 上市證券
    tpex = twstock.tpex  # 上櫃證券

    # for index in twse:
    #     fe = twse[index]


if __name__ == '__main__':
    fetch_company()
