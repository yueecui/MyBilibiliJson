import logging
import time
from .bili_activity_award import BiliActivityAward


def receive_reward(reward_id: str):
    award = BiliActivityAward(reward_id)

    logging.info(f'开始领取{award.name}')

    while True:
        if award.receive_id == 0:
            logging.info(f'没有达成领取条件，正在重试')
            award.update_award()
            time.sleep(0.3)
            continue

        if award.receive_status == 3:
            logging.info(f'该奖励已经领取')
            break

        if award.receive():
            logging.info(f'已领取成功，请去网页查看')
            break

        time.sleep(0.3)
