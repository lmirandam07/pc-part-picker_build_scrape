import os
import time
import json
import requests
import utilities
import traceback
from random import randint, choice
from bs4 import BeautifulSoup

FILE_NAME = 'builds.json'


def get_builds_amount():
    with open(f'{FILE_NAME}', 'r') as f:
        builds = json.load(f)

    return len(builds)


def clean_price(price):
    if price[0] == '$':
        price = price.replace('$', '').strip()
        if len(price.split(' ')) > 1:
            return None
    else:
        return None

    return float(price)


def get_links():
    if os.path.exists(f'./{FILE_NAME}'):
        with open(f'{FILE_NAME}', 'r') as f:
            links = json.load(f)

        # If links only has one key in json means that hasn't been scraped
        non_scraped_links = [(pos, link) for pos, link in enumerate(
            links) if link and len(link) == 1]
        if len(non_scraped_links) > 0:
            return non_scraped_links

    return []


def save_build(build, pos):
    if build:
        with open(f'{FILE_NAME}', 'r+') as f:
            builds = json.load(f)
            builds[pos] = build
            f.seek(0)
            json.dump(builds, f, indent=4)
    else:
        # If build link doesn't work delete it
        with open(f'{FILE_NAME}', 'r') as f:
            builds = json.load(f)
            del builds[pos]['Build Link']

        with open(f'{FILE_NAME}', 'w') as f:
            json.dump(builds, f, indent=4)

def remove_empty_builds():
    with open(f'{FILE_NAME}', 'r+') as f:
        builds = json.load(f)

    cleaned_builds = [b for b in builds if b != {}]

    with open(f'{FILE_NAME}', 'w') as f:
        json.dump(cleaned_builds, f, indent=4)



def build_scraper(url, user_agent, proxy):
    builds_dict = {}
    build_comps = ['Name', 'CPU', 'CPU Cooler', 'Motherboard', 'Memory',
                   'Storage', 'Video Card', 'Case', 'Power Supply', 'Build Price']

    try:
        rq = requests.get(url, headers=user_agent, proxies=proxy)
    except Exception as e:
        print(e)
        return {}

    soup = BeautifulSoup(rq.content, 'html.parser')
    name = soup.find('h1', {"class": "build__name"})
    # If build was erased or doesn't exist
    if name == None:
        return {}

    builds_dict['Build Name'] = name.text

    comp_table_rows = soup.find(
        'table', {"class": "partlist partlist--mini"}).find_all('tr')
    extra_price = 0

    # Two rows is one component, one for the name of the comp and other for the features
    row_it = iter(comp_table_rows)
    for name, component in zip(row_it, row_it):
        try:
            name_text = name.find('h4').text.strip()
            # Getting the name and price components
            component_el = component.find(
                'td', {'class': 'td__name'}).findChildren(text=True)
            component_el = list(filter(lambda el: el != '\n', component_el))

            if len(component_el) == 2:
                comp_name = component_el[0]
                comp_price = clean_price(component_el[1])
                # If price isn't in USD
                if comp_price == None:
                    print(component_el, comp_price)
                    return {}
            else:
                comp_name, comp_price = *component_el, None

            # If the component are in the selected list for scrape
            if name_text in build_comps:
                comp_els = {'Name': comp_name, 'Price': comp_price}

                if name_text not in builds_dict:
                    builds_dict[name_text] = comp_els
                else:

                    comp_copy = builds_dict[name_text].copy()
                    builds_dict[name_text] = []
                    #  If there are already two of the same component
                    if isinstance(comp_copy, list):
                        builds_dict[name_text].extend([comp_els, *comp_copy])
                    else:
                        builds_dict[name_text].extend([comp_els, comp_copy])
            else:
                # Calculate the total of the components not taken into account
                extra_price += comp_price if isinstance(
                    comp_price, float) else 0

        except Exception as e:
            print(traceback.format_exc())
            continue

        total_table_row = soup.find('table', {
                                    "class": "block partlist partlist--mini partlist--totals"}).find('td', {"class": "td__price"}).text
        builds_dict['Build Price'] = round(
            float(total_table_row.replace('$', '')) - extra_price, 2)

    return builds_dict


def main():
    builds_links = get_links()
    user_agents = utilities.get_user_agent()
    proxies = utilities.get_proxies()

    for pos, build in builds_links:
        try:
            link = build['Build Link']
            proxy = choice(proxies)
            user_agent = choice(user_agents)
            build_url = utilities.parse_url(build_link=link)
            build_dict = build_scraper(build_url, user_agent, proxy)
            if build_dict:
                build_dict['Build Link'] = link

            save_build(build_dict, pos)

            delay = randint(2, 10)
            time.sleep(delay)

        except Exception as e:
            print(traceback.format_exc(), build)
            continue

    remove_empty_builds()
    build_amount = get_builds_amount()
    return build_amount


if __name__ == '__main__':
    builds_amount = main()
    print(builds_amount)
