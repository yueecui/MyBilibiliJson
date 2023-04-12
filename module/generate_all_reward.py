import logging
import re
import os
import sys
import json
import time
from .requests_module import requests_get
from .bili_activity_award import BiliActivityAward


def generate_all_reward(args):
    # 获取所有需要生成的奖励列表
    task_list = parse_activity_reward(args)
    # 生成对应的bat
    generate_bat(task_list)


def parse_activity_reward(args):
    url = args.url
    if re.match(r'https://www.bilibili.com/blackboard/activity-[^.]+?.html', url) is None:
        raise ValueError('输入地址不是正确的活动网页地址')

    response = requests_get(url)
    html = response.text
    find = re.findall(r'window.__initialState = (.+);\n', html)
    if not find:
        find = re.findall(r'window\.__initialState=(.+)', html)
    if not find:
        raise Exception('查找 initialState 失败')
    # initial_state = json.loads(find[0])

    task_list = []
    all_task = re.findall(
        r'"https://www\.bilibili\.com/blackboard/activity-award-exchange\.html\?task_id=([^\s]{8}).*?"',
        find[0]
    )
    for task_id in all_task:
        time.sleep(args.sleep_time)
        award = BiliActivityAward(task_id)
        if not award.is_exist:
            logging.info(f'任务{task_id}：信息为空，跳过生成')
            continue
        if len(args.keyword) > 0:
            find = False
            for keyword in args.keyword:
                if award.name.find(keyword) > -1:
                    find = True
                    break
            if not find:
                logging.info(f'{award.name}：任务名称和奖励中没有符合条件的关键词，跳过生成')
                continue
        if award.is_end:
            logging.info(f'{award.name}：该奖励所处活动已经结束，跳过生成')
            continue
        if not award.has_total_stock:
            logging.info(f'{award.name}：奖励已无库存，跳过生成')
            continue
        if not award.is_daily and award.receive_status == 3:
            logging.info(f'{award.name}：已领取过，跳过生成')
            continue

        task_list.append({
            'id': award.task_id,
            'name': award.name.replace('\t', '').strip(),
        })
        logging.info(f'{award.name}：已找到')
    return task_list


# 生成执行用的BAT
def generate_bat(task_list):
    root_file_list = os.listdir()
    # 移除旧的
    for bat_name in root_file_list:
        (file_name, file_type) = os.path.splitext(bat_name)
        if not re.match(r'\[.*?].+', file_name):
            continue
        bat_file_path = os.path.join(bat_name)
        if file_type == '.bat' and (not os.path.isdir(bat_file_path)) and os.path.exists(bat_file_path):
            os.remove(bat_file_path)

    exe_name = os.path.split(sys.argv[0])[1]
    count = 0
    for task in task_list:
        bat_file_path = validate_title(os.path.join(f'{task["name"]}.bat'))
        with open(bat_file_path, 'w') as f:
            # f.write(f'@{exe_name} -r {task["id"]} --profile "{get_profile_name()}"\n@pause')
            f.write(f'@{exe_name} -r {task["id"]}\n@pause')
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

    url = args.url
    if re.match(r'https://www.bilibili.com/blackboard/activity-[^.]+?.html', url) is None:
        raise ValueError('输入地址不是正确的活动网页地址')

    response = requests_get(url)
    html = response.text

    # 先查找总天数
    find = re.findall(r'window.__initialState = (.+);\n', html)
    if not find:
        find = re.findall(r'window\.__initialState=(.+)', html)
    if not find:
        raise Exception('查找 initialState 失败')

    task_list = []
    all_task = re.findall(
        r'"https://www\.bilibili\.com/blackboard/activity-award-exchange\.html\?task_id=([^\s]{8}).*?"',
        find[0]
    )
    for task_id in all_task:
        award = BiliActivityAward(task_id)
        if not award.is_exist:
            continue
        from_start_days = award.get_length_from_start()
        logging.info(f'今天是活动开始的第{from_start_days}天')
        break

    find = re.findall(r'var jumpUrl = \'https://www\.bilibili\.com/blackboard/dynamic/(\d+)\';\n', html)
    if not find:
        find = re.findall(r'jumpUrl:"https://www\.bilibili\.com/blackboard/dynamic/(\d+)"', html)
    if not find:
        raise Exception('查找 jumpUrl 失败')

    dynamic_info_url = f'https://api.bilibili.com/x/native_page/dynamic/index?page_id={find[0]}&jsonp=jsonp'
    response = requests_get(dynamic_info_url)

    data = response.json()

    progress_number = get_progress_number_v2(args, data)
    if progress_number > -1:
        logging.info(f'目前里程碑已经完成{progress_number}天')
    else:
        logging.info(f'没有找到里程碑完成数据情况')


# 第二版获取方法 2022年11月5日
def get_progress_number_v2(args, data):
    for item in data['data']['cards']:
        progress_url = find_subpage_url(args, item)
        if progress_url:
            break

    if progress_url is None:
        raise Exception('查找 progress_url 失败')
    response = requests_get(progress_url)
    html = response.text

    # 查找数据位置
    find = re.findall(r'window.__initialState = (.+);\n', html)
    if not find:
        find = re.findall(r'window\.__initialState=(.+)', html)
    if not find:
        raise Exception('查找移动端 initialState 失败')

    data = json.loads(find[0])
    task_progress = data.get('task-progress', None)
    if task_progress is None or len(task_progress) == 0:
        return -1

    sid = task_progress[0]['sid']
    counter = task_progress[0]['counter']

    task_api_url = f'https://api.bilibili.com/x/task/total?counter_names={counter}&sid={sid}&type=2'
    response = requests_get(task_api_url)
    data = response.json()

    return data['data']['list'][0]['total']

def find_subpage_url(args, item):
    if not item['goto'].startswith('click'):
        return None

    if 'uri' in item:
        find = re.findall(r'https://www\.bilibili\.com/blackboard/activity-.*?\.html', item['uri'])
        if find:
            response = requests_get(item['uri'])
            html = response.text
            find = re.findall(r'<title>.*?' + args.progress_keyword + '.*?</title>', html)
            if find:
                return item['uri']

    if 'item' in item:
        for sub_item in item['item']:
            result = find_subpage_url(args, sub_item)
            if result:
                return result

    return None


# 该方法已经过期 2022年11月5日
def get_progress_number(data):
    for item in data['data']['cards']:
        progress_number = find_progress(item)
        if progress_number > -1:
            return progress_number

    return -1


def find_progress(item) -> int:
    if item.get('goto') == 'click_progress':
        return int(item['click_ext']['display_num'])

    if item.get('item'):
        for sub_item in item.get('item'):
            number = find_progress(sub_item)
            if number > -1:
                return number

    return -1
