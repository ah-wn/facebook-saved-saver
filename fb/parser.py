import re
from urllib import parse
import json


class ParseError(Exception):
    pass


class TokensParseException(ParseError):
    pass


def url(url):
    parsed = parse.urlparse(url)
    result = {'query_json': dict(parse.parse_qsl(parsed.query))}
    result.update(parsed._asdict())
    return result


def rx_json_var(key):
    return re.compile(fr'{key}[\'"]\s*:\s*[\'"]([^"\']+)')


find_csrf_token = rx_json_var('(async_get_token|token)').findall
photos_count = re.compile(r'(\d+) Photos?').findall


def post_item_if_photos(text):
    count = photos_count(text)
    if count:
        return int(count[0])
    return 0


def extract_csrf(text):
    raw = find_csrf_token(text)
    return dict(raw)


def extract_csrf_from_html(html):
    for i in html.find('script'):
        text = i.text.strip()
        if 'DTSGInitData' in text:
            return extract_csrf(text)


def parse_error(data):
    error = data.get('error', 'ERROR')
    errorSummary = data.get('errorSummary', '')
    errorDescription = data.get('errorDescription', '')
    text = f'[{errorSummary}-{error}]=>{errorDescription}'.upper()
    return text


def parse_saved_json_response_html(data):
    domops = data.get('domops', {})
    if not domops:
        error = parse_error(data)
        raise ParseError(error)

    try:
        html = domops[0][3]['__html']
    except Exception:
        raise ParseError(domops)

    return html


def remove_params(url, params=('fbclid', 'eid', 'ref')):
    url = parse_link(url)
    u = parse.urlparse(url)
    q = dict(parse.parse_qsl(u.query))
    for i in params:
        q.pop(i, '')
    q = parse.urlencode(q)
    return u._replace(query=q).geturl()


def parse_link(link):
    _url = url(link)

    if _url['netloc'] == 'l.facebook.com':
        link = _url['query_json']['u']

    return link
