import logging
import re
import json
import os
import sys
from .requests_module import requests_get, get_profile_name
from .bili_activity_award import BiliActivityAward


def generate_all_reward(args):
    # 获取所有需要生成的奖励列表
    task_list = parse_activity_reward(args)
    # 生成对应的bat
    generate_bat(task_list)


def parse_activity_reward(args):
    url = args.act_url
    if re.match(r'https://www.bilibili.com/blackboard/activity-[^\.]+?.html', url) is None:
        raise ValueError('输入地址不是正确的活动网页地址')

    response = requests_get(url)
    html = response.text
    find = re.findall(r'window.__initialState = (.+);\n', html)
    if not find:
        raise Exception('查找 initialState 失败')
    initial_state = json.loads(find[0])

    task_list = []
    for button in initial_state['button']:
        find = re.findall(r'https://www\.bilibili\.com/blackboard/activity-award-exchange\.html\?task_id=(.*)',
                          button['button_jump_url'])
        if not find:
            continue

        award = BiliActivityAward(find[0])
        if args.keyword is not None and award.reward_name.find(args.keyword) == -1:
            logging.info(f'{award.name}：奖励中没有关键词{args.keyword}，跳过生成')
            continue
        if not award.has_total_stock:
            logging.info(f'{award.name}：奖励已无库存，跳过生成')
            continue
        if not award.is_daily and award.receive_status == 3:
            logging.info(f'{award.name}：已领取过，跳过生成')
            continue

        task_list.append({
            'id': award.task_id,
            'name': award.name,
        })
        logging.info(f'{award.name}：已找到')
    return task_list


# 生成执行用的BAT
def generate_bat(task_list):
    root_file_list = os.listdir()
    # 移除旧的
    for bat_name in root_file_list:
        (file_name, file_type) = os.path.splitext(bat_name)
        if not re.match(r'\[.*?\].+', file_name):
            continue
        bat_file_path = os.path.join(bat_name)
        if file_type == '.bat' and (not os.path.isdir(bat_file_path)) and os.path.exists(bat_file_path):

            os.remove(bat_file_path)

    exe_name = os.path.split(sys.argv[0])[1]
    count = 0
    for task in task_list:
        bat_file_path = validate_title(os.path.join(f'{task["name"]}.bat'))
        with open(bat_file_path, 'w') as f:
            f.write(f'@{exe_name} -r {task["id"]} --profile "{get_profile_name()}"\n@pause')
        count += 1

    if count > 0:
        print(f'生成可执行bat文件完成！共生成{count}个')
    else:
        print(f'没有生成任何有效的项目，请检查输入地址是否存在活动')


def validate_title(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title


def get_days_number(args):
    logging.info('开始检查已完成里程碑的天数…')

    url = args.act_url
    if re.match(r'https://www.bilibili.com/blackboard/activity-[^\.]+?.html', url) is None:
        raise ValueError('输入地址不是正确的活动网页地址')

    response = requests_get(url)
    html = response.text
    find = re.findall(r'var jumpUrl = \'https://www\.bilibili\.com/blackboard/dynamic/(\d+)\';\n', html)
    if not find:
        raise Exception('查找 jumpUrl 失败')

    dynamic_info_url = f'https://api.bilibili.com/x/native_page/dynamic/index?page_id={find[0]}&jsonp=jsonp'
    response = requests_get(dynamic_info_url)

    data = response.json()
    for item in data['data']['cards']:
        progress_number = find_progress(item)
        if progress_number > -1:
            logging.info(f'目前里程碑已经完成{progress_number}天')
            return
    logging.info(f'没有找到里程碑完成数据情况')


def find_progress(item) -> int:
    if item.get('goto') == 'click_progress':
        return int(item['click_ext']['display_num'])

    if item.get('item'):
        for sub_item in item.get('item'):
            number = find_progress(sub_item)
            if number > -1:
                return number

    return -1
