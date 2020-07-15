from fb.saved_items import SavedItems
from www import Chrome
import pytest


@pytest.fixture
def FB():
    fb = SavedItems()
    fb.cookies = Chrome.get_cookies('Profile 1')
    print('Logged In:', fb.is_logged_in())
    print(fb.csrf)
    # fb.update_csrf()

    return fb


def test_login(FB):
    user = FB.is_logged_in()
    print(user)
    assert user


def test_should_update_csrf(FB):
    FB.update_csrf()
    assert FB.csrf


def test_should_update_csrf(FB):
    for i in FB.fetch():
        print(i)
