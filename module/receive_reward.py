import logging
import time
from .bili_activity_award import BiliActivityAward


def receive_reward(args):
    award = BiliActivityAward(args.reward)
    logging.info(f'任务开始：{award.name}')
    logging.info(f'===================================================================')

    check_start(args, award)

    count = 0
    while True:
        if award.receive_id == 0:
            logging.info(f'没有达成领取条件')
            award.update_award()
            time.sleep(args.sleep_time)
            continue

        if award.receive_status == 3:
            logging.info(f'该奖励已经领取')
            break

        if not award.has_total_stock:
            logging.info(f'该类型奖励已经达到领取总上限')
            break

        if not award.has_daily_stock:
            logging.info(f'每日领取数量已达上限')
            award.update_award()
            time.sleep(args.sleep_time)
            continue

        if award.receive():
            logging.info(f'已领取成功，请去网页查看')
            break
        else:
            logging.info(f'正在尝试进行领取奖励')
            count += 1
            if count % 10 == 0:
                award.update_award()
            time.sleep(args.sleep_time)


def check_start(args, award):
    if args.is_start:
        return
    start_time = args.start_time
    award_name = award.name
    for keyword, time_set in args.start_config.items():
        if award_name.find(keyword) > -1:
            start_time = time_set
            break

    if start_time is not None:
        while True:
            # 分别获取当前的时、分、秒
            now_time = time.localtime()
            # 判断当前时间是否大于开始时间
            if now_time.tm_hour > start_time[0]:
                break

            if now_time.tm_hour == start_time[0]:
                if now_time.tm_min > start_time[1]:
                    break
                if now_time.tm_min == start_time[1] and now_time.tm_sec >= start_time[2]:
                    break

            time.sleep(1)
            logging.info(f'[开始时间 {"%02d:%02d:%02d" % (start_time[0], start_time[1], start_time[2])}]{award_name}')

    args.is_start = True
