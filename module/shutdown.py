import time
import os
from .util import compare_time


def shutdown(args):
    # 分别获取当前的时、分、秒
    now_time = time.localtime()
    now_time = [now_time.tm_hour, now_time.tm_min, now_time.tm_sec]
    shutdown_time = args.shutdown

    if compare_time(now_time, shutdown_time):
        shutdown_time[0] += 24

    shutdown_sec = get_seconds(shutdown_time) - get_seconds(now_time)

    os.system('shutdown -s -t %d' % shutdown_sec)


def get_seconds(time_list):
    return time_list[0] * 3600 + time_list[1] * 60 + time_list[2]
