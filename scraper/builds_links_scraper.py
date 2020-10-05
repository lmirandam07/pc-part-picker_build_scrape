import os
import time
import json
import utilities
import traceback
from random import choice, randint
from bs4 import BeautifulSoup

def get_links():
    file_name = 'builds.json'
    if os.path.exists(f'./{file_name}'):
        with open(f'{file_name}', 'r') as f:
            data = json.load(f)
    else:
        return None

    return data if len(data) > 0 else None

def scrape_links():
    num_pages = 1
    user_agents = utilities.get_user_agent()
    proxies = utilities.get_proxies()
    file_name = 'builds.json'
    links_format = lambda links: [{'link': link} for link in links]
    links_scraped = []
    for i in range(1, num_pages+1):
        try:
            proxy = choice(proxies)
            user_agent = choice(user_agents)
            url = utilities.parse_url(page=i)
            browser = utilities.get_driver(user_agent, proxy)
            browser.get(url)
            time.sleep(randint(2, 5))
            soup = BeautifulSoup(browser.page_source, 'html.parser')

            # Get the link of all build cards per page
            links_el = soup.find_all("a", {"class": "logGroup__target"}, href=True)
            links_el = [l_el['href'] for l_el in links_el]
            links_scraped += links_format(links_el)
            browser.close()
        except Exception as e:
            browser.close()
            print(traceback.format_exc())
            continue

    if not os.path.exists(f'./{file_name}'):
        # Save build href in a json file
        with open(f'{file_name}', 'w') as f:
            json.dump(links_scraped, f, indent=2)

    else:
        # Only save the new links
        with open(f'{file_name}', 'r+') as f:
            old_links = json.load(f)
            old_links = [l['link'] for l in old_links]
            #  Get the difference between scraped links and scraped old links
            links_diff = set([l['link'] for l in links_scraped])
            links_diff.difference_update(old_links)

            if links_diff:
                f.seek(0)
                new_links = links_format([*links_diff, *old_links])
                del old_links
                json.dump(new_links, f, indent=2)

if __name__ == '__main__':
    scrape_links()