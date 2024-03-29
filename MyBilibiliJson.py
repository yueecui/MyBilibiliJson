import logging
import sys
import argparse
import re
import time
from module.generate_all_reward import generate_all_reward, get_days_number
from module.receive_reward import receive_reward
from module.chrome_cookies import init_bilibili_cookies
from module.config_loader import config_loader
from module.shutdown import shutdown


def init_logging(debug):
    # 初始化logging
    logging.basicConfig(stream=sys.stdout,
                        format='[%(asctime)s][%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.DEBUG if debug else logging.INFO)


# 更新参数
def update_args_from_config(args):
    # 读取配置文件
    cfg = config_loader('config.ini')
    # 初始化通用参数
    args.profile = cfg.get('GENERAL', 'profile')

    # 初始化查找时的参数
    args.url = cfg.get('FIND_CONFIG', 'url')
    args.progress_keyword = cfg.get('FIND_CONFIG', 'progress_keyword')
    args.keyword = cfg.get('FIND_CONFIG', 'keyword')
    if args.keyword == '':
        args.keyword = []
    else:
        args.keyword = args.keyword.replace('，', ',').split(',')

    # 初始化领取奖励时的参数
    args.sleep_time = cfg.getfloat('RECEIVE_CONFIG', 'sleep_time')
    args.start_time = find_start_time(cfg.get('RECEIVE_CONFIG', 'start_time'))
    args.day_start = find_start_time(cfg.get('RECEIVE_CONFIG', 'day_start'))
    if args.day_start is None:
        args.day_start = [3, 0, 0]

    args.start_config = {}
    if 'RECEIVE_START_TIME_MAP' in cfg:
        for key in cfg['RECEIVE_START_TIME_MAP']:
            args.start_config[key] = find_start_time(cfg.get('RECEIVE_START_TIME_MAP', key))

    args.is_start = False

    # 关机时间
    if args.shutdown is not None:
        args.shutdown = find_start_time(args.shutdown)

    return args


# 使用正则表达式找到HH:MM:SS，三个时间
def find_start_time(start_time_raw: str):
    find_time = re.findall(r'^(\d{1,2}):(\d{1,2}):(\d{1,2})$', start_time_raw.strip())
    if find_time:
        return [int(find_time[0][0]), int(find_time[0][1]), int(find_time[0][2])]
    else:
        return None


def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(
        description='My Bilibili Json',
        epilog='最后更新日期: 2023-03-01')

    # 不输入参数时显示帮助
    # 输入一个位置参数时，参数为活动地址网页（https://www.bilibili.com/blackboard/activity-8Zdc2qDY6R.html 类似），生成该网页所有奖励原石、还有货、还没领过的bat
    # bat格式为 带一个命名参数 --reward=xxxxxxx，尝试领取这个地址的奖励
    # parser.add_argument('url', nargs='?', help='填写一个活动网页地址，生成该地址中所有奖励原石、还有存货、还没领过的奖项对应的执行批处理')
    # parser.add_argument('-k', '--keyword', nargs='?', help='从活动网页保存奖励时，只包含关键词的的奖项')
    parser.add_argument('-d', '--days', action='store_true', help='查询当前用户已经完成任务的天数')
    # parser.add_argument('-p', '-u', '--profile', '--user', default='Default',
    #                     help='读取的chrome profile名称。默认为Default，路径：%%LOCALAPPDATA%%\\Google\\Chrome\\User Data')
    parser.add_argument('-r', '--reward', help='尝试不停领取目标ID奖励')
    parser.add_argument('--shutdown', action='store', help='关机时间，格式为HH:MM:SS')
    parser.add_argument('--debug', action='store_true', help='输出调试log')

    # 获取解析后的参数
    args = update_args_from_config(parser.parse_args())

    # 初始化logging
    init_logging(args.debug)

    init_bilibili_cookies(args.profile)

    if args.reward is not None:
        while True:
            try:
                receive_reward(args)
                break
            except Exception as e:
                logging.error('运行时出现错误，错误信息：%s' % e)
                logging.info(str(args.sleep_time)+'秒后开始重新运行')
                time.sleep(args.sleep_time)
    elif args.shutdown is not None:
        shutdown(args)
    elif args.url is not None:
        if args.days:
            get_days_number(args)
        else:
            generate_all_reward(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
