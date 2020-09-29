def get_proxies():
    pass


def get_user_agent():
    user_agent = [
        {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0'},
        {'User-Agent': ''}
    ]

    return user_agent[0]


def parse_url(page=1, low_range=250, up_range=5000, build_link=None):
    base_url = 'https://pcpartpicker.com'
    if build_link == None:
        fragment = f'/builds/#B=1&page={page}&X={low_range}00,{up_range}00'
    else:
        fragment = f'{build_link}'

    return f'{base_url}{fragment}'
