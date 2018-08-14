from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from stockcrawler.models import Company, Price, CrawlerLog, TimeSeries
import twstock
import datetime
import uuid
import time
import os
import json
import calendar


class FetchData:
    def __init__(self, duration: int):
        """
        init
        :param duration: fetch duration
        """

        self.__duration = duration

        # app directory
        app_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(app_dir, 'setting.json').replace('\\', '/')) as file:
            self.__setting = json.load(file)

        if 'connect' in os.environ:
            connect_info = os.environ.get('connect', None)
        else:
            # information
            driver = self.__setting['db_info']['driver']
            user = self.__setting['db_info']['user']
            password = self.__setting['db_info']['password']
            host = self.__setting['db_info']['host']
            port = self.__setting['db_info']['port']
            database = self.__setting['db_info']['database']
            connect_info = '{0}://{1}:{2}@{3}:{4}/{5}'.format(driver, user, password, host, port, database)

        # create_engine("数据库类型+数据库驱动://数据库用户名:数据库密码@IP地址:端口/数据库"，其他参数)
        engine = create_engine(connect_info)
        self.__session = sessionmaker(bind=engine, autoflush=False, autocommit=False)()

    @property
    def duration(self):
        """
        transfer duration months
        :return:
        """
        return self.__duration

    def fetch_company_info(self):
        """
        fetch all company information
        :return:
        """
        try:
            # models.metadata.create_all(engine)
            twse = twstock.twse
            tpex = twstock.tpex

            company_data = self.__session.query(Company.StockID).all()
            company_data = [value for (value,) in company_data]

            for index in twse:

                if twse[index].code in company_data:
                    continue

                company = Company(UID=str(uuid.uuid4()), Type=twse[index].type, StockID=twse[index].code,
                                  Name=twse[index].name, Category=twse[index].group, Start=twse[index].start,
                                  Market=twse[index].market, CreateDate=datetime.datetime.now())
                self.__session.add(company)

            for index in tpex:

                if tpex[index].code in company_data:
                    continue

                company = Company(UID=str(uuid.uuid4()), Type=tpex[index].type, StockID=tpex[index].code,
                                  Name=tpex[index].name, Category=tpex[index].group, Start=tpex[index].start,
                                  Market=tpex[index].market, CreateDate=datetime.datetime.now())
                self.__session.add(company)

            self.__session.commit()
        except Exception:
            raise

    def fetch_history_stock_price(self):
        """
        fetch history data
        :return:
        """
        try:
            # 建立時間序列
            self.__create_series()
            # 當月及上個月必須重轉, 無論是否已經轉過
            start = datetime.date.today()
            current_month = str(start.year) + str(start.month).zfill(2)
            last_month = self.__add_months(start, -1)
            last_month = str(last_month.year) + str(last_month.month).zfill(2)

            # # delete overlay part
            # delete_duration = self.__add_months(start, -self.duration)

            # query all need transfer companies
            company = self.__session.query(Company.StockID).filter(Company.Type == '股票')

            for item in company:
                # init instance
                stock = twstock.Stock(item.StockID, False)

                # check log, if this period has been executed, pass this loop
                log_history = self.__session.query(CrawlerLog.Param2).filter(
                    CrawlerLog.FunName == 'fetch_history_stock_price',
                    CrawlerLog.Type == 'info',
                    CrawlerLog.Param2 != current_month,
                    CrawlerLog.Param2 != last_month,
                    CrawlerLog.Param1 == item.StockID).all()

                log_history = [value for (value,) in log_history]

                time_series = self.__session.query(TimeSeries.Series).filter(
                    TimeSeries.Series.notin_(log_history)).all()

                time_series = [value for (value,) in time_series]

                for x in time_series:
                    try:
                        data = stock.fetch(int(x[0:4]), int(x[4:6]))
                    except ValueError:
                        continue

                    time.sleep(5)
                    for day in data:
                        # delete all this stock history price
                        self.__session.query(Price).filter(Price.Date == day.date,
                                                           Price.StockID == item.StockID).delete()

                        price = Price(UID=str(uuid.uuid4()), Date=day.date, StockID=item.StockID, Open=day.open,
                                      Close=day.close, High=day.high, Low=day.low, Change=day.change,
                                      Transaction=day.transaction, Capacity=day.capacity, Turnover=day.turnover,
                                      CreateDt=datetime.datetime.now())
                        self.__session.add(price)
                    self.__log('fetch_history_stock_price', item.StockID, x, 'info')
                    self.__session.commit()

        except Exception as e:
            self.__session.rollback()
            self.__log_error('fetch_history_stock_price', str(e))
            raise

    def execute(self):
        """
        execute fetch batch
        :return:
        """
        try:
            company = self.__setting['fetch_setting']['company']
            price = self.__setting['fetch_setting']['price']

            if company:
                self.fetch_company_info()

            if price:
                self.fetch_history_stock_price()
        except Exception:
            raise

    @staticmethod
    def __add_months(sourcedate, months):
        try:
            month = sourcedate.month - 1 + months
            year = sourcedate.year + month // 12
            month = month % 12 + 1
            day = min(sourcedate.day, calendar.monthrange(year, month)[1])
            return datetime.date(year, month, day)
        except Exception:
            raise

    def __log(self, name, param1, param2, log_type):
        try:
            # 先刪除
            self.__session.query(CrawlerLog).filter(CrawlerLog.Param1 == param1, CrawlerLog.Param2 == param2).delete()

            log = CrawlerLog(UID=str(uuid.uuid4()), FunName=name,
                             Param1=param1,
                             Param2=param2, Type=log_type,
                             CreateTime=datetime.datetime.now())

            # 新增
            self.__session.add(log)
        except Exception:
            raise

    def __log_error(self, name, message):
        try:
            log = CrawlerLog(UID=str(uuid.uuid4()), FunName=name, Type='error',
                             Msg=message, CreateTime=datetime.datetime.now())

            # 新增
            self.__session.add(log)
            self.__session.commit()
        except Exception:
            raise

    def __create_series(self):
        """
        建立時間序列
        :return:
        """
        try:
            start = datetime.date.today()

            all_series = self.__session.query(TimeSeries.Series).all()
            all_series = [value for (value,) in all_series]

            for x in range(0, self.duration):
                series = self.__add_months(start, -x)
                series = str(series.year) + str(series.month).zfill(2)

                if series in all_series:
                    continue

                time_series = TimeSeries(UID=str(uuid.uuid4()), Series=series)

                self.__session.add(time_series)
                self.__session.commit()

        except Exception:
            raise

