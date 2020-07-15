from requests_html import (HTMLSession, HTML)
from youtube_dl import YoutubeDL
from pathlib import Path
from . import parser
import shelve


class Facebook(object):
    parse = parser
    URL = 'https://facebook.com'

    class UserNotLoggedIn(Exception):
        pass

    def graph_url(self, id_):
        return f'http://graph.facebook.com/{id_}/picture'

    path = Path(__file__).parent / '.data'
    path.mkdir(exist_ok=True)

    def config(self):
        return shelve.open(f"{self.path / '.config'}", 'c')

    def __init__(self):
        self.client = HTMLSession()

        def response_hook(response, *args, **kwargs):
            unwanted_prefix = b'for (;;);'
            if response.content.startswith(unwanted_prefix):
                response._content = response.content[len(unwanted_prefix):]
            # print(r)

        self.client.hooks['response'].append(response_hook)
        self.__csrf = self.config()

    @classmethod
    def make_html(cls, raw_html):
        html = HTML(html=raw_html)
        html.url = cls.URL
        return html

    @property
    def csrf(self):
        return self.__csrf['csrf']

    @csrf.setter
    def csrf(self, data):
        self.__csrf['csrf'] = data

    @classmethod
    def join(cls, url):
        return cls.parse.parse.urljoin(cls.URL, url)

    def is_logged_in(self):
        for i in self.cookies:
            if i.domain == '.facebook.com' and i.name == 'c_user':
                return int(i.value)
        else:
            return False

    @property
    def cookies(self):
        return self.client.cookies

    @cookies.setter
    def cookies(self, value):
        self.client.cookies = value

    def home(self):
        return self.client.get(self.URL)

    def youtube_dl(self, *args, **kwargs):
        ydl = YoutubeDL(**kwargs)
        for cookie in self.cookies:
            ydl.cookiejar.set_cookie(cookie)
        return ydl
