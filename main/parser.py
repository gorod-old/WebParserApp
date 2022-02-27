import threading
import uuid
from random import uniform

import requests
import schedule
from time import sleep
from bs4 import BeautifulSoup as Bs

from main.g_spreadsheets import get_spreadsheet_id, get_service, get_data_from_sheet, get_range, add_text_to_sheet
from main.models import WorkTable

parser_info = {}


def check_parser():
    spreadsheet = check_spreadsheet_in_db()
    if parser_info.get('parser') is None and spreadsheet:
        Parser(spreadsheet).start()
        print('ProjSetup: start parser')


def check_spreadsheet_in_db(spreadsheet=None):
    try:
        obj = WorkTable.objects.all()[0]
        if spreadsheet is not None:
            obj.spreadsheet = spreadsheet
            obj.save()
        spreadsheet = obj.spreadsheet
    except Exception as e:
        print(str(e))
        if spreadsheet is not None:
            obj = WorkTable(spreadsheet=spreadsheet)
            obj.save()
    return spreadsheet


def delete_spreadsheet_from_db():
    try:
        WorkTable.objects.all()[0].delete()
    except Exception as e:
        print(str(e))


def get_request_data(url: str, random_wait: tuple = (.01, .05)):
    """Receiving data on request with a random time delay,
    a random user agent and a proxy. There is also a time limit for receiving a request."""
    data_ = None
    # 10 попыток запросов на сервер с временной отсрочкой сменой ip и user-agent
    for i in range(5):
        sleep(uniform(*random_wait))
        # choice proxy
        proxy_ = None
        if proxy_:
            prx = {
                'http': 'http://' + proxy_,
                'https': 'http://' + proxy_,
            }
        else:
            prx = None
        # choice user agent
        u_agent_ = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2740.77 Safari/537.36'
        u_agent = {
            'user-agent': u_agent_,
            'accept': '*/*'
        }
        try:
            data_ = request_data(url, u_agent, prx)
        except Exception as e:
            print('get_request_data', f'{str(e)}')
        finally:
            if data_ is not None and data_.status_code == 200:
                data_.encoding = 'utf-8'
                break
    return data_


def request_data(url, headers=None, proxies=None, timeout=None):
    """Receiving data on request with a user agent, proxy.
    There is also set a time limit for receiving a request."""
    r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
    return r


class Parser(threading.Thread):
    def __init__(self, spreadsheet, bot_id=None, name=None):
        super(Parser, self).__init__()
        self.id = uuid.uuid4() if bot_id is None else bot_id
        self.parser_name = name
        self.spreadsheet_link = spreadsheet
        self.spreadsheet_id = get_spreadsheet_id(spreadsheet)
        self._stop_event = threading.Event()
        self.g_service = None
        parser_info.update({'spreadsheet': spreadsheet})
        parser_info.update({'parser': self})

    def __del__(self):
        print(f'instance {self.id} - deleted')

    @property
    def instance_id(self):
        return str(self.id)

    @property
    def name(self):
        return self.parser_name

    @property
    def spreadsheet(self):
        return self.spreadsheet_link

    def stop(self):
        self._stop_event.set()
        parser_info.pop('parser')
        parser_info.pop('spreadsheet')
        print(f'parser with id {self.id} is stopped')

    def stopped(self):
        return self._stop_event.is_set()

    def run(self) -> None:
        self.job()
        job = schedule.every(10).minutes.do(self.job)
        while True:
            if self.stopped():
                schedule.cancel_job(job)
                break
            schedule.run_pending()
            sleep(1)

    def job(self):
        data, row_count = self.get_table_data()
        for i in range(row_count):
            row = data.get('values')[i]
            url = row[0]
            if 'https://' in url:
                r = get_request_data(url)
                print(r.status_code)
                if r and r.status_code == 200:
                    soup = Bs(r.text, 'html.parser')
                    row = []
                    title = None
                    try:
                        title = soup.select(
                            '#container > div.product-detail__same-part-kt.same-part-kt > div > '
                            'div.same-part-kt__header-wrap.hide-mobile > h1')[0].text.strip()
                    except Exception as e:
                        print(str(e))
                    row.append(title)
                    price_txt = None
                    try:
                        price_txt = soup.select(
                            '#infoBlockProductCard > div.same-part-kt__price-block > '
                            'div > div > p > span')[0].text.strip()
                    except Exception as e:
                        print(str(e))
                    price = ''
                    if price_txt:
                        for ch in price_txt:
                            if ch.isdigit():
                                price += ch
                    row.append(price)
                    range_ = get_range([2, i + 1], [4, i + 1])
                    print(range_)
                    add_text_to_sheet(self._get_g_service(), self.spreadsheet_id, [row], range_, 'ROWS')

    def change_spreadsheet(self, spreadsheet):
        self.spreadsheet_link = spreadsheet
        self.spreadsheet_id = get_spreadsheet_id(spreadsheet)
        parser_info.update({'spreadsheet': spreadsheet})

    def _get_g_service(self):
        if self.g_service is None:
            self.g_service = get_service()
        return self.g_service

    def get_table_data(self):
        data = get_data_from_sheet(self._get_g_service(), self.spreadsheet_id, range_='A1:B', major_dimension='ROWS')
        rows = data.get('values')
        row_count = len(rows) if rows else 0
        print('table data:', data)
        print('row count: ', row_count)
        return data, row_count

