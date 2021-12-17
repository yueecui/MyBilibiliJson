import logging
import sys
import argparse
from module.generate_all_reward import generate_all_reward
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
    parser.add_argument('-k', '--keyword', nargs='?', help='保存奖励中包含关键词的的奖项')
    parser.add_argument('-r', '--reward', help='尝试不停领取目标ID奖励')

    # 获取解析后的参数
    args = parser.parse_args()

    if args.act_url is not None:
        generate_all_reward(args)
    elif args.reward is not None:
        receive_reward(args.reward)
    else:
        parser.print_help()


if __name__ == '__main__':
    init()
    main()


