from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from stockcrawler.models import Company, Price, CrawlerLog, TimeSeries
import twstock
import datetime
import uuid
import time
import os
import json
import calendar
import requests
from decimal import Decimal


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
            collect = list()

            for index in twse:

                if twse[index].code in company_data:
                    continue

                company = Company(UID=str(uuid.uuid4()), Type=twse[index].type, StockID=twse[index].code,
                                  Name=twse[index].name, Category=twse[index].group, Start=twse[index].start,
                                  Market=twse[index].market, CreateDate=datetime.datetime.now())
                collect.append(company)

            for index in tpex:

                if tpex[index].code in company_data:
                    continue

                company = Company(UID=str(uuid.uuid4()), Type=tpex[index].type, StockID=tpex[index].code,
                                  Name=tpex[index].name, Category=tpex[index].group, Start=tpex[index].start,
                                  Market=tpex[index].market, CreateDate=datetime.datetime.now())
                collect.append(company)

            self.__session.commit()
        except Exception:
            self.__session.rollback()
            raise

    def fetch_history_stock_price(self):
        """
        fetch history data
        :return:
        """

        # 建立時間序列
        self.__create_series()

        # 轉檔範圍
        series = self.__session.query(TimeSeries.Series).filter(TimeSeries.Execute == 0). \
            order_by(asc(TimeSeries.Series))

        series = [value for (value,) in series]

        # 上市/上櫃 公司
        company = self.__session.query(Company.StockID).filter(Company.Type == '股票').all()

        company = [value for (value,) in company]

        for day in series:
            try:
                collect = list()
                time.sleep(1)
                # 上市
                result = requests.get(
                    'http://www.twse.com.tw/exchangeReport/MI_INDEX?'
                    'response=json&date=' + day + '&type=ALL')

                result = json.loads(result.text)

                if 'data2' in result:
                    for item in result['data2']:
                        item[2] = item[2].replace('--', '0').replace(' ', '')
                        item[3] = item[3].replace('--', '0').replace(' ', '')
                        item[4] = item[4].replace('--', '0').replace(' ', '')
                        item[5] = item[5].replace('--', '0').replace(' ', '')
                        item[8] = item[8].replace('--', '0').replace(' ', '')
                        item[10] = str(Decimal(item[5]) - Decimal(item[8]))  # 因為有除權息情況, 所以這邊用算的, 不帶入資料. 資料會有除權息的中文
                        item[6] = item[6].replace('--', '0').replace(' ', '')
                        item[7] = item[7].replace('--', '0').replace(' ', '')

                        if item[0] in company:
                            price = Price(UID=str(uuid.uuid4()), Date=datetime.datetime.strptime(day, '%Y%m%d').date(),
                                          StockID=item[0], Open=item[5].replace(',', ''),
                                          Close=item[8].replace(',', ''),
                                          High=item[6].replace(',', ''), Low=item[7].replace(',', ''),
                                          Change=item[10].replace(',', ''), Transaction=item[3].replace(',', ''),
                                          Capacity=item[2].replace(',', ''), Turnover=item[4].replace(',', ''),
                                          CreateDt=datetime.datetime.now())
                            collect.append(price)

                # 上櫃
                tw_time = self.__to_tw_time(day)
                result = requests.get(
                    'http://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?'
                    'l=zh-tw&o=json&d=' + tw_time + '&s=0,asc,0')

                result = json.loads(result.text)

                if 'aaData' in result:
                    for item in result['aaData']:
                        item[2] = item[2].replace('--', '0').replace(' ', '')
                        item[4] = item[4].replace('--', '0').replace(' ', '')
                        item[3] = str(Decimal(item[2]) - Decimal(item[4]))  # 因為有除權息情況, 所以這邊用算的, 不帶入資料. 資料會有除權息的中文
                        item[10] = item[10].replace('--', '0').replace(' ', '')
                        item[5] = item[5].replace('--', '0').replace(' ', '')
                        item[6] = item[6].replace('--', '0').replace(' ', '')
                        item[9] = item[9].replace('--', '0').replace(' ', '')
                        item[8] = item[8].replace('--', '0').replace(' ', '')
                        if item[0] in company:
                            price = Price(UID=str(uuid.uuid4()), Date=datetime.datetime.strptime(day, '%Y%m%d').date(),
                                          StockID=item[0], Open=item[4].replace(',', ''),
                                          Close=item[2].replace(',', ''),
                                          High=item[5].replace(',', ''), Low=item[6].replace(',', ''),
                                          Change=item[3].replace(',', ''), Transaction=item[10].replace(',', ''),
                                          Capacity=item[8].replace(',', ''), Turnover=item[9].replace(',', ''),
                                          CreateDt=datetime.datetime.now())
                            collect.append(price)

                self.__session.add_all(collect)
                time_series = self.__session.query(TimeSeries).filter(TimeSeries.Series == day).first()
                time_series.Execute = 1
                self.__session.commit()

            except Exception as e:
                self.__session.rollback()
                self.__log_error('fetch_history_stock_price', str(e) + '[param:' + day + ']')
                continue

    @staticmethod
    def __to_tw_time(ad_time):
        try:
            tw_time = str(int(ad_time[0:4]) - 1911) + '/' + ad_time[4:6] + '/' + ad_time[6:8]

            return tw_time
        except Exception:
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
            current = datetime.date.today()

            all_series = self.__session.query(TimeSeries.Series).all()
            all_series = [value for (value,) in all_series]

            start = self.__add_months(current, -self.duration)
            days = int((current - start).days)

            for x in range(0, days):
                series = start + datetime.timedelta(days=x)
                series = str(series.year) + str(series.month).zfill(2) + str(series.day).zfill(2)

                if series in all_series:
                    continue

                time_series = TimeSeries(UID=str(uuid.uuid4()), Series=series, Execute=0)

                self.__session.add(time_series)
                self.__session.commit()

        except Exception:
            raise
