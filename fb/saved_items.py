from fb import Facebook
from fb.entities.saved_item import SavedItem


class SavedItems(Facebook):
    def get_saved_page(self):
        url = 'https://www.facebook.com/saved/'
        res = self.client.get(url)
        return res

    def update_csrf(self, html=None):
        if not html:
            res = self.get_saved_page()
            html = res.html
            tokens = self.parse.extract_csrf_from_html(html)
        else:
            tokens = self.parse.extract_csrf(html)
        assert {'token', 'async_get_token'} == set(tokens.keys())
        self.csrf = tokens

    def ajax_get_saved_more(self, params):
        response = self.client.get(
            'https://www.facebook.com/saved/more/', params=params)
        data = response.json()
        html = self.parse.parse_saved_json_response_html(data)
        response._html = self.make_html(html)
        return response

    def get_saved_more(self):
        fb_dtsg_ag = self.csrf['async_get_token']
        params = {'__a': '1', 'fb_dtsg_ag': fb_dtsg_ag}

        while True:
            response = self.ajax_get_saved_more(params)
            self.update_csrf(response.text)
            html = response.html
            yield html

            try:
                more_pager = html.find(
                    SavedItem.MORE_PAGER_CSS, first=1).attrs['ajaxify']
                more_pager = self.parse.url(more_pager)
                cursor = more_pager['query_json']['cursor']
                if not cursor:
                    raise AttributeError
            except AttributeError as err:
                break
            params['cursor'] = cursor

    def fetch(self):
        saved_iter = self.get_saved_more()
        for html in saved_iter:
            yield from map(SavedItem, html.find(SavedItem.ITEMS_CSS))

    def remove(self, item_id):
        token = self.csrf['token']
        return self.client.post('https://www.facebook.com/save/story/', stream=True,
                                params={
                                    'object_id': item_id,
                                    'action': 'UNSAVE',
                                    'mechanism': 'xout_button',
                                    'surface': 'save_dashboard',
                                    'fb_dtsg': token
                                })
