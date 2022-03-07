import configparser
import os

# 默认配置
DEFAULT_CONFIG = {
    'GENERAL': {
        'profile': 'Default',
    },
    'FIND_CONFIG': {
        'url': '',
        'keyword': '',
    },
    'RECEIVE_CONFIG': {
        'sleep_time': 0.3,
        'day_start': '03:00:00',
        'start_time': '',
    }
}


def config_loader(config_path):
    # 获取配置文件
    if not os.path.exists(config_path):
        raise FileExistsError('配置文件《%s》未找到，请检查。' % os.path.split(config_path)[1])

    cfg = configparser.ConfigParser()
    cfg.read_dict(DEFAULT_CONFIG)
    try:
        cfg.read(config_path, encoding='GBK')
    except UnicodeDecodeError:
        cfg.read(config_path, encoding='UTF-8')

    # 错误检查
    return cfg
