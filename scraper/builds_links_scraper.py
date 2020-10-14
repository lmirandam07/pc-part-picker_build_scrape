import os
import json
import time
import utilities
import traceback
from random import choice, randint
from bs4 import BeautifulSoup

FILE_NAME = 'builds.json'

links_format = lambda links: [{'Build Link': link} for link in links]

def save_links(links):
    if not os.path.exists(f'./{FILE_NAME}'):
            # Save build href in a json file
            with open(f'{FILE_NAME}', 'w') as f:
                json.dump(links, f, indent=4)

    else:
        # Only save the new links
        with open(f'{FILE_NAME}', 'r') as f:
            old_data = json.load(f)

        old_links = [l['Build Link'] for l in old_data if l]
        #  Get the difference between new scraped links and scraped old links
        links_diff = set([l['Build Link'] for l in links])
        links_diff.difference_update(old_links)

        if links_diff:
            new_links = links_format(links_diff)
            all_data = new_links + old_data

            # print(len(new_links), len(all_data), all_data[10:30])
            with open(f'{FILE_NAME}', 'w') as f:
                json.dump(all_data, f, indent=4)

def scrape_links():
    num_pages = 5
    user_agents = utilities.get_user_agent()
    proxies = utilities.get_proxies()
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

    save_links(links_scraped)

    return True


if __name__ == '__main__':
    scrape_links()