import logging
import time
from .bili_activity_award import BiliActivityAward


def receive_reward(args):
    award = BiliActivityAward(args.reward)
    logging.info(f'任务开始：{award.name}')
    logging.info(f'===================================================================')

    check_start(args, award)
    award.update_award()

    # 启动时是否还有奖励
    start_at_has_remain = False

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
            if start_at_has_remain:
                logging.info(f'该类型奖励已经达到每日领取上限')
                break
            else:
                logging.info(f'每日领取数量已达上限')
                award.update_award()
                time.sleep(args.sleep_time)
                continue
        else:
            start_at_has_remain = True

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
        show_start_time = start_time.copy()
        if compare_time(args.day_start, start_time):
            start_time[0] += 24
        while True:
            if can_start(start_time, args.day_start):
                break

            time.sleep(1)
            logging.info(f'[开始时间 {"%02d:%02d:%02d" % (show_start_time[0], show_start_time[1], show_start_time[2])}]{award_name}')

    args.is_start = True


def can_start(start_time, day_start):
    # 分别获取当前的时、分、秒
    now_time = time.localtime()
    now_time = [now_time.tm_hour, now_time.tm_min, now_time.tm_sec]

    if compare_time(day_start, now_time):
        now_time[0] += 24

    if compare_time(now_time, start_time):
        return True
    return False


# 比较2个时间数组的大小
# 数组格式为：[小时，分钟，秒]
# 如果第一个数组大于等于第二个数组，返回True，否则返回False
def compare_time(time1, time2):
    if time1[0] > time2[0]:
        return True
    if time1[0] == time2[0]:
        if time1[1] > time2[1]:
            return True
        if time1[1] == time2[1] and time1[2] >= time2[2]:
            return True
    return False

