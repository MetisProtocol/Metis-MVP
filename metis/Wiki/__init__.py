# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: __init__.py.py
@time: 2020/5/9 11:44 上午
@desc:
"""
from requests import Session
from metis.config.Const import WIKI_API

__all__ = ["Wiki"]


class Wiki:

    def __init__(self):
        self.wiki_session = Session()
        self.token = None
        self.csrf_token = None

    def fetch_token(self):
        # Step 1: GET request to fetch login token
        params_0 = {
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json"
        }

        res = self.wiki_session.get(url=WIKI_API, params=params_0)
        data = res.json()
        self.token = data['query']['tokens']['logintoken']

    def login(self, token):
        # Step 2: POST request to log in. Use of main account for login is not
        # supported. Obtain credentials via Special:BotPasswords
        # (https://www.mediawiki.org/wiki/Special:BotPasswords) for lgname & lgpassword
        params_1 = {
            "action": "login",
            "lgname": "admin",
            "lgpassword": "uhnMqv9m3LT81q2xVcO4YxAbXwvJLu",
            "lgtoken": token,
            "format": "json"
        }

        self.wiki_session.post(WIKI_API, data=params_1)

    def fetch_csrf_token(self):
        # Step 3: GET request to fetch CSRF token
        params_2 = {
            "action": "query",
            "meta": "tokens",
            "format": "json"
        }

        res = self.wiki_session.get(url=WIKI_API, params=params_2)
        data = res.json()
        self.csrf_token = data['query']['tokens']['csrftoken']

    def edit(self, wiki_title: str, append_text: str):
        self.fetch_token()
        self.login(self.token)
        self.fetch_csrf_token()
        # Step 4: POST request to edit a page
        # 整个流程是wiki官方给的api演示提供的
        params_3 = {
            "action": "edit",
            "title": wiki_title,  # title不存在，自动创建一个新页面
            "token": self.csrf_token,
            "format": "json",
            "appendtext": append_text  # 在该页面上接着添加文本
        }

        self.wiki_session.post(WIKI_API, data=params_3)

    def create(self, title: str):
        template = """
        \r\n== 目的 == \r\n
        \r\n== 可衡量的结果 == \r\n
        \r\n== 时间要求 == \r\n
        \r\n== 需质押的MIS Token == \r\n
        \r\n== 交付物 == \r\n

        """
        self.fetch_token()
        self.login(self.token)
        self.fetch_csrf_token()

        params_3 = {
            "action": "edit",
            "title": title,  # title不存在，自动创建一个新页面
            "token": self.csrf_token,
            "format": "json",
            "appendtext": template  # 在该页面上接着添加文本
        }
        print("将数据写入wiki")

        self.wiki_session.post(WIKI_API, data=params_3)


if __name__ == '__main__':
    # wiki测试
    wiki = Wiki()
    wiki.edit('test_work10', '\r\n你好你好阿里圣诞节富利卡束带结发考虑拉上肯德基富利卡束带结发\r\n')
    # wiki.create('基于Metis协议搭建不同领域的DAC，并进行手动治理')
