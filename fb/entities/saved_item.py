from pprint import pformat
import fb.parser as parser


class SavedItem(object):
    MORE_PAGER_CSS = 'div.uiMorePager a[rel=ajaxify]'
    ITEMS_CSS = '#saveContentFragment div[id^=item-]'

    def __init__(self, html):
        # self.html = html
        self.id = html.attrs['id'][5:]
        item_info_css = 'div._tev div._4bl9._5yjp'

        info = html.find(item_info_css, first=1)
        # self.info = info
        a = info.find('div>a._24-s', first=1)
        span = info.find('span._5znp', first=1)
        self.url = parser.parse_link(a.absolute_links.pop())
        self.title = getattr(a, 'text', '').strip()

        if span:
            span = span.text.strip()
            if span == 'Post':
                span = info.find('div._3vo5._268b', first=1).text
                self.photos = parser.post_item_if_photos(span)

        try:
            self.orig = html._make_absolute(
                html.find('a._24-t[href]', first=1).attrs['href'])
        except AttributeError as e:
            print(e, self.url, span, '=================')
            self.orig = self.url

    def __repr__(self):
        return pformat(vars(self))
