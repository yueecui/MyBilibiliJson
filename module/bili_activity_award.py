import logging
import re
import json
from .requests_module import requests_post, requests_get
from .chrome_cookies import get_bilibili_csrf

RECEIVE_URL = 'https://api.bilibili.com/x/activity/mission/task/reward/receive'


class BiliActivityAward:
    def __init__(self, task_id: str):
        self._task_id = task_id
        self._task_url = f'https://api.bilibili.com/x/activity/mission/single_task?csrf={get_bilibili_csrf()}&id={task_id}'
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
        return f'[{self._task_id}]{self.task_name} - {self.reward_name}'

    @property
    def has_stock(self):
        if self._raw_data is None:
            self.update_award()
        for reward_stock in self._raw_data['data']['task_info']['reward_stock_configs']:
            if reward_stock['cycle_type'] == 1:
                return reward_stock['total'] > reward_stock['consumed']
        return False

    # true表示是日常奖励，false表示是一次性奖励
    @property
    def is_daily(self):
        if self._raw_data is None:
            self.update_award()
        return self._raw_data['data']['task_info']['task_period'] > 0

    # 尝试进行领取
    def receive(self):
        data = {
            'csrf': get_bilibili_csrf(),
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


