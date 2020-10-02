import os
import time
import json
import utilities
import traceback
from random import randint
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
    user_agent = utilities.get_user_agent()
    file_name = 'builds.json'
    links = []
    for i in range(1, num_pages+1):
        try:
            url = utilities.parse_url(page=i)
            browser = utilities.get_driver(user_agent=user_agent)
            browser.get(url)
            time.sleep(randint(2, 5))
            soup = BeautifulSoup(browser.page_source, 'html.parser')

            # Get the link of all build cards in a single page
            links_el = soup.find_all("a", {"class": "logGroup__target"}, href=True)
            links = [{'link': a['href']} for a in links_el]
            browser.close()
        except Exception as e:
            browser.close()
            print(traceback.format_exc())
            continue

    if not os.path.exists(f'./{file_name}'):
        # Save build href in a json file
        with open(f'{file_name}', 'w') as f:
            json.dump(links, f, indent=2)

    else:
        # Only save the new links
        with open(f'{file_name}', 'r+') as f:
            new_links = []
            data = json.load(f)
            data_list = [d['link'] for d in data]
            for link in links:
                if link['link'] not in data_list:
                    new_links.append(link)
                else:
                    break
            # Update json with new links
            if new_links:
                f.seek(0)
                new_links.extend(data)
                del data
                json.dump(new_links, f, indent=2)

if __name__ == '__main__':
    scrape_links()