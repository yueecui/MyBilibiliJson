import logging
import sys
import argparse
from module.generate_all_reward import generate_all_reward, get_days_number
from module.receive_reward import receive_reward


def init():
    # 初始化logging
    logging.basicConfig(stream=sys.stdout,
                        format='[%(asctime)s][%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)


def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(
        description='My Bilibili Json',
        epilog='最后更新日期: 2021-12-16')

    # 不输入参数时显示帮助
    # 输入一个位置参数时，参数为活动地址网页（https://www.bilibili.com/blackboard/activity-8Zdc2qDY6R.html 类似），生成该网页所有奖励原石、还有货、还没领过的bat
    # bat格式为 带一个命名参数 --reward=xxxxxxx，尝试领取这个地址的奖励
    parser.add_argument('act_url', nargs='?', help='填写一个活动网页地址，生成该地址中所有奖励原石、还有存货、还没领过的奖项对应的执行批处理')
    parser.add_argument('-k', '--keyword', nargs='?', help='从活动网页保存奖励时，只包含关键词的的奖项')
    parser.add_argument('-d', '--days', action='store_true', help='配合一个活动网址，查询当前用户已经完成任务的天数')
    parser.add_argument('-p', '-u', '--profile', '--user', default='Default', help='读取的chrome profile名称。默认为Default，路径：%%LOCALAPPDATA%%\\Google\\Chrome\\User Data')
    parser.add_argument('-r', '--reward', help='尝试不停领取目标ID奖励')

    # 获取解析后的参数
    args = parser.parse_args()

    if args.act_url is not None:
        if args.days:
            get_days_number(args)
        else:
            generate_all_reward(args)
    elif args.reward is not None:
        receive_reward(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    init()
    main()


