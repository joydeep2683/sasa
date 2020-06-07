# from settings import *
from utils import *
# from scrapers.utils import *
from pytrends.request import TrendReq
from datetime import date, datetime, timedelta
import pandas as pd
import json
import time
# from trend.snapshot import *
# from trend.utils import *
import logging



class GoogleTrends(object):
    """format for params = {'start_date:'2019-3-25', 'perid': 5}"""
    def __init__(self, source='googletrends', country='US', params={}):
        super(GoogleTrends, self).__init__()
        """date format = '2019-3-25'"""
        import datetime
        self.country = country
        self.source = source
        if 'start_date' in params:
            self.start_date = params['start_date']
        else:
            self.start_date = datetime.date.today()
        if 'period' in params:
            self.period = params['period']
        else:
            self.period = 5  

    # convert dict to dataframe
    def convert_to_df(self, ret_df, keyword):
        dc = ret_df.to_dict()
        date = []
        value = []
        for key, val in dc[keyword].items():
            date.append(key)
            value.append(val)
        df = pd.DataFrame(
            {'date': date,
             'value': value
            })
        return df

    def get_google_proxy_list(self):
        url = 'https://www.proxydocker.com/en/api/proxylist/'
        soup = get_source(url, dynamic=False)
        if soup is not None:
            x = json.loads(soup.get_text())
            proxylist = ["https://{}:{}".format(i['ip'], i['port']) for i in x['proxies'] if i['isGoogle'] is True]
            return proxylist

    # fetch keyword wise data
    def fetch(self, keyword):
        time.sleep(2)
        ndate = self.start_date
        if isinstance(ndate, str):
            yr, mnth, day = (int(i) for i in ndate.split('-'))
        else:
            yr = ndate.year
            mnth = ndate.month
            day = ndate.day
        pytrends = TrendReq(hl='en-US', tz=360)
        # pytrends = TrendReq(hl='en-US', proxies=self.get_google_proxy_list())
        date_last_5y = date(yr, mnth, day) - timedelta(days=365*self.period)
        from_to_date_5y = '{}-{}-{} {}'.format(date_last_5y.year, date_last_5y.month, date_last_5y.day, ndate)
        pytrends.build_payload([keyword], cat=0, timeframe=from_to_date_5y, geo=self.country, gprop='')
        iot_5y = pytrends.interest_over_time()
        if 'isPartial' in iot_5y.columns:
            del iot_5y['isPartial']
            iot5yweekwise = self.convert_to_df(iot_5y, keyword)
            # time.sleep(2)
            pytrends.build_payload([keyword], cat=0, timeframe='today 3-m', geo=self.country, gprop='')
            related_topic = self.get_related_topics(pytrends, keyword)
            related_query = self.get_related_queries(pytrends, keyword)
            new_js_data = {'keyword': keyword, 'country': self.country, 'source': self.source, 'dataframe': {'dataframe': iot5yweekwise.to_json(), 'related_topic': related_topic, 'related_query': related_query}}
            # new_js_data = {'keyword': keyword, 'country': self.country, 'source': self.source, 'dataframe': iot5yweekwise.to_json()}
            return new_js_data

    def get_related_topics(self, pytrends, keyword):
        related_topic = pytrends.related_topics()
        xc = {}
        top = {}
        rising = {}
        if 'top' in related_topic[keyword] and related_topic[keyword]['top'] is not None:
            if related_topic[keyword]['top'].empty is False:
                top['title'] = related_topic[keyword]['top']['topic_title']
                top['type'] = related_topic[keyword]['top']['topic_type']
                top['value'] = related_topic[keyword]['top']['value']
        if 'rising' in related_topic[keyword] and related_topic[keyword]['rising'] is not None:
            if related_topic[keyword]['rising'].empty is False:
                rising['title'] = related_topic[keyword]['rising']['topic_title']
                rising['type'] = related_topic[keyword]['rising']['topic_type']
                rising['value'] = related_topic[keyword]['rising']['value']
        if 'value' in related_topic[keyword]:
            if max(related_topic[keyword]['value']) == 100:
                top['title'] = related_topic[keyword]['title']
                top['type'] = related_topic[keyword]['type']
                top['value'] = related_topic[keyword]['value']
            else:
                rising['title'] = related_topic[keyword]['topic_title']
                rising['type'] = related_topic[keyword]['topic_type']
                rising['value'] = related_topic[keyword]['value']
        if len(top)>0:
            xc['top'] = [{'title': top['title'][i], 'type': top['type'][i], 'value': int(top['value'][i])} for i, j in enumerate(top['type'])]
        else:
            xc['top'] = [top]
        if len(rising) > 0:
            xc['rising'] = [{'title': rising['title'][i], 'type': rising['type'][i], 'value': int(rising['value'][i])} for i, j in enumerate(rising['type'])]
        else:
            xc['rising'] = [rising]
        return xc

    
    def get_related_queries(self, pytrends, keyword):
        related_query = pytrends.related_queries()
        print(related_query)
        xc = {}
        top = {}
        rising = {}
        if 'top' in related_query[keyword] and related_query[keyword]['top'] is not None:
            if related_query[keyword]['top'].empty is False:
                top['query'] = related_query[keyword]['top']['query']
                top['value'] = related_query[keyword]['top']['value']
        if 'rising' in related_query[keyword] and related_query[keyword]['rising'] is not None:
            if related_query[keyword]['rising'].empty is False:
                rising['query'] = related_query[keyword]['rising']['query']
                rising['value'] = related_query[keyword]['rising']['value']
        if 'value' in related_query[keyword]:
            if max(related_query[keyword]['value']) == 100:
                top['query'] = related_query[keyword]['query']
                top['value'] = related_query[keyword]['value']
            else:
                rising['query'] = related_query[keyword]['query']
                rising['value'] = related_query[keyword]['value']
        if len(top)>0:
            xc['top'] = [{'query': top['query'][i], 'value': int(top['value'][i])} for i, j in enumerate(top['query'])]
        else:
            xc['top'] = [top]
        if len(rising) > 0:
            xc['rising'] = [{'query': rising['query'][i], 'value': int(rising['value'][i])} for i, j in enumerate(rising['query'])]
        else:
            xc['rising'] = [rising]
        return xc




class HotnessData(object):
    def __init__(self, source = 'googletrends_hotness', country='US'):
        super(HotnessData, self).__init__()
        self.source = source
        self.country = country



    def fetch(self, keyword):
        import datetime
        pytrends = TrendReq(hl='en-US', tz=360)
        ndate = datetime.date.today()
        yr = ndate.year
        mnth = ndate.month
        day = ndate.day
        date_last_1y = datetime.date(int(yr), int(mnth), int(day)) - datetime.timedelta(days=365)
        from_to_date_1y = '{}-{}-{} {}'.format(date_last_1y.year, date_last_1y.month, date_last_1y.day, ndate)
        kw_list = [keyword]
        pytrends.build_payload(kw_list, cat=0, timeframe=from_to_date_1y, geo=self.country, gprop='')
        d = pytrends.interest_over_time()
        if not d.empty:
            t = int(d[keyword][-2])
            if t > 70:
                nature = 'Hot'
            elif t >50 and t<=70:
                nature = 'High'
            else:
                nature = 'Medium'
            xc = {'keyword': keyword, 'source': 'googletrends', 'type': 'hotness', 'Nature': nature, 'value': int(t)}
        else:
            xc = {'keyword': keyword, 'source': 'googletrends', 'type': 'hotness', 'Nature': 'No Data', 'value': 'No Data'}
        return xc







        
        