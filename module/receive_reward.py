import logging
import time
from .bili_activity_award import BiliActivityAward


def receive_reward(args):
    reward_id = args.reward
    award = BiliActivityAward(reward_id)

    logging.info(f'开始领取{award.name}')

    count = 0

    while True:
        if award.receive_id == 0:
            logging.info(f'没有达成领取条件，正在重试')
            award.update_award()
            time.sleep(0.3)
            continue

        if award.receive_status == 3:
            logging.info(f'该奖励已经领取')
            break

        if not award.has_daily_stock:
            logging.info(f'每日领取数量已达上限')
            break

        if award.receive():
            logging.info(f'已领取成功，请去网页查看')
            break
        else:
            logging.info(f'正在尝试进行领取奖励')
            count += 1
            if count % 10 == 0:
                award.update_award()
            time.sleep(0.3)
