import time
import math
from .requests_module import requests_post, requests_get
from .chrome_cookies import get_bilibili_cookies

RECEIVE_URL = 'https://api.bilibili.com/x/activity/mission/task/reward/receive'


class BiliActivityAward:
    def __init__(self, task_id: str):
        self._task_id = task_id
        self._csrf = get_bilibili_cookies().csrf
        self._task_url = f'https://api.bilibili.com/x/activity/mission/single_task?csrf={self._csrf}&id={task_id}'
        self._raw_data = None

    def update_award(self):
        response = requests_get(self._task_url)
        self._raw_data = response.json()

    @property
    def raw_data(self):
        if self._raw_data is None:
            self.update_award()
        return self._raw_data

    @property
    def task_id(self):
        return self._task_id

    @property
    def task_name(self):
        if self._raw_data is None:
            self.update_award()
        return self._raw_data['data']['task_info']['task_name']

    @property
    def is_exist(self):
        if self._raw_data is None:
            self.update_award()
        return not (self._raw_data['data']['act_info'] is None or self._raw_data['data']['task_info'] is None)

    @property
    def reward_name(self):
        if self._raw_data is None:
            self.update_award()
        return self._raw_data['data']['task_info']['reward_info']['reward_name']

    @property
    def receive_id(self):
        if self._raw_data is None:
            self.update_award()
        return self._raw_data['data']['task_info']['receive_id']

    @property
    def receive_status(self):
        if self._raw_data is None:
            self.update_award()
        return self._raw_data['data']['task_info']['receive_status']

    @property
    def name(self):
        if self._raw_data is None:
            self.update_award()
        daily, total = self.get_stock_config()
        if daily > 0 and total > 0:
            return f'[{self._task_id}]{self.task_name} - {self.reward_name}({daily},{total})'
        else:
            return f'[{self._task_id}]{self.task_name} - {self.reward_name}'

    @property
    def has_total_stock(self):
        if self._raw_data is None:
            self.update_award()
        for reward_stock in self._raw_data['data']['task_info']['reward_stock_configs']:
            if reward_stock['cycle_type'] == 1:
                return reward_stock['total'] > reward_stock['consumed']
        return False

    @property
    def has_daily_stock(self):
        if self._raw_data is None:
            self.update_award()
        for reward_stock in self._raw_data['data']['task_info']['reward_stock_configs']:
            if reward_stock['cycle_type'] == 2:
                return reward_stock['total'] > reward_stock['consumed']
        return False

    # true表示是日常奖励，false表示是一次性奖励
    @property
    def is_daily(self):
        if self._raw_data is None:
            self.update_award()
        return self._raw_data['data']['task_info']['task_period'] > 0

    # true表示是活动已经结束，false表示活动还在进行中
    @property
    def is_end(self):
        if self._raw_data is None:
            self.update_award()
        return time.time() >= self._raw_data['data']['act_info']['end_time']

    def get_stock_config(self):
        if self._raw_data is None:
            self.update_award()
        daily = 0
        total = 0
        data = self._raw_data['data']
        if data is None:
            return daily, total
        task_info = data.get('task_info')
        if task_info is None:
            return daily, total
        stock_config = task_info.get('reward_stock_configs')
        if stock_config is None:
            return daily, total

        for config in stock_config:
            if config['cycle_type'] == 2:
                daily = config['total']
            elif config['cycle_type'] == 1:
                total = config['total']
        return daily, total

    def get_start_date_timestamp(self):
        if self._raw_data is None:
            self.update_award()
        start = time.localtime(self._raw_data['data']['act_info']['begin_time'])
        return int(time.mktime(
            time.strptime(f'{start.tm_year}-{start.tm_mon}-{start.tm_mday} 00:00:00', '%Y-%m-%d %H:%M:%S')))

    # 获取今天是活动开始后的第几天
    def get_length_from_start(self):
        return math.ceil((time.time() - self.get_start_date_timestamp()) / 86400)

    # 尝试进行领取
    def receive(self):
        data = {
            'csrf': self._csrf,
            'act_id': self._raw_data['data']['task_info']['group_list'][0]['act_id'],
            'task_id': self._raw_data['data']['task_info']['group_list'][0]['task_id'],
            'group_id': self._raw_data['data']['task_info']['group_list'][0]['group_id'],
            'receive_id': self._raw_data['data']['task_info']['receive_id'],
            'receive_from': 'missionLandingPage'
        }

        response = requests_post(RECEIVE_URL, data=data)
        # with open('receive_response_content', 'wb') as f:
        #     f.write(response.content)
        # 这里有可能出现繁忙
        # 但不管，反正就是已领取之外都重新发
        if response.text.find('已领取') >= 0:
            return True
        return False
