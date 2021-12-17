from browser_cookie3 import ChromiumBased
import requests


class ChromeCookies(ChromiumBased):
    """Class for Google Chrome"""
    def __init__(self, cookie_file=None, domain_name="", key_file=None, profile_name="Default"):
        args = {
            'linux_cookies': [
                    '~/.config/google-chrome/'+profile_name+'/Cookies',
                    '~/.config/google-chrome-beta/'+profile_name+'/Cookies'
                ],
            'windows_cookies': [
                    {'env': 'APPDATA', 'path': '..\\Local\\Google\\Chrome\\User Data\\' + profile_name + '\\Cookies'},
                    {'env': 'LOCALAPPDATA', 'path': 'Google\\Chrome\\User Data\\' + profile_name + '\\Cookies'},
                    {'env': 'APPDATA', 'path': 'Google\\Chrome\\User Data\\' + profile_name + '\\Cookies'},
                    {'env': 'APPDATA', 'path': '..\\Local\\Google\\Chrome\\User Data\\' + profile_name + '\\Network\\Cookies'},
                    {'env': 'LOCALAPPDATA', 'path': 'Google\\Chrome\\User Data\\' + profile_name + '\\Network\\Cookies'},
                    {'env': 'APPDATA', 'path': 'Google\\Chrome\\User Data\\' + profile_name + '\\Network\\Cookies'}
                ],
            'osx_cookies': ['~/Library/Application Support/Google/Chrome/'+profile_name+'/Cookies'],
            'windows_keys': [
                    {'env': 'APPDATA', 'path': '..\\Local\\Google\\Chrome\\User Data\\Local State'},
                    {'env': 'LOCALAPPDATA', 'path': 'Google\\Chrome\\User Data\\Local State'},
                    {'env': 'APPDATA', 'path': 'Google\\Chrome\\User Data\\Local State'}
                ],
            'os_crypt_name': 'chrome',
            'osx_key_service': 'Chrome Safe Storage',
            'osx_key_user': 'Chrome'
        }

        super().__init__(browser='Chrome', cookie_file=cookie_file, domain_name=domain_name, key_file=key_file, **args)


def get_bilibili_cookies(profile_name="Default"):
    game_cookies = requests.cookies.RequestsCookieJar()
    for host in ['.bilibili.com']:
        cookies = ChromeCookies(domain_name=host, profile_name=profile_name).load()
        game_cookies.update(cookies)
    if len(game_cookies) == 0:
        return None
    else:
        return game_cookies


bilibili_csrf = None


def get_bilibili_csrf(profile_name="Default"):
    if bilibili_csrf is not None:
        return bilibili_csrf
    host = '.bilibili.com'
    cookies = ChromeCookies(domain_name=host, profile_name=profile_name).load()
    for cookie in cookies:
        if cookie.name == 'bili_jct':
            return cookie.value

    raise Exception('CSRF未找到，请检查是否登录了Bilibili')