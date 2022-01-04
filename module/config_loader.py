import configparser
import os
import logging


def config_loader(config_path):
    # 获取配置文件
    if not os.path.exists(config_path):
        raise FileExistsError('配置文件《%s》未找到，请检查。' % os.path.split(config_path)[1])

    cfg = configparser.ConfigParser()
    try:
        cfg.read(config_path, encoding='GBK')
    except UnicodeDecodeError:
        cfg.read(config_path, encoding='UTF-8')

    config = new_ordered_dict()

    for cfg_section in cfg.sections():
        if cfg_section not in config:
            config[cfg_section] = new_ordered_dict()
        for cf_key, cf_value in cfg[cfg_section].items():
            config[cfg_section][cf_key] = cf_value

    # 错误检查
    for check_section_name, check_info_list in error_check_list.items():
        if check_section_name not in config:
            log('配置文件错误：没有找到“%s”段落，请检查。' % check_section_name)
            return None
        for check_info in check_info_list:
            if check_info['n'] not in config[check_section_name]:
                if check_info['t'] == 'check_value':
                    config[check_section_name][check_info['n']] = check_info['d']
                else:
                    log('配置文件错误：“%s”段落中没有参数“%s”，请检查。' % (check_section_name, check_info['n']))
                    return None

            value = config[check_section_name][check_info['n']]
            if check_info['t'] == 'path_exists':
                if not os.path.exists(value):
                    log('文件夹未找到：“%s”，请检查。' % os.path.abspath(value))
            elif check_info['t'] == 'file_exists':
                if not os.path.exists(value):
                    log('文件未找到：“%s”，请检查。' % os.path.abspath(value))
            elif check_info['t'] == 'path_create':
                check_folder(value)

    if section_name != '' and section_name in config:
        return config[section_name]
    else:
        return config
